from __future__ import annotations

from typing import List

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.prompts import load_prompt_template
from app.models.message import Message
from app.models.memory import LongTermMemory
from app.services.rag_pipeline import build_llm, build_vector_store, format_documents


class RAGService:
    def __init__(self) -> None:
        self.vector_store = build_vector_store()
        self.llm = build_llm()

    def _load_history(self, db: Session, session_id) -> List[BaseMessage]:
        rows = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(settings.history_window)
            .all()
        )
        history: List[BaseMessage] = []
        for row in reversed(rows):
            if row.role == "assistant":
                history.append(AIMessage(content=row.content))
            else:
                history.append(HumanMessage(content=row.content))
        return history

    def _load_long_term_memory(self, db: Session, user_id) -> str:
        rows = (
            db.query(LongTermMemory)
            .filter(LongTermMemory.user_id == user_id)
            .order_by(LongTermMemory.created_at.desc())
            .limit(10)
            .all()
        )
        return "\n".join(row.content for row in rows)

    def _build_tools(self, db: Session, user_id):
        retriever = self.vector_store.as_retriever(search_kwargs={"k": settings.rag_top_k})

        @tool
        def search_documents(query: str) -> str:
            """Search the document store for grounded context relevant to the query."""
            docs = retriever.invoke(query)
            if not docs:
                return "No relevant documents found."
            return format_documents(docs)

        @tool
        def save_memory(content: str) -> str:
            """Save a durable user memory. Input should be a short fact or preference."""
            cleaned = content.strip()
            if not cleaned:
                return "Memory not saved: empty content."
            memory = LongTermMemory(user_id=user_id, content=cleaned)
            db.add(memory)
            db.commit()
            db.refresh(memory)
            return "Memory saved."

        return [search_documents, save_memory]

    def _build_agent(self, tools, long_term_memory: str):
        system_template = load_prompt_template()
        system_prompt = system_template.format(
            long_term_memory=long_term_memory,
        )
        return create_agent(model=self.llm, tools=tools, system_prompt=system_prompt)

    def _extract_final_message(self, result: dict) -> str:
        messages: List[BaseMessage] = result.get("messages", [])
        if not messages:
            return "No response."
        final_message = messages[-1]
        if isinstance(final_message.content, list):
            for part in final_message.content:
                text = part.get("text")
                if text:
                    return text
            return "Could not parse tool response."
        return str(final_message.content)

    def answer(self, db: Session, user_id, session_id, question: str) -> str:
        tools = self._build_tools(db, user_id)
        history = self._load_history(db, session_id)
        memory_text = self._load_long_term_memory(db, user_id)
        agent_executor = self._build_agent(tools, memory_text)

        result = agent_executor.invoke(
            {"messages": history + [HumanMessage(content=question)]}
        )
        return self._extract_final_message(result)
