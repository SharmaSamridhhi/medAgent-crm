# MEDGENT-004: CI pipeline

**Status:** To Do
**Priority:** Stretch — only after the MVP path is fully done; not required for submission
**Epic:** [EPIC-01: Foundation & Infrastructure](epics/EPIC-01-foundation.md)
**Branch:** `MEDGENT-004-ci-pipeline`
**Depends on:** MEDGENT-003

## User story

As a developer, I want lint/type-check/test to run automatically on every
PR, so that the standards in `steering/02-code-quality.md` are enforced
mechanically rather than by memory.

## Context

By this point the repo has a working frontend, backend, Docker Compose
stack, and a DB schema with migrations. This spec adds a GitHub Actions
workflow so every future spec's PR is checked automatically.

## Acceptance criteria

- [ ] `.github/workflows/ci.yml` runs on pull requests targeting `main`.
- [ ] Backend job: installs deps, runs `ruff check`, `ruff format --check`,
      `mypy`, and `pytest` (even if the test suite is currently minimal).
- [ ] Frontend job: installs deps, runs `eslint`, `prettier --check`, and
      the frontend test runner (even if minimal).
- [ ] Migration check: CI spins up a throwaway Postgres service and confirms
      `alembic upgrade head` runs cleanly from an empty database.
- [ ] CI fails the PR if any of the above fail.
- [ ] `README.md` mentions CI status and how to run the same checks locally
      before pushing.

## Technical details

- Use `actions/setup-node` and `actions/setup-python` (or `uv`/`astral-sh`
  setup action) with dependency caching to keep runs fast.
- Postgres service container in the workflow (`services: postgres:`)
  mirroring the version pinned in `docker-compose.yml`.
- Keep this a single workflow file with two jobs (backend, frontend) rather
  than a sprawling matrix — this project doesn't need multi-OS/multi-version
  coverage.
- No deployment step here — CI is check-only for now; deployment isn't in
  scope until/unless a future spec asks for it.
