import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black, gray

# A4 Dimensions
PAGE_WIDTH, PAGE_HEIGHT = A4

# --- FONT CONFIGURATION ---
# Define paths for both weights
FONT_PATH_REGULAR = os.path.join('fonts', 'NotoSansSC-Regular.ttf')
FONT_PATH_BOLD = os.path.join('fonts', 'NotoSansSC-Bold.ttf')

# Give them internal names
FONT_NAME_REGULAR = 'NotoRegular'
FONT_NAME_BOLD = 'NotoBold'

# Margins
MARGIN_TOP = 30
MARGIN_BOTTOM = 30
MARGIN_LEFT = 30
MARGIN_RIGHT = 30

# Grid Settings
COLUMNS = 4
IMG_ASPECT_RATIO = 3.5/4.5
IMG_BORDER_WIDTH = 1
GRID_GAP_X = 15
GRID_GAP_Y = 15

# Gap buffer between image and first line (Name)
# Formula: Gap = First_Line_Font_Size + TEXT_GAP_BUFFER
TEXT_GAP_BUFFER = 4

# Gap between the last line of text and the Table
TABLE_TOP_MARGIN = 2

# --- IMAGE OPTIMIZATION ---
ENABLE_IMAGE_RESAMPLING = True   # Set to True to shrink large photos
RESAMPLING_DPI = 200             # 200 is good for general A4 printing. Use 300 for high-quality.

# Header defaults (Use Bold for header?)
DEFAULT_HEADER_STYLE = {
    "text": "",
    "font": FONT_NAME_BOLD, # Header uses Bold
    "size": 12,
    "align": "center",
    "color": black,
    "bottom_padding": 10
}

# Calculated Widths
available_width = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
total_gaps_width = (COLUMNS - 1) * GRID_GAP_X
COL_WIDTH = (available_width - total_gaps_width) / COLUMNS

# --- TABLE CONFIGURATION ---
TABLE_OPTS = {
    "key_col_ratio": 0.4,
    "font": FONT_NAME_REGULAR, # Table uses Regular
    "size": 9,
    "text_color": black,
    "border_color": black,
    "border_width": 1,
    "padding": 2
}

# --- PARTICIPANT DETAILS CONFIGURATION ---
PARTICIPANT_STYLE = [
    {
        "key": "name",      
        "label": "",        
        "font": FONT_NAME_BOLD, # <--- USE BOLD FONT HERE
        "size": 13,         
        "color": black,
        "padding": 2
    },
    {
        "key": "line1",
        "label": "",        
        "font": FONT_NAME_REGULAR, # <--- USE REGULAR HERE
        "size": 11,
        "color": black,
        "padding": 0
    },
    # {
    #     "key": "line2",
    #     "label": "",
    #     "font": FONT_NAME_REGULAR,
    #     "size": 11,
    #     "color": black,
    #     "padding": 2
    # },
    # {
    #     "key": "line3",
    #     "label": "",
    #     "font": FONT_NAME_REGULAR,
    #     "size": 9,
    #     "color": gray,
    #     "padding": 4
    # }
]