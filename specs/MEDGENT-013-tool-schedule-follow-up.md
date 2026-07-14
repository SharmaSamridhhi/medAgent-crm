# MEDGENT-013: Tool — Schedule Follow-up

**Status:** Done
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-03: LangGraph AI Agent & Tools](epics/EPIC-03-ai-agent.md)
**Branch:** `MEDGENT-013-tool-schedule-follow-up`
**Depends on:** MEDGENT-007, MEDGENT-009

## User story

As a pharma sales rep, I want to tell the agent "remind me to follow up
with Dr. Patel next month about the dosing data" and have that turn into a
tracked follow-up task tied to the interaction, so that follow-ups don't
just live in my notes and get forgotten.

## Context

`interactions.follow_up_notes` (MEDGENT-007) is just a free-text field —
it doesn't capture *when* the follow-up is due, or let one be queried/
tracked independently of the interaction it originated from (e.g. "what
follow-ups do I have this week"). This tool introduces a dedicated,
datable, statusful follow-up record for that.

## Acceptance criteria

- [x] A `follow_ups` table (new migration) with: `id`, `interaction_id`
      (FK, nullable if not tied to a specific interaction), `hcp_id`,
      `rep_id`, `due_date`, `note`, `status`
      (`open`/`completed`/`cancelled`), `created_at`.
- [x] Minimal CRUD exposed at `/api/v1/follow-ups` (at least create, list
      by rep, mark complete) — full CRUD parity with HCP/Interaction isn't
      required unless the UI (EPIC-05) ends up needing it.
- [x] A `schedule_follow_up` tool registered on the agent with a Pydantic
      input schema (free-form request text + optional interaction/HCP
      context already in conversation) that extracts a due date and note,
      and an output schema confirming what was scheduled.
- [x] This tool is also the one invoked when a rep accepts one of the
      `suggested_follow_ups` proposed by MEDGENT-010's `log_interaction`
      output (the mockup's "AI Suggested Follow-ups" chips) — accepting a
      suggestion is just a `schedule_follow_up` call seeded with that
      suggestion's text rather than a separate code path.
- [x] Relative dates in the rep's phrasing ("next month", "in two weeks")
      are resolved to an actual date using the conversation's current date
      context.
- [x] The tool calls the follow-ups API to persist — no direct DB writes
      from the agent layer.
- [x] Unit tests cover: relative date resolution, follow-up tied to a
      specific interaction, follow-up with only an HCP (no specific
      interaction), with the LLM call mocked.

## Technical details

- New router at `backend/app/api/v1/follow_ups.py`; new migration alongside
  it (see `steering/02-code-quality.md` on migrations).
- Tool lives at `backend/app/agent/tools/schedule_follow_up.py`.
- Date resolution: pass the current date explicitly into the prompt context
  rather than relying on the model's own notion of "today".
- Surfacing follow-ups in the UI (a reminders list, notifications, etc.) is
  out of scope for this spec — it only needs to be creatable and queryable
  via the API. UI surfacing can be proposed as a future spec if wanted.
