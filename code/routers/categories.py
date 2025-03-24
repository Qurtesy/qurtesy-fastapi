from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from code.database import get_db
from code.models import SectionEnum, Category
from code.schemas import CategoryCreate, CategoryUpdate

router = APIRouter()


@router.get("/categories/", tags=["categories"])
async def read_categories(
    section: SectionEnum = Query(
        None, description="Filter transactions by section (EXPENSE or INCOME)"
    ),
    db: Session = Depends(get_db)
):
    categories = (
        db.query(Category)
        .filter(Category.section == section)
        .order_by(Category.id)
        .all()
    )
    return [
        {
            "id": c.id,
            "value": c.value,
            "emoji": c.emoji
        } for c in categories
    ]

@router.post("/categories/")
def create_category(
    section: SectionEnum = Query(
        None, description="Filter transactions by section (EXPENSE or INCOME)"
    ),
    category: CategoryCreate = Body(...),
    db: Session = Depends(get_db)
):
    # Check for uniqueness constraints
    if (
        db.query(Category).filter(Category.value == category.value).first()
        or db.query(Category).filter(Category.emoji == category.emoji).first()
    ):
        raise HTTPException(status_code=400, detail="Value or Emoji must be unique")

    new_category = Category(
        value=category.value,
        emoji=category.emoji,
        section=section
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.put("/categories/{category_id}", response_model=dict)
def update_category(category_id: int, category_data: CategoryUpdate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check for uniqueness constraints
    if (
        db.query(Category).filter(Category.value == category_data.value, Category.id != category_id).first()
        or db.query(Category).filter(Category.emoji == category_data.emoji, Category.id != category_id).first()
    ):
        raise HTTPException(status_code=400, detail="Value or Emoji must be unique")

    # Update fields
    category.value = category_data.value
    if category_data.emoji:
        category.emoji = category_data.emoji

    db.commit()
    db.refresh(category)

    return {"message": "Category updated successfully"}

@router.delete("/categories/{category_id}", response_model=dict)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    try:
        db.delete(category)
        db.commit()
        return {"message": "Category deleted successfully"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete category as it is linked to existing transactions"
        )
