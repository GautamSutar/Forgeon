# AI Job Application Agent — Browser Extension

Chrome MV3 extension that pairs with the [`backend/`](../backend) service. It
detects job application forms, extracts their fields, and drives the
backend's LangGraph agent to draft answers grounded in your resume and
profile — but it never fills a field or clicks Submit without your explicit
approval in the popup.

## How it works

1. **Detection** (`src/content/detect.ts`) — identifies the ATS platform
   (LinkedIn, Greenhouse, Lever, Ashby, SmartRecruiters, SuccessFactors,
   Workday, Oracle, SAP) from the page's hostname, or falls back to
   `generic` for self-hosted/custom HTML forms.
2. **Extraction** (`src/content/parser.ts`) — walks the live DOM of the
   application form (or the whole page if there's no `<form>` wrapper, common
   in SPA-heavy ATS UIs) and builds a structured field list: name, label,
   type, required, options, CSS selector, XPath. Mirrors the semantics of
   the backend's `html_form_parser.py` so extraction is consistent whether
   it happens server-side or here.
3. **Analysis** — the popup sends the extracted HTML + job description to
   the backend's `POST /agent/run`, which runs the same LangGraph pipeline
   used server-side (semantic field mapping, grounded answer generation,
   validation) and **pauses at a human-approval interrupt**.
4. **Review** — the popup shows every generated answer with its source
   (`profile` / `generated` / `refused`) so you can edit anything before
   approving.
5. **Approve or reject** — approving calls `POST /agent/{run_id}/approve`,
   which the backend guards so it will only mark the application `submitted`
   given actual approval. The extension then writes the approved answers
   into the live page's form fields (`src/content/dom-fill.ts`) and
   highlights the Submit button — **it never clicks Submit itself**.
   Rejecting calls `POST /agent/{run_id}/reject` and nothing is filled.

## Project layout

```
browser_extension/
  public/manifest.json       MV3 manifest (copied as-is into dist/)
  public/icons/               generated PNG icons (npm run generate-icons)
  src/background/             service worker: auth + REST client to the backend
  src/content/                content script: ATS detection, DOM parsing, DOM filling
  src/popup/                  React popup UI (login -> scan -> preview -> result)
  src/options/                React options page (backend API base URL)
  src/lib/                    shared types, chrome.storage wrapper, messaging helpers
  tests/                      vitest unit tests (jsdom) for detection/parsing/selector logic
```

## Setup

```bash
npm install
npm run generate-icons   # writes public/icons/icon{16,32,48,128}.png
npm run build             # tsc typecheck + two vite builds -> dist/
npm test                  # vitest
```

`npm run build` runs two separate Vite builds on purpose:
`vite.config.ts` builds the background service worker (an ES module, as
declared in the manifest) and the popup/options pages, while
`vite.content.config.ts` builds the content script as a single
self-contained IIFE (`dist/content.js`) — MV3's `content_scripts` field has
no module-type option, so it cannot use `import` statements.

## Loading the unpacked extension

1. `npm run build`
2. Open `chrome://extensions`
3. Enable **Developer mode** (top right)
4. Click **Load unpacked** and select `browser_extension/dist`
5. Open the extension's **Options** page and set the backend API base URL
   (defaults to `http://localhost:8000/api/v1` — matches the backend's
   `docker compose up` default)

## Permissions rationale

- `storage` — persists the JWT/refresh token and settings locally.
- `activeTab` + `scripting` — lets the popup inject the content script
  on-demand into the current tab for **custom/self-hosted application
  forms** that aren't in the declarative `content_scripts` match list,
  without requesting a broad `<all_urls>` permission.
- `host_permissions` — scoped to the backend origin (for `fetch` from the
  background worker) plus the known ATS domains (for the declarative content
  script injection).

## Known gaps

- Declarative `content_scripts` matches cover the ATS domains in scope for
  this phase; Workday and SAP often serve forms inside `<iframe>` — the
  parser walks `all_frames: true` content scripts but doesn't yet merge
  fields across frame boundaries into one preview.
- No automated end-to-end test against a live Chrome instance (e.g.
  Puppeteer) yet — `tests/` covers the pure DOM-parsing/detection/selector
  logic under jsdom.
- The options page has no validation beyond `type="url"` on the input.
