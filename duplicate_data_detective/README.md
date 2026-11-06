# Duplicate Data Detective 🕵️

A beginner-friendly Python data-cleaning project. Upload a CSV file, detect repeated email addresses and names, inspect possible duplicates, remove duplicates, and download a cleaned CSV.

## Features

- Upload CSV files
- Automatically suggests likely `email` and `name` columns
- Detects duplicate emails without case sensitivity
- Detects duplicate names while ignoring capitalization and extra spaces
- Displays duplicate records and summary counts
- Shows duplicate percentage
- Removes duplicates by email, name, or entire row
- Downloads the cleaned data as a CSV file

## Built with

- Python
- Streamlit
- Pandas

## Run the project on your computer

### 1. Install Python

Install Python 3.10 or newer from https://www.python.org/downloads/.

### 2. Download or clone this project

If you have Git installed:

```bash
git clone https://github.com/YOUR-USERNAME/duplicate-data-detective.git
cd duplicate-data-detective
```

Or download the ZIP from GitHub and extract it.

### 3. Create a virtual environment (recommended)

Windows:

```bash
py -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the app

```bash
streamlit run app.py
```

Your browser should open the app. If it does not, open the local URL printed in the terminal (usually http://localhost:8501).

## Try the sample data

Upload `sample_data/sample_customers.csv` in the app to test duplicate detection.

## CSV format

Your CSV can have any columns. For automatic column suggestions, use column names such as `name` and `email`. You can also select the correct columns manually in the app.

## Project structure

```text
duplicate-data-detective/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── sample_data/
    └── sample_customers.csv
```

## Important note

The app does not upload your data to a database. It processes the uploaded CSV during the app session. Always review flagged rows before removing records.

## Future improvements

- Export a separate duplicate-only report
- Add phone-number duplicate detection
- Add Excel (`.xlsx`) support
- Add fuzzy matching for similar but not identical names
