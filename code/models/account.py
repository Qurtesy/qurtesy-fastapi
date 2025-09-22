from models.base import BaseModel
from sqlalchemy import Column, String, Float
from sqlalchemy.orm import relationship

class Account(BaseModel):
    __tablename__ = "accounts"
    name = Column(String, unique=True, index=True, nullable=False)
    balance = Column(Float, nullable=True)

    transactions_rel = relationship("Transaction", back_populates="account_rel")
