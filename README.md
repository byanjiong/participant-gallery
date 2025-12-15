Participant Gallery PDF Generator
A flexible Python tool designed to generate grid-based PDF photo galleries or participant directories. It takes JSON data and images as input and produces a polished, print-ready PDF using reportlab.
This project is ideal for creating:
Student directories
Event attendee lists
Team rosters with photos
ID cards or badges (with layout adjustments)
🌟 Features
Grid Layout: Automatically arranges participants in a configurable grid (rows & columns).
Image Handling: Supports participant photos with automatic resizing and aspect ratio management.
Dynamic Text: Handles text wrapping for long names or descriptions.
Data Tables: Can render a key-value table for each participant (e.g., specific stats or details).
Row Alignment: Optional "Table Alignment" mode ensures data tables across a row start at the same visual height, even if text descriptions vary in length.
Customizable: Fully configurable margins, fonts, colors, and layout settings via config.py or runtime overrides.
🛠️ Prerequisites
Python 3.8+
ReportLab (PDF Generation)
Pillow (Image Processing)
📂 Project Structure
Ensure your directory looks like this before running:
.
├── data/                   # Place your JSON data files here
├── fonts/                  # Place .ttf font files here (e.g., NotoSansSC)
├── img/                    # Place participant photos here
├── main.py                 # Main entry point (and other variants)
├── generator.py            # Core PDF generation logic
├── config.py               # Default configuration settings
├── utils.py                # Helper functions
└── requirements.txt        # Python dependencies


🚀 Setup & Installation
Install Dependencies:
pip install -r requirements.txt


Add Fonts:
Download the required fonts (default uses Noto Sans SC) and place them in the fonts/ directory.
fonts/NotoSansSC-Regular.ttf
fonts/NotoSansSC-Bold.ttf
(You can change the font paths in config.py if using different fonts).
Prepare Data:
Add your images to the img/ folder and your JSON data to data/.
💻 Usage
Run the main script to generate the PDF:
python main.py


Or run specific variants for different groups:
python main-inperson-newstudent.py
python main-inperson-special.py


The output PDF will be saved in the root directory (e.g., output_in-person-old-student-std.pdf).
📄 Data Format (JSON)
Your JSON file (inside data/) should be a list of objects. Each object represents one participant.
Example data/example.json:
[
  {
    "name": "Alice Johnson",
    "line1": "Grade 10 - Science Stream",
    "potrait": "alice_photo.jpg",
    "table_data": {
      "Age": "16",
      "House": "Blue",
      "Diet": "Vegetarian"
    }
  },
  {
    "name": "Bob Smith",
    "line1": "Grade 11 - Arts Stream",
    "potrait": "bob_photo.png",
    "table_data": null
  }
]


name: Primary text (bold by default).
line1: Secondary text.
potrait: Filename of the image in the img/ folder.
table_data: (Optional) Key-value pairs to display in a small table below the text.
⚙️ Configuration
You can customize the output in two ways:
Global Defaults: Edit config.py to change default margins, fonts, or grid sizes.
Per-Script Overrides: In main.py, pass a custom_config dictionary to the generator.
Common Configuration Options
Option
Description
COLUMNS
Number of columns in the grid (e.g., 4).
IMG_ASPECT_RATIO
Aspect ratio for photos (Width / Height).
ALIGN_TABLES_ROW
(New) Set to True to align all tables in a specific row to the same starting height.
PARTICIPANT_STYLE
List defining how text fields (name, line1) are rendered.

Example Custom Config (in main.py)
    my_custom_config = {
        "MARGIN_TOP": 36,
        "COLUMNS": 4,
        "ALIGN_TABLES_ROW": True,  # Enables the row alignment feature
        "PARTICIPANT_STYLE": [
            {
                "key": "name",
                "label": "",
                "font": config.FONT_NAME_BOLD,
                "size": 14,
                "color": black,
                "padding": 0
            }
        ]
    }


