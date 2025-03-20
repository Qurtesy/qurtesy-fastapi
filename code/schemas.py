from pydantic import BaseModel, Field
from datetime import date as datetype

class CategoryCreate(BaseModel):
    value: str = Field(..., description="Category name (must be a meaningful text)")
    emoji: str = Field(None, description="Category emoji (must be an emoji's UTF-8 charset value)")


class CategoryUpdate(BaseModel):
    value: str = Field(..., description="Category name (must be a meaningful text)")
    emoji: str = Field(None, description="Category emoji (must be an emoji's UTF-8 charset value)")


class AccountCreate(BaseModel):
    value: str = Field(..., description="Account name (must be a meaningful text)")


class AccountUpdate(BaseModel):
    value: str = Field(..., description="Account name (must be a meaningful text)")


class TransactionCreate(BaseModel):
    date: datetype = Field(..., description="Transaction date in YYYY-MM-DD format")
    amount: float = Field(..., gt=0, description="Transaction amount (must be greater than 0)")
    category: int = Field(..., gt=0, description="Category ID (must be a positive integer)")
    account: int = Field(..., gt=0, description="Account ID (must be a positive integer)")


class TransactionUpdate(BaseModel):
    date: datetype = Field(None, description="Transaction date in YYYY-MM-DD format")
    amount: float = Field(None, gt=0, description="Transaction amount (must be greater than 0)")
    category: int = Field(None, gt=0, description="Category ID (must be a positive integer)")
    account: int = Field(None, gt=0, description="Account ID (must be a positive integer)")
