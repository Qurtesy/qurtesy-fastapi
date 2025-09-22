from datetime import datetime
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Literal, Optional

class TransactionBase(BaseModel):
    section: Literal['EXPENSE', 'INCOME', 'TRANSFER', 'INVESTMENT'] = Field(
        ..., description="Must be one of: EXPENSE, INCOME, TRANSFER, INVESTMENT"
    )
    date: str = Field(..., description="Transaction date in DD/MM/YYYY format")
    amount: float = Field(..., gt=0, description="Transaction amount (must be greater than 0)")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID (must be a positive integer)")
    account_id: Optional[int] = Field(None, gt=0, description="Account ID (must be a positive integer)")
    note: Optional[str] = Field(None, description="Optional note about the transaction")

    @validator("date")
    def parse_date(cls, name):
        try:
            return datetime.strptime(name, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(TransactionBase):
    id: int

class TransactionOut(TransactionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
