# Day 5 - Agentic RAG API (FastAPI + Postgres + pgvector)

This day replaces the old content with a clean, modular FastAPI project that demonstrates:
- JWT access/refresh auth
- Session-based chat
- Short-term memory (last N messages)
- Long-term memory (per user)
- RAG over ingested documents stored in pgvector

## Structure
- `app/` FastAPI app
- `alembic/` migrations
- `scripts/ingest.py` document ingestion
- `docker-compose.yml` Postgres + pgvector + app

## Quick Start (local)
1. Create a venv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create `.env` from `.env.example` and adjust values.
   Make sure `GEMINI_API_KEY` is set.

3. Run Postgres + pgvector:

```bash
docker compose up -d db
```

4. Run migrations:

```bash
alembic upgrade head
```

5. Ingest PDFs (from `./documents` by default). This fills the `PGVECTOR_COLLECTION` collection:

```bash
python -m scripts.ingest
```

6. Start the API:

```bash
uvicorn app.main:app --reload
```

## Docker Compose (full stack)

```bash
docker compose up --build
```

Then run migrations in the app container:

```bash
docker compose exec app alembic upgrade head
```

And ingest docs:

```bash
docker compose exec app python -m scripts.ingest
```

Docker compose mounts `../day_4/documents` into the container at `/docs` and overrides `DOCS_PATH` accordingly.

## API
- `POST /auth/register` → `{email, name, password}`
- `POST /auth/login` → `{email, password}`
- `POST /auth/refresh` → `{refresh_token}`
- `POST /session` → `{title?}`
- `GET /sessions`
- `PUT /session/{id}` → `{content}`

All session endpoints require `Authorization: Bearer <access_token>`.

## RAG Flow
When you call `PUT /session/{id}`:
1. Load prompt template
2. Inject short-term history and long-term memory
3. Retrieve context from pgvector
4. Invoke the agent (simple grounded answer in this baseline)
5. Save assistant response and any extracted long-term memory

To upgrade the agent, adjust `day_5/app/services/agent.py` and the prompt template in `day_5/app/core/system_prompt.txt`.
