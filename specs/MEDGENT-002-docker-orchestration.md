# MEDGENT-002: Docker & Docker Compose orchestration

**Status:** To Do
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-01: Foundation & Infrastructure](epics/EPIC-01-foundation.md)
**Branch:** `MEDGENT-002-docker-orchestration`
**Depends on:** MEDGENT-001

## User story

As a developer, I want to bring up the entire stack (frontend, backend,
database) with one command, so that local development and future deployment
are consistent and reproducible.

## Context

MEDGENT-001 gives us runnable-but-separate frontend and backend apps. This
spec containerizes both and adds Postgres as a service, wired together with
Docker Compose, per `steering/04-architecture-tech-stack.md`.

## Acceptance criteria

- [ ] `backend/Dockerfile` builds a working image that serves the FastAPI
      app (`/health` responds) via Uvicorn.
- [ ] `frontend/Dockerfile` builds a working dev-mode image serving the Vite
      dev server (prod-style static build can be a follow-up, not required
      here).
- [ ] Root `docker-compose.yml` defines `postgres`, `backend`, `frontend`
      services, wired with correct depends_on/health checks, using env vars
      from `.env` (not hardcoded credentials).
- [ ] `docker compose up` brings up all three services such that: Postgres
      is reachable from `backend`, `backend` `/health` responds, and
      `frontend` dev server is reachable in a browser.
- [ ] `.env.example` updated with `DATABASE_URL` and any Postgres-specific
      vars (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).
- [ ] `README.md` updated with the `docker compose up` quick-start,
      superseding (not deleting) the MEDGENT-001 non-Docker instructions.

## Technical details

- Postgres image: official `postgres:16` with a named volume for data
  persistence across restarts.
- Backend service depends on Postgres being healthy (Compose `healthcheck`
  + `condition: service_healthy`) before starting, since MEDGENT-003 will
  add startup migrations that need a live DB.
- Keep Dockerfiles dev-friendly (bind-mounted source for hot reload) for
  now; a separate prod-optimized multi-stage build can be a later spec if
  needed — don't over-build this before it's asked for.
- No CI wiring here — that's MEDGENT-004.
