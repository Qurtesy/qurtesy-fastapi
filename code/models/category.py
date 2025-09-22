import enum
from models.base import BaseModel
from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship

class SectionEnum(str, enum.Enum):
    EXPENSE = 'EXPENSE'
    INCOME = 'INCOME'
    TRANSFER = 'TRANSFER'
    INVESTMENT = 'INVESTMENT'

class Category(BaseModel):
    __tablename__ = "categories"
    name = Column(String, nullable=False, unique=True)
    emoji = Column(String, nullable=True)
    section = Column(Enum(SectionEnum, name="section_enum"), nullable=False)

    transactions_rel = relationship("Transaction", back_populates="category_rel")