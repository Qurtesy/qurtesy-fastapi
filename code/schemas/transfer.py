from datetime import datetime
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Literal, Optional

class TransferBase(BaseModel):
    section: Literal['EXPENSE', 'INCOME', 'TRANSFER', 'INVESTMENT'] = Field(
        ..., description="Must be one of: EXPENSE, INCOME, TRANSFER, INVESTMENT"
    )
    date: str = Field(..., description="Transfer date in DD/MM/YYYY format")
    amount: float = Field(..., gt=0, description="Transfer amount (must be greater than 0)")
    from_account_id: int = Field(..., gt=0, description="From Account ID (must be a positive integer)")
    to_account_id: int = Field(..., gt=0, description="To Account ID (must be a positive integer)")
    note: Optional[str] = Field(None, description="Optional note about the transfer")

    @validator("date")
    def parse_date(cls, name):
        try:
            return datetime.strptime(name, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")

class TransferCreate(TransferBase):
    pass

class TransferUpdate(TransferBase):
    id: int

class TransferOut(TransferBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
