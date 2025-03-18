from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"schema": "finance"}

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(Integer, nullable=False)
    account = Column(Integer, nullable=False)
