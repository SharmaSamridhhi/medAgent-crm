# MEDGENT-005: FastAPI app skeleton

**Status:** Done
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-02: Backend Core Services](epics/EPIC-02-backend-core.md)
**Branch:** `MEDGENT-005-fastapi-skeleton`
**Depends on:** MEDGENT-003

## User story

As a developer, I want a properly structured FastAPI application (config,
routing, CORS, logging) instead of a single-file placeholder, so that
domain routers (HCP, Interaction, Agent) all plug into the same consistent
app.

## Context

MEDGENT-001 created a minimal FastAPI placeholder; MEDGENT-003 added the DB
layer. This spec turns that into a real application skeleton: settings
management, a router registry, CORS for the frontend origin, and structured
logging — the shared foundation MEDGENT-006/007/009 all build on. This
build has no auth system (single-rep demo, see
`steering/04-architecture-tech-stack.md`), so this spec also establishes
the trivial `get_current_rep` dependency the domain routers and agent use.

## Acceptance criteria

- [x] `backend/app/core/config.py` provides a Pydantic `Settings` class
      reading all env vars (DB URL, Groq key/model names, CORS origins,
      etc.) — no `os.environ` reads scattered elsewhere in the codebase.
- [x] `backend/app/main.py` assembles the app from an `api/` router
      registry (`api/v1/router.py` aggregating sub-routers), rather than
      defining routes inline.
- [x] CORS configured to allow the frontend's dev origin (from settings).
- [x] Structured logging configured (JSON or key=value, not bare `print`),
      with request ID or similar correlation available for later
      observability work (MEDGENT-024).
- [x] `/health` endpoint now also confirms DB connectivity (not just that
      the process is up).
- [x] `/api/v1/` prefix established as the base for all future domain
      routes per `steering/04-architecture-tech-stack.md`.
- [x] A basic test confirms the app starts and `/health` returns 200 with a
      real DB connection (using the CI Postgres service / local Compose).
- [x] A `get_current_rep` FastAPI dependency resolves to a single hardcoded
      demo rep (seeded via the MEDGENT-003 baseline `reps` row, id read
      from a `DEFAULT_REP_ID` env var or simply the first row) — no
      header/token check, no login flow. This is the one and only identity
      mechanism for the whole build.

## Technical details

- Use FastAPI's `lifespan` context manager for startup/shutdown (DB engine
  disposal, etc.) instead of deprecated `@app.on_event`.
- Settings loaded once via `lru_cache`-wrapped factory, injected via
  FastAPI `Depends` where needed.
- This spec does not add any domain (HCP/Interaction) routes — it only
  establishes the router aggregation pattern those specs will plug into.
- No auth, ever, in this build — `get_current_rep` is a one-line lookup
  against the seeded demo rep, not a security boundary. Don't build
  anything resembling login/session/token validation; it's explicitly out
  of scope given the 36-hour, single-rep nature of this build.
