# MEDGENT-022: Edit Interaction flow

**Status:** To Do
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

- [ ] Once an HCP is selected in the form panel (MEDGENT-019), a minimal
      "recent interactions for this HCP" list appears inline on the same
      screen (using MEDGENT-012's history data), each with an "Edit"
      action.
- [ ] Opening one loads that interaction into the same shared draft state
      MEDGENT-021 established, pre-filling the form panel.
- [ ] The opened interaction can be edited two ways: directly via the form
      panel, or conversationally via the chat panel scoped to the
      `edit_interaction` tool (MEDGENT-011) with this interaction's id
      already in context.
- [ ] Both edit paths call through to `PATCH /api/v1/interactions/{id}`
      (directly for the form path, via the agent tool for the chat path)
      and show a clear before/after confirmation.
- [ ] Compliance re-flagging: if edited notes change materially, the
      compliance tool (MEDGENT-014) re-runs against the updated text.
- [ ] Render/interaction tests: direct form edit, conversational edit,
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
