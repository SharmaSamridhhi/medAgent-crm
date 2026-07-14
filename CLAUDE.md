# medAgent-CRM

AI-first CRM HCP (Healthcare Professional) module for a pharmaceutical sales
representative. Core deliverable is the **Log Interaction Screen**: a
single screen with a structured form panel and an AI Assistant (LangGraph)
chat panel side by side, backed by a shared FastAPI + Postgres backend.

This project is built against a real, time-boxed take-home assignment —
see `docs/med-agent-crm.pdf` for the original brief (deliverables: a GitHub
repo + README, and a 10-15 min demo video covering the frontend, all 5
LangGraph tools, code structure, and a summary of understanding). **Every
spec is tagged `Priority: MVP` or `Priority: Stretch`** in
`specs/README.md` — build MVP specs in order; only touch Stretch specs
(CI pipeline, observability epic, voice-note transcription) once the full
MVP path is done and staged.

## Before doing anything else

1. Read every file in `steering/` — it is the strict, binding process for
   this project (git workflow, code quality, development workflow,
   architecture/tech stack). It applies in every session, including a fresh
   one started for a single spec.
2. Read `specs/README.md` — the index of all epics and specs, their
   priority (MVP/Stretch), status, and dependency order. This is the
   source of truth for "what's next."
3. Each spec (`specs/MEDGENT-XXX-*.md`) is self-contained: user story,
   context, acceptance criteria, technical details, dependencies.

## The one-line version of the workflow

Branch per spec from latest `main` (`MEDGENT-XXX-branch-name`) → implement
against that spec's acceptance criteria only → mark the spec `In Progress`
when starting and `Done` when finished → stage the changes (`git add`) →
tell the user it's ready → **stop**. Committing, pushing, PRs, and merging
to `main` are the user's job, never yours. Full detail in
`steering/01-git-workflow.md`.

## Layout

```
medAgent-crm/
├── frontend/     # React + Redux (added starting MEDGENT-016)
├── backend/      # FastAPI + LangGraph (added starting MEDGENT-005)
├── docker/       # (added starting MEDGENT-002)
├── docs/         # original assignment brief (med-agent-crm.pdf)
├── specs/        # epics + specs, source of truth for scope/status
└── steering/     # binding process rules — read first
```
