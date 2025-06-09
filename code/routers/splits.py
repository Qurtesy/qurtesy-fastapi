from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import SplitTransaction, SplitParticipant, Account, Category, Profile, LendTransaction
from schemas import SplitTransactionCreate, SplitTransactionUpdate, SplitParticipantUpdate
from utils.datetime import format_date

router = APIRouter()


@router.get("/splits/", response_model=List[Dict])
async def get_split_transactions(
    db: Session = Depends(get_db)
):
    """Get all split transactions with participants"""
    splits = (
        db.query(SplitTransaction)
        .options(
            joinedload(SplitTransaction.category_rel),
            joinedload(SplitTransaction.created_by_account_rel),
            joinedload(SplitTransaction.participants_rel).joinedload(SplitParticipant.profile_rel)
        )
        .order_by(SplitTransaction.date.desc(), SplitTransaction.id.desc())
        .all()
    )
    
    result = []
    for split in splits:
        participants = []
        for participant in split.participants_rel:
            # Handle case where profile_rel might be None
            if participant.profile_rel:
                participants.append({
                    "id": participant.id,
                    "profile": {
                        "id": participant.profile_rel.id,
                        "name": participant.profile_rel.name,
                        "email": participant.profile_rel.email,
                        "is_self": participant.profile_rel.is_self
                    },
                    "share_amount": participant.share_amount,
                    "is_paid": participant.is_paid
                })
            else:
                # Log warning for missing profile and skip this participant
                print(f"Warning: Split participant {participant.id} has no associated profile")
                continue
        
        result.append({
            "id": split.id,
            "name": split.name,
            "total_amount": split.total_amount,
            "date": format_date(split.date),
            "category": {
                "id": split.category_rel.id,
                "value": split.category_rel.value,
                "emoji": split.category_rel.emoji
            } if split.category_rel else None,
            "created_by_account": {
                "id": split.created_by_account_rel.id,
                "value": split.created_by_account_rel.value
            },
            "participants": participants,
            "note": split.note,
            "total_paid": sum(p.share_amount for p in split.participants_rel if p.is_paid),
            "total_pending": sum(p.share_amount for p in split.participants_rel if not p.is_paid),
            "is_settled": all(p.is_paid for p in split.participants_rel)
        })
    
    return result


@router.post("/splits/", response_model=Dict)
async def create_split_transaction(
    split_data: SplitTransactionCreate = Body(...),
    db: Session = Depends(get_db)
):
    """Create a new split transaction"""
    try:
        # Validate that all profile IDs exist
        profile_ids = [p.profile_id for p in split_data.participants]
        existing_profiles = db.query(Profile).filter(Profile.id.in_(profile_ids)).all()
        if len(existing_profiles) != len(profile_ids):
            raise HTTPException(status_code=400, detail="One or more profile IDs are invalid")
        
        # Create the split transaction
        split_transaction = SplitTransaction(
            name=split_data.name,
            total_amount=split_data.total_amount,
            date=split_data.date,
            category_id=split_data.category_id,
            created_by_account_id=split_data.created_by_account_id,
            note=split_data.note
        )
        db.add(split_transaction)
        db.flush()  # Get the ID
        
        # Calculate even split amount
        share_amount = split_data.total_amount / len(split_data.participants)
        
        # Get the account that created the split to find the lender profile
        created_by_account = db.query(Account).filter(Account.id == split_data.created_by_account_id).first()
        if not created_by_account:
            raise HTTPException(status_code=400, detail="Created by account not found")
        
        # Find the self profile (lender) - the person who created the split
        self_profile = db.query(Profile).filter(Profile.is_self == True).first()
        if not self_profile:
            raise HTTPException(status_code=400, detail="Self profile not found")
        
        # Create participants and corresponding lend records
        created_participants = []
        for participant_data in split_data.participants:
            participant = SplitParticipant(
                split_transaction_id=split_transaction.id,
                profile_id=participant_data.profile_id,
                share_amount=share_amount,
                is_paid=False  # All participants start as unpaid initially
            )
            db.add(participant)
            db.flush()  # Get participant ID
            created_participants.append(participant)
            
            # Create lend record for participants who are not the self profile
            profile = db.query(Profile).filter(Profile.id == participant_data.profile_id).first()
            if profile and not profile.is_self:
                lend_record = LendTransaction(
                    amount=share_amount,
                    date=split_data.date,
                    lender_profile_id=self_profile.id,
                    borrower_profile_id=participant_data.profile_id,
                    category_id=split_data.category_id,
                    account_id=split_data.created_by_account_id,
                    note=f"From split: {split_data.name}",
                    is_repaid=False,
                    related_split_transaction_id=split_transaction.id,
                    related_split_participant_id=participant.id
                )
                db.add(lend_record)
        
        db.commit()
        db.refresh(split_transaction)
        
        return {
            "message": "Split transaction created successfully",
            "split_transaction_id": split_transaction.id,
            "share_amount": share_amount,
            "lend_records_created": len([p for p in created_participants if not db.query(Profile).filter(Profile.id == p.profile_id).first().is_self])
        }
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid account or category ID")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create split transaction: {str(e)}")


@router.get("/splits/{split_id}", response_model=Dict)
async def get_split_transaction(
    split_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific split transaction"""
    split = (
        db.query(SplitTransaction)
        .options(
            joinedload(SplitTransaction.category_rel),
            joinedload(SplitTransaction.created_by_account_rel),
            joinedload(SplitTransaction.participants_rel).joinedload(SplitParticipant.profile_rel)
        )
        .filter(SplitTransaction.id == split_id)
        .first()
    )
    
    if not split:
        raise HTTPException(status_code=404, detail="Split transaction not found")
    
    participants = []
    for participant in split.participants_rel:
        # Handle case where profile_rel might be None
        if participant.profile_rel:
            participants.append({
                "id": participant.id,
                "profile": {
                    "id": participant.profile_rel.id,
                    "name": participant.profile_rel.name,
                    "email": participant.profile_rel.email,
                    "is_self": participant.profile_rel.is_self
                },
                "share_amount": participant.share_amount,
                "is_paid": participant.is_paid
            })
        else:
            # Log warning for missing profile and skip this participant
            print(f"Warning: Split participant {participant.id} has no associated profile")
            continue
    
    return {
        "id": split.id,
        "name": split.name,
        "total_amount": split.total_amount,
        "date": format_date(split.date),
        "category": {
            "id": split.category_rel.id,
            "value": split.category_rel.value,
            "emoji": split.category_rel.emoji
        } if split.category_rel else None,
        "created_by_account": {
            "id": split.created_by_account_rel.id,
            "value": split.created_by_account_rel.value
        },
        "participants": participants,
        "note": split.note
    }


@router.put("/splits/{split_id}", response_model=Dict)
async def update_split_transaction(
    split_id: int,
    split_data: SplitTransactionUpdate,
    db: Session = Depends(get_db)
):
    """Update a split transaction"""
    split = db.query(SplitTransaction).filter(SplitTransaction.id == split_id).first()
    
    if not split:
        raise HTTPException(status_code=404, detail="Split transaction not found")
    
    try:
        # Update fields
        if split_data.name is not None:
            split.name = split_data.name
        if split_data.total_amount is not None:
            # Recalculate share amounts if total amount changed
            old_total = split.total_amount
            split.total_amount = split_data.total_amount
            
            participants = db.query(SplitParticipant).filter(
                SplitParticipant.split_transaction_id == split_id
            ).all()
            
            new_share_amount = split_data.total_amount / len(participants)
            for participant in participants:
                participant.share_amount = new_share_amount
        
        if split_data.date is not None:
            split.date = split_data.date
        if split_data.category_id is not None:
            split.category_id = split_data.category_id
        if split_data.note is not None:
            split.note = split_data.note
        
        db.commit()
        db.refresh(split)
        
        return {"message": "Split transaction updated successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update split transaction: {str(e)}")


@router.patch("/splits/{split_id}/participants/{participant_id}", response_model=Dict)
async def update_participant_payment_status(
    split_id: int,
    participant_id: int,
    participant_data: SplitParticipantUpdate,
    db: Session = Depends(get_db)
):
    """Mark a participant as paid or unpaid"""
    participant = (
        db.query(SplitParticipant)
        .filter(
            SplitParticipant.id == participant_id,
            SplitParticipant.split_transaction_id == split_id
        )
        .first()
    )
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    # Update participant payment status
    participant.is_paid = participant_data.is_paid
    
    # Also update the corresponding lend record if it exists
    lend_record = db.query(LendTransaction).filter(
        LendTransaction.related_split_participant_id == participant_id
    ).first()
    
    if lend_record:
        lend_record.is_repaid = participant_data.is_paid
        if participant_data.is_paid:
            # Set repaid date to the split transaction date or today
            split_transaction = db.query(SplitTransaction).filter(SplitTransaction.id == split_id).first()
            lend_record.repaid_date = split_transaction.date if split_transaction else lend_record.date
        else:
            lend_record.repaid_date = None
    
    db.commit()
    
    return {"message": "Participant payment status updated successfully"}


@router.delete("/splits/{split_id}", response_model=Dict)
async def delete_split_transaction(
    split_id: int,
    db: Session = Depends(get_db)
):
    """Delete a split transaction"""
    split = db.query(SplitTransaction).filter(SplitTransaction.id == split_id).first()
    
    if not split:
        raise HTTPException(status_code=404, detail="Split transaction not found")
    
    try:
        # Delete related lend records first
        db.query(LendTransaction).filter(
            LendTransaction.related_split_transaction_id == split_id
        ).delete()
        
        # Delete the split transaction (participants will be deleted by cascade)
        db.delete(split)
        db.commit()
        return {"message": "Split transaction deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete split transaction: {str(e)}")
