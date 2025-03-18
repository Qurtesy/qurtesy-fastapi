from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from code.database import get_db
from code.models import Transaction
from code.schemas import TransactionCreate

router = APIRouter()


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
