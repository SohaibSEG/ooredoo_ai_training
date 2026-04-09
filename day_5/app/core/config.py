from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "day5-agentic-rag"
    secret_key: str = Field(..., description="JWT signing key")
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    database_url: str = Field(..., description="SQLAlchemy database URL")
    history_window: int = 6

    docs_path: str = "./documents"
    embedding_model: str = "gemini-embedding-001"
    chat_model: str = "gemini-2.5-flash"
    gemini_api_key: str = Field(..., validation_alias="GEMINI_API_KEY")
    pgvector_collection: str = "day5_documents"
    chunk_size: int = 1000
    chunk_overlap: int = 150
    rag_top_k: int = 4


settings = Settings()
