import os

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings

def build_embeddings() -> GoogleGenerativeAIEmbeddings:
    api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=api_key,
    )
