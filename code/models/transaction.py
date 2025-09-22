import enum
from models.base import BaseModel
from sqlalchemy import Column, Enum, DateTime, Boolean, Float, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

class SectionEnum(str, enum.Enum):
    EXPENSE = 'EXPENSE'
    INCOME = 'INCOME'
    TRANSFER = 'TRANSFER'
    INVESTMENT = 'INVESTMENT'

class Transaction(BaseModel):
    __tablename__ = "transactions"
    date = Column(DateTime, nullable=False)
    credit = Column(Boolean, nullable=False, default=False)
    amount = Column(Float, nullable=False)
    section = Column(Enum(SectionEnum, name="section_enum"), nullable=False)
    category_id = Column("category", Integer, ForeignKey("categories.id"), nullable=True)
    account_id = Column("account", Integer, ForeignKey("accounts.id"), nullable=True)
    note = Column(Text, nullable=True)

    category_rel = relationship("Category", back_populates="transactions_rel")
    account_rel = relationship("Account", back_populates="transactions_rel")
