# MEDGENT-019: Structured form panel for Log Interaction

**Status:** To Do
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-05: Log Interaction Screen](epics/EPIC-05-log-interaction-screen.md)
**Branch:** `MEDGENT-019-structured-form-ui`
**Depends on:** MEDGENT-017

## User story

As a pharma sales rep who prefers structured data entry, I want a form to
log an HCP interaction — with all the fields shown in the reference
design — so that I can log quickly and precisely when I already know
exactly what I want to record, without needing to talk to the AI at all.

## Context

This is the **left panel** of the single "Log HCP Interaction" screen
(EPIC-05). Per the reference mockup in `docs/med-agent-crm.pdf`, the form
and the AI Assistant chat (MEDGENT-020) are not alternate modes toggled
between — they sit side by side on the same screen at the same time, and
the AI panel writes into this same form's fields as it extracts data from
conversation. This spec builds the form panel itself, including the HCP
picker; MEDGENT-021 wires it together with the chat panel's output.

## Acceptance criteria

Field list is taken directly from the mockup, in this order:

- [ ] **HCP Name** — "Search or select HCP..." typeahead against
      `GET /api/v1/hcps` (MEDGENT-006/017). This is the app's only HCP
      picker — there is no separate HCP list/nav screen in this build.
- [ ] **Interaction Type** — dropdown (Meeting, Call, Email, Conference,
      etc.).
- [ ] **Date** and **Time** — combined into `occurred_at` on submit.
- [ ] **Attendees** — free multi-value text input (names).
- [ ] **Topics Discussed** — multi-line text area, with a **"Summarize
      from Voice Note (Requires Consent)"** button. That button's actual
      recording/transcription behavior is out of scope for this spec (see
      the optional MEDGENT-026 stretch spec) — render it as present but
      disabled/"coming soon" if MEDGENT-026 isn't built yet, don't fake the
      functionality.
- [ ] **Materials Shared** — add/search multi-value list, distinct from
      Samples Distributed.
- [ ] **Samples Distributed** — add multi-value list, distinct from
      Materials Shared.
- [ ] **Observed/Inferred HCP Sentiment** — Positive / Neutral / Negative
      radio group.
- [ ] **Outcomes** — multi-line text area.
- [ ] **Follow-up Actions** — multi-line text area for free-text notes,
      plus a rendering slot for **AI Suggested Follow-ups** (populated by
      MEDGENT-021 from the chat panel's output — this spec just needs to
      render the slot and accept a list of suggestion strings as a prop).
- [ ] Client-side validation matches backend validation (HCP required,
      valid interaction type, valid sentiment value) with inline error
      messages.
- [ ] Submitting calls the Interaction create endpoint via MEDGENT-017's
      RTK Query mutation with `source: "form"`.
- [ ] Success state confirms the save; failure state (network/validation
      error) preserves the rep's entered data.
- [ ] Render/interaction tests: successful submit, validation error,
      network error, HCP typeahead selection.

## Technical details

- Form component under `frontend/src/features/logInteraction/FormPanel.tsx`
  (or similar), consuming design tokens/Inter font from MEDGENT-016.
- Use a lightweight form approach (controlled components + a small
  validation helper, or `react-hook-form` if it meaningfully reduces
  boilerplate) — don't introduce a full form framework beyond what's
  needed.
- Field naming in the form state should mirror MEDGENT-007's API schema
  directly (`interaction_type`, `attendees`, `topics_discussed`,
  `materials_shared`, `samples_distributed`, `sentiment`, `outcomes`,
  `follow_up_notes`) so MEDGENT-021's sync logic isn't translating between
  two different shapes.
- This spec owns the form panel's own submit action (direct form → API,
  bypassing the agent entirely) — the *shared* review/confirmation UX
  between this panel and the chat panel's extracted data is MEDGENT-021.
