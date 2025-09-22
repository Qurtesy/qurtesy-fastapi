from datetime import datetime
from fastapi import APIRouter, Depends, Body, HTTPException
from typing import List, Dict
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models.category import Category
from schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from crud import CRUDBase

router = APIRouter()


@router.get("/categories/", response_model=List[CategoryOut])
async def read_categories(db: Session = Depends(get_db)
):
    return CRUDBase(Category).get_all(db)

@router.post("/categories/")
def create_category(
    category: CategoryCreate = Body(...),
    db: Session = Depends(get_db)
):
    # Check for uniqueness constraints
    if (
        db.query(Category).filter(and_(Category.name == category.name, Category.emoji == category.emoji)).first()
    ):
        raise HTTPException(status_code=400, detail="Name or Emoji must be unique")

    new_category = Category(
        name=category.name,
        emoji=category.emoji,
        section=category.section
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
        db.query(Category).filter(Category.name == category_data.name, Category.id != category_id).first()
        or db.query(Category).filter(Category.emoji == category_data.emoji, Category.id != category_id).first()
    ):
        raise HTTPException(status_code=400, detail="Name or Emoji must be unique")

    # Update fields
    category.name = category_data.name
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
    seen_emoji_name_section = set()
    
    valid_categories = []
    
    for idx, category_data in enumerate(categories):
        try:
            name = category_data.get('name')
            emoji = category_data.get('emoji')
            section = category_data.get('section')
            
            # Validate required fields
            if not name or not emoji or not section:
                errors.append({
                    "row": idx + 1, 
                    "error": "Missing required fields: name, emoji, or section"
                })
                continue
            
            # Check for duplicates within the current batch
            emoji_name_section_key = f"{emoji}_{name}_{section}"
            if emoji_name_section_key in seen_emoji_name_section:
                errors.append({
                    "row": idx + 1, 
                    "error": f"Duplicate emoji-name-section combination '{emoji}' + '{name}' + '{section}' found in batch"
                })
                continue
            
            # Add to seen sets
            seen_emoji_name_section.add(emoji_name_section_key)
            
            # Add to valid categories for database check
            valid_categories.append({
                'index': idx,
                'data': category_data
            })
            
        except Exception as e:
            errors.append({"row": idx + 1, "error": f"Data validation error: {str(e)}"})

    # Step 2: Check against existing categories in database (bulk query)
    if valid_categories:
        # Extract names and emoji-section combinations for bulk query
        emoji_name_sections_to_check = [
            (cat['data']['emoji'], cat['data']['name'], cat['data']['section']) 
            for cat in valid_categories
        ]
        
        # Single query to check existing emoji-vaue-section combinations
        existing_emoji_name_sections = set()
        if emoji_name_sections_to_check:
            emoji_name_section_conditions = [
                and_(Category.emoji == emoji, Category.name == name, Category.section == section)
                for emoji, name, section in emoji_name_sections_to_check
            ]

            existing_emoji_name_section_results = db.query(Category.emoji, Category.name, Category.section, Category.id)\
                .filter(or_(*emoji_name_section_conditions))\
                .all()
            for emoji, name, section, id in existing_emoji_name_section_results:
                all_categories.append({
                    'id': id,
                    'emoji': emoji,
                    'name': name,
                    'section': section.name
                })
            
            existing_emoji_name_sections = set(
                f"{row[0]}_{row[1]}_{row[2].name}" for row in existing_emoji_name_section_results
            )
        
        # Step 3: Validate each category against database
        final_valid_categories = []

        for cat in valid_categories:
            idx = cat['index']
            category_data = cat['data']
            emoji = category_data['emoji']
            name = category_data['name']
            section = category_data['section']
            
            # Check if emoji-section combination already exists in database
            emoji_name_section_key = f"{emoji}_{name}_{section}"
            if emoji_name_section_key in existing_emoji_name_sections:
                errors.append({
                    "row": idx + 1,
                    "error": f"Emoji-name-section combination '{emoji}' + '{name}' + '{section}' already exists in database"
                })
                continue
            
            final_valid_categories.append(category_data)

    # Step 4: Create valid categories
    for category_data in final_valid_categories:
        try:
            new_category = Category(
                name=category_data.get('name'),
                emoji=category_data.get('emoji'),
                section=category_data.get('section'),
                created_at=datetime.now().date(),
                updated_at=datetime.now().date()
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
