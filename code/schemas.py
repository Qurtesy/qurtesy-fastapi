from datetime import datetime
from pydantic import BaseModel, Field, validator

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
    date: str = Field(..., description="Transaction date in DD/MM/YYYY format")
    amount: float = Field(..., gt=0, description="Transaction amount (must be greater than 0)")
    category: int = Field(..., description="Category ID")
    account: int = Field(..., description="Account ID")

    @validator("date")
    def parse_date(cls, value):
        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")


class TransactionUpdate(BaseModel):
    date: str = Field(None, description="Transaction date in DD/MM/YYYY format")
    amount: float = Field(None, gt=0, description="Transaction amount (must be greater than 0)")
    category: int = Field(None, gt=0, description="Category ID (must be a positive integer)")
    account: int = Field(None, gt=0, description="Account ID (must be a positive integer)")

    @validator("date")
    def parse_date(cls, value):
        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")

# Transfer schemas
class TransferCreate(BaseModel):
    date: str = Field(None, description="Transaction date in DD/MM/YYYY format")
    amount: float = Field(None, gt=0, description="Transaction amount (must be greater than 0)")
    from_account: int = Field(None, gt=0, description="Account ID (must be a positive integer)")
    to_account: int = Field(None, gt=0, description="Account ID (must be a positive integer)")

    @validator("date")
    def parse_date(cls, value):
        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")
