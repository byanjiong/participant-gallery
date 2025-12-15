import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
import config
import utils

# Try importing Pillow for image optimization
try:
    from PIL import Image
    from reportlab.lib.utils import ImageReader
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: 'Pillow' library not found. Image optimization disabled. Install via: pip install Pillow")

class PDFGenerator:
    def __init__(self, filename, pagesize, header_items, participants, meta_info=None):
        # 1. Update Config with new Page Size
        # This is crucial because utils.py and internal logic rely on config.COL_WIDTH.
        # By updating the module-level config variable, utils.py will see the correct width.
        config.PAGE_WIDTH, config.PAGE_HEIGHT = pagesize
        
        # 2. Recalculate Column Width
        # We must re-run the logic from config.py to adapt to the new width
        available_width = config.PAGE_WIDTH - config.MARGIN_LEFT - config.MARGIN_RIGHT
        total_gaps_width = (config.COLUMNS - 1) * config.GRID_GAP_X
        config.COL_WIDTH = (available_width - total_gaps_width) / config.COLUMNS

        self.c = canvas.Canvas(filename, pagesize=pagesize)
        self.header_items = header_items
        self.participants = participants
        self.meta_info = meta_info if meta_info else []
        self.cursor_y = config.PAGE_HEIGHT - config.MARGIN_TOP
        self.page_number = 1
        
        # --- ROBUST FONT REGISTRATION ---
        self.register_fonts()

    def register_fonts(self):
        """Helper to register all fonts"""
        fonts_to_register = [
            (config.FONT_NAME_REGULAR, config.FONT_PATH_REGULAR),
            (config.FONT_NAME_BOLD, config.FONT_PATH_BOLD)
        ]

        for name, path in fonts_to_register:
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                print(f"Font '{name}' registered successfully.")
            except Exception as e:
                print(f"WARNING: Could not load font '{name}' from '{path}'. Defaulting to Helvetica.")
                
                # --- FALLBACK MECHANISM ---
                try:
                    if name == config.FONT_NAME_REGULAR:
                        config.FONT_NAME_REGULAR = "Helvetica"
                    elif name == config.FONT_NAME_BOLD:
                        config.FONT_NAME_BOLD = "Helvetica-Bold" 
                        
                except Exception as inner_e:
                    print(f"Critical font error: {inner_e}")

    def resolve_meta_text(self, text, page_num):
        """Replaces variables in meta text"""
        now = datetime.now()
        resolved = text.replace("{{dd}}", now.strftime("%d"))
        resolved = resolved.replace("{{mm}}", now.strftime("%m"))
        resolved = resolved.replace("{{yyyy}}", now.strftime("%Y"))
        resolved = resolved.replace("{{page}}", str(page_num))
        return resolved

    def draw_meta_info(self):
        """Draws meta info items on the current page"""
        if not self.meta_info:
            return

        w, h = config.PAGE_WIDTH, config.PAGE_HEIGHT
        
        for item in self.meta_info:
            # defaults
            text_template = item.get('text', '')
            font = item.get('font', 'Helvetica')
            size = item.get('size', 10)
            color = item.get('color', black)
            pos = item.get('position', 1)
            padding = item.get('padding', 10)

            resolved_text = self.resolve_meta_text(text_template, self.page_number)
            
            self.c.setFont(font, size)
            self.c.setFillColor(color)
            
            # Keypad Position Logic
            # 7 8 9
            # 4 5 6
            # 1 2 3
            
            # X Coordinates
            if pos in [1, 4, 7]: # Left
                x = padding
                align = 'left'
            elif pos in [2, 5, 8]: # Center
                x = w / 2
                align = 'center'
            elif pos in [3, 6, 9]: # Right
                x = w - padding
                align = 'right'
            else:
                x = padding
                align = 'left'

            # Y Coordinates
            # Note: For Top (7,8,9), we subtract font size to ensure text is below the very top edge
            if pos in [1, 2, 3]: # Bottom
                y = padding
            elif pos in [4, 5, 6]: # Middle
                y = h / 2
            elif pos in [7, 8, 9]: # Top
                y = h - padding - size 
            else:
                y = padding

            # Draw
            if align == 'center':
                self.c.drawCentredString(x, y, resolved_text)
            elif align == 'right':
                self.c.drawRightString(x, y, resolved_text)
            else:
                self.c.drawString(x, y, resolved_text)

    def apply_header_defaults(self, item):
        defaults = config.DEFAULT_HEADER_STYLE.copy()
        defaults.update(item)
        return defaults

    def draw_header(self):
        for item in self.header_items:
            attrs = self.apply_header_defaults(item)
            self.c.setFont(attrs['font'], attrs['size'])
            self.c.setFillColor(attrs['color'])
            text = attrs['text']
            if attrs['align'] == 'center':
                self.c.drawCentredString(config.PAGE_WIDTH / 2, self.cursor_y, text)
            elif attrs['align'] == 'right':
                self.c.drawRightString(config.PAGE_WIDTH - config.MARGIN_RIGHT, self.cursor_y, text)
            else:
                self.c.drawString(config.MARGIN_LEFT, self.cursor_y, text)
            self.cursor_y -= (attrs['size'] + attrs['bottom_padding'])
        self.cursor_y -= 20

    def draw_participant_card(self, x, y, data, max_height):
        # 1. Draw Image
        img_filename = data.get('potrait') 
        img_h = config.COL_WIDTH / config.IMG_ASPECT_RATIO
        image_drawn = False

        if img_filename and isinstance(img_filename, str) and img_filename.strip():
            img_path = os.path.join("img", img_filename)
            if os.path.exists(img_path) and os.path.isfile(img_path):
                try:
                    img_y_bottom = y - img_h
                    
                    # --- IMAGE OPTIMIZATION LOGIC ---
                    # Default to using the path (ReportLab loads original)
                    image_source = img_path 
                    
                    if config.ENABLE_IMAGE_RESAMPLING and HAS_PIL:
                        try:
                            # 1. Calculate required pixels: (Size_in_Points / 72_points_per_inch) * DPI
                            target_w_px = int((config.COL_WIDTH / 72.0) * config.RESAMPLING_DPI)
                            target_h_px = int((img_h / 72.0) * config.RESAMPLING_DPI)
                            
                            with Image.open(img_path) as im:
                                # 2. Check if source is significantly larger (e.g. > 20% larger)
                                if im.width > target_w_px * 1.2 or im.height > target_h_px * 1.2:
                                    
                                    # Ensure RGB (removes alpha channel which can cause PDF issues, or CMYK)
                                    if im.mode not in ('L', 'RGB'):
                                        im = im.convert('RGB')
                                    
                                    # 3. Resize
                                    im_resized = im.resize((target_w_px, target_h_px), Image.Resampling.LANCZOS)
                                    image_source = ImageReader(im_resized)
                        except Exception as opt_err:
                            print(f"Image optimization skipped for {img_filename}: {opt_err}")

                    self.c.drawImage(image_source, x, img_y_bottom, width=config.COL_WIDTH, height=img_h)
                    self.c.rect(x, img_y_bottom, config.COL_WIDTH, img_h)
                    image_drawn = True
                except Exception as e:
                    print(f"Error loading image: {e}")
        
        if not image_drawn:
            self.c.setFont("Helvetica", 8)
            self.c.drawString(x, y - 20, "No Image") 
            self.c.rect(x, y - img_h, config.COL_WIDTH, img_h)

        # 2. Draw Text Details
        first_line_size = config.PARTICIPANT_STYLE[0]['size']
        text_gap = first_line_size + config.TEXT_GAP_BUFFER
        text_y = y - img_h - text_gap
        
        for field in config.PARTICIPANT_STYLE:
            self.c.setFont(field['font'], field['size'])
            self.c.setFillColor(field['color'])
            
            val = str(data.get(field['key'], '-'))
            full_text = f"{field['label']}{val}"
            
            wrapped = utils.get_wrapped_text_lines(
                full_text, 
                field['font'], 
                field['size'], 
                config.COL_WIDTH - 4 
            )
            
            line_height = field['size'] * 1.2
            for w_line in wrapped:
                self.c.drawString(x, text_y, w_line)
                text_y -= line_height
            text_y -= field['padding']

        # 3. Draw Table
        raw_table_data = data.get('table_data')
        if raw_table_data:
            formatted_data = utils.prepare_table_data(raw_table_data)
            if formatted_data:
                col_width_key = config.COL_WIDTH * config.TABLE_OPTS['key_col_ratio']
                col_width_val = config.COL_WIDTH * (1 - config.TABLE_OPTS['key_col_ratio'])
                
                t = Table(formatted_data, colWidths=[col_width_key, col_width_val])
                t.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), config.TABLE_OPTS['font'], config.TABLE_OPTS['size']),
                    ('TEXTCOLOR', (0, 0), (-1, -1), config.TABLE_OPTS['text_color']),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), config.TABLE_OPTS['border_width'], config.TABLE_OPTS['border_color']),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), config.TABLE_OPTS['padding']),
                    ('TOPPADDING', (0, 0), (-1, -1), config.TABLE_OPTS['padding']),
                ]))
                
                text_y -= config.TABLE_TOP_MARGIN 
                
                w, h = t.wrap(config.COL_WIDTH, config.PAGE_HEIGHT)
                table_y_position = text_y - h
                t.drawOn(self.c, x, table_y_position)

    def generate(self):
        self.draw_header()
        rows = [self.participants[i:i + config.COLUMNS] for i in range(0, len(self.participants), config.COLUMNS)]
        
        for row in rows:
            row_heights = [utils.calculate_card_height(p) for p in row]
            max_row_height = max(row_heights) if row_heights else 0
            
            if (self.cursor_y - max_row_height) < config.MARGIN_BOTTOM:
                self.draw_meta_info()
                self.c.showPage()
                self.page_number += 1
                self.cursor_y = config.PAGE_HEIGHT - config.MARGIN_TOP
            
            current_x = config.MARGIN_LEFT
            for i, participant in enumerate(row):
                self.draw_participant_card(current_x, self.cursor_y, participant, max_row_height)
                current_x += config.COL_WIDTH + config.GRID_GAP_X
            
            self.cursor_y -= (max_row_height + config.GRID_GAP_Y)
        
        self.draw_meta_info()
        self.c.save()
        print(f"PDF Generated successfully.")