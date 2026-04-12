import json
import os
from reportlab.lib.colors import gray, black, blue
from reportlab.lib.pagesizes import landscape, A4
from generator import PDFGenerator

# Import config constants mainly if you want to reuse specific names (like font names)
# But you don't *need* to import it to override it.
import config 

INPUT_FILENAME = 'in-person-ANK.json'
OUTPUT_FILENAME = "output_ANK.pdf"
TOP_RIGHT_TEXT = "ANK Group"

# --- COVER PAGE CONFIGURATION ---
# Note: If the ♫ emoji shows up as a black box in your PDF, 
# it means your Noto font doesn't support emojis. If that happens, replace it with "(Mic)".
COVER_PAGE_INFO = {
    "title": "Ajahn Napatpol Kunatanasate (Ajahn Song) Group",
    "interview_symbols": [
        ["★", "is interviewing"],
        ["★*", "is interviewing, but with other online ajahn."]
    ],
    "ajahn_codes": [
        ["Ajahn Khun Mae Oranuch Santayakorn", "AKMOS"],
        ["Phra Thanusorn Jirasarano (Kruba Mon)", "PTJKM"],
        ["Phra Ajahn Krit Nimmalo", "PAKN"],
        ["Phra Ajahn Somchai Kittiyano", "PASK"]
    ],
    "new_student_guide": [
        ["Videos", "Watched 30 Luangpu Videos?"],
        ["Precepts", "Observed 5 Precepts?"],
        ["Practice", "Meditation frequency (never/seldom/frequently/daily)"]
    ],
    "old_student_guide": [
        ["TH", "Thai (in-person) retreat count"],
        ["MY", "Malaysia (in-person) retreat count"],
        ["CH", "China (in-person) retreat count"],
        ["TW", "Taiwan (in-person) retreat count"],
        ["SG", "Singapore (in-person) retreat count"],
        ["English", "International English course count"],
        ["Online", "All types of online course count"],
        ["Practice", "Meditation frequency (never/seldom/frequently/daily)"]
    ]
}

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
                "key": "line3",
                "label": "",
                "font": config.FONT_NAME_REGULAR,
                "size": 10,
                "color": gray,
                "padding": 0
            },


            # {
            #     "key": "line2",          # Adding a 3rd line that might not be in the default config
            #     "label": "",
            #     "font": config.FONT_NAME_REGULAR,
            #     "size": 10,
            #     "color": blue,           # Using a custom color (requires import)
            #     "padding": 0
            # }
        ]
    }

    # Pass 'custom_config' as the last argument
    pdf_gen = PDFGenerator(
        OUTPUT_FILENAME, 
        page_layout, 
        header_info, 
        participants, 
        meta_info, 
        custom_config=my_custom_config,
        cover_info=COVER_PAGE_INFO # <--- New cover info passed here
    )
    
    pdf_gen.generate()

if __name__ == "__main__":
    main()