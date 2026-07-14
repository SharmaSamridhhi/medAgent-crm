# MEDGENT-012: Tool — Retrieve HCP History

**Status:** Done
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

- [x] A `retrieve_hcp_history` tool is registered with a Pydantic input
      schema (HCP id or name) and output schema (HCP profile summary +
      recent interactions, most recent first, capped at a reasonable
      count).
- [x] Given an HCP name instead of an id, the tool resolves it the same way
      MEDGENT-010 does (existing HCP records via MEDGENT-006's API),
      returning a clarification if ambiguous.
- [x] Output includes an LLM-generated short summary of the relationship
      (e.g. "3 interactions in the last quarter, primarily discussing
      CardioX dosing; last follow-up was requested for next month") in
      addition to the raw interaction list.
- [x] The tool only reads via the existing HCP/Interaction APIs
      (MEDGENT-006/007) — no direct DB queries from the agent layer.
- [x] Unit tests cover: HCP with history, HCP with no prior interactions,
      ambiguous HCP name, with the LLM call mocked.

## Technical details

- Tool lives at `backend/app/agent/tools/retrieve_hcp_history.py`.
- Summary generation can use `GROQ_MODEL_DEFAULT` — this is a lighter task
  than the structured extraction in MEDGENT-010/011, so the faster model is
  appropriate here. Skipped entirely (no LLM call) when there are zero
  prior interactions — nothing to summarize.
- Calls `list_hcps`/`get_hcp`/`list_interactions` (MEDGENT-006/007's own
  router functions) in-process rather than raw SQLAlchemy queries, per
  this spec's "no direct DB queries" requirement. Gotcha worth flagging
  for any later spec doing the same: those functions' `search`,
  `specialty`, `skip`, `limit` parameters default to FastAPI `Query(...)`
  marker objects, not their real defaults — that resolution only happens
  through FastAPI's request handling. Calling them directly in Python
  means every such parameter must be passed explicitly (e.g.
  `list_hcps(search=name, specialty=None, skip=0, limit=20, db=db)`), or
  the marker object itself leaks in as the "value" and breaks the query.
- This tool is read-only — it must not create, update, or delete any
  record. Keep it side-effect-free so the agent can call it freely for
  context without risk.
- Designed to be called by the agent proactively (e.g. right after an HCP
  is identified in conversation), not only when the rep explicitly asks for
  history — wire that into the graph's routing logic in MEDGENT-015.
