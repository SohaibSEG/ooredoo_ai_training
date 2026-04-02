from pathlib import Path

from app.core.config import settings
from app.services.rag_pipeline import ingest_pdfs


def main() -> None:
    folder = Path(settings.docs_path).resolve()
    if not folder.exists():
        raise SystemExit(f"Docs path not found: {folder}")
    count = ingest_pdfs(folder)
    print(f"Ingested {count} chunks from {folder}")


if __name__ == "__main__":
    main()
