# AI Job Application Agent — Backend (Slice 1)

FastAPI + LangGraph backend implementing: auth, profile/resume management,
resume parsing + embeddings (pgvector RAG), and a human-in-the-loop LangGraph
agent that extracts a job application form, maps fields to a canonical
profile taxonomy, generates grounded answers, validates them, pauses for
human approval, and only then fills/submits the form via Playwright.

## Run with Docker Compose

```bash
cp .env.example backend/.env   # fill in ANTHROPIC_API_KEY at minimum
docker compose up --build
```

This starts Postgres (pgvector/pgvector:pg16), Redis, and the backend on
`http://localhost:8000`.

Apply migrations (from the `backend/` directory, against the running Postgres):

```bash
cd backend
alembic upgrade head
```

## Run locally (without Docker)

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate   # Windows Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env       # edit DATABASE_URL/REDIS_URL to localhost, add API key
alembic upgrade head
uvicorn app.main:app --reload
```

## Tests

```bash
pytest
```

Tests use a SQLite (aiosqlite) database by default (see `tests/conftest.py`)
so they run without a live Postgres instance, and monkeypatch
`app.llm.client.LLMClient` to return deterministic fixtures — no real LLM
calls are made in the test suite.

## API examples

Register + login:

```bash
curl -X POST localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"a@b.com","password":"secret123","full_name":"Ada Lovelace"}'

TOKEN=$(curl -s -X POST localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"a@b.com","password":"secret123"}' | jq -r .access_token)
```

Update profile:

```bash
curl -X PUT localhost:8000/api/v1/profiles/me \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"location":"Remote","years_experience":5}'
```

Upload a resume (triggers parse + embed automatically):

```bash
curl -X POST localhost:8000/api/v1/resumes/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@resume.pdf" -F "set_default=true"
```

Run the agent against a job posting form + JD:

```bash
curl -X POST localhost:8000/api/v1/agent/run \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"html":"<form>...</form>","job_description":"We are hiring a..."}'
# -> {"run_id": "...", "status": "interrupted", "preview": {...}}
```

Approve (only after this does the agent proceed to fill+submit via Playwright):

```bash
curl -X POST localhost:8000/api/v1/agent/<run_id>/approve \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"edited_answers": {}}'
```

Or reject:

```bash
curl -X POST localhost:8000/api/v1/agent/<run_id>/reject \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{}'
```

## Non-negotiables implemented

- **No hallucination**: `answer_generation_service` uses an explicit
  anti-fabrication system prompt and refuses (`"I don't have information to
  answer this accurately."`) when no grounding context is available.
- **Never auto-submit**: `submit_node` and `PlaywrightTool.submit_form` both
  raise `ApprovalNotGrantedError` unless invoked with `approved=True`, which
  is only set after the `human_approval` LangGraph interrupt resolves to
  `"approved"`.
- **JWT auth** required on every endpoint except `/auth/register` and
  `/auth/login`.
- **Async everywhere**: SQLAlchemy 2.0 async ORM + asyncpg driver.

## Known gaps for the next phase

- Frontend, browser extension, and the 8 ATS-specific adapters are out of
  scope for this slice.
- `submit_node`'s field->selector mapping is naive (uses the raw CSS
  selector captured at extraction time); production ATS adapters will need
  site-specific fill strategies.
- Admin panel, CI/CD pipeline, and full docs site are not part of this slice.
- The LangGraph checkpointer defaults to a local SQLite file
  (`storage/checkpoints.db`); swapping to a Postgres-backed checkpointer for
  multi-instance deployments is a follow-up.
