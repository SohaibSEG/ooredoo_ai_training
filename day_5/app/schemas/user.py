from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    name: str

    class Config:
        from_attributes = True
