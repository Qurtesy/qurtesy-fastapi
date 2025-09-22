from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class AccountBase(BaseModel):
    name: str = Field(..., description="Account name (must be a meaningful text)")
    balance: Optional[float] = Field(None, description="Account balance (must be number)")

class AccountCreate(AccountBase):
    pass

class AccountUpdate(AccountBase):
    id: int

class AccountOut(AccountBase):
    id: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
