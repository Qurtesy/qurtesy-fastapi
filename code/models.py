from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": "finance"}

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=False)
    emoji = Column(Float, nullable=False)

    transactions = relationship("Transaction", back_populates="category")


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = {"schema": "finance"}

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=False)

    transactions = relationship("Transaction", back_populates="account")

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"schema": "finance"}

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("finance.categories.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("finance.accounts.id"), nullable=False)

    category = relationship("Category", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
