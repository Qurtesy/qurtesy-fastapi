import os
import csv
from sqlalchemy.orm import Session
from code.models import Base, Account, Category, Transaction  # Import your models
from code.database import get_db

# CSV file paths
CSV_FILES = {
    "accounts": "accounts.csv",
    "categories": "categories.csv",
    "transactions": "transactions.csv"
}

# Ensure the 'db_dump' directory exists
DUMP_DIR = "db_dump"
os.makedirs(DUMP_DIR, exist_ok=True)

# EXPORT FUNCTION
def export_data():
    """Exports accounts, categories, and transactions tables to CSV."""
    db: Session = next(get_db())

    tables = {
        "accounts": (Account, ["id", "value"]),
        "categories": (Category, ["id", "value", "emoji"]),
        "transactions": (Transaction, ["id", "date", "amount", "category", "account"]),
    }

    # Export Tables
    for table_name, (model, columns) in tables.items():
        file_path = os.path.join(DUMP_DIR, f"{table_name}.csv")

        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(columns)  # Write headers

            for row in db.query(model).all():
                writer.writerow([getattr(row, col) for col in columns])  # Write data

        print(f"✅ Exported {table_name} to {file_path}")
