# AI Job Application Agent — Web Dashboard

React + TypeScript + Tailwind (Vite) dashboard for the
[`backend/`](../backend) service. This is the account-management surface —
profile, resumes, saved answers, application history — plus a "Run agent
manually" page for exercising the LangGraph human-in-the-loop flow without
the browser extension.

## Pages

- **Login / Register** — JWT auth against `/api/v1/auth`.
- **Applications** — history list + detail view (status editor, delete).
- **Run Agent** — paste a form's raw HTML and a job description, run the
  same backend pipeline the extension uses, review generated answers
  (grounded/refused/from-profile, all editable), then approve or reject.
  Nothing is ever submitted anywhere from this page — it only exercises
  `/api/v1/agent/run|approve|reject`.
- **Resumes** — upload PDF, set default, view parsed skills, delete.
- **Saved Answers** — CRUD for reusable answers the agent can draw on.
- **Profile** — the structured fields (salary, visa status, preferred
  roles/locations, links) used for static-field answers.

## Project layout

```
frontend/
  src/api/          typed REST client (client.ts = fetch wrapper w/ 401 refresh, endpoints.ts, types.ts)
  src/auth/          AuthContext (login/register/logout, current user)
  src/components/    shared UI primitives + DashboardLayout + ProtectedRoute
  src/lib/           useAsync data-fetching hook, status-badge mapping
  src/pages/         one file per route
  tests/             vitest + @testing-library/react
```

## Setup

```bash
npm install
npm run build   # tsc typecheck + vite build -> dist/
npm test        # vitest
npm run dev     # dev server on :5173
```

By default the app talks to `http://localhost:8000/api/v1` (the backend's
`docker compose up` default). Override with a `.env.local`:

```
VITE_API_BASE_URL=https://your-backend.example.com/api/v1
```

The backend's CORS config (`CORS_ORIGINS` in `backend/app/core/config.py`)
already allows `http://localhost:5173`.

## Known gaps

- The backend has no endpoint to list `ApplicationAnswer` rows for a given
  application, so the application detail page shows the application's own
  fields (status, platform, timestamps) but not the individual
  question/answer pairs that were generated for it — those currently only
  surface in the interrupted-run preview at generation time (Run Agent page
  or the extension popup). Adding a `GET /applications/{id}/answers`
  endpoint on the backend would close this.
- No admin panel yet (unknown fields/questions review, field-alias
  management, LLM/prompt logs) — out of scope for this phase.
- No pagination UI on the Applications list yet; the API supports
  `offset`/`limit` but the page always requests the first 50.
