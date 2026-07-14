# MEDGENT-015: Agent orchestration & conversational endpoint

**Status:** To Do
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-03: LangGraph AI Agent & Tools](epics/EPIC-03-ai-agent.md)
**Branch:** `MEDGENT-015-agent-orchestration-endpoint`
**Depends on:** MEDGENT-010, MEDGENT-011, MEDGENT-012, MEDGENT-013, MEDGENT-014

## User story

As a pharma sales rep, I want a single chat interface where I can log an
interaction, edit one, ask about an HCP's history, or set a follow-up — all
in one conversation — so that I don't need to know which "feature" handles
which request.

## Context

MEDGENT-010 through MEDGENT-014 built five independent tools. This spec
wires all of them onto the LangGraph graph from MEDGENT-009 with real
routing logic, and exposes the whole thing behind a chat API endpoint the
frontend (MEDGENT-020) will call.

## Acceptance criteria

- [ ] All five tools (`log_interaction`, `edit_interaction`,
      `retrieve_hcp_history`, `schedule_follow_up`,
      `flag_compliance_risks`) are registered on the graph with routing
      driven by the LLM's tool-calling decision, not hardcoded
      keyword/intent matching.
- [ ] `POST /api/v1/agent/chat` accepts a rep message (+ conversation/session
      id) and returns the agent's reply, plus any structured side effects
      (e.g. "interaction logged: {id}", "flags raised: [...]").
- [ ] Conversation state persists across turns within a session (in-memory
      or DB-backed session store — pick the simpler option unless
      multi-instance deployment is already a concern) so multi-turn flows
      (e.g. clarification requests from MEDGENT-010/011) work correctly.
- [ ] `retrieve_hcp_history` (MEDGENT-012) is invoked automatically once an
      HCP is identified in conversation, without the rep having to ask for
      it explicitly, per that spec's acceptance criteria.
- [ ] Streaming or at least reasonably fast non-streaming responses — note
      whichever is chosen and why; streaming is preferred for chat UX but
      not mandatory if it meaningfully complicates this spec.
- [ ] Integration test drives a multi-turn conversation end-to-end (log →
      immediately edit → ask for history) against the real graph with the
      LLM mocked, confirming state carries correctly between turns.

## Technical details

- Endpoint at `backend/app/api/v1/agent.py`, scoping the session and any
  tool calls to the single hardcoded default rep established in
  MEDGENT-005 (no auth system in this build — see
  [[04-architecture-tech-stack]]).
- This spec is where the graph nodes/edges actually get non-trivial —
  earlier specs added tools independently; this is the first place their
  interactions (e.g. log-then-immediately-edit in the same conversation)
  are tested together.
- If session state is kept in-memory, document that restarting the backend
  drops in-flight conversations — acceptable for this project's scope, but
  call it out in the spec/PR rather than leaving it implicit.
