from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import List, Dict, Optional
from datetime import date, datetime
import calendar
from pydantic import BaseModel
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import CategoryGroup, Transaction, SectionEnum
from schemas import TransferCreate
from utils.datetime import format_date

router = APIRouter()

TRANSFER_CATEGORY = 'Transfer (Default)'


# API Route to Fetch Transactions
@router.post("/transfers/", response_model=List[Dict])
def create_transfer(
    transaction: TransferCreate = Body(...),
    db: Session = Depends(get_db)
):
    category = (
        db.query(CategoryGroup)
        .filter(CategoryGroup.value == TRANSFER_CATEGORY)
        .first()
    )
    debit_transaction = Transaction(
        date=transaction.date,
        credit=False,
        amount=transaction.amount,
        section=SectionEnum.TRANSFER.name,
        category_group=category.id,
        account_group=transaction.from_account
    ).create()
    db.add(debit_transaction)
    credit_transaction = Transaction(
        date=transaction.date,
        credit=True,
        amount=transaction.amount,
        section=SectionEnum.TRANSFER.name,
        category_group=category.id,
        account_group=transaction.to_account
    ).create()
    db.add(credit_transaction)
    db.commit()
    db.refresh(debit_transaction)
    db.refresh(credit_transaction)
    return [
        {
            "id": t.id,
            "date": format_date(t.date),
            "amount": t.amount,
            "category_group": {
                "id": t.category_groups_rel.id,
                "emoji": t.category_groups_rel.emoji,
                "value": t.category_groups_rel.value,
            },
            "account": {
                "id": t.account_groups_rel.id,
                "value": t.account_groups_rel.value,
            }
        } for t in [debit_transaction, credit_transaction]
    ]
    
