from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import LendTransaction, Account, Category, Profile
from schemas import LendTransactionCreate, LendTransactionUpdate, LendRepaymentUpdate
from utils.datetime import format_date

router = APIRouter()


@router.get("/lends/", response_model=List[Dict])
async def get_lend_transactions(
    status: str = None,  # 'pending', 'repaid', or None for all
    db: Session = Depends(get_db)
):
    """Get all lend transactions"""
    query = (
        db.query(LendTransaction)
        .options(
            joinedload(LendTransaction.lender_profile_rel),
            joinedload(LendTransaction.borrower_profile_rel),
            joinedload(LendTransaction.category_rel),
            joinedload(LendTransaction.account_rel),
            joinedload(LendTransaction.related_split_transaction_rel)
        )
        .order_by(LendTransaction.date.desc(), LendTransaction.id.desc())
    )
    
    # Filter by status if provided
    if status == 'pending':
        query = query.filter(LendTransaction.is_repaid == False)
    elif status == 'repaid':
        query = query.filter(LendTransaction.is_repaid == True)
    
    lends = query.all()
    
    result = []
    for lend in lends:
        result.append({
            "id": lend.id,
            "amount": lend.amount,
            "date": format_date(lend.date),
            "lender_profile": {
                "id": lend.lender_profile_rel.id,
                "name": lend.lender_profile_rel.name,
                "is_self": lend.lender_profile_rel.is_self
            },
            "borrower_profile": {
                "id": lend.borrower_profile_rel.id,
                "name": lend.borrower_profile_rel.name,
                "is_self": lend.borrower_profile_rel.is_self
            },
            "category": {
                "id": lend.category_rel.id,
                "value": lend.category_rel.value,
                "emoji": lend.category_rel.emoji
            } if lend.category_rel else None,
            "account": {
                "id": lend.account_rel.id,
                "value": lend.account_rel.value
            } if lend.account_rel else None,
            "note": lend.note,
            "is_repaid": lend.is_repaid,
            "repaid_date": format_date(lend.repaid_date) if lend.repaid_date else None,
            "related_split_transaction_id": lend.related_split_transaction_id,
            "related_split_participant_id": lend.related_split_participant_id,
            "created_from_split": lend.related_split_transaction_id is not None
        })
    
    return result


@router.post("/lends/", response_model=Dict)
async def create_lend_transaction(
    lend_data: LendTransactionCreate = Body(...),
    db: Session = Depends(get_db)
):
    """Create a new lend transaction"""
    try:
        # Get the lender profile (should be the 'self' profile)
        lender_profile = db.query(Profile).filter(Profile.is_self == True).first()
        if not lender_profile:
            raise HTTPException(status_code=400, detail="No self profile found. Please create your profile first.")
        
        # Validate borrower profile exists
        borrower_profile = db.query(Profile).filter(Profile.id == lend_data.borrower_profile_id).first()
        if not borrower_profile:
            raise HTTPException(status_code=400, detail="Borrower profile not found")
        
        # Prevent lending to self
        if borrower_profile.is_self:
            raise HTTPException(status_code=400, detail="Cannot create a lend record to yourself")
        
        # Validate account if provided
        if lend_data.account_id:
            account = db.query(Account).filter(Account.id == lend_data.account_id).first()
            if not account:
                raise HTTPException(status_code=400, detail="Account not found")
        
        # Validate category if provided
        if lend_data.category_id:
            category = db.query(Category).filter(Category.id == lend_data.category_id).first()
            if not category:
                raise HTTPException(status_code=400, detail="Category not found")
        
        # Create the lend transaction
        lend_transaction = LendTransaction(
            amount=lend_data.amount,
            date=lend_data.date,
            lender_profile_id=lender_profile.id,
            borrower_profile_id=lend_data.borrower_profile_id,
            category_id=lend_data.category_id,
            account_id=lend_data.account_id,
            note=lend_data.note,
            is_repaid=False
        )
        
        db.add(lend_transaction)
        db.commit()
        db.refresh(lend_transaction)
        
        return {
            "message": "Lend transaction created successfully",
            "lend_transaction_id": lend_transaction.id,
            "amount": lend_transaction.amount,
            "borrower": borrower_profile.name
        }
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid data provided")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create lend transaction: {str(e)}")


@router.get("/lends/{lend_id}", response_model=Dict)
async def get_lend_transaction(
    lend_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific lend transaction"""
    lend = (
        db.query(LendTransaction)
        .options(
            joinedload(LendTransaction.lender_profile_rel),
            joinedload(LendTransaction.borrower_profile_rel),
            joinedload(LendTransaction.category_rel),
            joinedload(LendTransaction.account_rel),
            joinedload(LendTransaction.related_split_transaction_rel)
        )
        .filter(LendTransaction.id == lend_id)
        .first()
    )
    
    if not lend:
        raise HTTPException(status_code=404, detail="Lend transaction not found")
    
    return {
        "id": lend.id,
        "amount": lend.amount,
        "date": format_date(lend.date),
        "lender_profile": {
            "id": lend.lender_profile_rel.id,
            "name": lend.lender_profile_rel.name,
            "is_self": lend.lender_profile_rel.is_self
        },
        "borrower_profile": {
            "id": lend.borrower_profile_rel.id,
            "name": lend.borrower_profile_rel.name,
            "is_self": lend.borrower_profile_rel.is_self
        },
        "category": {
            "id": lend.category_rel.id,
            "value": lend.category_rel.value,
            "emoji": lend.category_rel.emoji
        } if lend.category_rel else None,
        "account": {
            "id": lend.account_rel.id,
            "value": lend.account_rel.value
        } if lend.account_rel else None,
        "note": lend.note,
        "is_repaid": lend.is_repaid,
        "repaid_date": format_date(lend.repaid_date) if lend.repaid_date else None,
        "related_split_transaction_id": lend.related_split_transaction_id,
        "created_from_split": lend.related_split_transaction_id is not None
    }


@router.put("/lends/{lend_id}", response_model=Dict)
async def update_lend_transaction(
    lend_id: int,
    lend_data: LendTransactionUpdate,
    db: Session = Depends(get_db)
):
    """Update a lend transaction"""
    lend = db.query(LendTransaction).filter(LendTransaction.id == lend_id).first()
    
    if not lend:
        raise HTTPException(status_code=404, detail="Lend transaction not found")
    
    try:
        # Update fields
        if lend_data.amount is not None:
            lend.amount = lend_data.amount
        if lend_data.date is not None:
            lend.date = lend_data.date
        if lend_data.borrower_profile_id is not None:
            # Validate borrower profile exists
            borrower_profile = db.query(Profile).filter(Profile.id == lend_data.borrower_profile_id).first()
            if not borrower_profile:
                raise HTTPException(status_code=400, detail="Borrower profile not found")
            if borrower_profile.is_self:
                raise HTTPException(status_code=400, detail="Cannot lend to yourself")
            lend.borrower_profile_id = lend_data.borrower_profile_id
        if lend_data.category_id is not None:
            lend.category_id = lend_data.category_id
        if lend_data.account_id is not None:
            lend.account_id = lend_data.account_id
        if lend_data.note is not None:
            lend.note = lend_data.note
        if lend_data.is_repaid is not None:
            lend.is_repaid = lend_data.is_repaid
            if lend_data.is_repaid and lend_data.repaid_date:
                lend.repaid_date = lend_data.repaid_date
            elif not lend_data.is_repaid:
                lend.repaid_date = None
        
        db.commit()
        db.refresh(lend)
        
        return {"message": "Lend transaction updated successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update lend transaction: {str(e)}")


@router.patch("/lends/{lend_id}/repayment", response_model=Dict)
async def update_lend_repayment_status(
    lend_id: int,
    repayment_data: LendRepaymentUpdate,
    db: Session = Depends(get_db)
):
    """Mark a lend transaction as repaid or pending"""
    lend = db.query(LendTransaction).filter(LendTransaction.id == lend_id).first()
    
    if not lend:
        raise HTTPException(status_code=404, detail="Lend transaction not found")
    
    lend.is_repaid = repayment_data.is_repaid
    if repayment_data.is_repaid:
        lend.repaid_date = repayment_data.repaid_date if repayment_data.repaid_date else lend.date
    else:
        lend.repaid_date = None
    
    db.commit()
    
    return {"message": "Lend repayment status updated successfully"}


@router.delete("/lends/{lend_id}", response_model=Dict)
async def delete_lend_transaction(
    lend_id: int,
    db: Session = Depends(get_db)
):
    """Delete a lend transaction"""
    lend = db.query(LendTransaction).filter(LendTransaction.id == lend_id).first()
    
    if not lend:
        raise HTTPException(status_code=404, detail="Lend transaction not found")
    
    # Don't allow deletion of lends created from splits
    if lend.related_split_transaction_id:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete lend transaction created from a split. Modify the split instead."
        )
    
    try:
        db.delete(lend)
        db.commit()
        return {"message": "Lend transaction deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete lend transaction: {str(e)}")


@router.get("/lends/summary/", response_model=Dict)
async def get_lend_summary(
    db: Session = Depends(get_db)
):
    """Get summary of lend transactions"""
    # Get self profile
    self_profile = db.query(Profile).filter(Profile.is_self == True).first()
    if not self_profile:
        return {
            "total_lent": 0,
            "total_pending": 0,
            "total_repaid": 0,
            "pending_count": 0,
            "repaid_count": 0
        }
    
    # Get all lends where user is the lender
    lends = db.query(LendTransaction).filter(
        LendTransaction.lender_profile_id == self_profile.id
    ).all()
    
    total_lent = sum(lend.amount for lend in lends)
    total_pending = sum(lend.amount for lend in lends if not lend.is_repaid)
    total_repaid = sum(lend.amount for lend in lends if lend.is_repaid)
    pending_count = len([lend for lend in lends if not lend.is_repaid])
    repaid_count = len([lend for lend in lends if lend.is_repaid])
    
    return {
        "total_lent": total_lent,
        "total_pending": total_pending,
        "total_repaid": total_repaid,
        "pending_count": pending_count,
        "repaid_count": repaid_count
    }
