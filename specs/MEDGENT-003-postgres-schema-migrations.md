# MEDGENT-003: Postgres schema & migrations setup

**Status:** To Do
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-01: Foundation & Infrastructure](epics/EPIC-01-foundation.md)
**Branch:** `MEDGENT-003-postgres-schema-migrations`
**Depends on:** MEDGENT-002

## User story

As a developer, I want Alembic migrations and a baseline schema wired into
the backend, so that every later spec that needs a new table or column has
a consistent, versioned way to make that change.

## Context

Postgres is now running as a Compose service (MEDGENT-002). This spec wires
SQLAlchemy 2.0 + Alembic into the backend and creates the baseline tables
that the domain specs (MEDGENT-006, MEDGENT-007) will extend: a minimal
`hcps` and `interactions` table shape, plus a minimal `reps` table holding
a single seeded demo rep (no auth system — this build is single-rep, see
`steering/04-architecture-tech-stack.md`). This spec owns migration
*infrastructure* and the baseline tables; it does not build the CRUD API —
that's MEDGENT-006/007.

## Acceptance criteria

- [ ] `backend/app/core/db.py` provides a SQLAlchemy 2.0 engine/session
      factory reading `DATABASE_URL` from env.
- [ ] `backend/alembic/` initialized and wired to the app's `DATABASE_URL`
      and SQLAlchemy metadata (`alembic revision --autogenerate` works).
- [ ] Baseline migration creates: `reps` (id, name, email, created_at),
      `hcps` (id, name, specialty, institution, contact_info, created_at),
      `interactions` (id, hcp_id FK, rep_id FK, occurred_at, channel,
      notes, created_at, updated_at) — columns are a floor, not a ceiling;
      MEDGENT-006/007 may extend via new migrations.
- [ ] `docker compose up` runs the migration automatically on backend
      startup (or via a documented one-off command) before the app accepts
      traffic.
- [ ] A basic model/session smoke test confirms the app can connect and
      query an empty table.
- [ ] `README.md` documents how to generate and apply a new migration.

## Technical details

- SQLAlchemy 2.0 declarative models under `backend/app/models/`.
- Use UUID primary keys (`uuid4`) for all tables — avoids exposing
  sequential IDs and plays well with future multi-rep/multi-tenant needs.
- `interactions.channel` as a Postgres enum or a plain string with
  app-level validation — pick a plain string with a Pydantic `Literal` at
  the API layer for now; don't over-engineer a full enum migration story
  this early.
- Keep this migration minimal — just enough columns for MEDGENT-006/007 to
  build real CRUD against. Don't anticipate every future field (e.g.
  compliance flags, follow-up scheduling) here; those land as their own
  migrations in the specs that need them (MEDGENT-013, MEDGENT-014).
