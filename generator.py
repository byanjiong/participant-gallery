import os
from datetime import datetime
from types import SimpleNamespace
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
import config  # We import this ONLY to read defaults
import utils

try:
    from PIL import Image
    from reportlab.lib.utils import ImageReader
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: 'Pillow' library not found. Image optimization disabled.")

class PDFGenerator:
    def __init__(self, filename, pagesize, header_items, participants, meta_info=None, custom_config=None):
        """
        Initializes the generator with an optional custom_config dictionary.
        If custom_config is provided, it overrides values from config.py.
        """
        # 1. Load Defaults
        # We assume all UPPERCASE variables in config.py are settings.
        # We create a dictionary of these defaults.
        default_settings = {k: v for k, v in vars(config).items() if k.isupper()}
        
        # 2. Apply Custom Overrides
        if custom_config:
            default_settings.update(custom_config)
            
        # 3. Create a Configuration Object
        # SimpleNamespace allows us to access settings like objects: self.cfg.COL_WIDTH
        self.cfg = SimpleNamespace(**default_settings)

        # 4. Handle Page Size Logic
        # Update the config object with the runtime page size
        self.cfg.PAGE_WIDTH, self.cfg.PAGE_HEIGHT = pagesize
        
        # 5. Recalculate Dynamic Values (Widths)
        # Since margins or page size might have changed, we must recalculate COL_WIDTH here.
        available_width = self.cfg.PAGE_WIDTH - self.cfg.MARGIN_LEFT - self.cfg.MARGIN_RIGHT
        total_gaps_width = (self.cfg.COLUMNS - 1) * self.cfg.GRID_GAP_X
        self.cfg.COL_WIDTH = (available_width - total_gaps_width) / self.cfg.COLUMNS

        # 6. Setup Canvas and State
        self.c = canvas.Canvas(filename, pagesize=pagesize)
        self.header_items = header_items
        self.participants = participants
        self.meta_info = meta_info if meta_info else []
        self.cursor_y = self.cfg.PAGE_HEIGHT - self.cfg.MARGIN_TOP
        self.page_number = 1
        
        # 7. Register Fonts
        self.register_fonts()

    def register_fonts(self):
        fonts_to_register = [
            (self.cfg.FONT_NAME_REGULAR, self.cfg.FONT_PATH_REGULAR),
            (self.cfg.FONT_NAME_BOLD, self.cfg.FONT_PATH_BOLD)
        ]

        for name, path in fonts_to_register:
            try:
                pdfmetrics.registerFont(TTFont(name, path))
            except Exception as e:
                print(f"WARNING: Could not load font '{name}' from '{path}'. Defaulting to Helvetica.")
                # Fallback in our local config object only
                if name == self.cfg.FONT_NAME_REGULAR:
                    self.cfg.FONT_NAME_REGULAR = "Helvetica"
                elif name == self.cfg.FONT_NAME_BOLD:
                    self.cfg.FONT_NAME_BOLD = "Helvetica-Bold"

    def resolve_meta_text(self, text, page_num):
        now = datetime.now()
        resolved = text.replace("{{dd}}", now.strftime("%d"))
        resolved = resolved.replace("{{mm}}", now.strftime("%m"))
        resolved = resolved.replace("{{yyyy}}", now.strftime("%Y"))
        resolved = resolved.replace("{{page}}", str(page_num))
        return resolved

    def draw_meta_info(self):
        if not self.meta_info:
            return

        w, h = self.cfg.PAGE_WIDTH, self.cfg.PAGE_HEIGHT
        
        for item in self.meta_info:
            text_template = item.get('text', '')
            font = item.get('font', 'Helvetica')
            size = item.get('size', 10)
            color = item.get('color', black)
            pos = item.get('position', 1)
            padding = item.get('padding', 10)

            resolved_text = self.resolve_meta_text(text_template, self.page_number)
            
            self.c.setFont(font, size)
            self.c.setFillColor(color)
            
            # Position Logic
            if pos in [1, 4, 7]: x = padding; align = 'left'
            elif pos in [2, 5, 8]: x = w / 2; align = 'center'
            elif pos in [3, 6, 9]: x = w - padding; align = 'right'
            else: x = padding; align = 'left'

            if pos in [1, 2, 3]: y = padding
            elif pos in [4, 5, 6]: y = h / 2
            elif pos in [7, 8, 9]: y = h - padding - size 
            else: y = padding

            if align == 'center': self.c.drawCentredString(x, y, resolved_text)
            elif align == 'right': self.c.drawRightString(x, y, resolved_text)
            else: self.c.drawString(x, y, resolved_text)

    def apply_header_defaults(self, item):
        defaults = self.cfg.DEFAULT_HEADER_STYLE.copy()
        defaults.update(item)
        return defaults

    def draw_header(self):
        for item in self.header_items:
            attrs = self.apply_header_defaults(item)
            self.c.setFont(attrs['font'], attrs['size'])
            self.c.setFillColor(attrs['color'])
            text = attrs['text']
            
            if attrs['align'] == 'center':
                self.c.drawCentredString(self.cfg.PAGE_WIDTH / 2, self.cursor_y, text)
            elif attrs['align'] == 'right':
                self.c.drawRightString(self.cfg.PAGE_WIDTH - self.cfg.MARGIN_RIGHT, self.cursor_y, text)
            else:
                self.c.drawString(self.cfg.MARGIN_LEFT, self.cursor_y, text)
            
            self.cursor_y -= (attrs['size'] + attrs['bottom_padding'])
        self.cursor_y -= 20

    def draw_participant_card(self, x, y, data, max_height):
        # 1. Draw Image
        img_filename = data.get('potrait') 
        img_h = self.cfg.COL_WIDTH / self.cfg.IMG_ASPECT_RATIO
        image_drawn = False

        if img_filename and isinstance(img_filename, str) and img_filename.strip():
            img_path = os.path.join("img", img_filename)
            if os.path.exists(img_path) and os.path.isfile(img_path):
                try:
                    img_y_bottom = y - img_h
                    
                    # Use self.cfg for settings
                    image_source = img_path 
                    if self.cfg.ENABLE_IMAGE_RESAMPLING and HAS_PIL:
                        try:
                            target_w_px = int((self.cfg.COL_WIDTH / 72.0) * self.cfg.RESAMPLING_DPI)
                            target_h_px = int((img_h / 72.0) * self.cfg.RESAMPLING_DPI)
                            
                            with Image.open(img_path) as im:
                                if im.width > target_w_px * 1.2 or im.height > target_h_px * 1.2:
                                    if im.mode not in ('L', 'RGB'):
                                        im = im.convert('RGB')
                                    im_resized = im.resize((target_w_px, target_h_px), Image.Resampling.LANCZOS)
                                    image_source = ImageReader(im_resized)
                        except Exception as e:
                            pass 

                    self.c.drawImage(image_source, x, img_y_bottom, width=self.cfg.COL_WIDTH, height=img_h)
                    self.c.rect(x, img_y_bottom, self.cfg.COL_WIDTH, img_h)
                    image_drawn = True
                except Exception:
                    pass
        
        if not image_drawn:
            self.c.setFont("Helvetica", 8)
            self.c.drawString(x, y - 20, "No Image") 
            self.c.rect(x, y - img_h, self.cfg.COL_WIDTH, img_h)

        # 2. Draw Text Details
        first_line_size = self.cfg.PARTICIPANT_STYLE[0]['size']
        text_gap = first_line_size + self.cfg.TEXT_GAP_BUFFER
        text_y = y - img_h - text_gap
        
        for field in self.cfg.PARTICIPANT_STYLE:
            self.c.setFont(field['font'], field['size'])
            self.c.setFillColor(field['color'])
            
            val = str(data.get(field['key'], '-'))
            full_text = f"{field['label']}{val}"
            
            # PASS self.cfg TO UTILS
            wrapped = utils.get_wrapped_text_lines(
                full_text, 
                field['font'], 
                field['size'], 
                self.cfg.COL_WIDTH - 4 
            )
            
            line_height = field['size'] * 1.2
            for w_line in wrapped:
                self.c.drawString(x, text_y, w_line)
                text_y -= line_height
            text_y -= field['padding']

        # 3. Draw Table
        raw_table_data = data.get('table_data')
        if raw_table_data:
            # PASS self.cfg TO UTILS
            formatted_data = utils.prepare_table_data(raw_table_data, self.cfg)
            if formatted_data:
                col_width_key = self.cfg.COL_WIDTH * self.cfg.TABLE_OPTS['key_col_ratio']
                col_width_val = self.cfg.COL_WIDTH * (1 - self.cfg.TABLE_OPTS['key_col_ratio'])
                
                t = Table(formatted_data, colWidths=[col_width_key, col_width_val])
                t.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), self.cfg.TABLE_OPTS['font'], self.cfg.TABLE_OPTS['size']),
                    ('TEXTCOLOR', (0, 0), (-1, -1), self.cfg.TABLE_OPTS['text_color']),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), self.cfg.TABLE_OPTS['border_width'], self.cfg.TABLE_OPTS['border_color']),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), self.cfg.TABLE_OPTS['padding']),
                    ('TOPPADDING', (0, 0), (-1, -1), self.cfg.TABLE_OPTS['padding']),
                ]))
                
                text_y -= self.cfg.TABLE_TOP_MARGIN 
                
                w, h = t.wrap(self.cfg.COL_WIDTH, self.cfg.PAGE_HEIGHT)
                table_y_position = text_y - h
                t.drawOn(self.c, x, table_y_position)

    def generate(self):
        self.draw_header()
        rows = [self.participants[i:i + self.cfg.COLUMNS] for i in range(0, len(self.participants), self.cfg.COLUMNS)]
        
        for row in rows:
            # PASS self.cfg TO UTILS
            row_heights = [utils.calculate_card_height(p, self.cfg) for p in row]
            max_row_height = max(row_heights) if row_heights else 0
            
            if (self.cursor_y - max_row_height) < self.cfg.MARGIN_BOTTOM:
                self.draw_meta_info()
                self.c.showPage()
                self.page_number += 1
                self.cursor_y = self.cfg.PAGE_HEIGHT - self.cfg.MARGIN_TOP
            
            current_x = self.cfg.MARGIN_LEFT
            for i, participant in enumerate(row):
                self.draw_participant_card(current_x, self.cursor_y, participant, max_row_height)
                current_x += self.cfg.COL_WIDTH + self.cfg.GRID_GAP_X
            
            self.cursor_y -= (max_row_height + self.cfg.GRID_GAP_Y)
        
        self.draw_meta_info()
        self.c.save()
        print(f"PDF Generated successfully.")