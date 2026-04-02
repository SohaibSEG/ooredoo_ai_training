"""init

Revision ID: 0001
Revises: 
Create Date: 2026-04-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"], unique=False)

    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_messages_session_id"), "messages", ["session_id"], unique=False)
    op.create_index(op.f("ix_messages_user_id"), "messages", ["user_id"], unique=False)

    op.create_table(
        "long_term_memories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_long_term_memories_user_id"), "long_term_memories", ["user_id"], unique=False)

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vector", Vector(384), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
    )
    op.create_index(op.f("ix_embeddings_document_id"), "embeddings", ["document_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_embeddings_document_id"), table_name="embeddings")
    op.drop_table("embeddings")
    op.drop_table("documents")
    op.drop_index(op.f("ix_long_term_memories_user_id"), table_name="long_term_memories")
    op.drop_table("long_term_memories")
    op.drop_index(op.f("ix_messages_user_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_session_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index(op.f("ix_sessions_user_id"), table_name="sessions")
    op.drop_table("sessions")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
