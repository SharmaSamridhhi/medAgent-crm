# MEDGENT-028: Render deployment config

**Status:** Done
**Priority:** Dev tooling — deployment support the user asked for directly;
built ahead of `MEDGENT-023`/`MEDGENT-025` at their explicit request. Not
itself a required assignment deliverable, but makes the deliverable
(a running, shareable app) easier to demo.
**Epic:** [EPIC-06: Quality, Docs & Deployment](epics/EPIC-06-quality-deployment.md)
**Branch:** bundled into `EPIC-05-log-interaction-screen` (same rationale
as MEDGENT-027 — nothing is merged to `main` yet, so this rides along
rather than branching fresh)
**Depends on:** MEDGENT-002 (Docker), MEDGENT-005 (backend `/health`)

## User story

As the person deploying this, I want a one-file Render Blueprint plus
clear docs, so that standing up a live, shareable instance doesn't
require hand-configuring three separate Render resources by trial and
error.

## Context

`docker-compose.yml`'s three services don't map 1:1 onto Render: the
`postgres` service becomes Render's own managed Postgres, `backend` maps
directly onto a Docker-runtime web service (its Dockerfile is already
production-viable), but `frontend`'s Dockerfile just runs the Vite *dev*
server — for Render, the frontend needs to be a static site built via
`npm run build` instead.

## Acceptance criteria

- [x] `render.yaml` at the repo root provisions: a managed Postgres
      database, the backend as a Docker web service (reusing
      `backend/Dockerfile` as-is), and the frontend as a static site
      (`npm run build` → `dist/`) with an SPA rewrite rule so client-side
      routes (`/`, `/hcps`) survive a direct load/refresh.
- [x] Backend `DATABASE_URL` is wired from the Blueprint's own Postgres
      resource (`fromDatabase`); `GROQ_API_KEY` is left as a manual
      secret (`sync: false`), never written into the file.
- [x] `README.md` documents the two-pass step Render's URL-assignment
      forces: `CORS_ORIGINS` (backend) and `VITE_API_BASE_URL` (frontend,
      build-time) can't be set correctly until each service's Render URL
      exists, i.e. after a first deploy.
- [x] Backend normalizes a bare `postgresql://` URL (what Render's
      managed Postgres hands out) to `postgresql+psycopg://` (the only
      driver installed) — provider-agnostic, not Render-specific, and a
      no-op for the existing local `.env` value which already has the
      driver suffix.

## Technical details

**Implementation notes (as built):**
- `backend/app/core/config.py`: added a Pydantic `field_validator` on
  `database_url` doing the scheme rewrite described above, rather than
  touching `db.py` — keeps the normalization at the config boundary.
- Did not modify `frontend/Dockerfile` (still a plain dev-server image,
  used only by `docker compose up` for local dev) — Render's static site
  build bypasses it entirely via `buildCommand`/`staticPublishPath`, so
  there was nothing to fix there for this spec's purpose.
- `render.yaml`'s `plan: free` fields are placeholders — Render's actual
  available plan names/tiers can change; the file notes to adjust them if
  the connecting account doesn't have a `free` tier.
- Verified: `ruff check`, `mypy --strict`, and the full backend pytest
  suite (43 tests) still pass after the `config.py` change.
