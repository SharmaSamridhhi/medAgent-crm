# MEDGENT-022: Edit Interaction flow

**Status:** Done
**Priority:** MVP — required for the 36-hour submission (this is the UI
surface for the assignment's second mandatory tool, Edit Interaction).
**Epic:** [EPIC-05: Log Interaction Screen](epics/EPIC-05-log-interaction-screen.md)
**Branch:** `MEDGENT-022-edit-interaction-flow`
**Depends on:** MEDGENT-011, MEDGENT-021

## User story

As a pharma sales rep, I want to find a previously logged interaction and
correct it — either by editing fields directly or by telling the agent
what changed — so that mistakes are easy to fix regardless of how the
interaction was originally logged.

## Context

MEDGENT-011 built the agent-side edit tool; MEDGENT-021 wired the form and
chat panels together for a fresh, not-yet-saved draft. This spec delivers
the surface for editing an *already-saved* interaction. There is no
separate HCP history page in this build (see EPIC-04) — the entry point
into this flow lives directly on the same Log Interaction Screen.

## Acceptance criteria

- [x] Once an HCP is selected in the form panel (MEDGENT-019), a minimal
      "recent interactions for this HCP" list appears inline on the same
      screen (using MEDGENT-012's history data), each with an "Edit"
      action.
- [x] Opening one loads that interaction into the same shared draft state
      MEDGENT-021 established, pre-filling the form panel.
- [x] The opened interaction can be edited two ways: directly via the form
      panel, or conversationally via the chat panel scoped to the
      `edit_interaction` tool (MEDGENT-011) with this interaction's id
      already in context.
- [x] Both edit paths call through to `PATCH /api/v1/interactions/{id}`
      (directly for the form path, via the agent tool for the chat path)
      and show a clear before/after confirmation.
- [x] Compliance re-flagging: if edited notes change materially, the
      compliance tool (MEDGENT-014) re-runs against the updated text.
- [x] Render/interaction tests: direct form edit, conversational edit,
      before/after confirmation display, re-flagging on edit.

## Technical details

- Reuses MEDGENT-019's `FormPanel` and MEDGENT-020's `ChatPanel` in "edit
  mode" (pre-filled / pre-scoped to an existing interaction id) rather than
  building parallel components — this is the payoff for keeping those
  panels clean and composable in the earlier specs.
- The "recent interactions" list only needs to be as complete as this flow
  requires — don't build a full interaction-history page beyond what's
  needed to reach edit; a simple list under/beside the HCP picker is
  enough, and it directly demonstrates the Edit Interaction tool for the
  submission video.

**Implementation notes (as built):**
- The "recent interactions" list reuses MEDGENT-017's existing
  `GET /api/v1/interactions?hcp_id=...` RTK Query endpoint directly
  (`RecentInteractionsList.tsx`) rather than going through the agent's
  `retrieve_hcp_history` tool — same underlying data MEDGENT-012 exposes,
  simpler path for a plain list-and-edit UI.
- Conversational edit context is passed the same in-band way MEDGENT-020
  established for the active HCP: `useAgentChat` now accepts a
  `{ hcp, interactionId }` context object and prefixes the *outgoing*
  first-turn message with both when present, e.g. `[Context: HCP "..." is
  selected in the form; the rep is editing an already-logged interaction
  with id ....]` — the displayed transcript stays clean.
- **Compliance re-flagging required one small, necessarily cross-epic
  backend change.** Neither the direct `PATCH /api/v1/interactions/{id}`
  endpoint nor the `edit_interaction` agent tool (MEDGENT-011) re-ran
  compliance screening on an edit — only `log_interaction`'s own
  post-create flagging existed. Both edit paths already call through the
  exact same `update_interaction()` function in
  `backend/app/api/v1/interactions.py` (`edit_interaction.py` imports and
  calls it directly), so the re-screening was added there, once: if an
  update touches `topics_discussed` or `outcomes` and doesn't itself set
  `compliance_flags` explicitly, `flag_compliance_risks` re-runs against
  the interaction's current combined text and the result is persisted.
  This automatically covers both edit paths from one change. Added two
  backend tests (`test_update_interaction_re_screens_compliance_on_note_edit`,
  `test_update_interaction_without_note_changes_skips_compliance_check`)
  and mocked the new dependency in the existing tests that touch
  `update_interaction` with real `outcomes`/`topics_discussed` changes, so
  no test hits the real Groq API.
- Before/after confirmation is rendered by one shared component
  (`FieldChangesList.tsx`) used by both the form panel's own post-save
  banner and the chat panel's `edit_interaction` side-effect card, so the
  two edit paths render identically as required.
- Verified live end-to-end against the real backend (Groq + Postgres via
  `docker compose up`): chat extraction → form sync, direct-edit
  before/after confirmation, and HCP/materials extraction all confirmed
  working against the actual agent, not just mocked tests.
