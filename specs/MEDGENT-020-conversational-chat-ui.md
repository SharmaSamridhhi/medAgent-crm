# MEDGENT-020: AI Assistant chat panel for Log Interaction

**Status:** To Do
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-05: Log Interaction Screen](epics/EPIC-05-log-interaction-screen.md)
**Branch:** `MEDGENT-020-conversational-chat-ui`
**Depends on:** MEDGENT-015, MEDGENT-017

## User story

As a pharma sales rep, I want to log an interaction by just describing it
in natural language in a chat panel next to the form, so that logging is as
quick as typing what happened, while still seeing (and being able to
correct) the structured result before it's final.

## Context

This is the **right panel** of the single "Log HCP Interaction" screen, per
the reference mockup in `docs/med-agent-crm.pdf`: labeled "AI Assistant —
Log interaction via chat", with a message area, an input box ("Describe
interaction...") and a "Log" action button. It talks to the agent's chat
endpoint (MEDGENT-015), not the CRUD API directly. This spec builds the
panel itself; MEDGENT-021 wires its output into the form panel
(MEDGENT-019) sitting beside it.

## Acceptance criteria

- [ ] Chat UI: message list (rep + agent turns), input box, send/"Log"
      action — matching the mockup's layout (chat above, input + Log
      button pinned at the bottom of the panel).
- [ ] The currently-selected HCP (from MEDGENT-019's picker, if one is
      selected) is passed along as context so the rep doesn't have to
      restate who they're talking about; if no HCP is selected yet, the
      agent can resolve one from the rep's message instead (per
      MEDGENT-010).
- [ ] Calls `POST /api/v1/agent/chat` (MEDGENT-015) and renders the agent's
      reply, including structured side effects it returns: extracted
      fields (handed to MEDGENT-021 to populate the form panel), suggested
      follow-ups (rendered as the mockup's clickable chips), and any
      compliance flags from MEDGENT-014 (shown distinctly, e.g. a
      warning-styled inline note).
- [ ] Conversation/session id is preserved across turns within the screen
      so multi-turn flows (clarification questions from MEDGENT-010/011)
      work.
- [ ] Loading state while awaiting the agent's response (typing indicator
      or similar).
- [ ] Error state if the agent call fails, without losing the rep's typed
      message.
- [ ] Render/interaction tests: send message → see reply + form-panel
      side effect, clarification round-trip, suggested-follow-up chip
      click, error state.

## Technical details

- Component under `frontend/src/features/logInteraction/ChatPanel.tsx`,
  sitting alongside MEDGENT-019's `FormPanel` inside the same screen
  component (wired together in MEDGENT-021).
- If MEDGENT-015 implements streaming responses, this UI should stream the
  reply incrementally; if not, a simple request/response render is fine —
  match whatever MEDGENT-015 actually shipped rather than assuming.
- Structured side effects (extracted fields, suggested follow-ups,
  compliance flags) should be visually distinct from plain conversational
  text so the rep can scan a long chat and immediately spot what was
  actually recorded — this is also what will read clearly in the demo
  video.
- This panel does not itself decide when data is "final" — whether the
  chat's extraction pre-fills the form for review before saving, or saves
  immediately with an editable confirmation, is MEDGENT-021's call to make
  and document.
