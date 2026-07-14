# MEDGENT-025: README, architecture docs & demo seed data

**Status:** To Do
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-06: Quality, Docs & Deployment](epics/EPIC-06-quality-deployment.md)
**Branch:** `MEDGENT-025-docs-seed-data`
**Depends on:** MEDGENT-023

## User story

As anyone picking up this project fresh (including a reviewer or a future
version of myself), I want a clear README, an architecture overview, and
realistic seed data, so that the project is understandable and demoable
without having to reverse-engineer it from code or manually create test
HCPs.

## Context

Documentation and quick-start instructions were added incrementally by
almost every prior spec (per their acceptance criteria). This spec is a
final consolidation pass plus the one net-new thing none of them owned:
demo seed data realistic enough to actually show off the Log Interaction
Screen. It also closes out the assignment's literal deliverables list
(`docs/med-agent-crm.pdf`): a single GitHub repo with frontend + backend
code and a clear README, ready for the 10-15 minute walkthrough video
(frontend demo, all 5 tools working, code/structure explanation, a summary
of what was understood from the brief).

## Acceptance criteria

- [ ] `README.md` consolidated into a single coherent quick-start (Docker
      Compose path primary, non-Docker path as an alternative), replacing
      the incrementally-patched version from earlier specs.
- [ ] A short architecture overview (can live in `README.md` or a
      `docs/architecture.md`) covering: monorepo layout, request flow for
      both form and chat logging paths, the LangGraph agent's tools and
      what each does.
- [ ] A seed script/fixture creates: a demo rep, a handful of realistic
      HCPs (varied specialties), and a few historical interactions per HCP
      — enough to meaningfully demo `retrieve_hcp_history` (MEDGENT-012)
      and the Log Interaction Screen without starting from an empty
      database.
- [ ] Seed script is idempotent (safe to re-run) and documented in the
      README.
- [ ] A brief note on the two mandatory-tool requirement and the full
      five-tool agent design (mapping back to the original project brief)
      for anyone evaluating the project against that brief.

## Technical details

- Seed data should be realistic but clearly fictional (no real HCP names/
  institutions) — invent plausible pharma-sales-realistic names/specialties/
  products.
- Keep the architecture doc concise — a diagram-in-words or a simple ASCII/
  mermaid diagram is enough; this isn't a formal design document.
- This is the natural last spec in the project's initial build-out; after
  it, the project should be fully demoable end to end via `docker compose
  up` plus the seed script.
