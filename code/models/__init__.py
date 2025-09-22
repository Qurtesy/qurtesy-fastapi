import enum
from datetime import datetime
from models.base import BaseModel
from sqlalchemy import Column, Boolean, Integer, String, DateTime, Float, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import relationship

class TransactionSectionEnum(str, enum.Enum):
    EXPENSE = 'TRANSACTION'
    LEND = 'LEND'
    SPLIT = 'SPLIT'

class PersonalSectionEnum(str, enum.Enum):
    EXPENSE = 'EXPENSE'
    INCOME = 'INCOME'
    TRANSFER = 'TRANSFER'
    INVESTMENT = 'INVESTMENT'


class Budget(BaseModel):
    __tablename__ = "budgets"

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    budgeted_amount = Column(Float, nullable=False)
    spent_amount = Column(Float, nullable=False, default=0.0)

    category_rel = relationship("Category")


class RecurringTransaction(BaseModel):
    __tablename__ = "recurring_transactions"

    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    section = Column(Enum(PersonalSectionEnum, name="section_enum", schema="finance"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    frequency = Column(String, nullable=False)  # daily, weekly, monthly, yearly
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    next_execution = Column(DateTime, nullable=False)
    note = Column(Text, nullable=True)

    category_rel = relationship("Category")
    account_rel = relationship("Account")


class SplitTransaction(BaseModel):
    __tablename__ = "split_transactions"

    name = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_by_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    note = Column(Text, nullable=True)

    category_rel = relationship("Category")
    created_by_account_rel = relationship("Account", foreign_keys=[created_by_account_id])
    participants_rel = relationship("SplitParticipant", back_populates="split_transaction_rel", cascade="all, delete-orphan")


class SplitParticipant(BaseModel):
    __tablename__ = "split_participants"

    split_transaction_id = Column(Integer, ForeignKey("split_transactions.id", ondelete="CASCADE"), nullable=False)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    share_amount = Column(Float, nullable=False)
    is_paid = Column(Boolean, nullable=False, default=False)

    split_transaction_rel = relationship("SplitTransaction", back_populates="participants_rel")
    profile_rel = relationship("Profile")


class LendTransaction(BaseModel):
    __tablename__ = "lend_transactions"

    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    lender_profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)  # Who lent the money
    borrower_profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)  # Who borrowed the money
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)  # Account used for lending
    note = Column(Text, nullable=True)
    is_repaid = Column(Boolean, nullable=False, default=False)
    repaid_date = Column(DateTime, nullable=True)
    
    # Reference to split transaction if this lend was created from a split
    related_split_transaction_id = Column(Integer, ForeignKey("split_transactions.id"), nullable=True)
    related_split_participant_id = Column(Integer, ForeignKey("split_participants.id"), nullable=True)

    # Relationships
    lender_profile_rel = relationship("Profile", foreign_keys=[lender_profile_id])
    borrower_profile_rel = relationship("Profile", foreign_keys=[borrower_profile_id])
    category_rel = relationship("Category")
    account_rel = relationship("Account")
    related_split_transaction_rel = relationship("SplitTransaction", foreign_keys=[related_split_transaction_id])
    related_split_participant_rel = relationship("SplitParticipant", foreign_keys=[related_split_participant_id])
