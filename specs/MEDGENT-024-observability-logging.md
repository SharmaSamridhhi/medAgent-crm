# MEDGENT-024: Observability & logging

**Status:** To Do
**Priority:** Stretch — only after the MVP path is fully done; not required for submission
**Epic:** [EPIC-06: Quality, Docs & Deployment](epics/EPIC-06-quality-deployment.md)
**Branch:** `MEDGENT-024-observability-logging`
**Depends on:** MEDGENT-015

## User story

As a developer, I want visibility into what the agent is doing — which
tools it calls, how long LLM calls take, what errors occur — so that
issues in a non-deterministic AI system are debuggable instead of opaque.

## Context

MEDGENT-005 set up basic structured logging for the API. This spec extends
that specifically to the LangGraph agent (MEDGENT-009 through MEDGENT-015),
where debugging is much harder without visibility into tool selection and
LLM latency/errors.

## Acceptance criteria

- [ ] Every tool invocation logs: tool name, input summary (no PII/secrets
      leaked into logs), duration, success/failure.
- [ ] Every Groq LLM call logs: model used, duration, token usage if the
      API exposes it, success/failure — request/response content itself is
      not logged at info level (could contain sensitive HCP/notes data);
      debug-level logging of content is acceptable if clearly gated behind
      a debug flag.
- [ ] API-level request logging (from MEDGENT-005) includes a correlation
      id that ties together the HTTP request and any agent/tool logs it
      triggered.
- [ ] Errors (tool failures, LLM API errors, DB errors) are logged with
      enough context to reproduce, and return a clean error to the client
      rather than a stack trace.
- [ ] Document in `README.md` how to view logs locally (`docker compose
      logs backend`) and what to look for when debugging a bad agent
      response.

## Technical details

- Reuse the structured logging setup from MEDGENT-005 rather than
  introducing a second logging library.
- If LangSmith or an equivalent LangGraph tracing tool is desired for
  deeper agent debugging, propose it to the user as an optional addition
  here rather than assuming it's in scope — it's not part of the fixed
  stack in `steering/04-architecture-tech-stack.md`.
- Keep PII/compliance-sensitive content (HCP names, notes) out of
  info-level logs given the pharma compliance context established in
  MEDGENT-014.
