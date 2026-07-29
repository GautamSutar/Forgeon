<div align="center">

# 🤖 AI Job Application Agent

**An AI agent that reads job application forms, fills them from your profile and resume, and only submits after you say so.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](backend/pyproject.toml)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)](backend)
[![LangGraph](https://img.shields.io/badge/LangGraph-agent-1C3C3C)](backend/app/agents)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](frontend)
[![Chrome MV3](https://img.shields.io/badge/Chrome-MV3_Extension-4285F4?logo=googlechrome&logoColor=white)](browser_extension)

</div>

---

## What this is

Job hunting means filling the same application form fifty times with slightly
different wording. This project automates that: a Chrome extension detects a
job application form on the page, a LangGraph agent maps every field to your
profile, drafts grounded answers for anything that needs a written response,
and shows you a full preview — **nothing is filled or submitted until you
click Approve.**

Three pieces work together:

| Piece | What it does |
|---|---|
| 🧠 **Backend** — FastAPI + LangGraph | Auth, profile/resume storage, RAG over your resume (pgvector), the agent pipeline itself |
| 🖥️ **Dashboard** — React + TypeScript | Manage your profile, resumes, application history, and saved answers |
| 🧩 **Browser extension** — Chrome MV3 | Detects forms on real ATS pages (Workday, Greenhouse, Lever, LinkedIn, ...), runs the agent, fills the page after you approve |

## Why it won't hallucinate or auto-submit for you

These two guarantees are enforced in code, not just prompted for:

- **Grounded answers only.** `answer_generation_service` refuses
  (`"I don't have information to answer this accurately."`) whenever there's
  no retrieved context to ground an answer in — it never invents experience
  you don't have.
- **Human approval is a hard gate.** The LangGraph pipeline pauses at a real
  `interrupt()` before submission. `submit_node` and the Playwright tool both
  raise if called without `approved=True`, and that flag is only set after
  you explicitly approve in the extension popup or dashboard.

## How a run flows

```
   extract_fields → extract_jd → retrieve_context → semantic_matching
          │                                                 │
          └──────────────────────┬──────────────────────────┘
                                  ▼
                          generate_answers ─────┐
                                  │              │ (validation errors,
                                  ▼              │  retries remaining)
                              validate ──────────┘
                                  │
                       (no errors / retries exhausted)
                                  ▼
                     🛑 human_approval  (LangGraph interrupt)
                          │                    │
                     approved              rejected
                          ▼                    │
                        submit                 │
                          ▼                    ▼
                     save_history ────────► save_history → END
```

1. **extract_fields** — parses the form's HTML into a structured field list (name, label, type, selector).
2. **extract_jd** — pulls structured signal out of the job description.
3. **retrieve_context** — pgvector similarity search over your embedded resume.
4. **semantic_matching** — maps each field label to a canonical profile key (embedding similarity, with a keyword-pattern fallback when no embeddings model is configured).
5. **generate_answers** — static fields resolve straight from your profile; anything dynamic goes through a grounded, concurrency-capped LLM call.
6. **validate** — checks the drafted answers; loops back to regenerate (bounded retries) if something's off.
7. **human_approval** — pauses. You review every answer and its source (`profile` / `generated` / `refused`) before anything happens.
8. **submit** — only reachable after approval; drives the page via Playwright (server-side) or writes into the live DOM (extension) and highlights Submit — it never clicks it.
9. **save_history** — persists the outcome either way.

## Tech stack

- **Backend**: FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL + pgvector, LangGraph, LiteLLM (provider-agnostic — OpenRouter free tier by default), Playwright, pdfplumber
- **Dashboard**: React 18, TypeScript, React Router, Tailwind CSS, Vite, Vitest
- **Extension**: Chrome MV3, TypeScript, React (popup/options), Vite (dual build: ES module background worker + IIFE content script)
- **Infra**: Docker Compose, Redis, Neon (managed Postgres) / Cloudinary (resume storage) in the cloud deployment

## Quick start

The fastest path — everything in Docker:

```bash
cp backend/.env.example backend/.env   # fill in an LLM API key
docker compose up --build
```

- Backend → `http://localhost:8000`
- Dashboard → `http://localhost:3000`

For native (hot-reload) setup of each piece individually, see **[RUNNING.md](RUNNING.md)** — it also covers the browser extension, which has to be loaded unpacked into Chrome.

## Repository layout

```
backend/             FastAPI app, LangGraph agent, Alembic migrations, tests
frontend/             React dashboard (profile, resumes, applications, saved answers)
browser_extension/    Chrome MV3 extension (detection, extraction, popup, fill)
docker-compose.yml     backend + frontend + redis
RUNNING.md             step-by-step run instructions for every setup
```

## Non-negotiables

- JWT auth required on every endpoint except register/login.
- No fabricated answers — grounded generation only, explicit refusal otherwise.
- No auto-submission — ever, under any code path.
- Async end-to-end on the backend (SQLAlchemy 2.0 async ORM + asyncpg).

## License

[MIT](LICENSE)
