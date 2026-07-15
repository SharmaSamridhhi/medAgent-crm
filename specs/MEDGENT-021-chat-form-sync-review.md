# MEDGENT-021: Chat-to-form sync & save/confirmation UX

**Status:** Done
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-05: Log Interaction Screen](epics/EPIC-05-log-interaction-screen.md)
**Branch:** `MEDGENT-021-chat-form-sync-review`
**Depends on:** MEDGENT-019, MEDGENT-020

## User story

As a pharma sales rep, I want the AI Assistant panel and the form panel to
work together on the same interaction — whatever the AI extracts from my
conversation shows up in the form fields where I can see and correct it —
so that I always know exactly what's about to be saved, however I entered
it.

## Context

MEDGENT-019 and MEDGENT-020 built the two panels independently. This spec
is what actually makes the "Log HCP Interaction" screen from
`docs/med-agent-crm.pdf` work as one screen: the two panels share state,
not just layout. There is no mode toggle in the reference design — form
and chat are visible and usable simultaneously, side by side.

## Acceptance criteria

- [x] The Log Interaction Screen (the app's single route, per EPIC-04's
      scope) renders MEDGENT-019's form panel on the left and MEDGENT-020's
      chat panel on the right simultaneously, matching the mockup layout.
- [x] When the chat panel's `log_interaction` call (MEDGENT-010) returns
      extracted fields, those fields populate the form panel's fields
      (not a separate preview surface) so the rep sees exactly what will
      be saved and can edit any field before it's final.
- [x] Selecting an HCP in the form panel's picker is reflected as context
      for the chat panel (and vice versa: if the chat resolves/creates HCP
      context, the form panel's HCP field updates to match) — the two
      panels share one underlying "current interaction draft" state, not
      two independent ones.
- [x] A single, explicit save action commits the current draft (whichever
      panel most recently touched it) via the Interaction API, with the
      correct `source` (`form` if the rep never used chat this session,
      `chat` if the AI extraction produced the fields currently saved,
      even if the rep tweaked them afterward in the form).
- [x] Suggested follow-ups from MEDGENT-010's output render as clickable
      chips (per the mockup) in the follow-up actions area; clicking one
      calls MEDGENT-013's `schedule_follow_up`.
- [x] Compliance flags (MEDGENT-014) are shown identically regardless of
      which panel most recently touched the draft.
- [x] Render/interaction tests: chat extraction populates form fields,
      rep edits a chat-populated field before saving, HCP selection syncs
      both directions, suggested-follow-up chip creates a real follow-up,
      flags render consistently.

## Technical details

- Shared draft state lives in a Redux slice (`logInteractionDraftSlice` or
  similar) that both `FormPanel` and `ChatPanel` read/write — this is the
  actual integration point; resist making one panel own the state and the
  other just "an event emitter" into it, since the mockup implies genuine
  two-way sync (edit in form after AI fills it, or vice versa).
- This spec is primarily composition and state-sync glue — most of the
  heavy lifting already exists in MEDGENT-019/020; resist rebuilding
  either panel's internals here.
- Document here (once implemented) exactly when the save actually commits
  to the backend: on every chat extraction (auto-save with edit-after) or
  only on an explicit rep action (a "Log Interaction" button reflecting the
  mockup's `⚠ Log` button on the chat panel, or a save action on the form
  panel). Whichever is chosen, MEDGENT-022 needs to know so its edit flow
  matches.

**Implementation note (as built):** `log_interaction` (MEDGENT-010) already
writes to the database itself as soon as the LLM calls it — that's
existing MEDGENT-010/015 behavior, not something this spec could defer.
So the actual save model is a hybrid:
- **Chat path:** auto-save on extraction. The moment `log_interaction`
  returns `status: "created"`, the interaction already exists server-side
  (`interaction_id` is real). The shared Redux slice
  (`logInteractionDraftSlice`) records that id and sets `source: "chat"`.
- **Form-panel button is the single explicit save action for edits.**
  `FormPanel`'s existing submit button (labelled "Log Interaction" for a
  fresh draft, "Save Changes" once an `interactionId` exists) is the one
  control that ever calls the Interaction API directly. If
  `interactionId` is set (chat already created the row), clicking it
  issues a `PATCH` against that same interaction — so a rep edit after a
  chat extraction updates the existing record rather than creating a
  duplicate, and `source` stays `"chat"` (untouched by the `PATCH`, whose
  body omits `source` entirely). If no chat extraction happened yet,
  clicking it `POST`s a new interaction with `source: "form"`.
- **The chat panel's own "⚠ Log" button** is just the composer's send
  action (per MEDGENT-020) — it always goes through the conversational
  `log_interaction`/`edit_interaction` tools, which persist on their own.
  There's no second, separate "commit" step on the chat side.
- After a successful form-panel save, the shared draft resets to a fresh,
  empty interaction (`draftReset`) so the rep can start the next one.
