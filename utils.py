import json
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import Table, TableStyle

# NOTE: We removed 'import config'. 
# All functions now accept a 'cfg' object containing the necessary settings.

def get_wrapped_text_lines(text, font_name, font_size, max_width):
    """
    Wraps text into lines that fit within max_width.
    This function is 'pure' and doesn't need the config object.
    """
    if not text:
        return []
    return simpleSplit(text, font_name, font_size, max_width)

def prepare_table_data(raw_dict, cfg):
    """
    Converts JSON dict to a List of Lists format required by ReportLab Table.
    """
    if not raw_dict:
        return None

    if isinstance(raw_dict, str):
        try:
            raw_dict = json.loads(raw_dict)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse table data string: {raw_dict}")
            return None

    if not isinstance(raw_dict, dict):
        return None

    # Access settings from the passed 'cfg' object instead of global 'config'
    col_width_key = cfg.COL_WIDTH * cfg.TABLE_OPTS['key_col_ratio']
    col_width_val = cfg.COL_WIDTH * (1 - cfg.TABLE_OPTS['key_col_ratio'])

    table_data = []
    
    for key, val in raw_dict.items():
        # Wrap the Key
        key_lines = get_wrapped_text_lines(str(key), cfg.TABLE_OPTS['font'], cfg.TABLE_OPTS['size'], col_width_key - 6)
        key_text = "\n".join(key_lines)
        
        # Wrap the Value
        val_lines = get_wrapped_text_lines(str(val), cfg.TABLE_OPTS['font'], cfg.TABLE_OPTS['size'], col_width_val - 6)
        val_text = "\n".join(val_lines)

        table_data.append([key_text, val_text])
        
    return table_data

def get_table_height(table_data_list, cfg):
    """
    Builds a temporary table to calculate its height.
    """
    if not table_data_list:
        return 0
        
    col_width_key = cfg.COL_WIDTH * cfg.TABLE_OPTS['key_col_ratio']
    col_width_val = cfg.COL_WIDTH * (1 - cfg.TABLE_OPTS['key_col_ratio'])
    
    t = Table(table_data_list, colWidths=[col_width_key, col_width_val])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), cfg.TABLE_OPTS['font'], cfg.TABLE_OPTS['size']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), cfg.TABLE_OPTS['padding']),
        ('TOPPADDING', (0, 0), (-1, -1), cfg.TABLE_OPTS['padding']),
        ('GRID', (0, 0), (-1, -1), cfg.TABLE_OPTS['border_width'], cfg.TABLE_OPTS['border_color']),
    ]))
    
    # Calculate size (w, h)
    _, h = t.wrap(cfg.COL_WIDTH, cfg.PAGE_HEIGHT)
    return h

def get_card_metrics(participant_data, cfg):
    """
    Calculates detailed height metrics for a participant card.
    Returns a dictionary separating content height and table height.
    """
    # 1. Image Height
    img_height = cfg.COL_WIDTH / cfg.IMG_ASPECT_RATIO
    
    # Calculate dynamic offset matching generator.py (font size + buffer)
    first_line_size = cfg.PARTICIPANT_STYLE[0]['size']
    text_gap = first_line_size + cfg.TEXT_GAP_BUFFER
    
    # This 'non_table_height' represents everything from the top of the card
    # down to the bottom of the last text line (including padding).
    current_non_table_height = img_height + text_gap 
    
    # 2. Text Height (Dynamic)
    for field in cfg.PARTICIPANT_STYLE:
        val = str(participant_data.get(field['key'], '-'))
        full_text = f"{field['label']}{val}"
        
        wrapped_lines = get_wrapped_text_lines(
            full_text, 
            field['font'], 
            field['size'], 
            cfg.COL_WIDTH - 4
        )
        
        line_height = field['size'] * 1.2
        current_non_table_height += (len(wrapped_lines) * line_height) + field['padding']
    
    # 3. Table Height
    table_height = 0
    raw_table_data = participant_data.get('table_data', {})
    table_exists = False
    
    if raw_table_data:
        formatted_list = prepare_table_data(raw_table_data, cfg)
        if formatted_list:
            table_height = get_table_height(formatted_list, cfg)
            table_exists = True
        
    return {
        'non_table_height': current_non_table_height,
        'table_height': table_height,
        'table_top_margin': cfg.TABLE_TOP_MARGIN if table_exists else 0,
        'img_border_width': cfg.IMG_BORDER_WIDTH
    }

def calculate_card_height(participant_data, cfg):
    """
    Calculates the total height of a participant card based on image, text, and table.
    Uses get_card_metrics internally.
    """
    metrics = get_card_metrics(participant_data, cfg)
    
    total = metrics['non_table_height']
    if metrics['table_height'] > 0:
        total += metrics['table_top_margin'] + metrics['table_height']
    
    total += metrics['img_border_width']
    return total