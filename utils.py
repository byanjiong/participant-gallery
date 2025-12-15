import json
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import config

def get_wrapped_text_lines(text, font_name, font_size, max_width):
    if not text:
        return []
    return simpleSplit(text, font_name, font_size, max_width)

def prepare_table_data(raw_dict):
    """
    Converts JSON dict to a List of Lists format required by ReportLab Table.
    Also handles text wrapping inside cells manually.
    """
    if not raw_dict:
        return None

    # --- FIX: Handle JSON string input ---
    if isinstance(raw_dict, str):
        try:
            raw_dict = json.loads(raw_dict)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse table data string: {raw_dict}")
            return None

    if not isinstance(raw_dict, dict):
        return None

    col_width_key = config.COL_WIDTH * config.TABLE_OPTS['key_col_ratio']
    col_width_val = config.COL_WIDTH * (1 - config.TABLE_OPTS['key_col_ratio'])

    table_data = []
    
    for key, val in raw_dict.items():
        # Wrap the Key
        key_lines = get_wrapped_text_lines(str(key), config.TABLE_OPTS['font'], config.TABLE_OPTS['size'], col_width_key - 6)
        key_text = "\n".join(key_lines)
        
        # Wrap the Value
        val_lines = get_wrapped_text_lines(str(val), config.TABLE_OPTS['font'], config.TABLE_OPTS['size'], col_width_val - 6)
        val_text = "\n".join(val_lines)

        table_data.append([key_text, val_text])
        
    return table_data

def get_table_height(table_data_list):
    """
    Builds a temporary table to calculate its height.
    """
    if not table_data_list:
        return 0
        
    col_width_key = config.COL_WIDTH * config.TABLE_OPTS['key_col_ratio']
    col_width_val = config.COL_WIDTH * (1 - config.TABLE_OPTS['key_col_ratio'])
    
    t = Table(table_data_list, colWidths=[col_width_key, col_width_val])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), config.TABLE_OPTS['font'], config.TABLE_OPTS['size']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), config.TABLE_OPTS['padding']),
        ('TOPPADDING', (0, 0), (-1, -1), config.TABLE_OPTS['padding']),
        ('GRID', (0, 0), (-1, -1), config.TABLE_OPTS['border_width'], config.TABLE_OPTS['border_color']),
    ]))
    
    # Calculate size (w, h)
    _, h = t.wrap(config.COL_WIDTH, config.PAGE_HEIGHT)
    return h

def calculate_card_height(participant_data):
    # 1. Image Height
    img_height = config.COL_WIDTH / config.IMG_ASPECT_RATIO
    
    # Calculate dynamic offset matching generator.py (font size + buffer)
    first_line_size = config.PARTICIPANT_STYLE[0]['size']
    text_gap = first_line_size + config.TEXT_GAP_BUFFER
    
    current_height = img_height + text_gap 
    
    # 2. Text Height (Dynamic)
    for field in config.PARTICIPANT_STYLE:
        val = str(participant_data.get(field['key'], '-'))
        full_text = f"{field['label']}{val}"
        
        wrapped_lines = get_wrapped_text_lines(
            full_text, 
            field['font'], 
            field['size'], 
            config.COL_WIDTH - 4
        )
        
        line_height = field['size'] * 1.2
        current_height += (len(wrapped_lines) * line_height) + field['padding']
    
    # 3. Table Height
    raw_table_data = participant_data.get('table_data', {})
    if raw_table_data:
        formatted_list = prepare_table_data(raw_table_data)
        table_h = get_table_height(formatted_list)
        # Use config variable for table top margin
        current_height += table_h + config.TABLE_TOP_MARGIN 
        
    return current_height + config.IMG_BORDER_WIDTH