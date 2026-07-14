# MEDGENT-001: Monorepo scaffold & tooling

**Status:** To Do
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-01: Foundation & Infrastructure](epics/EPIC-01-foundation.md)
**Branch:** `MEDGENT-001-monorepo-scaffold`
**Depends on:** none

## User story

As a developer on this project, I want a consistent monorepo layout with
baseline tooling for both the frontend and backend, so that every later spec
has an obvious place to add code and a consistent way to lint/format it.

## Context

The repo currently has nothing but `specs/` and `steering/`. Per the fixed
architecture in `steering/04-architecture-tech-stack.md`, this is a monorepo
containing a React/Redux frontend and a FastAPI/LangGraph backend, with
Docker Compose tying them together. This spec creates the empty-but-wired
skeleton; it does not implement any product feature.

## Acceptance criteria

- [ ] Root-level `frontend/` and `backend/` directories exist matching the
      layout in `steering/04-architecture-tech-stack.md`.
- [ ] `frontend/` is a working Vite + React + TypeScript app that starts
      with `npm run dev` and shows a placeholder page.
- [ ] `frontend/` has ESLint + Prettier configured and a `lint`/`format`
      npm script; both run clean on the placeholder app.
- [ ] `backend/` is a FastAPI app (`backend/app/main.py`) with a `/health`
      endpoint returning `{"status": "ok"}`, runnable via `uvicorn`.
- [ ] `backend/` has Ruff (lint + format) and mypy configured, both clean on
      the placeholder app; dependencies managed via `pyproject.toml`.
- [ ] Root `.env.example` exists listing every env var either app currently
      needs (even if placeholder values).
- [ ] Root `README.md` explains how to run frontend and backend locally
      without Docker (Docker comes in MEDGENT-002).
- [ ] `specs/README.md` and this file's `Status` updated per the git
      workflow.

## Technical details

- Frontend: `npm create vite@latest frontend -- --template react-ts`,
  add ESLint (`@typescript-eslint`, `eslint-plugin-react-hooks`) + Prettier.
- Backend: `backend/pyproject.toml` with FastAPI, Uvicorn, Pydantic v2,
  Ruff, mypy as dependencies/dev-dependencies. Use `backend/app/` package
  layout from `steering/04-architecture-tech-stack.md` (`api/`, `models/`,
  `schemas/`, `agent/`, `core/`) — subpackages can start as empty
  `__init__.py` files; they'll be filled by later specs.
- No database connection yet — that's MEDGENT-003. No Docker yet — that's
  MEDGENT-002.
- Keep the placeholder frontend page and `/health` endpoint intentionally
  minimal; this spec is plumbing, not product surface.
