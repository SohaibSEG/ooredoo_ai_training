from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.session import Session as ChatSession
from app.models.message import Message


class SessionService:
    def create_session(self, db: Session, user_id, title: str | None) -> ChatSession:
        session = ChatSession(user_id=user_id, title=title)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def list_sessions(self, db: Session, user_id) -> list[ChatSession]:
        return (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
            .all()
        )

    def add_message(self, db: Session, session_id, user_id, role: str, content: str) -> Message:
        message = Message(session_id=session_id, user_id=user_id, role=role, content=content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_history(self, db: Session, session_id) -> list[Message]:
        rows = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(settings.history_window)
            .all()
        )
        return list(reversed(rows))
