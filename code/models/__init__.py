import enum
from datetime import datetime
from sqlalchemy import Column, Boolean, Integer, String, Date, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class SectionEnum(str, enum.Enum):
    EXPENSE = 'EXPENSE'
    INCOME = 'INCOME'
    TRANSFER = 'TRANSFER'
    INVESTMENT = 'INVESTMENT'
    LEND = 'LEND'
    SPLIT = 'SPLIT'


class CategoryGroup(Base):
    __tablename__ = "category_groups"
    __table_args__ = {"schema": "finance"}

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=False, unique=True)
    emoji = Column(String)
    section = Column(Enum(SectionEnum, name="section_enum", schema="finance"), nullable=False)
    created_date = Column(Date, nullable=False)
    updated_date = Column(Date, nullable=False)

    categories_rel = relationship("Category", back_populates="category_groups_rel")
    transactions_rel = relationship("Transaction", back_populates="category_groups_rel")


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": "finance"}

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=False, unique=True)
    emoji = Column(String)
    section = Column(Enum(SectionEnum, name="section_enum", schema="finance"), nullable=False)
    category_group = Column(Integer, ForeignKey("finance.category_groups.id"), nullable=False)
    created_date = Column(Date, nullable=False)
    updated_date = Column(Date, nullable=False)

    category_groups_rel = relationship("CategoryGroup", back_populates="categories_rel")
    transactions_rel = relationship("Transaction", back_populates="categories_rel")


class AccountGroup(Base):
    __tablename__ = "account_groups"
    __table_args__ = {"schema": "finance"}

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=False, unique=True)
    created_date = Column(Date, nullable=False)
    updated_date = Column(Date, nullable=False)

    accounts_rel = relationship("Account", back_populates="account_groups_rel")
    transactions_rel = relationship("Transaction", back_populates="account_groups_rel")


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = {"schema": "finance"}

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=False, unique=True)
    account_group = Column(Integer, ForeignKey("finance.account_groups.id"), nullable=False)
    created_date = Column(Date, nullable=False)
    updated_date = Column(Date, nullable=False)

    account_groups_rel = relationship("AccountGroup", back_populates="accounts_rel")
    transactions_rel = relationship("Transaction", back_populates="accounts_rel")


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"schema": "finance"}

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    credit = Column(Boolean, nullable=False)
    amount = Column(Float, nullable=False)
    section = Column(Enum(SectionEnum, name="section_enum", schema="finance"), nullable=False)
    category_group = Column(Integer, ForeignKey("finance.category_groups.id"), nullable=False)
    category = Column(Integer, ForeignKey("finance.categories.id"), nullable=True)
    account_group = Column(Integer, ForeignKey("finance.account_groups.id"), nullable=False)
    account = Column(Integer, ForeignKey("finance.accounts.id"), nullable=True)
    note = Column(String, nullable=True)
    created_date = Column(Date, nullable=False)
    updated_date = Column(Date, nullable=False)

    category_groups_rel = relationship("CategoryGroup", back_populates="transactions_rel")
    account_groups_rel = relationship("AccountGroup", back_populates="transactions_rel")
    categories_rel = relationship("Category", back_populates="transactions_rel")
    accounts_rel = relationship("Account", back_populates="transactions_rel")

    def create(self):
        self.created_date=datetime.now()
        self.updated_date=datetime.now()
        return self
