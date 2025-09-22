from models.base import BaseModel
from sqlalchemy import Column, Boolean, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Profile(BaseModel):
    __tablename__ = "profiles"

    name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    default_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    is_self = Column(Boolean, nullable=False, default=False)

    default_account_rel = relationship("Account")