#!/usr/bin/env python3
"""
Data Import Script for Qurtesy Finance
Imports transactions from CSV and sets up initial categories and accounts
"""

import csv
import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the code directory to the path
sys.path.append('/Users/souvikdey/Documents/qurtesy/server/code')

from models import Base, Transaction, Category, Account, SectionEnum
from config import DATABASE_URL

def setup_database():
    """Create database engine and session"""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def create_categories_and_accounts(db, transactions_data):
    """Create categories and accounts from transaction data"""
    categories = set()
    accounts = set()
    
    # Extract unique categories and accounts
    for row in transactions_data:
        if row['category']:
            categories.add((row['category'], row['section']))
        if row['account']:
            accounts.add(row['account'])
    
    # Create categories
    category_map = {}
    for category_name, section in categories:
        # Extract emoji from category name if present
        emoji = None
        if category_name.startswith(('🎮', '🍟', '🚃', '💰', '🏠', '📱', '🎯', '🛒', '⚡', '🏥')):
            emoji = category_name[0]
            category_name = category_name[2:].strip()  # Remove emoji and space
        
        existing_category = db.query(Category).filter(Category.value == category_name).first()
        if not existing_category:
            new_category = Category(
                value=category_name,
                emoji=emoji,
                section=SectionEnum(section),
                created_date=datetime.now().date(),
                updated_date=datetime.now().date()
            )
            db.add(new_category)
            db.flush()
            category_map[category_name] = new_category.id
        else:
            category_map[category_name] = existing_category.id
    
    # Create accounts
    account_map = {}
    for account_name in accounts:
        existing_account = db.query(Account).filter(Account.value == account_name).first()
        if not existing_account:
            new_account = Account(
                value=account_name,
                created_date=datetime.now().date(),
                updated_date=datetime.now().date()
            )
            db.add(new_account)
            db.flush()
            account_map[account_name] = new_account.id
        else:
            account_map[account_name] = existing_account.id
    
    db.commit()
    return category_map, account_map

def import_transactions(csv_file_path):
    """Import transactions from CSV file"""
    db = setup_database()
    
    try:
        # Read CSV data
        transactions_data = []
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                transactions_data.append({
                    'date': row['date'],
                    'section': row['section'],
                    'amount': float(row['amount']) if row['amount'] else 0,
                    'category': row['category'].strip() if row['category'] else None,
                    'account': row['account'].strip() if row['account'] else None,
                    'note': row.get('note', '').strip() if len(row) > 5 else None
                })
        
        print(f"Read {len(transactions_data)} transactions from CSV")
        
        # Create categories and accounts
        print("Creating categories and accounts...")
        category_map, account_map = create_categories_and_accounts(db, transactions_data)
        
        print(f"Created {len(category_map)} categories and {len(account_map)} accounts")
        
        # Import transactions
        print("Importing transactions...")
        imported_count = 0
        skipped_count = 0
        
        for row in transactions_data:
            try:
                # Parse date
                transaction_date = datetime.strptime(row['date'], '%d/%m/%Y').date()
                
                # Handle transfers differently
                if row['section'] == 'TRANSFER':
                    # For transfers, amount can be negative (outgoing) or positive (incoming)
                    credit = row['amount'] > 0
                    amount = abs(row['amount'])
                else:
                    # For regular transactions
                    credit = row['section'] in ['INCOME', 'INVESTMENT']
                    amount = row['amount']
                
                # Skip if amount is 0
                if amount == 0:
                    skipped_count += 1
                    continue
                
                # Get category and account IDs
                category_id = None
                if row['category']:
                    # Clean category name (remove emoji)
                    clean_category = row['category']
                    if clean_category.startswith(('🎮', '🍟', '🚃', '💰', '🏠', '📱', '🎯', '🛒', '⚡', '🏥')):
                        clean_category = clean_category[2:].strip()
                    category_id = category_map.get(clean_category)
                
                account_id = account_map.get(row['account']) if row['account'] else None
                
                # Create transaction
                transaction = Transaction(
                    date=transaction_date,
                    credit=credit,
                    amount=amount,
                    section=SectionEnum(row['section']),
                    category_id=category_id,
                    account_id=account_id,
                    note=row['note']
                ).create()
                
                db.add(transaction)
                imported_count += 1
                
            except Exception as e:
                print(f"Error importing transaction {row}: {e}")
                skipped_count += 1
        
        # Commit all transactions
        db.commit()
        
        print(f"Successfully imported {imported_count} transactions")
        print(f"Skipped {skipped_count} transactions")
        
        # Print summary
        print("\n=== Import Summary ===")
        print(f"Total transactions processed: {len(transactions_data)}")
        print(f"Successfully imported: {imported_count}")
        print(f"Skipped: {skipped_count}")
        print(f"Categories created: {len(category_map)}")
        print(f"Accounts created: {len(account_map)}")
        
    except Exception as e:
        print(f"Error during import: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    csv_file_path = "/Users/souvikdey/Documents/qurtesy/server/db_dump/transactions.csv"
    
    if not os.path.exists(csv_file_path):
        print(f"CSV file not found: {csv_file_path}")
        sys.exit(1)
    
    print("Starting data import...")
    import_transactions(csv_file_path)
    print("Data import completed!")
