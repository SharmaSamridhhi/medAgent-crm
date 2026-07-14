# MEDGENT-010: Tool — Log Interaction

**Status:** Done
**Priority:** MVP — required for the 36-hour submission; this is one of the
two explicitly mandatory tools in the assignment brief.
**Epic:** [EPIC-03: LangGraph AI Agent & Tools](epics/EPIC-03-ai-agent.md)
**Branch:** `MEDGENT-010-tool-log-interaction`
**Depends on:** MEDGENT-007, MEDGENT-009

## User story

As a pharma sales rep, I want to describe an HCP interaction in my own
words in the chat interface and have the agent turn that into a structured,
saved interaction record — including my own read on the HCP's sentiment
and sensible next-step suggestions — so that logging a call is as fast as
typing a sentence instead of filling out a form.

## Context

This is one of the two mandatory tools required by the project brief
(`docs/med-agent-crm.pdf`). It's the first real tool added to the
LangGraph graph from MEDGENT-009, so it also establishes the tool-calling
pattern (typed input/output, routing) that MEDGENT-011 through MEDGENT-014
follow. Its output shape is driven directly by the reference "Log HCP
Interaction" mockup in that doc — including the AI Suggested Follow-ups
panel shown there — not invented independently.

## Acceptance criteria

- [x] A `log_interaction` tool is registered on the LangGraph agent with a
      Pydantic input schema (raw rep utterance/notes, optionally an already
      -identified `hcp_id` or HCP name to resolve) and output schema (the
      structured fields extracted + created interaction id + suggested
      follow-ups).
- [x] Given free-form text like "Met Dr. Patel this morning, discussed the
      new dosing data for CardioX, left 2 sample packs, she seemed
      positive and wants a follow-up next month", the tool extracts:
      - HCP (resolved to an existing `hcps` record or flagged unresolved)
      - `interaction_type` and `occurred_at` (defaulting sensibly if not
        stated)
      - `attendees` (if mentioned)
      - `topics_discussed`
      - `materials_shared` and `samples_distributed` (kept distinct —
        materials are marketing/leave-behind collateral, samples are
        product samples)
      - `sentiment` (`positive` | `neutral` | `negative`) — the agent's
        read on the HCP's reaction, inferred from the rep's description
      - `outcomes` (key agreements/results, if any were described)
- [x] The tool additionally generates 1-3 `suggested_follow_ups` (short,
      actionable strings, e.g. "Schedule follow-up meeting in 2 weeks",
      "Send CardioX Phase III data sheet") — these are proposals only, not
      persisted as real follow-ups unless the rep accepts one (which then
      calls MEDGENT-013).
- [x] Extraction uses `GROQ_MODEL_HEAVY` (`llama-3.3-70b-versatile`) for
      the structured extraction step; the lighter default model can still
      handle the surrounding conversational turns.
- [x] If the HCP name can't be confidently resolved to an existing record,
      the tool returns a clarification request rather than guessing or
      silently creating a duplicate HCP.
- [x] On success, the tool calls the Interaction API (MEDGENT-007) with
      `source: "chat"` to persist the record — it does not write to the DB
      directly, keeping the API as the single write path.
- [x] Unit tests cover: full extraction success (including sentiment and
      suggested follow-ups), ambiguous/unresolvable HCP, missing required
      info (e.g. no discernible topic), with the LLM call mocked.

## Technical details

- Tool lives at `backend/app/agent/tools/log_interaction.py`, following the
  pure-function contract in `steering/04-architecture-tech-stack.md`.
- Entity extraction prompt should request a structured (JSON-mode /
  function-calling) response from the model rather than parsing free text
  with regex — the response schema should mirror MEDGENT-007's interaction
  fields plus the `suggested_follow_ups` list.
- HCP resolution: fuzzy match against `GET /api/v1/hcps` results (from
  MEDGENT-006) by name; below a confidence threshold, surface the
  candidates back to the conversation rather than picking one.
- Compliance flagging (MEDGENT-014) runs as a follow-on step after this
  tool successfully creates the interaction — this tool's own job is
  extraction and persistence, not compliance review.
- This tool calls the REST API (in-process client, not over HTTP loopback)
  to create the interaction — reuses the same Pydantic schemas as
  MEDGENT-007 for consistency between form and chat entry paths.
- "Registered on the LangGraph agent" is satisfied at the pure-function/
  contract level here (a plain, independently-testable `log_interaction(payload, db)`
  function with typed Pydantic input/output) — actually binding it as a
  LangChain tool into a multi-tool graph with LLM-driven routing is
  MEDGENT-015's job, once all five tools exist. MEDGENT-011 through
  MEDGENT-014 follow this same pattern.
