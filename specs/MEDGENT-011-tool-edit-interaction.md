# MEDGENT-011: Tool — Edit Interaction

**Status:** Done
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-03: LangGraph AI Agent & Tools](epics/EPIC-03-ai-agent.md)
**Branch:** `MEDGENT-011-tool-edit-interaction`
**Depends on:** MEDGENT-007, MEDGENT-010

## User story

As a pharma sales rep, I want to correct or add to an interaction I already
logged just by telling the agent what changed ("actually it was 3 samples,
not 2"), so that fixing a mistake doesn't require opening a form and
hunting for the right record.

## Context

This is the second of the two mandatory tools required by the project
brief. It depends on MEDGENT-010 existing first because it reuses the same
extraction/resolution patterns (identifying which interaction and which
fields are being changed) that MEDGENT-010 establishes.

## Acceptance criteria

- [x] An `edit_interaction` tool is registered on the agent with a Pydantic
      input schema (free-form correction text, plus optional explicit
      `interaction_id` if already known from conversation context) and
      output schema (updated interaction fields + a diff of what changed).
- [x] The tool can resolve *which* interaction is being referred to from
      conversational context (e.g. "the one I just logged with Dr. Patel")
      without the user supplying an ID — using recency + HCP name matching
      against the rep's recent interactions.
- [x] If the target interaction can't be confidently resolved (e.g. more
      than one plausible match, or none), the tool asks for clarification
      rather than guessing.
- [x] The tool extracts which field(s) are being changed and their new
      values (e.g. samples_distributed, notes, follow_up_needed) and calls
      `PATCH /api/v1/interactions/{id}` (MEDGENT-007) — it does not write
      to the DB directly.
- [x] The response confirms exactly what changed (old value → new value)
      so the rep can verify the correction was applied correctly.
- [x] Unit tests cover: unambiguous edit, ambiguous target requiring
      clarification, edit to a field that doesn't exist/isn't editable,
      with the LLM call mocked.

## Technical details

- Tool lives at `backend/app/agent/tools/edit_interaction.py`, same
  pure-function contract as MEDGENT-010.
- Factored the shared "call GROQ_MODEL_HEAVY with structured output"
  boilerplate into `app/agent/tools/_extraction.py`'s
  `extract_structured(prompt, schema)`, used by both this tool and
  MEDGENT-010's `log_interaction`.
- Resolution happens in two steps, not one: (1) find the target
  interaction using recency (last 7 days, scoped to the current rep) plus
  — only when genuinely ambiguous — a lightweight LLM call extracting just
  the HCP name mentioned, if any; (2) *then* run the field-diff extraction
  against that specific interaction's current values, embedded in the
  prompt as context. A live test against the real Groq API caught why the
  order matters: a correction like "it was 3, not 2" gives the model no
  way to know what "it" refers to without seeing the current
  `samples_distributed` value first — a single one-shot extraction
  (resolve + diff together) fabricated a placeholder list instead of
  correcting the real one.
- "Recent interactions" resolution is scoped to the current rep (`rep_id`
  from the MEDGENT-005 default-rep dependency) within a 7-day window;
  0 or >1 matches always returns `needs_clarification` rather than
  guessing.
- Does not handle deleting an interaction — that's the existing `DELETE`
  endpoint from MEDGENT-007, not part of this tool's scope unless a later
  spec asks for a conversational delete.
