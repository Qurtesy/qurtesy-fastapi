from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

class ProfileBase(BaseModel):
    name: str = Field(..., description="Profile name (must be a meaningful text)")
    email: str = Field(..., description="Profile email (must be a valid email id)")
    phone: str = Field(..., description="Profile phone (must be a valid phone)")
    avatar_url: str = Field(..., description="Profile avatar url (must be a valid image url)")
    default_account_id: int = Field(..., description="Profile default account id (must be a valid account id)")
    is_self: bool = Field(..., description="is self field (must be true if the Profile is the current user profile)")

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    id: int

class ProfileOut(ProfileBase):
    id: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
