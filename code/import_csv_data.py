import csv
import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session

# Add the parent directory to sys.path so we can import from the code directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, SessionLocal
from models import Transaction, Category, Account, SectionEnum


def parse_csv_and_insert_data():
    """Parse CSV file and insert data into database"""
    db = SessionLocal()
    
    try:
        # Read CSV file
        csv_file_path = "/code/db_dump/transactions.csv"
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            categories_cache = {}
            accounts_cache = {}
            transactions_to_insert = []
            
            for row in reader:
                try:
                    # Parse date
                    date_obj = datetime.strptime(row['date'], '%d/%m/%Y').date()
                    
                    # Parse section
                    section = SectionEnum(row['section'])
                    
                    # Parse amount
                    amount = float(row['amount'])
                    
                    # Handle category
                    category_id = None
                    if row.get('category') and row['category'].strip():
                        category_name = row['category'].strip()
                        
                        if category_name not in categories_cache:
                            # Check if category exists
                            existing_category = db.query(Category).filter(
                                Category.value == category_name,
                                Category.section == section
                            ).first()
                            
                            if not existing_category:
                                # Extract emoji if present
                                emoji = None
                                if any(ord(char) > 127 for char in category_name):
                                    # Likely contains emoji - extract first emoji
                                    for char in category_name:
                                        if ord(char) > 127:
                                            emoji = char
                                            break
                                
                                # Create new category
                                new_category = Category(
                                    value=category_name,
                                    emoji=emoji,
                                    section=section,
                                    created_date=datetime.now().date(),
                                    updated_date=datetime.now().date()
                                )
                                db.add(new_category)
                                db.flush()  # Get the ID
                                categories_cache[category_name] = new_category.id
                            else:
                                categories_cache[category_name] = existing_category.id
                        
                        category_id = categories_cache[category_name]
                    
                    # Handle account
                    account_id = None
                    if row.get('account') and row['account'].strip():
                        account_name = row['account'].strip()
                        
                        if account_name not in accounts_cache:
                            # Check if account exists
                            existing_account = db.query(Account).filter(
                                Account.value == account_name
                            ).first()
                            
                            if not existing_account:
                                # Create new account
                                new_account = Account(
                                    value=account_name,
                                    created_date=datetime.now().date(),
                                    updated_date=datetime.now().date()
                                )
                                db.add(new_account)
                                db.flush()  # Get the ID
                                accounts_cache[account_name] = new_account.id
                            else:
                                accounts_cache[account_name] = existing_account.id
                        
                        account_id = accounts_cache[account_name]
                    
                    # Handle note - look for additional columns after the main ones
                    note = None
                    # Get all keys beyond the standard ones
                    extra_keys = [k for k in row.keys() if k not in ['date', 'section', 'amount', 'category', 'account'] and k is not None]
                    if extra_keys:
                        note_parts = []
                        for key in extra_keys:
                            if row[key] and str(row[key]).strip():
                                note_parts.append(str(row[key]).strip())
                        if note_parts:
                            note = ', '.join(note_parts)
                    
                    # Determine if it's credit or debit
                    credit = section in [SectionEnum.INCOME, SectionEnum.INVESTMENT]
                    if section == SectionEnum.TRANSFER:
                        credit = amount > 0
                        amount = abs(amount)
                    
                    # Create transaction
                    transaction = Transaction(
                        date=date_obj,
                        credit=credit,
                        amount=amount,
                        section=section,
                        category_id=category_id,
                        account_id=account_id,
                        note=note,
                        created_date=datetime.now().date(),
                        updated_date=datetime.now().date()
                    )
                    
                    transactions_to_insert.append(transaction)
                    
                except Exception as e:
                    print(f"Error processing row {row}: {e}")
                    continue
            
            # Insert all transactions
            db.add_all(transactions_to_insert)
            db.commit()
            
            print(f"Successfully imported {len(transactions_to_insert)} transactions")
            print(f"Created {len(categories_cache)} categories")
            print(f"Created {len(accounts_cache)} accounts")
            
    except Exception as e:
        print(f"Error importing data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    parse_csv_and_insert_data()
