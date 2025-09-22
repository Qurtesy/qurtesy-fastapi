from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import RecurringTransaction, PersonalSectionEnum
from models.transaction import Transaction
from schemas import RecurringTransactionCreate, RecurringTransactionUpdate

router = APIRouter()


def calculate_next_execution(start_date: date, frequency: str) -> date:
    """Calculate the next execution date based on frequency"""
    today = date.today()
    
    if frequency == "daily":
        return today + timedelta(days=1)
    elif frequency == "weekly":
        return today + timedelta(weeks=1)
    elif frequency == "monthly":
        return today + relativedelta(months=1)
    elif frequency == "yearly":
        return today + relativedelta(years=1)
    else:
        return today + timedelta(days=1)


@router.get("/recurring-transactions/", response_model=List[Dict])
def get_recurring_transactions(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    section: Optional[PersonalSectionEnum] = Query(None, description="Filter by section"),
    db: Session = Depends(get_db)
):
    query = db.query(RecurringTransaction).options(
        joinedload(RecurringTransaction.category_rel),
        joinedload(RecurringTransaction.account_rel)
    )
    
    if is_active is not None:
        query = query.filter(RecurringTransaction.is_active == is_active)
    if section:
        query = query.filter(RecurringTransaction.section == section)
    
    recurring_transactions = query.order_by(RecurringTransaction.next_execution).all()
    
    return [
        {
            "id": rt.id,
            "name": rt.name,
            "amount": rt.amount,
            "section": rt.section,
            "category": {
                "id": rt.category_rel.id,
                "name": rt.category_rel.name,
                "emoji": rt.category_rel.emoji
            } if rt.category_rel else None,
            "account": {
                "id": rt.account_rel.id,
                "name": rt.account_rel.name
            } if rt.account_rel else None,
            "frequency": rt.frequency,
            "start_date": rt.start_date.strftime("%d/%m/%Y"),
            "end_date": rt.end_date.strftime("%d/%m/%Y") if rt.end_date else None,
            "next_execution": rt.next_execution.strftime("%d/%m/%Y"),
            "is_active": rt.is_active,
            "note": rt.note
        } for rt in recurring_transactions
    ]


@router.get("/recurring-transactions/{recurring_id}", response_model=Dict)
def get_recurring_transaction(recurring_id: int, db: Session = Depends(get_db)):
    rt = db.query(RecurringTransaction).options(
        joinedload(RecurringTransaction.category_rel),
        joinedload(RecurringTransaction.account_rel)
    ).filter(RecurringTransaction.id == recurring_id).first()
    
    if not rt:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    
    return {
        "id": rt.id,
        "name": rt.name,
        "amount": rt.amount,
        "section": rt.section,
        "category": {
            "id": rt.category_rel.id,
            "name": rt.category_rel.name,
            "emoji": rt.category_rel.emoji
        } if rt.category_rel else None,
        "account": {
            "id": rt.account_rel.id,
            "name": rt.account_rel.name
        } if rt.account_rel else None,
        "frequency": rt.frequency,
        "start_date": rt.start_date.strftime("%d/%m/%Y"),
        "end_date": rt.end_date.strftime("%d/%m/%Y") if rt.end_date else None,
        "next_execution": rt.next_execution.strftime("%d/%m/%Y"),
        "is_active": rt.is_active,
        "note": rt.note,
        "created_at": rt.created_at,
        "updated_at": rt.updated_at
    }


@router.post("/recurring-transactions/", response_model=Dict)
def create_recurring_transaction(
    section: PersonalSectionEnum = Query(..., description="Transaction section"),
    recurring: RecurringTransactionCreate = Body(...),
    db: Session = Depends(get_db)
):
    next_execution = calculate_next_execution(recurring.start_date, recurring.frequency)
    
    new_recurring = RecurringTransaction(
        name=recurring.name,
        amount=recurring.amount,
        section=section,
        category_id=recurring.category_id,
        account_id=recurring.account_id,
        frequency=recurring.frequency,
        start_date=recurring.start_date,
        end_date=recurring.end_date,
        next_execution=next_execution,
        note=recurring.note
    )
    
    db.add(new_recurring)
    db.commit()
    db.refresh(new_recurring)
    
    return {
        "id": new_recurring.id,
        "message": "Recurring transaction created successfully"
    }


@router.put("/recurring-transactions/{recurring_id}", response_model=Dict)
def update_recurring_transaction(
    recurring_id: int,
    recurring_data: RecurringTransactionUpdate = Body(...),
    db: Session = Depends(get_db)
):
    rt = db.query(RecurringTransaction).filter(RecurringTransaction.id == recurring_id).first()
    
    if not rt:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    
    # Update fields
    if recurring_data.name is not None:
        rt.name = recurring_data.name
    if recurring_data.amount is not None:
        rt.amount = recurring_data.amount
    if recurring_data.category_id is not None:
        rt.category_id = recurring_data.category_id
    if recurring_data.account_id is not None:
        rt.account_id = recurring_data.account_id
    if recurring_data.frequency is not None:
        rt.frequency = recurring_data.frequency
        # Recalculate next execution if frequency changed
        rt.next_execution = calculate_next_execution(date.today(), rt.frequency)
    if recurring_data.end_date is not None:
        rt.end_date = recurring_data.end_date
    if recurring_data.is_active is not None:
        rt.is_active = recurring_data.is_active
    if recurring_data.note is not None:
        rt.note = recurring_data.note
    
    rt.updated_date = datetime.now().date()
    db.commit()
    
    return {"message": "Recurring transaction updated successfully"}


@router.delete("/recurring-transactions/{recurring_id}", response_model=Dict)
def delete_recurring_transaction(recurring_id: int, db: Session = Depends(get_db)):
    rt = db.query(RecurringTransaction).filter(RecurringTransaction.id == recurring_id).first()
    
    if not rt:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    
    db.delete(rt)
    db.commit()
    
    return {"message": "Recurring transaction deleted successfully"}


@router.post("/recurring-transactions/execute-pending", response_model=Dict)
def execute_pending_recurring_transactions(db: Session = Depends(get_db)):
    """Execute all pending recurring transactions"""
    today = date.today()
    
    pending_transactions = db.query(RecurringTransaction).filter(
        and_(
            RecurringTransaction.is_active == True,
            RecurringTransaction.next_execution <= today,
            or_(
                RecurringTransaction.end_date.is_(None),
                RecurringTransaction.end_date >= today
            )
        )
    ).all()
    
    executed_count = 0
    errors = []
    
    for rt in pending_transactions:
        try:
            # Create the actual transaction
            new_transaction = Transaction(
                date=today,
                credit=True if rt.section in [PersonalSectionEnum.INCOME, PersonalSectionEnum.INVESTMENT] else False,
                amount=rt.amount,
                section=rt.section,
                category_id=rt.category_id,
                account_id=rt.account_id,
                note=f"Auto-generated from recurring: {rt.name}"
            ).create()
            
            db.add(new_transaction)
            
            # Update next execution date
            if rt.frequency == "daily":
                rt.next_execution = rt.next_execution + timedelta(days=1)
            elif rt.frequency == "weekly":
                rt.next_execution = rt.next_execution + timedelta(weeks=1)
            elif rt.frequency == "monthly":
                rt.next_execution = rt.next_execution + relativedelta(months=1)
            elif rt.frequency == "yearly":
                rt.next_execution = rt.next_execution + relativedelta(years=1)
            
            executed_count += 1
            
        except Exception as e:
            errors.append({"recurring_id": rt.id, "name": rt.name, "error": str(e)})
    
    try:
        db.commit()
        return {
            "message": f"Successfully executed {executed_count} recurring transactions",
            "executed_count": executed_count,
            "errors": errors
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to execute recurring transactions: {str(e)}")


@router.get("/recurring-transactions/due-today", response_model=List[Dict])
def get_due_today(db: Session = Depends(get_db)):
    """Get recurring transactions due today"""
    today = date.today()
    
    due_transactions = db.query(RecurringTransaction).options(
        joinedload(RecurringTransaction.category_rel),
        joinedload(RecurringTransaction.account_rel)
    ).filter(
        and_(
            RecurringTransaction.is_active == True,
            RecurringTransaction.next_execution <= today,
            or_(
                RecurringTransaction.end_date.is_(None),
                RecurringTransaction.end_date >= today
            )
        )
    ).all()
    
    return [
        {
            "id": rt.id,
            "name": rt.name,
            "amount": rt.amount,
            "section": rt.section,
            "category": {
                "id": rt.category_rel.id,
                "name": rt.category_rel.name,
                "emoji": rt.category_rel.emoji
            } if rt.category_rel else None,
            "account": {
                "id": rt.account_rel.id,
                "name": rt.account_rel.name
            } if rt.account_rel else None,
            "frequency": rt.frequency,
            "next_execution": rt.next_execution.strftime("%d/%m/%Y"),
            "days_overdue": (today - rt.next_execution).days
        } for rt in due_transactions
    ]
