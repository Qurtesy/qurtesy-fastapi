from sqlalchemy import create_engine, MetaData, select, String
from config import db_path

def fetch_all_records():
    """
    Fetch all records from all tables in an SQLite database using SQLAlchemy.

    Returns:
        dict: A dictionary where keys are table names and values are lists of rows.
    """
    # Connect to the SQLite database
    engine = create_engine(f"sqlite:///{db_path}")
    metadata = MetaData()

    # Reflect the tables
    metadata.reflect(bind=engine)

    records = {}

    # Loop through all tables
    with engine.connect() as connection:
        for table_name, table in metadata.tables.items():
            # Patch datetime columns to String
            for col in table.columns:
                if str(col.type).lower() in ("datetime", "timestamp", "date"):
                    col.type = String()  # override


            query = select(table)
            result = connection.execute(query).fetchall()
            records[table_name] = [dict(row._mapping) for row in result]

    return records


if __name__ == "__main__":
    data = fetch_all_records()

    # Print results
    for table, rows in data.items():
        print(f"\nTable: {table}")
        for row in rows:
            print(row)
