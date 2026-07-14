# medAgent-CRM — Specs Index

Source of truth for scope, sequencing, and status. See `steering/` for the
binding process rules (git workflow, code quality, development workflow,
architecture) that apply to every spec below, and `docs/med-agent-crm.pdf`
for the original assignment brief this project is built against.

Status values: `To Do` → `In Progress` → `Done`. A spec's `Done` here means
its branch is merged into `main`.

## ⏱ This is time-boxed — read this first

The source assignment is a 36-hour take-home with a required deliverable:
a GitHub repo (frontend + backend + README) and a 10-15 minute demo video
(frontend walkthrough, all 5 LangGraph tools working, code/structure
explanation, a summary of what was understood from the brief).

Every spec below is tagged `Priority: MVP` or `Priority: Stretch`:

- **MVP** — required to hit the deliverable. Build these, in order,
  before touching anything else.
- **Stretch** — only pick up if the full MVP path is done, staged, and
  reviewed, with real time left before the deadline. Currently: MEDGENT-004
  (CI pipeline), MEDGENT-024 (observability epic), MEDGENT-026 (voice note
  transcription — a mockup detail, not a required tool).

If time gets tight, cut scope by dropping to a smaller MEDGENT-023
(smoke tests only, already scoped that way) and a leaner MEDGENT-025
(README + seed data, skip the extra architecture doc polish) before ever
touching a Stretch spec.

## EPIC-01: Foundation & Infrastructure

| Spec | Title | Priority | Status | Depends on | Branch |
|------|-------|----------|--------|------------|--------|
| [MEDGENT-001](MEDGENT-001-monorepo-scaffold.md) | Monorepo scaffold & tooling | MVP | Done | — | `MEDGENT-001-monorepo-scaffold` |
| [MEDGENT-002](MEDGENT-002-docker-orchestration.md) | Docker & Docker Compose orchestration | MVP | Done | MEDGENT-001 | `MEDGENT-002-docker-orchestration` |
| [MEDGENT-003](MEDGENT-003-postgres-schema-migrations.md) | Postgres schema & migrations setup | MVP | Done | MEDGENT-002 | `MEDGENT-003-postgres-schema-migrations` |
| [MEDGENT-004](MEDGENT-004-ci-pipeline.md) | CI pipeline | **Stretch** | To Do | MEDGENT-003 | `MEDGENT-004-ci-pipeline` |

## EPIC-02: Backend Core Services

No auth system in this build (single hardcoded demo rep — see
`steering/04-architecture-tech-stack.md`).

| Spec | Title | Priority | Status | Depends on | Branch |
|------|-------|----------|--------|------------|--------|
| [MEDGENT-005](MEDGENT-005-fastapi-skeleton.md) | FastAPI app skeleton | MVP | Done | MEDGENT-003 | `MEDGENT-005-fastapi-skeleton` |
| [MEDGENT-006](MEDGENT-006-hcp-domain-crud.md) | HCP domain model & CRUD API | MVP | Done | MEDGENT-005 | `MEDGENT-006-hcp-domain-crud` |
| [MEDGENT-007](MEDGENT-007-interaction-domain-crud.md) | Interaction domain model & CRUD API | MVP | Done | MEDGENT-006 | `MEDGENT-007-interaction-domain-crud` |

## EPIC-03: LangGraph AI Agent & Tools

The five required tools (two mandatory: Log Interaction, Edit Interaction).

| Spec | Title | Priority | Status | Depends on | Branch |
|------|-------|----------|--------|------------|--------|
| [MEDGENT-009](MEDGENT-009-groq-langgraph-scaffold.md) | Groq LLM integration & agent scaffolding | MVP | Done | MEDGENT-005 | `MEDGENT-009-groq-langgraph-scaffold` |
| [MEDGENT-010](MEDGENT-010-tool-log-interaction.md) | Tool: Log Interaction *(mandatory)* | MVP | To Do | MEDGENT-007, MEDGENT-009 | `MEDGENT-010-tool-log-interaction` |
| [MEDGENT-011](MEDGENT-011-tool-edit-interaction.md) | Tool: Edit Interaction *(mandatory)* | MVP | To Do | MEDGENT-007, MEDGENT-010 | `MEDGENT-011-tool-edit-interaction` |
| [MEDGENT-012](MEDGENT-012-tool-retrieve-hcp-history.md) | Tool: Retrieve HCP History | MVP | To Do | MEDGENT-006, MEDGENT-007, MEDGENT-009 | `MEDGENT-012-tool-retrieve-hcp-history` |
| [MEDGENT-013](MEDGENT-013-tool-schedule-follow-up.md) | Tool: Schedule Follow-up | MVP | To Do | MEDGENT-007, MEDGENT-009 | `MEDGENT-013-tool-schedule-follow-up` |
| [MEDGENT-014](MEDGENT-014-tool-compliance-flag.md) | Tool: Compliance Flag | MVP | To Do | MEDGENT-009, MEDGENT-010 | `MEDGENT-014-tool-compliance-flag` |
| [MEDGENT-015](MEDGENT-015-agent-orchestration-endpoint.md) | Agent orchestration & conversational endpoint | MVP | To Do | MEDGENT-010..014 | `MEDGENT-015-agent-orchestration-endpoint` |

## EPIC-04: Frontend Core

No separate navigation shell or HCP list page — the app is one route (the
Log Interaction Screen), with the HCP picker inline on that screen.

| Spec | Title | Priority | Status | Depends on | Branch |
|------|-------|----------|--------|------------|--------|
| [MEDGENT-016](MEDGENT-016-react-redux-scaffold.md) | React + Redux app scaffold | MVP | To Do | MEDGENT-001 | `MEDGENT-016-react-redux-scaffold` |
| [MEDGENT-017](MEDGENT-017-api-client-redux-slices.md) | API client & Redux slices for HCP/Interaction | MVP | To Do | MEDGENT-006, MEDGENT-007, MEDGENT-016 | `MEDGENT-017-api-client-redux-slices` |

## EPIC-05: Log Interaction Screen

The core deliverable. Field list and two-panel layout are taken directly
from the reference mockup in `docs/med-agent-crm.pdf` — form panel and AI
Assistant chat panel side by side, sharing one draft, not toggled between.

| Spec | Title | Priority | Status | Depends on | Branch |
|------|-------|----------|--------|------------|--------|
| [MEDGENT-019](MEDGENT-019-structured-form-ui.md) | Structured form panel for Log Interaction | MVP | To Do | MEDGENT-017 | `MEDGENT-019-structured-form-ui` |
| [MEDGENT-020](MEDGENT-020-conversational-chat-ui.md) | AI Assistant chat panel for Log Interaction | MVP | To Do | MEDGENT-015, MEDGENT-017 | `MEDGENT-020-conversational-chat-ui` |
| [MEDGENT-021](MEDGENT-021-chat-form-sync-review.md) | Chat-to-form sync & save/confirmation UX | MVP | To Do | MEDGENT-019, MEDGENT-020 | `MEDGENT-021-chat-form-sync-review` |
| [MEDGENT-022](MEDGENT-022-edit-interaction-flow.md) | Edit Interaction flow *(mandatory tool's UI)* | MVP | To Do | MEDGENT-011, MEDGENT-021 | `MEDGENT-022-edit-interaction-flow` |
| [MEDGENT-026](MEDGENT-026-voice-note-transcription.md) | Voice note capture & summarization | **Stretch** | To Do | MEDGENT-009, MEDGENT-019 | `MEDGENT-026-voice-note-transcription` |

## EPIC-06: Quality, Docs & Deployment

Trimmed for the time-box: light smoke tests, not a coverage initiative;
observability demoted to stretch.

| Spec | Title | Priority | Status | Depends on | Branch |
|------|-------|----------|--------|------------|--------|
| [MEDGENT-023](MEDGENT-023-automated-test-suites.md) | Critical-path smoke tests | MVP | To Do | MEDGENT-021, MEDGENT-022 | `MEDGENT-023-automated-test-suites` |
| [MEDGENT-025](MEDGENT-025-docs-seed-data.md) | README, architecture docs & demo seed data | MVP | To Do | MEDGENT-023 | `MEDGENT-025-docs-seed-data` |
| [MEDGENT-024](MEDGENT-024-observability-logging.md) | Observability & logging | **Stretch** | To Do | MEDGENT-015 | `MEDGENT-024-observability-logging` |

## MVP build order (the actual path to submission)

```
001 → 002 → 003                              (foundation)
005 → 006 → 007      ⟍
016 → 017            ⟍
                       009 → 010 → 011 → 012 → 013 → 014 → 015   (agent, 5 tools)
                       019 → 020 → 021 → 022                     (Log Interaction Screen)
                       023 → 025                                  (smoke tests, README/seed data)
```

`005..007` and `016..017` can run in parallel once `001..003` are done.
`009..015` needs `007`. `019..022` needs both `015` and `017`. Always
confirm against each spec's own `Depends on` field before starting.

Stretch specs (`004`, `024`, `026`) only after `025` is done and staged.

## Submission checklist (from `docs/med-agent-crm.pdf`)

- [ ] One GitHub repo with frontend + backend code (this monorepo).
- [ ] Clear `README.md` explaining the project and how to run it
      (MEDGENT-025).
- [ ] 10-15 min video: frontend walkthrough, all 5 tools demoed working,
      code/structure explanation, summary of understanding of the task.
- [ ] GitHub repo link + video submitted via the assignment's Google Form.
