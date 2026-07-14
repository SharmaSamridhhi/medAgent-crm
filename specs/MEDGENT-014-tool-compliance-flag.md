# MEDGENT-014: Tool — Compliance Flag

**Status:** Done
**Priority:** MVP — required for the 36-hour submission (this is the 5th
of the 5 required agent tools).
**Epic:** [EPIC-03: LangGraph AI Agent & Tools](epics/EPIC-03-ai-agent.md)
**Branch:** `MEDGENT-014-tool-compliance-flag`
**Depends on:** MEDGENT-010, MEDGENT-009

## User story

As a pharma sales rep (and as the compliance function behind me), I want
logged interaction notes to be automatically screened for potentially
non-compliant content — off-label claims, unsubstantiated efficacy/safety
statements, mentions of adverse events — so that risky language is
surfaced for review instead of silently sitting in the CRM.

## Context

Pharma sales interactions are heavily regulated: reps must stay within
approved, on-label claims, and any adverse event (AE) mention has separate
regulatory reporting obligations. This tool doesn't block or auto-correct
anything — it flags. It runs as a follow-on step after the Log Interaction
flow (MEDGENT-010) so every chat-logged interaction gets screened
consistently.

Note: this tool is deliberately scoped to *compliance risk* only. HCP
*sentiment* (positive/neutral/negative) is a separate concept owned by
MEDGENT-010's extraction and MEDGENT-007's schema — don't conflate the
two here.

## Acceptance criteria

- [x] `interactions` table extended (migration) with `compliance_flags`
      (JSONB — list of `{category, excerpt, rationale}`) and
      `has_compliance_flags` (bool, indexed) for quick filtering.
- [x] A `flag_compliance_risks` tool registered on the agent with a
      Pydantic input schema (the interaction's notes/topics text) and
      output schema (list of flags, possibly empty).
- [x] Flag categories cover at minimum: off-label claim, unsubstantiated
      efficacy/safety claim, potential adverse event mention, other (with
      rationale).
- [x] The tool uses `GROQ_MODEL_HEAVY` given the higher stakes of missed or
      wrong flags on regulated content.
- [x] The tool runs automatically as part of `log_interaction`
      (MEDGENT-010) after an interaction is created, updating the
      persisted record with any flags — it does not block the save (a
      flagged interaction still gets logged; it's a review signal, not a
      gate).
- [x] Flags are surfaced back in the tool's conversational response so the
      rep sees them immediately (e.g. "Logged — heads up, this mentions a
      possible adverse event; you may want to check AE reporting
      requirements").
- [x] Unit tests cover: clean text (no flags), off-label mention, AE
      mention, with the LLM call mocked. Include a short fixture set of
      realistic pharma rep notes for both flagged and clean cases — reuse
      for the demo video if a flagged example is needed there.

## Technical details

- Tool lives at `backend/app/agent/tools/flag_compliance_risks.py`.
- This tool is explicitly advisory, not a hard gate — never silently drop
  or refuse to log an interaction because of a flag; that's a business
  decision far beyond this project's scope, and false positives would
  otherwise block real work.
- Keep the flag category list config-driven (a small constant/enum) so it
  can be adjusted without touching the extraction logic.
- Structured form entries (MEDGENT-019) bypass the LLM by default since
  there's no free text to screen unless `topics_discussed` or `outcomes`
  is filled in — if either is non-empty on a form-sourced interaction,
  this tool should still run against it (wire that into MEDGENT-019/021,
  not just the chat path).
- Screens the persisted `topics_discussed` + `outcomes` text (not the raw
  chat utterance directly) so the same tool works identically for both
  entry paths. This surfaced a real bug live-testing this spec: MEDGENT-010's
  extraction prompt was compressing `topics_discussed` down to a bare
  product-name label (e.g. "CardioX") instead of a fuller account,
  silently discarding the exact off-label/adverse-event language this
  tool needs to see. Fixed by adding an explicit rule to MEDGENT-010's
  `_EXTRACTION_PROMPT` to preserve specific claims/statements verbatim in
  `topics_discussed` — confirmed live afterward that a genuinely risky
  note (off-label + AE mention) now gets flagged correctly, and a clean
  note still produces no false positives.
