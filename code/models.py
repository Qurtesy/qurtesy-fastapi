import enum
from sqlalchemy import Column, Integer, String, Date, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class SectionEnum(str, enum.Enum):
    EXPENSE = 'EXPENSE'
    INCOME = 'INCOME'
    INVESTMENT = 'INVESTMENT'
    LEND = 'LEND'
    SPLIT = 'SPLIT'


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": "finance"}

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=False, unique=True)
    emoji = Column(String)
    section = Column(Enum(SectionEnum, name="section_enum"), nullable=False)

    transactions = relationship("Transaction", back_populates="category_rel")


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = {"schema": "finance"}

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=False, unique=True)
    section = Column(Enum(SectionEnum, name="section_enum"), nullable=False)

    transactions = relationship("Transaction", back_populates="account_rel")


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"schema": "finance"}

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    section = Column(Enum(SectionEnum, name="section_enum"), nullable=False)
    category = Column(Integer, ForeignKey("finance.categories.id"), nullable=False)
    account = Column(Integer, ForeignKey("finance.accounts.id"), nullable=False)

    category_rel = relationship("Category", back_populates="transactions")
    account_rel = relationship("Account", back_populates="transactions")
