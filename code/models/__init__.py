import enum
from datetime import datetime
from sqlalchemy import Column, Boolean, Integer, String, Date, Float, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class SectionEnum(str, enum.Enum):
    EXPENSE = 'EXPENSE'
    INCOME = 'INCOME'
    TRANSFER = 'TRANSFER'
    INVESTMENT = 'INVESTMENT'
    LEND = 'LEND'
    SPLIT = 'SPLIT'


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        Index('ix_categories_section', 'section'),
        Index('ix_categories_value', 'value'),
        {"schema": "finance"}
    )

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=False, unique=True)
    emoji = Column(String)
    section = Column(Enum(SectionEnum, name="section_enum", schema="finance"), nullable=False)
    created_date = Column(Date, nullable=False, default=datetime.now)
    updated_date = Column(Date, nullable=False, default=datetime.now, onupdate=datetime.now)

    transactions_rel = relationship("Transaction", back_populates="category_rel")


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        Index('ix_accounts_value', 'value'),
        {"schema": "finance"}
    )

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=False, unique=True)
    balance = Column(Float, nullable=False, default=0.0)
    created_date = Column(Date, nullable=False, default=datetime.now)
    updated_date = Column(Date, nullable=False, default=datetime.now, onupdate=datetime.now)

    transactions_rel = relationship("Transaction", back_populates="account_rel")


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        Index('ix_transactions_date', 'date'),
        Index('ix_transactions_section', 'section'),
        Index('ix_transactions_date_section', 'date', 'section'),
        {"schema": "finance"}
    )

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    credit = Column(Boolean, nullable=False, default=False)
    amount = Column(Float, nullable=False)
    section = Column(Enum(SectionEnum, name="section_enum", schema="finance"), nullable=False)
    category_id = Column("category", Integer, ForeignKey("finance.categories.id"), nullable=True)
    account_id = Column("account", Integer, ForeignKey("finance.accounts.id"), nullable=True)
    note = Column(Text, nullable=True)
    created_date = Column(Date, nullable=False, default=datetime.now)
    updated_date = Column(Date, nullable=False, default=datetime.now, onupdate=datetime.now)

    category_rel = relationship("Category", back_populates="transactions_rel")
    account_rel = relationship("Account", back_populates="transactions_rel")

    def create(self):
        self.created_date = datetime.now().date()
        self.updated_date = datetime.now().date()
        return self


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        Index('ix_budgets_category_month', 'category_id', 'month', 'year'),
        {"schema": "finance"}
    )

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("finance.categories.id"), nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    budgeted_amount = Column(Float, nullable=False)
    spent_amount = Column(Float, nullable=False, default=0.0)
    created_date = Column(Date, nullable=False, default=datetime.now)
    updated_date = Column(Date, nullable=False, default=datetime.now, onupdate=datetime.now)

    category_rel = relationship("Category")


class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"
    __table_args__ = {"schema": "finance"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    section = Column(Enum(SectionEnum, name="section_enum", schema="finance"), nullable=False)
    category_id = Column(Integer, ForeignKey("finance.categories.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("finance.accounts.id"), nullable=True)
    frequency = Column(String, nullable=False)  # daily, weekly, monthly, yearly
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    next_execution = Column(Date, nullable=False)
    note = Column(Text, nullable=True)
    created_date = Column(Date, nullable=False, default=datetime.now)
    updated_date = Column(Date, nullable=False, default=datetime.now, onupdate=datetime.now)

    category_rel = relationship("Category")
    account_rel = relationship("Account")


class SplitTransaction(Base):
    __tablename__ = "split_transactions"
    __table_args__ = (
        Index('idx_split_transactions_date', 'date'),
        Index('idx_split_transactions_created_by', 'created_by_account_id'),
        {"schema": "finance"}
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    category_id = Column(Integer, ForeignKey("finance.categories.id"), nullable=True)
    created_by_account_id = Column(Integer, ForeignKey("finance.accounts.id"), nullable=False)
    note = Column(Text, nullable=True)
    created_date = Column(Date, nullable=False, default=datetime.now)
    updated_date = Column(Date, nullable=False, default=datetime.now, onupdate=datetime.now)

    category_rel = relationship("Category")
    created_by_account_rel = relationship("Account", foreign_keys=[created_by_account_id])
    participants_rel = relationship("SplitParticipant", back_populates="split_transaction_rel", cascade="all, delete-orphan")


class SplitParticipant(Base):
    __tablename__ = "split_participants"
    __table_args__ = (
        Index('idx_split_participants_split_id', 'split_transaction_id'),
        Index('idx_split_participants_profile', 'profile_id'),
        {"schema": "finance"}
    )

    id = Column(Integer, primary_key=True, index=True)
    split_transaction_id = Column(Integer, ForeignKey("finance.split_transactions.id", ondelete="CASCADE"), nullable=False)
    profile_id = Column(Integer, ForeignKey("finance.profiles.id"), nullable=False)
    share_amount = Column(Float, nullable=False)
    is_paid = Column(Boolean, nullable=False, default=False)
    created_date = Column(Date, nullable=False, default=datetime.now)
    updated_date = Column(Date, nullable=False, default=datetime.now, onupdate=datetime.now)

    split_transaction_rel = relationship("SplitTransaction", back_populates="participants_rel")
    profile_rel = relationship("Profile")


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = (
        Index('ix_profiles_name', 'name'),
        {"schema": "finance"}
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    default_account_id = Column(Integer, ForeignKey("finance.accounts.id"), nullable=True)
    is_self = Column(Boolean, nullable=False, default=False)
    created_date = Column(Date, nullable=False, default=datetime.now)
    updated_date = Column(Date, nullable=False, default=datetime.now, onupdate=datetime.now)

    default_account_rel = relationship("Account")


class LendTransaction(Base):
    __tablename__ = "lend_transactions"
    __table_args__ = (
        Index('idx_lend_transactions_date', 'date'),
        Index('idx_lend_transactions_lender', 'lender_profile_id'),
        Index('idx_lend_transactions_borrower', 'borrower_profile_id'),
        {"schema": "finance"}
    )

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    lender_profile_id = Column(Integer, ForeignKey("finance.profiles.id"), nullable=False)  # Who lent the money
    borrower_profile_id = Column(Integer, ForeignKey("finance.profiles.id"), nullable=False)  # Who borrowed the money
    category_id = Column(Integer, ForeignKey("finance.categories.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("finance.accounts.id"), nullable=True)  # Account used for lending
    note = Column(Text, nullable=True)
    is_repaid = Column(Boolean, nullable=False, default=False)
    repaid_date = Column(Date, nullable=True)
    
    # Reference to split transaction if this lend was created from a split
    related_split_transaction_id = Column(Integer, ForeignKey("finance.split_transactions.id"), nullable=True)
    related_split_participant_id = Column(Integer, ForeignKey("finance.split_participants.id"), nullable=True)
    
    created_date = Column(Date, nullable=False, default=datetime.now)
    updated_date = Column(Date, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationships
    lender_profile_rel = relationship("Profile", foreign_keys=[lender_profile_id])
    borrower_profile_rel = relationship("Profile", foreign_keys=[borrower_profile_id])
    category_rel = relationship("Category")
    account_rel = relationship("Account")
    related_split_transaction_rel = relationship("SplitTransaction", foreign_keys=[related_split_transaction_id])
    related_split_participant_rel = relationship("SplitParticipant", foreign_keys=[related_split_participant_id])
