from pydantic import BaseModel, Field
from datetime import date as datetype

class TransactionCreate(BaseModel):
    date: datetype = Field(..., description="Transaction date in YYYY-MM-DD format")
    amount: float = Field(..., gt=0, description="Transaction amount (must be greater than 0)")
    category: int = Field(..., gt=0, description="Category ID (must be a positive integer)")
    account: int = Field(..., gt=0, description="Account ID (must be a positive integer)")
