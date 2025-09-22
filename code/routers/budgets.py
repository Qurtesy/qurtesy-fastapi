from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Budget, PersonalSectionEnum
from models.transaction import Transaction
from schemas import BudgetCreate, BudgetUpdate

router = APIRouter()


@router.get("/budgets/", response_model=List[Dict])
def get_budgets(
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    year: Optional[int] = Query(None, ge=2020, description="Filter by year"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db)
):
    query = db.query(Budget).options(joinedload(Budget.category_rel))
    
    if month:
        query = query.filter(Budget.month == month)
    if year:
        query = query.filter(Budget.year == year)
    if category_id:
        query = query.filter(Budget.category_id == category_id)
    
    budgets = query.order_by(Budget.year.desc(), Budget.month.desc()).all()
    
    return [
        {
            "id": budget.id,
            "category": {
                "id": budget.category_rel.id,
                "name": budget.category_rel.name,
                "emoji": budget.category_rel.emoji
            },
            "month": budget.month,
            "year": budget.year,
            "budgeted_amount": budget.budgeted_amount,
            "spent_amount": budget.spent_amount,
            "remaining_amount": budget.budgeted_amount - budget.spent_amount,
            "percentage_used": (budget.spent_amount / budget.budgeted_amount * 100) if budget.budgeted_amount > 0 else 0,
            "is_over_budget": budget.spent_amount > budget.budgeted_amount
        } for budget in budgets
    ]


@router.get("/budgets/{budget_id}", response_model=Dict)
def get_budget(budget_id: int, db: Session = Depends(get_db)):
    budget = db.query(Budget).options(joinedload(Budget.category_rel))\
        .filter(Budget.id == budget_id).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return {
        "id": budget.id,
        "category": {
            "id": budget.category_rel.id,
            "name": budget.category_rel.name,
            "emoji": budget.category_rel.emoji
        },
        "month": budget.month,
        "year": budget.year,
        "budgeted_amount": budget.budgeted_amount,
        "spent_amount": budget.spent_amount,
        "remaining_amount": budget.budgeted_amount - budget.spent_amount,
        "percentage_used": (budget.spent_amount / budget.budgeted_amount * 100) if budget.budgeted_amount > 0 else 0,
        "is_over_budget": budget.spent_amount > budget.budgeted_amount,
        "created_at": budget.created_at,
        "updated_at": budget.updated_at
    }


@router.post("/budgets/", response_model=Dict)
def create_budget(budget: BudgetCreate = Body(...), db: Session = Depends(get_db)):
    # Check if budget already exists for this category, month, and year
    existing_budget = db.query(Budget).filter(
        and_(
            Budget.category_id == budget.category_id,
            Budget.month == budget.month,
            Budget.year == budget.year
        )
    ).first()
    
    if existing_budget:
        raise HTTPException(
            status_code=400, 
            detail="Budget already exists for this category and time period"
        )
    
    # Calculate current spent amount for this category and time period
    spent_amount = db.query(func.coalesce(func.sum(Transaction.amount), 0))\
                    .filter(and_(
                        Transaction.category_id == budget.category_id,
                        func.extract('month', Transaction.date) == budget.month,
                        func.extract('year', Transaction.date) == budget.year,
                        Transaction.section == PersonalSectionEnum.EXPENSE
                    )).scalar()
    
    new_budget = Budget(
        category_id=budget.category_id,
        month=budget.month,
        year=budget.year,
        budgeted_amount=budget.budgeted_amount,
        spent_amount=spent_amount
    )
    
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    
    return {
        "id": new_budget.id,
        "message": "Budget created successfully"
    }


@router.put("/budgets/{budget_id}", response_model=Dict)
def update_budget(
    budget_id: int, 
    budget_data: BudgetUpdate = Body(...), 
    db: Session = Depends(get_db)
):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    if budget_data.budgeted_amount is not None:
        budget.budgeted_amount = budget_data.budgeted_amount
    
    budget.updated_date = datetime.now().date()
    db.commit()
    
    return {"message": "Budget updated successfully"}


@router.delete("/budgets/{budget_id}", response_model=Dict)
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    db.delete(budget)
    db.commit()
    
    return {"message": "Budget deleted successfully"}


@router.post("/budgets/refresh-spent-amounts", response_model=Dict)
def refresh_budget_spent_amounts(db: Session = Depends(get_db)):
    """Refresh all budget spent amounts based on actual transactions"""
    budgets = db.query(Budget).all()
    updated_count = 0
    
    for budget in budgets:
        spent_amount = db.query(func.coalesce(func.sum(Transaction.amount), 0))\
                        .filter(and_(
                            Transaction.category_id == budget.category_id,
                            func.extract('month', Transaction.date) == budget.month,
                            func.extract('year', Transaction.date) == budget.year,
                            Transaction.section == PersonalSectionEnum.EXPENSE
                        )).scalar()
        
        if budget.spent_amount != spent_amount:
            budget.spent_amount = spent_amount
            budget.updated_date = datetime.now().date()
            updated_count += 1
    
    db.commit()
    
    return {
        "message": f"Successfully refreshed {updated_count} budgets",
        "updated_count": updated_count
    }


@router.get("/budgets/summary/{year}/{month}", response_model=Dict)
def get_budget_summary(year: int, month: int, db: Session = Depends(get_db)):
    """Get budget summary for a specific month"""
    budgets = db.query(Budget).options(joinedload(Budget.category_rel))\
                .filter(and_(Budget.year == year, Budget.month == month)).all()
    
    if not budgets:
        return {
            "year": year,
            "month": month,
            "total_budgeted": 0,
            "total_spent": 0,
            "budgets": []
        }
    
    total_budgeted = sum(b.budgeted_amount for b in budgets)
    total_spent = sum(b.spent_amount for b in budgets)
    
    return {
        "year": year,
        "month": month,
        "total_budgeted": total_budgeted,
        "total_spent": total_spent,
        "remaining_budget": total_budgeted - total_spent,
        "percentage_used": (total_spent / total_budgeted * 100) if total_budgeted > 0 else 0,
        "budgets": [
            {
                "id": budget.id,
                "category": {
                    "id": budget.category_rel.id,
                    "name": budget.category_rel.name,
                    "emoji": budget.category_rel.emoji
                },
                "budgeted_amount": budget.budgeted_amount,
                "spent_amount": budget.spent_amount,
                "remaining_amount": budget.budgeted_amount - budget.spent_amount,
                "percentage_used": (budget.spent_amount / budget.budgeted_amount * 100) if budget.budgeted_amount > 0 else 0,
                "is_over_budget": budget.spent_amount > budget.budgeted_amount
            } for budget in budgets
        ]
    }