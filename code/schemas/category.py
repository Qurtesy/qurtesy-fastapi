from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

class CategoryBase(BaseModel):
    section: Literal['EXPENSE', 'INCOME', 'TRANSFER', 'INVESTMENT'] = Field(
        ..., description="Must be one of: EXPENSE, INCOME, TRANSFER, INVESTMENT"
    )
    name: str = Field(..., description="Category name (must be a meaningful text)")
    emoji: str = Field(None, description="Category emoji (must be an emoji's UTF-8 charset name)")

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    id: int

class CategoryOut(CategoryBase):
    id: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
