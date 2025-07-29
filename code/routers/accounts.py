from datetime import datetime
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, case, or_, and_
from database import get_db
from models import SectionEnum, Account, Transaction
from schemas import AccountCreate, AccountUpdate

router = APIRouter()

@router.get("/accounts/", response_model=List[Dict])
async def read_accounts(
    db: Session = Depends(get_db)
):
    # Get accounts with calculated balance from transactions
    accounts_query = db.query(Account).order_by(Account.id).all()
    
    result = []
    for account in accounts_query:
        # Calculate balance from transactions
        # For each account: sum(credit transactions) - sum(debit transactions)
        transaction_balance = db.query(
            func.coalesce(
                func.sum(
                    case(
                        (Transaction.credit == True, Transaction.amount),
                        else_=-Transaction.amount
                    )
                ), 0
            )
        ).filter(Transaction.account_id == account.id).scalar()
        
        result.append({
            "id": account.id,
            "value": account.value,
            "balance": account.balance or 0.0,  # Manual balance
            "calculated_balance": float(transaction_balance or 0.0),  # Calculated from transactions
            "balance_difference": (account.balance or 0.0) - float(transaction_balance or 0.0)
        })
    
    return result

@router.post("/accounts/", tags=["accounts"])
async def create_account(
    account: AccountCreate = Body(...),
    db: Session = Depends(get_db)
):
    # Check for uniqueness constraints
    if (
        db.query(Account).filter(Account.value == account.value).first()
    ):
        raise HTTPException(status_code=400, detail="Value must be unique")

    new_account = Account(
        value=account.value,
        balance=account.balance or 0.0
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return {
        "id": new_account.id,
        "value": new_account.value,
        "balance": new_account.balance
    }

@router.put("/accounts/{account_id}", response_model=dict)
def update_account(account_id: int, account_data: AccountUpdate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Check for uniqueness constraints
    if (
        db.query(Account).filter(Account.value == account_data.value, Account.id != account_id).first()
    ):
        raise HTTPException(status_code=400, detail="Value must be unique")

    # Store previous balance for difference calculation
    previous_balance = account.balance or 0.0

    # Update fields
    account.value = account_data.value
    if account_data.balance is not None:
        account.balance = account_data.balance

    db.commit()
    db.refresh(account)

    return {
        "message": "Account updated successfully",
        "account": {
            "id": account.id,
            "value": account.value,
            "balance": account.balance
        },
        "previous_balance": previous_balance,
        "balance_difference": account.balance - previous_balance
    }

@router.delete("/accounts/{account_id}", response_model=dict)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        db.delete(account)
        db.commit()
        return {"message": "Account deleted successfully"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete account as it is linked to existing transactions"
        )

@router.patch("/accounts/{account_id}/balance", response_model=dict)
def update_account_balance(account_id: int, balance_data: dict, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Store previous balance for difference calculation  
    previous_balance = account.balance or 0.0
    new_balance = balance_data.get("balance", 0.0)
    
    # Update balance
    account.balance = new_balance
    db.commit()
    db.refresh(account)
    
    return {
        "message": "Account balance updated successfully",
        "account": {
            "id": account.id,
            "value": account.value,
            "balance": account.balance
        },
        "previous_balance": previous_balance,
        "balance_difference": account.balance - previous_balance
    }

@router.post("/accounts/bulk")
def bulk_create_accounts(
    accounts: List[Dict] = Body(...),
    db: Session = Depends(get_db)
):
    """Bulk create accounts from CSV data or array with uniqueness validation"""
    created_accounts = []
    all_accounts = []
    errors = []

    # Step 1: Check for duplicates within the batch itself
    seen_values = set()
    
    valid_accounts = []
    
    for idx, account_data in enumerate(accounts):
        try:
            value = account_data.get('value')
            
            # Validate required fields
            if not value:
                errors.append({
                    "row": idx + 1, 
                    "error": "Missing required fields: value"
                })
                continue
            
            # Add to seen sets
            seen_values.add(value)
            
            # Add to valid accounts for database check
            valid_accounts.append({
                'index': idx,
                'data': account_data
            })
            
        except Exception as e:
            errors.append({"row": idx + 1, "error": f"Data validation error: {str(e)}"})
    
    # Step 2: Check against existing accounts in database (bulk query)
    if valid_accounts:
        # Extract values for bulk query
        values_to_check = [cat['data']['value'] for cat in valid_accounts]
        
        # Single query to check existing values
        existing_results = db.query(Account.value, Account.id)\
            .filter(Account.value.in_(values_to_check))\
            .all()
        for value, id in existing_results:
            all_accounts.append({
                'id': id,
                'value': value
            })
        existing_values = set(
            row[0] for row in existing_results
        )
        
        # Step 3: Validate each account against database
        final_valid_accounts = []
        
        for acc in valid_accounts:
            idx = acc['index']
            account_data = acc['data']
            value = account_data['value']
            
            # Check if value already exists in database
            if value in existing_values:
                errors.append({
                    "row": idx + 1,
                    "error": f"Value '{value}' already exists in database"
                })
                continue
            
            final_valid_accounts.append(account_data)
    
    # Step 4: Create valid accounts
    for account_data in final_valid_accounts:
        try:
            new_account = Account(
                value=account_data.get('value'),
                created_date=datetime.now().date(),
                updated_date=datetime.now().date()
            )
            
            db.add(new_account)
            created_accounts.append(new_account)
            
        except Exception as e:
            errors.append({
                "row": "unknown", 
                "error": f"Database insertion error: {str(e)}"
            })
    
    # Step 5: Commit transaction
    try:
        if created_accounts:
            db.commit()
            # Refresh all created accounts
            for account in created_accounts:
                db.refresh(account)
        all_accounts.extend(created_accounts)
        return {
            "message": f"Successfully created {len(created_accounts)} accounts",
            "created_count": len(created_accounts),
            "total_submitted": len(accounts),
            "errors_count": len(errors),
            "errors": errors,
            "accounts": all_accounts
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Bulk insert failed during commit: {str(e)}"
        )
