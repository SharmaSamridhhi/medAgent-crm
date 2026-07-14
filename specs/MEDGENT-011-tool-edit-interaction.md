# MEDGENT-011: Tool — Edit Interaction

**Status:** To Do
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

- [ ] An `edit_interaction` tool is registered on the agent with a Pydantic
      input schema (free-form correction text, plus optional explicit
      `interaction_id` if already known from conversation context) and
      output schema (updated interaction fields + a diff of what changed).
- [ ] The tool can resolve *which* interaction is being referred to from
      conversational context (e.g. "the one I just logged with Dr. Patel")
      without the user supplying an ID — using recency + HCP name matching
      against the rep's recent interactions.
- [ ] If the target interaction can't be confidently resolved (e.g. more
      than one plausible match, or none), the tool asks for clarification
      rather than guessing.
- [ ] The tool extracts which field(s) are being changed and their new
      values (e.g. samples_distributed, notes, follow_up_needed) and calls
      `PATCH /api/v1/interactions/{id}` (MEDGENT-007) — it does not write
      to the DB directly.
- [ ] The response confirms exactly what changed (old value → new value)
      so the rep can verify the correction was applied correctly.
- [ ] Unit tests cover: unambiguous edit, ambiguous target requiring
      clarification, edit to a field that doesn't exist/isn't editable,
      with the LLM call mocked.

## Technical details

- Tool lives at `backend/app/agent/tools/edit_interaction.py`, same
  pure-function contract as MEDGENT-010.
- Reuses the entity-extraction approach from MEDGENT-010 but scoped to
  "what changed" rather than "log a new record" — consider whether the two
  tools can share a common extraction helper rather than duplicating
  prompt logic; if so, factor it out during this spec.
- "Recent interactions" resolution should be scoped to the current rep
  (`rep_id` from the MEDGENT-005 default-rep dependency) and a reasonable
  recency window (e.g. last 7
  days) before falling back to asking the user directly.
- Does not handle deleting an interaction — that's the existing `DELETE`
  endpoint from MEDGENT-007, not part of this tool's scope unless a later
  spec asks for a conversational delete.
