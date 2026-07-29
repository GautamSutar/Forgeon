# Running this project

Three pieces: **backend** (FastAPI + LangGraph), **frontend** (React dashboard),
**browser_extension** (Chrome MV3). The backend must be running first — both
the frontend and extension talk to it over HTTP.

## Docker Compose — backend + frontend together (recommended)

```bash
cp backend/.env.example backend/.env
# edit backend/.env: set OPENROUTER_API_KEY (or another provider's key),
# and DATABASE_URL if you're not using a local Postgres container.
docker compose up --build
```

This builds and starts:

- **backend** → `http://localhost:8000` (FastAPI + LangGraph)
- **frontend** → `http://localhost:3000` (React dashboard, built and served via nginx)
- **redis** → used by the backend

(`docker-compose.yml`'s `postgres` service is defined but unused by default —
`DATABASE_URL` in `backend/.env` currently points at a cloud Postgres/Neon
instance; switch it back to the local `postgres` service's connection string
if you want a fully local DB.)

Apply migrations once Postgres is reachable:

```bash
cd backend
alembic upgrade head
```

To build/start only one service: `docker compose up --build backend` or
`docker compose up --build frontend`.

The frontend image bakes in `VITE_API_BASE_URL` at build time (Vite inlines
`import.meta.env.*` into the static bundle). It defaults to
`http://localhost:8000/api/v1`, which is correct as-is because the browser —
not the frontend container — makes that request, and the backend's port is
published to the host. Override it at build time if you deploy somewhere
other than localhost:

```bash
docker compose build frontend --build-arg VITE_API_BASE_URL=https://api.example.com/api/v1
```

## 1. Backend

### Option A — Docker Compose (recommended)

See above — `docker compose up --build` starts backend + frontend together.
To run only the backend in Docker: `docker compose up --build backend redis`.

### Option B — Run locally without Docker

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash; use .venv\Scripts\activate.ps1 in PowerShell
pip install -r requirements.txt
playwright install chromium
cp .env.example .env               # edit DATABASE_URL/REDIS_URL to localhost, add an LLM API key
alembic upgrade head
uvicorn app.main:app --reload
```

Backend tests (SQLite-backed, no live Postgres/LLM needed):

```bash
cd backend
pytest
```

## 2. Frontend (React dashboard)

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

Other useful commands:

```bash
npm run build       # typecheck + production build
npm test            # vitest
```

## 3. Browser extension (Chrome MV3)

```bash
cd browser_extension
npm install
npm run generate-icons   # one-time: writes public/icons/*.png
npm run build             # tsc typecheck + two Vite builds -> dist/
```

Then load it into Chrome:

1. Open `chrome://extensions`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked**, select `browser_extension/dist`
4. Open the extension's **Options** page and confirm/set the backend API
   base URL (defaults to `http://localhost:8000/api/v1`)

For iterative development, `npm run dev` runs a watch build instead of a
one-shot `build`. Extension tests: `npm test`.

## Typical local dev order

```bash
# terminal 1
cd backend && uvicorn app.main:app --reload

# terminal 2
cd frontend && npm run dev

# terminal 3 (rebuild after content/background script changes)
cd browser_extension && npm run dev
```
