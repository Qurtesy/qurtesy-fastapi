from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from code.database import get_db
from code.models import SectionEnum, Account
from code.schemas import AccountCreate, AccountUpdate

router = APIRouter()


@router.get("/accounts/", response_model=List[Dict])
async def read_accounts(
    db: Session = Depends(get_db)
):
    accounts = (
        db.query(Account)
        .order_by(Account.id)
        .all()
    )
    return [
        {
            "id": c.id,
            "value": c.value
        } for c in accounts
    ]

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
        value=account.value
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account

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

    # Update fields
    account.value = account_data.value

    db.commit()
    db.refresh(account)

    return {"message": "Account updated successfully"}

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
