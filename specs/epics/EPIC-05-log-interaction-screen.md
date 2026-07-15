# EPIC-05: Log Interaction Screen

**Status:** To Do

## Goal

The core product deliverable and the entire point of the assignment
(`docs/med-agent-crm.pdf`): a single "Log HCP Interaction" screen with a
structured form panel on the left and an AI Assistant chat panel on the
right, running side by side — not toggled between — sharing one draft so
whatever the AI extracts is visible and editable in the same fields a
manual entry would use.

## Specs in this epic

| Spec | Title | Status |
|------|-------|--------|
| [MEDGENT-019](../MEDGENT-019-structured-form-ui.md) | Structured form panel for Log Interaction | Done |
| [MEDGENT-020](../MEDGENT-020-conversational-chat-ui.md) | AI Assistant chat panel for Log Interaction | Done |
| [MEDGENT-021](../MEDGENT-021-chat-form-sync-review.md) | Chat-to-form sync & save/confirmation UX | To Do |
| [MEDGENT-022](../MEDGENT-022-edit-interaction-flow.md) | Edit Interaction screen/flow | To Do |
| [MEDGENT-026](../MEDGENT-026-voice-note-transcription.md) | Voice note capture & summarization *(stretch)* | To Do |

## Notes

Depends on EPIC-03 (chat path needs the agent + tools) and EPIC-04 (needs
the Redux store/API client). This is the epic the whole project exists to
deliver — everything upstream exists to unblock it. Before touching any
spec in this epic, look at the reference mockup in `docs/med-agent-crm.pdf`
— the field list and layout are taken directly from it, not invented.
