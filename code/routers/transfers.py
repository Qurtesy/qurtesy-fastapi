from fastapi import APIRouter, Depends, Body
from typing import List, Dict
from sqlalchemy.orm import Session
from database import get_db
from models import PersonalSectionEnum
from models.category import Category
from models.transaction import Transaction
from schemas.transfer import TransferCreate
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
        db.query(Category)
        .filter(Category.name == TRANSFER_CATEGORY)
        .first()
    )
    debit_transaction = Transaction(
        date=transaction.date,
        credit=False,
        amount=transaction.amount,
        section=PersonalSectionEnum.TRANSFER.name,
        category_id=category.id,
        account_id=transaction.from_account_id
    ).create()
    db.add(debit_transaction)
    credit_transaction = Transaction(
        date=transaction.date,
        credit=True,
        amount=transaction.amount,
        section=PersonalSectionEnum.TRANSFER.name,
        category_id=category.id,
        account_id=transaction.to_account_id
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
                "id": t.category_rel.id,
                "emoji": t.category_rel.emoji,
                "name": t.category_rel.name,
            },
            "account": {
                "id": t.account_rel.id,
                "name": t.account_rel.name,
            }
        } for t in [debit_transaction, credit_transaction]
    ]
    
