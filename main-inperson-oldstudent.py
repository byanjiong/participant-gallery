import json
import os
from reportlab.lib.colors import gray, black
from reportlab.lib.pagesizes import landscape, A4
from generator import PDFGenerator

def load_data():
    path = os.path.join('data', 'in-person-old-student-std.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # 1. Define Header Info
    header_info = [
        # {"text": "PARTICIPANT REGISTRATION LIST", "size": 18, "font": "Helvetica-Bold"},
        # {"text": "Annual Gathering 2025", "size": 14, "color": "gray"},
        # {"text": "------------------------------------------------", "size": 10},
    ]

    # 2. Define Meta Info
    meta_info = [
        {
            "text": "Last updated: {{dd}}-{{mm}}-{{yyyy}}",
            "font": "Helvetica",
            "size": 12,
            "color": gray,
            "position": 1, # Bottom Left
            "padding": 20
        },
        {
            "text": "Page {{page}}",
            "font": "Helvetica-Bold",
            "size": 14,
            "color": black,
            "position": 3, # Bottom Right
            "padding": 20
        },
        {
            "text": "In-person & Old student",
            "font": "Helvetica",
            "size": 12,
            "color": gray,
            "position": 9, # Top Right
            "padding": 20
        }
    ]

    # 3. Load Participants
    participants = load_data()

    # 4. Define Page Layout
    # You can change this to A4, landscape(A4), or a custom tuple (width, height)
    page_layout = A4

    # 5. Generate
    pdf_gen = PDFGenerator("output_participants.pdf", page_layout, header_info, participants, meta_info)
    pdf_gen.generate()

if __name__ == "__main__":
    main()