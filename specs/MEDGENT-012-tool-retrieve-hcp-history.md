# MEDGENT-012: Tool — Retrieve HCP History

**Status:** To Do
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-03: LangGraph AI Agent & Tools](epics/EPIC-03-ai-agent.md)
**Branch:** `MEDGENT-012-tool-retrieve-hcp-history`
**Depends on:** MEDGENT-006, MEDGENT-007, MEDGENT-009

## User story

As a pharma sales rep, I want the agent to know what I've discussed with an
HCP before, so that it can ground the conversation ("last time you
mentioned she wanted more data on X — did you bring that up?") instead of
treating every interaction as a blank slate.

## Context

Without this tool, the agent has no memory of past interactions beyond the
current chat session. This tool gives it read access to an HCP's history so
it can both inform the rep and improve extraction quality in MEDGENT-010
(e.g. resolving an ambiguous HCP name using "who have I talked to
recently").

## Acceptance criteria

- [ ] A `retrieve_hcp_history` tool is registered with a Pydantic input
      schema (HCP id or name) and output schema (HCP profile summary +
      recent interactions, most recent first, capped at a reasonable
      count).
- [ ] Given an HCP name instead of an id, the tool resolves it the same way
      MEDGENT-010 does (existing HCP records via MEDGENT-006's API),
      returning a clarification if ambiguous.
- [ ] Output includes an LLM-generated short summary of the relationship
      (e.g. "3 interactions in the last quarter, primarily discussing
      CardioX dosing; last follow-up was requested for next month") in
      addition to the raw interaction list.
- [ ] The tool only reads via the existing HCP/Interaction APIs
      (MEDGENT-006/007) — no direct DB queries from the agent layer.
- [ ] Unit tests cover: HCP with history, HCP with no prior interactions,
      ambiguous HCP name, with the LLM call mocked.

## Technical details

- Tool lives at `backend/app/agent/tools/retrieve_hcp_history.py`.
- Summary generation can use `GROQ_MODEL_DEFAULT` — this is a lighter task
  than the structured extraction in MEDGENT-010/011, so the faster model is
  appropriate here.
- This tool is read-only — it must not create, update, or delete any
  record. Keep it side-effect-free so the agent can call it freely for
  context without risk.
- Designed to be called by the agent proactively (e.g. right after an HCP
  is identified in conversation), not only when the rep explicitly asks for
  history — wire that into the graph's routing logic in MEDGENT-015.
