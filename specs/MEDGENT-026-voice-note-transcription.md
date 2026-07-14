# MEDGENT-026: Voice note capture & summarization (stretch)

**Status:** To Do
**Priority:** Stretch — only after the full MVP path (through MEDGENT-025)
is done and the submission is otherwise ready; not required for
submission.
**Epic:** [EPIC-05: Log Interaction Screen](epics/EPIC-05-log-interaction-screen.md)
**Branch:** `MEDGENT-026-voice-note-transcription`
**Depends on:** MEDGENT-009, MEDGENT-019

## User story

As a pharma sales rep, I want to record a quick voice note right after a
meeting and have it transcribed and summarized straight into the Topics
Discussed field, so that I can log an interaction without typing at all.

## Context

The reference mockup (`docs/med-agent-crm.pdf`) shows a "Summarize from
Voice Note (Requires Consent)" button on the Topics Discussed field.
MEDGENT-019 renders that button as present-but-inert; this spec is what
would make it real. It's explicitly a stretch goal — the assignment's
required deliverable is the form + chat logging flows and the five agent
tools, not audio capture, so this should only be picked up if the MVP path
is fully done with time to spare.

## Acceptance criteria

- [ ] A record/upload control on the Topics Discussed field captures a
      short audio clip, with an explicit consent confirmation step before
      recording starts (the mockup's "(Requires Consent)" label is not
      decorative — treat it as a real requirement).
- [ ] Audio is transcribed via Groq's Whisper-family speech-to-text model.
- [ ] The transcript is summarized (via the existing Groq LLM integration
      from MEDGENT-009) into the Topics Discussed field, editable by the
      rep before saving like any other field.
- [ ] Raw audio is not persisted beyond the transcription step unless the
      user explicitly asks for that — treat recorded audio of a real
      conversation as sensitive by default.
- [ ] Tests: transcription + summarization pipeline with both the STT and
      LLM calls mocked.

## Technical details

- New tool or a direct backend endpoint (`POST /api/v1/interactions/
  transcribe-voice-note`) — a dedicated LangGraph tool isn't necessary
  here since this isn't a conversational capability, it's a one-shot
  transform feeding into the form.
- Confirm Groq's available Whisper model name/id before implementing
  (check https://console.groq.com/docs/models rather than assuming).
- Keep this fully isolated from the five required LangGraph tools — it
  must not become a dependency of MEDGENT-010 through MEDGENT-015.
