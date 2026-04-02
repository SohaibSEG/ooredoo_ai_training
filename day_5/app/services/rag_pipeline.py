import os
from pathlib import Path
from typing import Iterable, List, Sequence

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.services.embeddings import build_embeddings


def build_llm() -> ChatGoogleGenerativeAI:
    api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return ChatGoogleGenerativeAI(
        model=settings.chat_model,
        google_api_key=api_key,
        temperature=0.2,
    )


def build_vector_store() -> PGVector:
    embeddings = build_embeddings()
    return PGVector(
        embeddings=embeddings,
        collection_name=settings.pgvector_collection,
        connection=settings.database_url,
    )


def load_pdf_documents(pdf_dir: Path) -> List[Document]:
    docs: List[Document] = []
    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        loader = PyPDFLoader(str(pdf_path))
        docs.extend(loader.load())
    if not docs:
        raise RuntimeError(f"No PDF files found in {pdf_dir}.")
    return docs


def chunk_documents(
    documents: Iterable[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(list(documents))


def format_documents(docs: Sequence[Document]) -> str:
    formatted = []
    for idx, doc in enumerate(docs, start=1):
        formatted.append(f"[{idx}] {doc.page_content.strip()}")
    return "\n\n".join(formatted)


def ingest_pdfs(pdf_dir: Path) -> int:
    if not pdf_dir.exists():
        raise FileNotFoundError(f"PDF directory '{pdf_dir}' does not exist.")
    if not pdf_dir.is_dir():
        raise RuntimeError(f"'{pdf_dir}' is not a directory.")

    vector_store = build_vector_store()
    vector_store.delete_collection()
    vector_store.create_collection()
    documents = load_pdf_documents(pdf_dir)
    chunks = chunk_documents(
        documents,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    vector_store.add_documents(chunks)
    return len(chunks)
