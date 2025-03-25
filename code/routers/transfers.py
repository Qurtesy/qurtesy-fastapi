from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import List, Dict, Optional
from datetime import date, datetime
import calendar
from pydantic import BaseModel
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from code.database import get_db
from code.models import Category, Transaction, SectionEnum
from code.schemas import TransferCreate
from code.utils.datetime import format_date

router = APIRouter()

TRANSFER_CATEGORY = 'Transfer (Default)'


# API Route to Fetch Transactions
@router.post("/transfers/", response_model=List[Dict])
def create_transfer(
    transaction: TransferCreate = Body(...),
    db: Session = Depends(get_db)
):
    category = (
        db.query(Category)
        .filter(Category.value == TRANSFER_CATEGORY)
        .first()
    )
    debit_transaction = Transaction(
        date=transaction.date,
        amount=transaction.amount,
        section=SectionEnum.TRANSFER.name,
        category=category.id,
        account=transaction.from_account
    )
    db.add(debit_transaction)
    credit_transaction = Transaction(
        date=transaction.date,
        amount=transaction.amount,
        section=SectionEnum.TRANSFER.name,
        category=category.id,
        account=transaction.to_account
    )
    db.add(credit_transaction)
    db.commit()
    db.refresh(debit_transaction)
    db.refresh(credit_transaction)
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
            }
        } for t in [debit_transaction, credit_transaction]
    ]
    
