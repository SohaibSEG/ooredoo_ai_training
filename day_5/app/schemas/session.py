from uuid import UUID
from pydantic import BaseModel


class SessionCreate(BaseModel):
    title: str | None = None


class SessionOut(BaseModel):
    id: UUID
    title: str | None = None

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    role: str
    content: str


class SessionMessagePage(BaseModel):
    session_id: UUID
    total: int
    limit: int
    offset: int
    messages: list[MessageOut]
