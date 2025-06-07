from datetime import datetime, date
from typing import Optional, List
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
    category_id: Optional[int] = Field(None, gt=0, description="Category ID (must be a positive integer)")
    account_id: Optional[int] = Field(None, gt=0, description="Account ID (must be a positive integer)")
    note: Optional[str] = Field(None, description="Optional note about the transaction")

    @validator("date")
    def parse_date(cls, value):
        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")


class TransactionUpdate(BaseModel):
    date: Optional[str] = Field(None, description="Transaction date in DD/MM/YYYY format")
    amount: Optional[float] = Field(None, gt=0, description="Transaction amount (must be greater than 0)")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID (must be a positive integer)")
    account_id: Optional[int] = Field(None, gt=0, description="Account ID (must be a positive integer)")
    note: Optional[str] = Field(None, description="Optional note about the transaction")

    @validator("date")
    def parse_date(cls, value):
        if value is None:
            return value
        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")


class TransferCreate(BaseModel):
    date: str = Field(..., description="Transaction date in DD/MM/YYYY format")
    amount: float = Field(..., gt=0, description="Transaction amount (must be greater than 0)")
    from_account_id: int = Field(..., gt=0, description="From Account ID (must be a positive integer)")
    to_account_id: int = Field(..., gt=0, description="To Account ID (must be a positive integer)")
    note: Optional[str] = Field(None, description="Optional note about the transfer")

    @validator("date")
    def parse_date(cls, value):
        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")


class BudgetCreate(BaseModel):
    category_id: int = Field(..., gt=0, description="Category ID")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    year: int = Field(..., ge=2020, description="Year")
    budgeted_amount: float = Field(..., gt=0, description="Budget amount")


class BudgetUpdate(BaseModel):
    budgeted_amount: Optional[float] = Field(None, gt=0, description="Budget amount")


class RecurringTransactionCreate(BaseModel):
    name: str = Field(..., description="Name of the recurring transaction")
    amount: float = Field(..., gt=0, description="Transaction amount")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID")
    account_id: Optional[int] = Field(None, gt=0, description="Account ID")
    frequency: str = Field(..., description="Frequency: daily, weekly, monthly, yearly")
    start_date: str = Field(..., description="Start date in DD/MM/YYYY format")
    end_date: Optional[str] = Field(None, description="End date in DD/MM/YYYY format")
    note: Optional[str] = Field(None, description="Optional note")

    @validator("frequency")
    def validate_frequency(cls, value):
        allowed_frequencies = ["daily", "weekly", "monthly", "yearly"]
        if value not in allowed_frequencies:
            raise ValueError(f"Frequency must be one of: {', '.join(allowed_frequencies)}")
        return value

    @validator("start_date")
    def parse_start_date(cls, value):
        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Start date format must be DD/MM/YYYY")

    @validator("end_date")
    def parse_end_date(cls, value):
        if value is None:
            return value
        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("End date format must be DD/MM/YYYY")


class RecurringTransactionUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the recurring transaction")
    amount: Optional[float] = Field(None, gt=0, description="Transaction amount")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID")
    account_id: Optional[int] = Field(None, gt=0, description="Account ID")
    frequency: Optional[str] = Field(None, description="Frequency: daily, weekly, monthly, yearly")
    end_date: Optional[str] = Field(None, description="End date in DD/MM/YYYY format")
    is_active: Optional[bool] = Field(None, description="Whether the recurring transaction is active")
    note: Optional[str] = Field(None, description="Optional note")

    @validator("frequency")
    def validate_frequency(cls, value):
        if value is None:
            return value
        allowed_frequencies = ["daily", "weekly", "monthly", "yearly"]
        if value not in allowed_frequencies:
            raise ValueError(f"Frequency must be one of: {', '.join(allowed_frequencies)}")
        return value

    @validator("end_date")
    def parse_end_date(cls, value):
        if value is None:
            return value
        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("End date format must be DD/MM/YYYY")


class SplitParticipantCreate(BaseModel):
    account_id: int = Field(..., gt=0, description="Account ID of the participant")


class SplitTransactionCreate(BaseModel):
    name: str = Field(..., description="Name/description of the split transaction")
    total_amount: float = Field(..., gt=0, description="Total amount to be split")
    date: str = Field(..., description="Transaction date in DD/MM/YYYY format")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID")
    created_by_account_id: int = Field(..., gt=0, description="Account ID of who created/paid the transaction")
    participants: List[SplitParticipantCreate] = Field(..., description="List of participants (including creator)")
    note: Optional[str] = Field(None, description="Optional note")

    @validator("date")
    def parse_date(cls, value):
        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")

    @validator("participants")
    def validate_participants(cls, value):
        if len(value) < 2:
            raise ValueError("Split transaction must have at least 2 participants")
        return value


class SplitTransactionUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name/description of the split transaction")
    total_amount: Optional[float] = Field(None, gt=0, description="Total amount to be split")
    date: Optional[str] = Field(None, description="Transaction date in DD/MM/YYYY format")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID")
    note: Optional[str] = Field(None, description="Optional note")

    @validator("date")
    def parse_date(cls, value):
        if value is None:
            return value
        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")


class SplitParticipantUpdate(BaseModel):
    is_paid: bool = Field(..., description="Whether the participant has paid their share")
