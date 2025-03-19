from fastapi import APIRouter, Depends, Query, Body
from typing import List, Dict
from datetime import date
from sqlalchemy import text
from sqlalchemy.orm import Session
from code.database import get_db
from code.models import Transaction
from code.schemas import TransactionCreate

router = APIRouter()

# API Route to Fetch Transactions
@router.get("/transactions/", response_model=List[Dict])
def get_transactions(yearmonth: str = Query(
        date.today().strftime("%Y-%m"),
        regex="^\d{4}-\d{2}$", 
        description="Format: YYYY-MM (defaults to current month)"
    ), db: Session = Depends(get_db)):
    # transactions = db.query(Transaction).all()
    # return [
    #     {"id": t.id, "date": t.date, "amount": t.amount, "category": t.category, "account": t.account}
    #     for t in transactions
    # ]
    """
    Fetch transactions for a given month using the provided SQL query.
    Example input: yearmonth="2025-03"
    """
    query = text(f"""
        SELECT
            t.date,
            t.amount,
            c.value AS category,
            c.emoji AS category_emoji,
            a.value AS account
        FROM finance.transactions t
        JOIN finance.categories c ON t.category = c.id
        JOIN finance.accounts a ON t.account = a.id
        WHERE date >= date(:start_date) AND date <= date(:end_date)
        ORDER BY date;
    """)

    start_date = f"{yearmonth}-01"
    end_date = f"{yearmonth}-31"

    result = db.execute(query, {"start_date": start_date, "end_date": end_date}).fetchall()

    return [
        {"date": row.date, "amount": row.amount, "category": row.category, "category_emoji": row.category_emoji, "account": row.account}
        for row in result
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
    return new_transaction
