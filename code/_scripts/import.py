import os
import csv
from sqlalchemy import inspect, Boolean
from sqlalchemy.orm import Session
from models import Base, Account, Category, Transaction  # Import your models
from database import get_db

# Directory containing CSV files
DUMP_DIR = "db_dump"

# CSV file paths
CSV_FILES = {
    "accounts": "accounts.csv",
    "categories": "categories.csv",
    "transactions": "transactions.csv"
}

# IMPORT FUNCTION
def execute_command():
    """Imports data from CSV files into the database."""
    if not os.path.exists(DUMP_DIR):
        print(f"❌ Error: Directory '{DUMP_DIR}' not found. Please export data first.")
        return

    db: Session = next(get_db())

    tables = {
        # Parent tables
        # "accounts.csv": (Account, ["value"]),
        # "categories.csv": (Category, ["value", "emoji", "section"]),
        # Child tables
        "transactions.csv": (Transaction, ["date","credit","amount","section","category"]),
    }

    # model_map = {}
    # for model in [Category, Account]:
    #     for r in db.query(model).all():
    #         model_map[f'{model.__name__}:{r.value}'] = r.id

    for file_name, (model, columns) in tables.items():
        file_path = os.path.join(DUMP_DIR, file_name)

        if not os.path.exists(file_path):
            print(f"⚠️ Warning: File '{file_path}' not found. Skipping...")
            continue

        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter="\t")
            headers = next(reader)  # Skip the header row

            for row in reader:
                row_data = {}
                for col, val in zip(columns, row):
                    mapper = inspect(model)
                    column = mapper.columns.get(col)
                    print(column)
                    if isinstance(column.type, Boolean):
                        row_data[col] = True if val == 'TRUE' else False
                    elif not val:
                        row_data[col] = None
                    else:
                        row_data[col] = val
                # Map unique field value to id
                # if model == Transaction:
                #     if row_data['category']:
                #         row_data['category'] = model_map[f'{Category.__name__}:{row_data['category']}']
                #     if row_data['account']:
                #         row_data['account'] = model_map[f'{Account.__name__}:{row_data['account']}']
                db.add(model(**row_data))

        db.commit()
        if model == Category or model == Account:
            for r in db.query(model).all():
                model_map[f'{model.__name__}:{r.value}'] = r.id
        print(f"✅ Imported data to parent table {model} from {file_name} successfully.")
