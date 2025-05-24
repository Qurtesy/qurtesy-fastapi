from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import List, Dict, Optional
from datetime import date, datetime
import calendar
from sqlalchemy import and_, desc, func, or_, extract, text
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import SectionEnum, Transaction, Category, Account
from schemas import TransactionCreate, TransactionUpdate
from utils.datetime import format_date

router = APIRouter()


@router.get("/transactions/", response_model=Dict)
def get_transactions(
    section: SectionEnum = Query(
        None, description="Filter transactions by section (EXPENSE, INCOME, etc.)"
    ),
    yearmonth: str = Query(
        date.today().strftime("%Y-%m"),
        regex=r"^\d{4}-\d{2}$", 
        description="Format: YYYY-MM (defaults to current month)"
    ),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search in notes, category, or account"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum amount filter"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum amount filter"),
    db: Session = Depends(get_db)
):
    # Build base query with joins
    query = db.query(Transaction).options(
        joinedload(Transaction.category_rel),
        joinedload(Transaction.account_rel)
    )
    
    # Date filter
    start_date = f"{yearmonth}-01"
    _, lastdate = calendar.monthrange(int(yearmonth[:4]), int(yearmonth[5:]))
    end_date = f"{yearmonth}-{lastdate}"
    query = query.filter(and_(Transaction.date >= start_date, Transaction.date <= end_date))
    
    # Section filter
    if section:
        query = query.filter(Transaction.section == section)
    
    # Category filter
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    
    # Account filter
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    
    # Amount filters
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)
    
    # Search filter
    if search:
        search_filter = or_(
            Transaction.note.ilike(f"%{search}%"),
            Category.value.ilike(f"%{search}%"),
            Account.value.ilike(f"%{search}%")
        )
        query = query.join(Category, Transaction.category_id == Category.id, isouter=True)\
                    .join(Account, Transaction.account_id == Account.id, isouter=True)\
                    .filter(search_filter)
    
    # Get total count for pagination
    total_count = query.count()
    
    # Apply pagination and ordering
    transactions = query.order_by(desc(Transaction.date), desc(Transaction.id))\
                       .offset((page - 1) * page_size)\
                       .limit(page_size)\
                       .all()
    
    return {
        "transactions": [
            {
                "id": t.id,
                "date": format_date(t.date),
                "credit": t.credit,
                "amount": t.amount,
                "section": t.section,
                "category": {
                    "id": t.category_rel.id,
                    "emoji": t.category_rel.emoji,
                    "value": t.category_rel.value,
                } if t.category_rel else None,
                "account": {
                    "id": t.account_rel.id,
                    "value": t.account_rel.value,
                } if t.account_rel else None,
                "note": t.note
            } for t in transactions
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": (total_count + page_size - 1) // page_size
        }
    }


@router.get("/transactions/{transaction_id}", response_model=Dict)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).options(
        joinedload(Transaction.category_rel),
        joinedload(Transaction.account_rel)
    ).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {
        "id": transaction.id,
        "date": format_date(transaction.date),
        "credit": transaction.credit,
        "amount": transaction.amount,
        "section": transaction.section,
        "category": {
            "id": transaction.category_rel.id,
            "emoji": transaction.category_rel.emoji,
            "value": transaction.category_rel.value,
        } if transaction.category_rel else None,
        "account": {
            "id": transaction.account_rel.id,
            "value": transaction.account_rel.value,
        } if transaction.account_rel else None,
        "note": transaction.note,
        "created_date": transaction.created_date,
        "updated_date": transaction.updated_date
    }


@router.post("/transactions/")
def create_transaction(
    section: SectionEnum = Query(
        None, description="Transaction section (EXPENSE, INCOME, etc.)"
    ),
    transaction: TransactionCreate = Body(...),
    db: Session = Depends(get_db)
):
    new_transaction = Transaction(
        date=transaction.date,
        credit=True if section in [SectionEnum.INCOME, SectionEnum.INVESTMENT] else False, 
        amount=transaction.amount,
        section=section,
        category_id=transaction.category_id,
        account_id=transaction.account_id,
        note=transaction.note
    ).create()
    
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
    return {
        "id": new_transaction.id,
        "date": format_date(new_transaction.date),
        "message": "Transaction created successfully"
    }


@router.put("/transactions/{transaction_id}")
def update_transaction(
    transaction_id: int, 
    transaction_data: TransactionUpdate = Body(...), 
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Update fields
    if transaction_data.date is not None:
        transaction.date = transaction_data.date
    if transaction_data.amount is not None:
        transaction.amount = transaction_data.amount
    if transaction_data.category_id is not None:
        transaction.category_id = transaction_data.category_id
    if transaction_data.account_id is not None:
        transaction.account_id = transaction_data.account_id
    if transaction_data.note is not None:
        transaction.note = transaction_data.note
    
    transaction.updated_date = datetime.now().date()

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
            detail="Cannot delete transaction due to database constraints"
        )


@router.post("/transactions/bulk")
def bulk_create_transactions(
    transactions: List[Dict] = Body(...),
    db: Session = Depends(get_db)
):
    """Bulk create transactions from CSV data or array"""
    created_transactions = []
    errors = []
    
    for idx, transaction_data in enumerate(transactions):
        try:
            # Parse the transaction data
            new_transaction = Transaction(
                date=datetime.strptime(transaction_data['date'], "%d/%m/%Y").date(),
                credit=transaction_data.get('credit', transaction_data['section'] in ['INCOME', 'INVESTMENT']),
                amount=float(transaction_data['amount']),
                section=SectionEnum(transaction_data['section']),
                category_id=transaction_data.get('category_id'),
                account_id=transaction_data.get('account_id'),
                note=transaction_data.get('note')
            ).create()
            
            db.add(new_transaction)
            created_transactions.append(new_transaction)
            
        except Exception as e:
            errors.append({"row": idx + 1, "error": str(e)})
    
    try:
        db.commit()
        return {
            "message": f"Successfully created {len(created_transactions)} transactions",
            "created_count": len(created_transactions),
            "errors": errors
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Bulk insert failed: {str(e)}")


@router.get("/transactions/summary", response_model=Dict)
def summary_transactions(
    start_date: Optional[str] = Query(None, description="Start date (DD/MM/YYYY)"),
    end_date: Optional[str] = Query(None, description="End date (DD/MM/YYYY)"),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction)
    
    # Apply date filters if provided
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%d/%m/%Y").date()
            query = query.filter(Transaction.date >= start_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use DD/MM/YYYY")
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%d/%m/%Y").date()
            query = query.filter(Transaction.date <= end_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use DD/MM/YYYY")
    
    income = query.filter(Transaction.section == SectionEnum.INCOME)\
                 .with_entities(func.coalesce(func.sum(Transaction.amount), 0))\
                 .scalar()
    
    expense = query.filter(Transaction.section == SectionEnum.EXPENSE)\
                  .with_entities(func.coalesce(func.sum(Transaction.amount), 0))\
                  .scalar()
    
    investment = query.filter(Transaction.section == SectionEnum.INVESTMENT)\
                     .with_entities(func.coalesce(func.sum(Transaction.amount), 0))\
                     .scalar()
    
    return {
        "balance": income - expense,
        "expense": expense,
        "income": income,
        "investment": investment,
        "net_worth": income - expense + investment
    }


@router.get("/transactions/analytics/spending-by-category")
def get_spending_by_category(
    yearmonth: str = Query(
        date.today().strftime("%Y-%m"),
        regex=r"^\d{4}-\d{2}$"
    ),
    section: SectionEnum = Query(SectionEnum.EXPENSE),
    db: Session = Depends(get_db)
):
    start_date = f"{yearmonth}-01"
    _, lastdate = calendar.monthrange(int(yearmonth[:4]), int(yearmonth[5:]))
    end_date = f"{yearmonth}-{lastdate}"
    
    results = db.query(
        Category.value,
        Category.emoji,
        func.sum(Transaction.amount).label('total_amount'),
        func.count(Transaction.id).label('transaction_count')
    ).join(Transaction, Transaction.category_id == Category.id)\
     .filter(and_(
         Transaction.date >= start_date,
         Transaction.date <= end_date,
         Transaction.section == section
     ))\
     .group_by(Category.id, Category.value, Category.emoji)\
     .order_by(desc('total_amount'))\
     .all()
    
    return [
        {
            "category": result.value,
            "emoji": result.emoji,
            "total_amount": result.total_amount,
            "transaction_count": result.transaction_count
        } for result in results
    ]


@router.get("/transactions/analytics/trends")
def get_spending_trends(
    months: int = Query(6, ge=1, le=24, description="Number of months to analyze"),
    db: Session = Depends(get_db)
):
    # Use a simpler approach for the date filtering
    current_date = func.current_date()
    months_ago = func.date_sub(current_date, text(f'INTERVAL {months} MONTH'))
    
    results = db.query(
        extract('year', Transaction.date).label('year'),
        extract('month', Transaction.date).label('month'),
        Transaction.section,
        func.sum(Transaction.amount).label('total_amount')
    ).filter(Transaction.date >= months_ago)\
     .group_by('year', 'month', Transaction.section)\
     .order_by('year', 'month')\
     .all()
    
    # Format results by month
    trends = {}
    for result in results:
        month_key = f"{int(result.year)}-{int(result.month):02d}"
        if month_key not in trends:
            trends[month_key] = {"income": 0, "expense": 0, "investment": 0}
        
        section_key = result.section.lower()
        if section_key in trends[month_key]:
            trends[month_key][section_key] = result.total_amount
    
    return {"trends": trends}
