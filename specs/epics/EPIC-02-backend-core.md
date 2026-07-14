# EPIC-02: Backend Core Services

**Status:** Done

## Goal

Deliver the FastAPI application skeleton and the core domain APIs (HCP,
Interaction) that both the AI agent and the frontend will build on. No auth
system — this is a single-rep demo build (see
[[04-architecture-tech-stack]]); identity is a single hardcoded rep
resolved in MEDGENT-005.

## Specs in this epic

| Spec | Title | Status |
|------|-------|--------|
| [MEDGENT-005](../MEDGENT-005-fastapi-skeleton.md) | FastAPI app skeleton | Done |
| [MEDGENT-006](../MEDGENT-006-hcp-domain-crud.md) | HCP domain model & CRUD API | Done |
| [MEDGENT-007](../MEDGENT-007-interaction-domain-crud.md) | Interaction domain model & CRUD API | To Do |

## Notes

Depends on EPIC-01. Can proceed in parallel with EPIC-04 (Frontend Core).
EPIC-03 (AI Agent) depends on the domain models delivered here.
