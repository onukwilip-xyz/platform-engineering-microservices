from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    name: str
    email: str
    mobile: str


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None


class UserRead(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)