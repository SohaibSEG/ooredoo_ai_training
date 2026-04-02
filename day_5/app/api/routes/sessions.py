from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.session import Session as ChatSession
from app.schemas import SessionCreate, SessionOut, MessageCreate, MessageOut
from app.services.sessions import SessionService
from app.services.agent import RAGService

router = APIRouter(tags=["sessions"])

sessions_service = SessionService()
rag_service = RAGService()


@router.post("/session", response_model=SessionOut)
def create_session(
    payload: SessionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    session = sessions_service.create_session(db, current_user.id, payload.title)
    return session


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return sessions_service.list_sessions(db, current_user.id)


@router.put("/session/{session_id}", response_model=MessageOut)
def send_message(
    session_id: UUID,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    sessions_service.add_message(db, session_id, current_user.id, "user", payload.content)

    answer = rag_service.answer(db, current_user.id, session_id, payload.content)
    sessions_service.add_message(db, session_id, current_user.id, "assistant", answer)

    return MessageOut(role="assistant", content=answer)
