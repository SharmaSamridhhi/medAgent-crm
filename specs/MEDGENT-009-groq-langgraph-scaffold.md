# MEDGENT-009: Groq LLM integration & agent scaffolding

**Status:** Done
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-03: LangGraph AI Agent & Tools](epics/EPIC-03-ai-agent.md)
**Branch:** `MEDGENT-009-groq-langgraph-scaffold`
**Depends on:** MEDGENT-005

## User story

As a developer, I want a working LangGraph graph wired to Groq, with no
tools yet, so that every tool spec (MEDGENT-010 through MEDGENT-014) can
plug into an already-working agent loop instead of each reinventing LLM
wiring.

## Context

This is the agent's foundation: the LangGraph state definition, the Groq
client wrapper, and a trivial single-node graph that can hold a
conversation with no tools. Tools are added incrementally by later specs.
This keeps MEDGENT-009 testable in isolation (can the agent talk at all?)
before any tool-calling complexity is introduced.

## Acceptance criteria

- [x] `backend/app/agent/llm.py` wraps the Groq client, reading
      `GROQ_API_KEY`, `GROQ_MODEL_DEFAULT` (`llama-3.1-8b-instant` — the
      brief's `gemma2-9b-it` was decommissioned by Groq in Oct 2025; this
      is Groq's own recommended replacement, same speed tier), and
      `GROQ_MODEL_HEAVY` (`llama-3.3-70b-versatile`) from settings — no
      hardcoded key or model name anywhere else in the codebase.
- [x] `backend/app/agent/state.py` defines the LangGraph state schema:
      conversation messages, current rep id, optional in-progress
      interaction draft, optional active HCP context.
- [x] `backend/app/agent/graph.py` defines a minimal graph: one LLM node,
      no tools, that can take a user message and return a model response
      using `GROQ_MODEL_DEFAULT`.
- [x] The graph is invokable from a small script or test without going
      through the API layer yet (API endpoint is MEDGENT-015).
- [x] Tests mock the Groq client — no real network calls in the test suite,
      per `steering/02-code-quality.md`.
- [x] `.env.example` updated with `GROQ_API_KEY`, `GROQ_MODEL_DEFAULT`,
      `GROQ_MODEL_HEAVY`.

## Technical details

- Uses `langchain-groq`'s `ChatGroq` (not the bare Groq SDK) — it's a
  `langchain_core` chat model, so it plugs directly into LangGraph's
  message-based state and `bind_tools`/tool-calling node pattern that
  MEDGENT-010+ need, rather than requiring a hand-rolled adapter.
- Keep the state schema intentionally small at this stage; tool-specific
  state (e.g. draft interaction fields) is added when MEDGENT-010 needs it,
  not speculatively here.
- No tool-calling wiring yet — that pattern is introduced by MEDGENT-010,
  the first tool, so the tool-routing design is proven against a real tool
  rather than designed in the abstract.
