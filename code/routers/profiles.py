from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Profile, Account
from schemas import ProfileCreate, ProfileUpdate

router = APIRouter()


@router.get("/profiles/", response_model=List[Dict])
async def get_profiles(
    db: Session = Depends(get_db)
):
    """Get all profiles"""
    profiles = (
        db.query(Profile)
        .options(joinedload(Profile.default_account_rel))
        .order_by(Profile.is_self.desc(), Profile.name)
        .all()
    )
    
    result = []
    for profile in profiles:
        result.append({
            "id": profile.id,
            "name": profile.name,
            "email": profile.email,
            "phone": profile.phone,
            "avatar_url": profile.avatar_url,
            "default_account": {
                "id": profile.default_account_rel.id,
                "value": profile.default_account_rel.value
            } if profile.default_account_rel else None,
            "is_self": profile.is_self
        })
    
    return result


@router.post("/profiles/", response_model=Dict)
async def create_profile(
    profile_data: ProfileCreate = Body(...),
    db: Session = Depends(get_db)
):
    """Create a new profile"""
    try:
        # Check if name already exists
        existing_profile = db.query(Profile).filter(Profile.name == profile_data.name).first()
        if existing_profile:
            raise HTTPException(status_code=400, detail="Profile name already exists")
        
        # Validate default_account_id if provided
        if profile_data.default_account_id:
            account = db.query(Account).filter(Account.id == profile_data.default_account_id).first()
            if not account:
                raise HTTPException(status_code=400, detail="Invalid default account ID")
        
        profile = Profile(
            name=profile_data.name,
            email=profile_data.email,
            phone=profile_data.phone,
            avatar_url=profile_data.avatar_url,
            default_account_id=profile_data.default_account_id,
            is_self=profile_data.is_self
        )
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        return {
            "message": "Profile created successfully",
            "profile_id": profile.id
        }
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Profile name must be unique")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create profile: {str(e)}")


@router.get("/profiles/{profile_id}", response_model=Dict)
async def get_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific profile"""
    profile = (
        db.query(Profile)
        .options(joinedload(Profile.default_account_rel))
        .filter(Profile.id == profile_id)
        .first()
    )
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "id": profile.id,
        "name": profile.name,
        "email": profile.email,
        "phone": profile.phone,
        "avatar_url": profile.avatar_url,
        "default_account": {
            "id": profile.default_account_rel.id,
            "value": profile.default_account_rel.value
        } if profile.default_account_rel else None,
        "is_self": profile.is_self
    }


@router.put("/profiles/{profile_id}", response_model=Dict)
async def update_profile(
    profile_id: int,
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update a profile"""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    try:
        # Check if new name conflicts with existing profiles
        if profile_data.name and profile_data.name != profile.name:
            existing_profile = db.query(Profile).filter(
                Profile.name == profile_data.name,
                Profile.id != profile_id
            ).first()
            if existing_profile:
                raise HTTPException(status_code=400, detail="Profile name already exists")
        
        # Validate default_account_id if provided
        if profile_data.default_account_id:
            account = db.query(Account).filter(Account.id == profile_data.default_account_id).first()
            if not account:
                raise HTTPException(status_code=400, detail="Invalid default account ID")
        
        # Update fields
        if profile_data.name is not None:
            profile.name = profile_data.name
        if profile_data.email is not None:
            profile.email = profile_data.email
        if profile_data.phone is not None:
            profile.phone = profile_data.phone
        if profile_data.avatar_url is not None:
            profile.avatar_url = profile_data.avatar_url
        if profile_data.default_account_id is not None:
            profile.default_account_id = profile_data.default_account_id
        
        db.commit()
        db.refresh(profile)
        
        return {"message": "Profile updated successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")


@router.delete("/profiles/{profile_id}", response_model=Dict)
async def delete_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """Delete a profile"""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Don't allow deleting self profile
    if profile.is_self:
        raise HTTPException(status_code=400, detail="Cannot delete your own profile")
    
    try:
        db.delete(profile)
        db.commit()
        return {"message": "Profile deleted successfully"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete profile as it is linked to existing split transactions"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete profile: {str(e)}")
