from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import List, Dict, Optional
from datetime import date, datetime
import calendar
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import SectionEnum, Transaction
from schemas import TransactionCreate, TransactionUpdate
from utils.datetime import format_date

router = APIRouter()


# API Route to Fetch Transactions
@router.get("/transactions/", response_model=List[Dict])
def get_transactions(
    section: SectionEnum = Query(
        None, description="Filter transactions by section (EXPENSE or INCOME)"
    ),
    yearmonth: str = Query(
        date.today().strftime("%Y-%m"),
        regex="^\d{4}-\d{2}$", 
        description="Format: YYYY-MM (defaults to current month)"
    ),
    db: Session = Depends(get_db)
):
    # Fetch transactions for a given month using the provided SQL query.
    # Example input: yearmonth="2025-03"
    start_date = f"{yearmonth}-01"
    _, lastdate = calendar.monthrange(int(yearmonth[:4]), int(yearmonth[5:]))
    end_date = f"{yearmonth}-{lastdate}"
    transactions: list[Transaction] = (
        db.query(Transaction)
        .filter(and_(Transaction.date >= start_date, Transaction.date <= end_date, Transaction.section == section))
        .order_by(desc(Transaction.date), desc(Transaction.id))
        .all()
    )
    return [
        {
            "id": t.id,
            "date": format_date(t.date),
            "credit": t.credit,
            "amount": t.amount,
            "category_group": {
                "id": t.category_groups_rel.id,
                "emoji": t.category_groups_rel.emoji,
                "value": t.category_groups_rel.value,
            },
            "category": {
                "id": t.categories_rel.id,
                "emoji": t.categories_rel.emoji,
                "value": t.categories_rel.value,
            } if t.categories_rel else {},
            "account_group": {
                "id": t.account_groups_rel.id,
                "value": t.account_groups_rel.value,
            },
            "account": {
                "id": t.accounts_rel.id,
                "value": t.accounts_rel.value,
            } if t.accounts_rel else {},
            "note": t.note
        } for t in transactions
    ]

@router.post("/transactions/")
def create_transaction(
    section: SectionEnum = Query(
        None, description="Filter transactions by section (EXPENSE or INCOME)"
    ),
    transaction: TransactionCreate = Body(...),
    db: Session = Depends(get_db)
):
    new_transaction = Transaction(
        date=transaction.date,
        credit=True if section == SectionEnum.INCOME or section == SectionEnum.INVESTMENT else False, 
        amount=transaction.amount,
        section=section,
        category_group=transaction.category_group,
        category=transaction.category,
        account_group=transaction.account_group,
        account=transaction.account
    ).create()
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    new_transaction.date = format_date(new_transaction.date)
    return new_transaction

@router.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: int, transaction_data: TransactionUpdate = Body(...), db: Session = Depends(get_db)):
    transaction: Transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Update fields
    if transaction_data.date:
        transaction.date = transaction_data.date
    if transaction_data.amount:
        transaction.amount = transaction_data.amount
    if transaction_data.category:
        transaction.category = transaction_data.category
    if transaction_data.categorygroup:
        transaction.category_group = transaction_data.categorygroup
    if transaction_data.account:
        transaction.account = transaction_data.account
    if transaction_data.accountgroup:
        transaction.account_group = transaction_data.accountgroup
    transaction.updated_date=datetime.now(),

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
    income = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(Transaction.section == SectionEnum.INCOME)
        .scalar()
    )
    expense = (
        db.query(func.sum(Transaction.amount))
        .filter(Transaction.section == SectionEnum.EXPENSE)
        .scalar()
    )
    return {
        "balance": income - expense,
        "expense": expense,
        "income": income
    }
