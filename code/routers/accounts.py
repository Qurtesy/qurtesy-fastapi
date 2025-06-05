from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, case
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
