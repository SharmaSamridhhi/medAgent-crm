# EPIC-06: Quality, Docs & Deployment

**Status:** To Do

## Goal

Close out the submission: a light smoke-test pass and the README/seed data
the assignment's deliverables literally require. Observability is a
stretch goal given the project's time-box — see `specs/README.md`.

## Specs in this epic

| Spec | Title | Priority | Status |
|------|-------|----------|--------|
| [MEDGENT-023](../MEDGENT-023-automated-test-suites.md) | Critical-path smoke tests | MVP | To Do |
| [MEDGENT-025](../MEDGENT-025-docs-seed-data.md) | README, architecture docs & demo seed data | MVP | To Do |
| [MEDGENT-024](../MEDGENT-024-observability-logging.md) | Observability & logging | **Stretch** | To Do |
| [MEDGENT-028](../MEDGENT-028-render-deployment.md) | Render deployment config | Dev tooling | Done |

## Notes

MEDGENT-023 is deliberately scoped down to a handful of integration tests,
not a coverage initiative — the per-spec testing minimums in
`steering/02-code-quality.md` already apply throughout. MEDGENT-025 is
required: it's the README the assignment's GitHub submission deliverable
calls for, plus seed data needed to demo the tools in the video.

MEDGENT-028 was built out of order, ahead of 023/025, at the user's
explicit request — see the spec file for why. It's bundled into the
`EPIC-05-log-interaction-screen` branch rather than a fresh `main`-based
one, same as MEDGENT-027, since nothing is merged to `main` yet.
