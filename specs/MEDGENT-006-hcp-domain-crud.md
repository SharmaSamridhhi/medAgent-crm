# MEDGENT-006: HCP domain model & CRUD API

**Status:** To Do
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-02: Backend Core Services](epics/EPIC-02-backend-core.md)
**Branch:** `MEDGENT-006-hcp-domain-crud`
**Depends on:** MEDGENT-005

## User story

As a pharma sales rep, I want the system to know about the healthcare
professionals I call on (name, specialty, institution, contact info), so
that I can look them up and log interactions against a real HCP record
instead of free text.

## Context

MEDGENT-003 created a baseline `hcps` table. This spec builds the full
CRUD API and any schema extensions needed for a usable HCP directory. It's
a prerequisite for both the Interaction API (MEDGENT-007, via FK) and the
agent's "Retrieve HCP History" tool (MEDGENT-012).

## Acceptance criteria

- [ ] `GET /api/v1/hcps` — list HCPs, with basic search/filter by name and
      specialty, paginated.
- [ ] `GET /api/v1/hcps/{id}` — fetch a single HCP with full profile.
- [ ] `POST /api/v1/hcps` — create an HCP (name required; specialty,
      institution, contact info optional).
- [ ] `PATCH /api/v1/hcps/{id}` — partial update.
- [ ] `DELETE /api/v1/hcps/{id}` — soft delete (retain history for
      interactions logged against them) rather than a hard delete.
- [ ] Pydantic schemas for request/response are distinct from the
      SQLAlchemy model (no ORM object returned directly).
- [ ] Validation errors return 422 with a clear field-level message;
      not-found returns 404.
- [ ] Alembic migration adds any columns beyond the MEDGENT-003 baseline
      that this spec's acceptance criteria require (e.g. `is_active` for
      soft delete).
- [ ] Tests: happy-path create/read/update/delete, plus not-found and
      validation-failure cases, per `steering/02-code-quality.md`.

## Technical details

- Router at `backend/app/api/v1/hcps.py`, registered into the router
  aggregator from MEDGENT-005.
- Soft delete via an `is_active` boolean column + a query filter, not a
  status enum — keep it simple until there's a reason for more states.
- Search/filter: simple `ILIKE` on name for now; don't build full-text
  search infrastructure unless a later spec asks for it.
- No authentication/authorization on these routes — this is a single-rep
  demo project (see [[04-architecture-tech-stack]]); a real auth spec is
  out of scope for the current build.
- The list/search endpoint (`GET /api/v1/hcps?search=`) is also what
  powers the "Search or select HCP..." picker inline on the Log Interaction
  Screen (MEDGENT-019) — keep it fast and simple (name `ILIKE`) since it's
  on that screen's critical path.
