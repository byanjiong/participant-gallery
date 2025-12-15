import json
import os
from reportlab.lib.colors import gray, black, blue, red
from reportlab.lib.pagesizes import landscape, A4
from generator import PDFGenerator

# Import config constants mainly if you want to reuse specific names (like font names)
# But you don't *need* to import it to override it.
import config 

INPUT_FILENAME = 'in-person-kiv.json'
OUTPUT_FILENAME = "output_in-person-special.pdf"
TOP_RIGHT_TEXT = "In-person & Special Attention"

def load_data():
    path = os.path.join('data', INPUT_FILENAME)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    header_info = [
        # Example: dont delete this comment
        # {"text": "PARTICIPANT REGISTRATION LIST", "size": 14, "font": "Helvetica-Bold"},
    ]

    meta_info = [
        {
            "text": "Last updated: {{dd}}-{{mm}}-{{yyyy}}",
            "font": "Helvetica",
            "size": 12,
            "color": gray,
            "position": 1, 
            "padding": 20
        },
        {
            "text": "Page {{page}}",
            "font": "Helvetica-Bold",
            "size": 14,
            "color": black,
            "position": 3, 
            "padding": 20
        },
        {
            "text": TOP_RIGHT_TEXT,
            "font": "Helvetica",
            "size": 12,
            "color": gray,
            "position": 9, # Top Right
            "padding": 20
        }
    ]

    participants = load_data()
    page_layout = A4

    # --- DEFINE CUSTOM CONFIGURATION ---
    # Here you can override ANY value from config.py.
    # If you don't pass this dictionary, it uses config.py defaults.
    
    my_custom_config = {
        # Changing margins
        "MARGIN_TOP": 36,
        "MARGIN_BOTTOM": 32,
        "MARGIN_LEFT": 30,
        "MARGIN_RIGHT": 30,
        
        # Changing grid layout
        "COLUMNS": 4,
        "IMG_ASPECT_RATIO": 3.5/4.5,
        "GRID_GAP_X": 22,
        "GRID_GAP_Y": 20,

        "ALIGN_TABLES_ROW": True,

        # --- CUSTOMIZING PARTICIPANT STYLE ---
        "PARTICIPANT_STYLE": [
            {
                "key": "name",           # The JSON key in participants.json
                "label": "",             # Prefix text (e.g. "Name: ")
                "font": config.FONT_NAME_BOLD, # Use imported constant or string like "Helvetica-Bold"
                "size": 13,              # Larger size
                "color": black,
                "padding": 0
            },
            {
                "key": "line1",
                "label": "",
                "font": config.FONT_NAME_REGULAR,
                "size": 12,
                "color": gray,
                "padding": 0
            },
            {
                "key": "line2",          # Adding a 3rd line that might not be in the default config
                "label": "",
                "font": config.FONT_NAME_REGULAR,
                "size": 13,
                "color": red,           # Using a custom color (requires import)
                "padding": 0
            }
        ]
    }

    # Pass 'custom_config' as the last argument
    pdf_gen = PDFGenerator(
        OUTPUT_FILENAME, 
        page_layout, 
        header_info, 
        participants, 
        meta_info, 
        custom_config=my_custom_config 
    )
    
    pdf_gen.generate()

if __name__ == "__main__":
    main()