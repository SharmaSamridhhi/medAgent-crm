# EPIC-01: Foundation & Infrastructure

**Status:** To Do

## Goal

Stand up the monorepo skeleton, containerization, and database schema
baseline so that every later epic has a consistent place to add code and a
consistent way to run it. CI (MEDGENT-004) is a stretch goal given the
project's time-box — see `specs/README.md`.

## Specs in this epic

| Spec | Title | Priority | Status |
|------|-------|----------|--------|
| [MEDGENT-001](../MEDGENT-001-monorepo-scaffold.md) | Monorepo scaffold & tooling | MVP | Done |
| [MEDGENT-002](../MEDGENT-002-docker-orchestration.md) | Docker & Docker Compose orchestration | MVP | Done |
| [MEDGENT-003](../MEDGENT-003-postgres-schema-migrations.md) | Postgres schema & migrations setup | MVP | To Do |
| [MEDGENT-004](../MEDGENT-004-ci-pipeline.md) | CI pipeline | **Stretch** | To Do |

## Notes

Nothing in this epic depends on any other epic — it's the starting point.
Backend Core and Frontend Core both depend on it.
