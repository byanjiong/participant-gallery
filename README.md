Here is the complete, formatted `README.md` for your project in standard Markdown format, ready to be copied and saved into your repository:

```markdown
# Participant Gallery PDF Generator

A flexible, Python-based tool designed to generate grid-based PDF photo galleries and participant directories. It takes JSON data and images as input and produces polished, print-ready PDFs using `reportlab` and `Pillow`.

Originally tailored for organizing meditation retreats and grouping students under specific teachers (Ajahns), this tool is highly adaptable for creating student directories, event attendee lists, team rosters, or ID badges.

## 🌟 Features

* **Smart Grid Layout:** Automatically arranges participants in a configurable grid (rows & columns) with adjustable gaps and margins.
* **Automated Image Handling:** Supports participant photos with automatic resampling, aspect ratio management, and dynamic resizing via `Pillow`.
* **Dynamic Text & Wrapping:** Handles text wrapping for long names or descriptions seamlessly.
* **Key-Value Data Tables:** Renders a clean key-value table for each participant (e.g., specific stats, retreat counts, or dietary details).
* **Intelligent Row Alignment (`ALIGN_TABLES_ROW`):** Ensures that data tables across a single row start at the exact same visual height, keeping the layout perfectly aligned even if the text descriptions above them vary in length.
* **Dedicated Cover Pages:** Automatically generates an informative front cover with group titles, interview symbols, and guideline tables (e.g., Shortcodes, New/Old Student Guides).
* **Highly Customizable:** Fully configurable margins, fonts, colors, and layout settings via `config.py` or dynamic runtime overrides in your main scripts.

## 🛠️ Prerequisites

* Python 3.8+
* [ReportLab](https://pypi.org/project/reportlab/) (PDF Generation) `>= 4.0.0`
* [Pillow](https://pypi.org/project/Pillow/) (Image Processing) `>= 10.0.0`

## 📂 Project Structure

Ensure your directory matches this structure before running the scripts:

```text
.
├── data/                               # Place your JSON data files here (e.g., in-person-AKP.json)
├── fonts/                              # Place .ttf font files here (e.g., NotoSansSC-Regular.ttf)
├── img/                                # Place participant portrait photos here
├── main.py                             # Standard entry point
├── main-inperson-*.py                  # Variant scripts for specific Ajahn groups (AKP, ANK, etc.)
├── generator.py                        # Core PDF generation and layout logic
├── config.py                           # Global default configuration settings
├── utils.py                            # Helper functions for text wrapping and metric calculations
└── requirements.txt                    # Python dependencies
```

## 🚀 Setup & Installation

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add Fonts:**
   Download the required fonts (the default configuration uses *Noto Sans SC* to support Chinese characters and special symbols) and place them in the `fonts/` directory:
   * `fonts/NotoSansSC-Regular.ttf`
   * `fonts/NotoSansSC-Bold.ttf`
   *(Note: You can change the font paths and names in `config.py` if using different fonts).*

3. **Prepare Data:**
   * Add participant images to the `img/` folder.
   * Add your structured JSON data to the `data/` folder.

## 💻 Usage

Run the standard main script to generate a generic PDF:
```bash
python main.py
```

**Running Group-Specific Variants:**
The project includes pre-configured scripts for specific retreat groups. These scripts automatically inject a cover page and custom table configurations.
```bash
python main-inperson-AKP.py    # Ajahn Kittiya Pholkerd (Ajahn Ooi) Group
python main-inperson-ANK.py    # Ajahn Napatpol Kunatanasate (Ajahn Song) Group
python main-inperson-ANP.py    # Ajahn Nitiya Petchpaibool Group
python main-inperson-ANS.py    # Ajahn Nat Sriwachirawat Group
python main-inperson-APB.py    # Ajahn Prasan Bhuddhakulsomsiri Group
python main-inperson-EG.py     # English Group
python main-inperson-special.py # Special Attention / KIV Group
```
The output PDFs will be saved in the root directory (e.g., `output_AKP.pdf`).

## 📄 Data Format (JSON)

Your JSON file (inside `data/`) should contain a list of objects representing each participant.

**Example `data/in-person-AKP.json`:**
```json
[
  {
    "name": "Alice Johnson",
    "line1": "New Student",
    "line3": "Practice: Daily",
    "potrait": "alice_photo.jpg",
    "table_data": {
      "Videos": "Yes",
      "Precepts": "Yes"
    }
  },
  {
    "name": "Bob Smith",
    "line1": "Old Student",
    "potrait": "bob_photo.png",
    "table_data": null
  }
]
```
* `name`: Primary text (rendered bold by default).
* `line1`, `line2`, `line3`: Secondary text lines customized via `PARTICIPANT_STYLE` in your Python script.
* `potrait`: Filename of the image located in the `img/` folder.
* `table_data`: (Optional) Key-value pairs displayed in a small data table below the text.

## ⚙️ Configuration & Customization

You can customize the PDF output in two ways:

1. **Global Defaults:** Edit `config.py` to change default margins, fonts, colors, or grid sizes across all scripts.
2. **Per-Script Overrides:** Pass a `custom_config` dictionary to the `PDFGenerator` inside your `main.py` files.

### Example Custom Config Override
```python
my_custom_config = {
    "MARGIN_TOP": 36,
    "COLUMNS": 4,
    "ALIGN_TABLES_ROW": True,  # Ensures all tables in a row align to the same starting height
    "PARTICIPANT_STYLE": [
        {
            "key": "name",
            "label": "",
            "font": config.FONT_NAME_BOLD,
            "size": 13,
            "color": black,
            "padding": 0
        },
        {
            "key": "line2",
            "label": "Status: ",
            "font": config.FONT_NAME_REGULAR,
            "size": 13,
            "color": red,  # Great for highlighting special statuses
            "padding": 0
        }
    ]
}
```

### Cover Pages
Scripts like `main-inperson-AKP.py` utilize a `COVER_PAGE_INFO` dictionary to generate a front page. You can customize this dictionary to define the title, interview symbols, and reference tables for your specific group's PDF. If a font does not support a specific symbol (like emojis), you can safely replace them with standard text in this dictionary.
```