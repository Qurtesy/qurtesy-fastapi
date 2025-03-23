import os
import csv
from sqlalchemy.orm import Session
from code.models import Base, Account, Category, Transaction  # Import your models
from code.database import get_db

# Directory containing CSV files
DUMP_DIR = "db_dump"

# CSV file paths
CSV_FILES = {
    "accounts": "accounts.csv",
    "categories": "categories.csv",
    "transactions": "transactions.csv"
}

# IMPORT FUNCTION
def import_data():
    """Imports data from CSV files into the database."""
    if not os.path.exists(DUMP_DIR):
        print(f"❌ Error: Directory '{DUMP_DIR}' not found. Please export data first.")
        return

    db: Session = next(get_db())

    tables = {
        "accounts.csv": (Account, ["id", "value"]),
        "categories.csv": (Category, ["id", "value", "emoji"]),
        "transactions.csv": (Transaction, ["id", "date", "amount", "section", "category", "account"]),
    }

    for file_name, (model, columns) in tables.items():
        file_path = os.path.join(DUMP_DIR, file_name)

        if not os.path.exists(file_path):
            print(f"⚠️ Warning: File '{file_path}' not found. Skipping...")
            continue

        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)  # Skip the header row

            for row in reader:
                row_data = {col: val for col, val in zip(columns, row)}
                db.add(model(**row_data))

        db.commit()
        print(f"✅ Imported data from {file_name} successfully.")
