from sqlalchemy.orm import Session

from app.models.memory import LongTermMemory


class MemoryService:
    def save_memory(self, db: Session, user_id, content: str) -> LongTermMemory:
        memory = LongTermMemory(user_id=user_id, content=content)
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory

    def list_memories(self, db: Session, user_id) -> list[str]:
        rows = (
            db.query(LongTermMemory)
            .filter(LongTermMemory.user_id == user_id)
            .order_by(LongTermMemory.created_at.desc())
            .limit(10)
            .all()
        )
        return [row.content for row in rows]
