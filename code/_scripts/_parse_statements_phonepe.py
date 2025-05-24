import os
import csv
import pdfplumber
import csv
from pdfminer.high_level import extract_text

# Directory containing PDF files
STATEMENTS_DIR = "statements"

# PDF file paths
PDF_FILES = [
    "PhonePe_Statement_Mar2025_Mar2025.pdf"
]

# IMPORT FUNCTION
def parse_statements_phonepe():
    """Imports data from CSV files into the database."""
    if not os.path.exists(STATEMENTS_DIR):
        print(f"❌ Error: Directory '{STATEMENTS_DIR}' not found. Please export data first.")
        return

    for file_name in PDF_FILES:
        pdf_path = f"{STATEMENTS_DIR}/{file_name}"
        csv_path = f"{STATEMENTS_DIR}/{file_name.split(".")[0]}.csv"
        txt_path = f"{STATEMENTS_DIR}/{file_name.split(".")[0]}.txt"

        text = extract_text(pdf_path)
        with open(txt_path, "w") as f:
            f.write(text)
