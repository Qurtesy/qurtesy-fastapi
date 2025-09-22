from datetime import datetime, date
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, validator


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
    def validate_frequency(cls, name):
        allowed_frequencies = ["daily", "weekly", "monthly", "yearly"]
        if name not in allowed_frequencies:
            raise ValueError(f"Frequency must be one of: {', '.join(allowed_frequencies)}")
        return name

    @validator("start_date")
    def parse_start_date(cls, name):
        try:
            return datetime.strptime(name, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Start date format must be DD/MM/YYYY")

    @validator("end_date")
    def parse_end_date(cls, name):
        if name is None:
            return name
        try:
            return datetime.strptime(name, "%d/%m/%Y").date()
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
    def validate_frequency(cls, name):
        if name is None:
            return name
        allowed_frequencies = ["daily", "weekly", "monthly", "yearly"]
        if name not in allowed_frequencies:
            raise ValueError(f"Frequency must be one of: {', '.join(allowed_frequencies)}")
        return name

    @validator("end_date")
    def parse_end_date(cls, name):
        if name is None:
            return name
        try:
            return datetime.strptime(name, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("End date format must be DD/MM/YYYY")


class SplitParticipantCreate(BaseModel):
    profile_id: int = Field(..., gt=0, description="Profile ID of the participant")


class SplitTransactionCreate(BaseModel):
    name: str = Field(..., description="Name/description of the split transaction")
    total_amount: float = Field(..., gt=0, description="Total amount to be split")
    date: str = Field(..., description="Transaction date in DD/MM/YYYY format")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID")
    created_by_account_id: int = Field(..., gt=0, description="Account ID of who created/paid the transaction")
    participants: List[SplitParticipantCreate] = Field(..., description="List of participants (including creator)")
    note: Optional[str] = Field(None, description="Optional note")

    @validator("date")
    def parse_date(cls, name):
        try:
            return datetime.strptime(name, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")

    @validator("participants")
    def validate_participants(cls, name):
        if len(name) < 2:
            raise ValueError("Split transaction must have at least 2 participants")
        return name


class SplitTransactionUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name/description of the split transaction")
    total_amount: Optional[float] = Field(None, gt=0, description="Total amount to be split")
    date: Optional[str] = Field(None, description="Transaction date in DD/MM/YYYY format")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID")
    note: Optional[str] = Field(None, description="Optional note")

    @validator("date")
    def parse_date(cls, name):
        if name is None:
            return name
        try:
            return datetime.strptime(name, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")


class SplitParticipantUpdate(BaseModel):
    is_paid: bool = Field(..., description="Whether the participant has paid their share")


class LendTransactionCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Amount being lent")
    date: str = Field(..., description="Lend date in DD/MM/YYYY format")
    borrower_profile_id: int = Field(..., gt=0, description="Profile ID of the borrower")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID")
    account_id: Optional[int] = Field(None, gt=0, description="Account ID used for lending")
    note: Optional[str] = Field(None, description="Optional note about the lend")

    @validator("date")
    def parse_date(cls, name):
        try:
            return datetime.strptime(name, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")


class LendTransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0, description="Amount being lent")
    date: Optional[str] = Field(None, description="Lend date in DD/MM/YYYY format")
    borrower_profile_id: Optional[int] = Field(None, gt=0, description="Profile ID of the borrower")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID")
    account_id: Optional[int] = Field(None, gt=0, description="Account ID used for lending")
    note: Optional[str] = Field(None, description="Optional note about the lend")
    is_repaid: Optional[bool] = Field(None, description="Whether the lend has been repaid")
    repaid_date: Optional[str] = Field(None, description="Repayment date in DD/MM/YYYY format")

    @validator("date")
    def parse_date(cls, name):
        if name is None:
            return name
        try:
            return datetime.strptime(name, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")

    @validator("repaid_date")
    def parse_repaid_date(cls, name):
        if name is None:
            return name
        try:
            return datetime.strptime(name, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Repaid date format must be DD/MM/YYYY")


class LendRepaymentUpdate(BaseModel):
    is_repaid: bool = Field(..., description="Whether the lend has been repaid")
    repaid_date: Optional[str] = Field(None, description="Repayment date in DD/MM/YYYY format")

    @validator("repaid_date")
    def parse_repaid_date(cls, name):
        if name is None:
            return name
        try:
            return datetime.strptime(name, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Repaid date format must be DD/MM/YYYY")
