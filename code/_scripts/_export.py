import os
import csv
from datetime import date
from enum import Enum
from sqlalchemy.orm import Session
from code.models import Base, Account, Category, Transaction  # Import your models
from code.database import get_db
from code.utils.datetime import format_date

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
        "accounts": (Account, ["value", "section"]),
        "categories": (Category, ["value", "emoji", "section"]),
        "transactions": (Transaction, ["date", "amount", "section", "category_rel", "account_rel"]),
    }

    # Export Tables
    for table_name, (model, columns) in tables.items():
        file_path = os.path.join(DUMP_DIR, f"{table_name}.csv")

        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(columns)  # Write headers

            for row in db.query(model).all():
                line = []
                for col in columns:
                    if type(getattr(row, col)) == Category or type(getattr(row, col)) == Account:
                        line.append(getattr(getattr(row, col), 'value'))
                    # Enums
                    elif isinstance(getattr(row, col), Enum):
                        line.append(getattr(getattr(row, col), 'value'))
                    elif type(getattr(row, col)) == date:
                        line.append(format_date(getattr(row, col)))
                    else:
                        line.append(str(getattr(row, col)))
                writer.writerow(line)  # Write data

        print(f"✅ Exported {table_name} to {file_path}")
