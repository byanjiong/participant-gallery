import json
import os
from generator import PDFGenerator

def load_data():
    path = os.path.join('data', 'participants.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # 1. Define Header Info
    header_info = [
        {"text": "PARTICIPANT REGISTRATION LIST", "size": 18, "font": "Helvetica-Bold"},
        {"text": "Annual Gathering 2025", "size": 14, "color": "gray"},
        {"text": "------------------------------------------------", "size": 10},
    ]

    # 2. Load Participants
    participants = load_data()

    # 3. Generate
    pdf_gen = PDFGenerator("output_participants.pdf", header_info, participants)
    pdf_gen.generate()

if __name__ == "__main__":
    main()