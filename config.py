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
MARGIN_TOP = 50
MARGIN_BOTTOM = 50
MARGIN_LEFT = 40
MARGIN_RIGHT = 40

# Grid Settings
COLUMNS = 3
IMG_ASPECT_RATIO = 3.5/4.5
IMG_BORDER_WIDTH = 1
GRID_GAP_X = 20
GRID_GAP_Y = 30

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
    "key_col_ratio": 0.35,
    "font": FONT_NAME_REGULAR, # Table uses Regular
    "size": 9,
    "text_color": black,
    "border_color": black,
    "border_width": 1,
    "padding": 4
}

# --- PARTICIPANT DETAILS CONFIGURATION ---
PARTICIPANT_STYLE = [
    {
        "key": "name",      
        "label": "",        
        "font": FONT_NAME_BOLD, # <--- USE BOLD FONT HERE
        "size": 16,         
        "color": black,
        "padding": 6
    },
    {
        "key": "line1",
        "label": "",        
        "font": FONT_NAME_REGULAR, # <--- USE REGULAR HERE
        "size": 10,
        "color": black,
        "padding": 2
    },
    {
        "key": "line2",
        "label": "",
        "font": FONT_NAME_REGULAR,
        "size": 10,
        "color": black,
        "padding": 2
    },
    {
        "key": "line3",
        "label": "",
        "font": FONT_NAME_REGULAR,
        "size": 8,
        "color": gray,
        "padding": 4
    }
]