from datetime import datetime
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import List, Dict, Optional
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import SectionEnum, Category
from schemas import CategoryCreate, CategoryUpdate

router = APIRouter()


@router.get("/categories/")
async def read_categories(
    section: SectionEnum = Query(
        None, description="Filter transactions by section (EXPENSE or INCOME)"
    ),
    db: Session = Depends(get_db)
):
    categories: list[Category] = (
        db.query(Category)
        .filter(or_(Category.section == section, not bool(section)))
        .order_by(Category.id)
        .all()
    )
    return [
        {
            "id": c.id,
            "value": c.value,
            "emoji": c.emoji,
            "section": c.section,
            "created_date": c.created_date,
            "updated_date": c.updated_date
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
        db.query(Category).filter(and_(Category.value == category.value, Category.emoji == category.emoji, Category.section == section.value)).first()
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

@router.post("/categories/bulk")
def bulk_create_categories(
    categories: List[Dict] = Body(...),
    db: Session = Depends(get_db)
):
    """Bulk create categories from CSV data or array with uniqueness validation"""
    created_categories = []
    all_categories = []
    errors = []

    # Step 1: Check for duplicates within the batch itself
    seen_emoji_value_section = set()
    
    valid_categories = []
    
    for idx, category_data in enumerate(categories):
        try:
            value = category_data.get('value')
            emoji = category_data.get('emoji')
            section = category_data.get('section')
            
            # Validate required fields
            if not value or not emoji or not section:
                errors.append({
                    "row": idx + 1, 
                    "error": "Missing required fields: value, emoji, or section"
                })
                continue
            
            # Check for duplicates within the current batch
            emoji_value_section_key = f"{emoji}_{value}_{section}"
            if emoji_value_section_key in seen_emoji_value_section:
                errors.append({
                    "row": idx + 1, 
                    "error": f"Duplicate emoji-value-section combination '{emoji}' + '{value}' + '{section}' found in batch"
                })
                continue
            
            # Add to seen sets
            seen_emoji_value_section.add(emoji_value_section_key)
            
            # Add to valid categories for database check
            valid_categories.append({
                'index': idx,
                'data': category_data
            })
            
        except Exception as e:
            errors.append({"row": idx + 1, "error": f"Data validation error: {str(e)}"})

    # Step 2: Check against existing categories in database (bulk query)
    if valid_categories:
        # Extract values and emoji-section combinations for bulk query
        emoji_value_sections_to_check = [
            (cat['data']['emoji'], cat['data']['value'], cat['data']['section']) 
            for cat in valid_categories
        ]
        
        # Single query to check existing emoji-vaue-section combinations
        existing_emoji_value_sections = set()
        if emoji_value_sections_to_check:
            emoji_value_section_conditions = [
                and_(Category.emoji == emoji, Category.value == value, Category.section == section)
                for emoji, value, section in emoji_value_sections_to_check
            ]

            existing_emoji_value_section_results = db.query(Category.emoji, Category.value, Category.section, Category.id)\
                .filter(or_(*emoji_value_section_conditions))\
                .all()
            for emoji, value, section, id in existing_emoji_value_section_results:
                all_categories.append({
                    'id': id,
                    'emoji': emoji,
                    'value': value,
                    'section': section.value
                })
            
            existing_emoji_value_sections = set(
                f"{row[0]}_{row[1]}_{row[2].value}" for row in existing_emoji_value_section_results
            )
        
        # Step 3: Validate each category against database
        final_valid_categories = []

        for cat in valid_categories:
            idx = cat['index']
            category_data = cat['data']
            emoji = category_data['emoji']
            value = category_data['value']
            section = category_data['section']
            
            # Check if emoji-section combination already exists in database
            emoji_value_section_key = f"{emoji}_{value}_{section}"
            if emoji_value_section_key in existing_emoji_value_sections:
                errors.append({
                    "row": idx + 1,
                    "error": f"Emoji-value-section combination '{emoji}' + '{value}' + '{section}' already exists in database"
                })
                continue
            
            final_valid_categories.append(category_data)

    # Step 4: Create valid categories
    for category_data in final_valid_categories:
        try:
            new_category = Category(
                value=category_data.get('value'),
                emoji=category_data.get('emoji'),
                section=category_data.get('section'),
                created_date=datetime.now().date(),
                updated_date=datetime.now().date()
            )
            
            db.add(new_category)
            created_categories.append(new_category)
            
        except Exception as e:
            errors.append({
                "row": "unknown", 
                "error": f"Database insertion error: {str(e)}"
            })
    
    # Step 5: Commit transaction
    try:
        if created_categories:
            db.commit()
            # Refresh all created categories
            for category in created_categories:
                db.refresh(category)
        all_categories.extend(created_categories)
        return {
            "message": f"Successfully created {len(created_categories)} categories",
            "created_count": len(created_categories),
            "total_submitted": len(categories),
            "errors_count": len(errors),
            "errors": errors,
            "categories": all_categories
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Bulk insert failed during commit: {str(e)}"
        )
