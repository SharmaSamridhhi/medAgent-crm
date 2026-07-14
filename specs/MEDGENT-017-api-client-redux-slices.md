# MEDGENT-017: API client & Redux slices for HCP/Interaction

**Status:** To Do
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-04: Frontend Core](epics/EPIC-04-frontend-core.md)
**Branch:** `MEDGENT-017-api-client-redux-slices`
**Depends on:** MEDGENT-006, MEDGENT-007, MEDGENT-016

## User story

As a developer, I want typed API access to the HCP and Interaction
endpoints wired into Redux, so that the Log Interaction Screen (EPIC-05)
can fetch/create/update data without each component talking to `fetch`
directly.

## Context

The backend's HCP (MEDGENT-006) and Interaction (MEDGENT-007) CRUD APIs
exist. This spec wires a typed client for them into the Redux store from
MEDGENT-016, using RTK Query so caching/loading/error states come for free
rather than being hand-rolled per component.

## Acceptance criteria

- [ ] RTK Query API slice(s) for HCPs (list, get, create, update, delete)
      and Interactions (list, get, create, update, delete), typed against
      the backend's Pydantic schemas (mirrored as TS types).
- [ ] Base query points at `VITE_API_BASE_URL` — no auth header needed
      since the backend is single-rep with no auth system in this build
      (see `steering/04-architecture-tech-stack.md`).
- [ ] Loading and error states are exposed via the generated RTK Query
      hooks (no separate hand-written thunks duplicating this).
- [ ] A dev-only `.env` var for the API base URL (`VITE_API_BASE_URL`),
      documented in `.env.example`.
- [ ] Tests: slice/endpoint configuration is covered by at least a mocked
      request/response test (e.g. via `msw` or RTK Query's built-in test
      utocols) confirming a create + list round-trip.

## Technical details

- One RTK Query `createApi` instance (`backend/frontend` — actually
  `frontend/src/api/apiSlice.ts`) with injected endpoints per domain
  (`hcpsApi`, `interactionsApi` as endpoint groups), not two separate
  `createApi` instances, to share caching/tag invalidation across domains
  (e.g. creating an interaction should invalidate the relevant HCP's
  history view).
- TS types for HCP/Interaction payloads should be hand-mirrored from the
  backend Pydantic schemas for now; generating them automatically (e.g. via
  OpenAPI codegen) is a reasonable future improvement but not required
  here — don't build that tooling unless asked.
- This spec does not include the agent chat endpoint client — that's part
  of MEDGENT-020, scoped separately since it's a different interaction
  shape (streaming/session-based chat vs. CRUD).
