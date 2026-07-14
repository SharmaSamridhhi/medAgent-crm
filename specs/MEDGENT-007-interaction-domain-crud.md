# MEDGENT-007: Interaction domain model & CRUD API

**Status:** Done
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-02: Backend Core Services](epics/EPIC-02-backend-core.md)
**Branch:** `MEDGENT-007-interaction-domain-crud`
**Depends on:** MEDGENT-006

## User story

As a pharma sales rep, I want a structured record of each interaction I
have with an HCP (when, how, who attended, what was discussed, what
materials/samples were shared, the HCP's sentiment, outcomes, and
follow-up needs), so that my call history is queryable and consistent
regardless of whether I logged it via form or chat.

## Context

This is the core data model the whole project revolves around. Its field
list is taken directly from the reference "Log HCP Interaction" mockup in
`docs/med-agent-crm.pdf` (the original assignment brief), not invented
independently — see that doc before changing this schema. MEDGENT-003
created a baseline `interactions` table; this spec fleshes it out to match
the mockup and exposes CRUD. Both the structured form panel (MEDGENT-019)
and the agent's Log/Edit Interaction tools (MEDGENT-010, MEDGENT-011) write
through this same API — it is the single source of truth for interaction
data regardless of entry method.

## Acceptance criteria

- [x] `interactions` table extended (via migration) to include, matching
      the mockup's field set:
      - `hcp_id` (FK), `rep_id` (FK)
      - `interaction_type` (e.g. Meeting, Call, Email, Conference —
        mockup's "Interaction Type" dropdown)
      - `occurred_at` (date + time combined — mockup's "Date"/"Time")
      - `attendees` (JSONB list of names — mockup's "Attendees")
      - `topics_discussed` (free text — mockup's "Topics Discussed")
      - `materials_shared` (JSONB list — mockup's "Materials Shared")
      - `samples_distributed` (JSONB list — mockup's "Samples Distributed")
      - `sentiment` (`positive` | `neutral` | `negative`, nullable —
        mockup's "Observed/Inferred HCP Sentiment")
      - `outcomes` (free text — mockup's "Outcomes")
      - `follow_up_notes` (free text — mockup's "Follow-up Actions"; the
        *tracked, dated* follow-up record itself is MEDGENT-013's
        `follow_ups` table, this field is just the free-text note)
      - `source` (`form` | `chat`), `created_at`, `updated_at`
- [x] `GET /api/v1/interactions` — list, filterable by `hcp_id`, `rep_id`,
      date range; paginated.
- [x] `GET /api/v1/interactions/{id}` — fetch one.
- [x] `POST /api/v1/interactions` — create.
- [x] `PATCH /api/v1/interactions/{id}` — partial update.
- [x] `DELETE /api/v1/interactions/{id}` — soft delete, consistent with
      MEDGENT-006's approach.
- [x] `hcp_id` must reference an existing, active HCP — 422/404 otherwise.
- [x] `sentiment`, if provided, must be one of the three allowed values —
      422 otherwise.
- [x] Pydantic request/response schemas distinct from the ORM model.
- [x] Tests: happy-path CRUD, invalid `hcp_id`, invalid `sentiment`,
      validation failures.

## Technical details

- Router at `backend/app/api/v1/interactions.py`.
- `attendees`, `materials_shared`, `samples_distributed` as Postgres
  `JSONB` columns holding lists of strings — a normalized
  attendees/materials/products table is out of scope for this build.
- `sentiment` as a Postgres enum or a Pydantic `Literal["positive",
  "neutral", "negative"]` validated at the API layer — either is fine,
  don't over-engineer.
- `source` column exists specifically so it's always visible which entry
  path (form vs. chat) produced a given record — needed for MEDGENT-021's
  review UX and useful for the demo video's narration.
- This spec's schema is the floor the AI agent tools build on. Two fields
  are intentionally deferred to the specs that own them rather than added
  here: LLM-generated compliance flags (`compliance_flags`,
  `has_compliance_flags` — added by MEDGENT-014's migration) and the
  suggested-follow-ups the agent proposes at log time (these are a
  MEDGENT-010 tool *output*, surfaced in the UI as suggestions — they are
  not persisted on the interaction itself unless/until the rep accepts one,
  at which point MEDGENT-013 creates a real `follow_ups` row).
