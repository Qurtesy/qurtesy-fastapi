from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import List, Dict, Optional
from datetime import date, datetime
import calendar
from pydantic import BaseModel
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from code.database import get_db
from code.models import Transaction, SectionEnum
from code.schemas import TransactionCreate, TransactionUpdate
from code.utils.datetime import format_date

router = APIRouter()


# API Route to Fetch Transactions
@router.get("/transactions/", response_model=List[Dict])
def get_transactions(
    yearmonth: str = Query(
        date.today().strftime("%Y-%m"),
        regex="^\d{4}-\d{2}$", 
        description="Format: YYYY-MM (defaults to current month)"
    ),
    section: Optional[SectionEnum] = Query(
        None, description="Filter transactions by section (EXPENSE or INCOME)"
    ),
    db: Session = Depends(get_db)
):
    # Fetch transactions for a given month using the provided SQL query.
    # Example input: yearmonth="2025-03"
    start_date = f"{yearmonth}-01"
    _, lastdate = calendar.monthrange(int(yearmonth[:4]), int(yearmonth[5:]))
    end_date = f"{yearmonth}-{lastdate}"
    transactions = (
        db.query(Transaction)
        .filter(and_(Transaction.date >= start_date, Transaction.date <= end_date, Transaction.section == section))
        .order_by(desc(Transaction.date), desc(Transaction.id))
        .all()
    )
    balance = db.query(func.sum(Transaction.amount)).scalar()
    return [
        {
            "id": t.id,
            "date": format_date(t.date),
            "amount": t.amount,
            "category": {
                "id": t.category_rel.id,
                "emoji": t.category_rel.emoji,
                "value": t.category_rel.value,
            },
            "account": {
                "id": t.account_rel.id,
                "value": t.account_rel.value,
            },
            "balance": balance
        } for t in transactions
    ]

@router.post("/transactions/")
def create_transaction(transaction: TransactionCreate = Body(...), db: Session = Depends(get_db)):
    new_transaction = Transaction(
        date=transaction.date,
        amount=transaction.amount,
        category=transaction.category,
        account=transaction.account
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    new_transaction.date = new_transaction.date.strftime("%d/%m/%Y")
    return new_transaction

@router.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: int, transaction_data: TransactionUpdate = Body(...), db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Update fields
    if transaction_data.date:
        transaction.date = transaction_data.date
    if transaction_data.amount:
        transaction.amount = transaction_data.amount
    if transaction_data.category:
        transaction.category = transaction_data.category
    if transaction_data.account:
        transaction.account = transaction_data.account
    

    db.commit()
    db.refresh(transaction)

    return {"message": "Transaction updated successfully"}

@router.delete("/transactions/{transaction_id}", response_model=dict)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    try:
        db.delete(transaction)
        db.commit()
        return {"message": "Transaction deleted successfully"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete transaction as it is linked to existing transactions"
        )

@router.get("/transactions/summary", response_model=Dict)
def summary_transactions(db: Session = Depends(get_db)):
    balance = db.query(func.sum(Transaction.amount)).scalar()
    return {
        "balance": balance or 0,
        "expense": balance,
        "income": 0
    }
