# MEDGENT-023: Critical-path smoke tests

**Status:** To Do
**Priority:** MVP — required for the 36-hour submission, but deliberately
small: a confidence check before recording the demo video, not a coverage
initiative.
**Epic:** [EPIC-06: Quality, Docs & Deployment](epics/EPIC-06-quality-deployment.md)
**Branch:** `MEDGENT-023-automated-test-suites`
**Depends on:** MEDGENT-021, MEDGENT-022

## User story

As a developer about to record the submission demo video, I want a quick
end-to-end check that the two logging paths and all five agent tools
actually work together, so I'm not discovering a broken integration while
the camera is rolling.

## Context

Every prior spec already added its own unit tests per the minimums in
`steering/02-code-quality.md` (one happy-path + one failure-path per
endpoint/tool). Given the 36-hour time-box, this spec is intentionally
**not** a full test-suite build-out — it's a short, targeted integration
pass covering the seams between specs that no single spec owned, run right
before the demo video.

## Acceptance criteria

- [ ] One backend integration test: log an interaction via the API
      directly (form path) and confirm the row is shaped correctly.
- [ ] One agent integration test: a single conversation that exercises all
      five tools in sequence (log → edit → retrieve history → schedule a
      follow-up → confirm a compliance flag fires on a deliberately risky
      note), LLM mocked.
- [ ] One frontend integration test: the Log Interaction Screen end to end
      in chat mode (extraction populates the form, rep saves) per
      MEDGENT-021.
- [ ] Any bug found while writing these is fixed here and called out
      clearly in the handoff summary, since it wasn't originally scoped as
      a bug-fix spec.
- [ ] No new test infrastructure introduced — reuse whatever mocking/test
      setup earlier specs already established.

## Technical details

- This is explicitly scoped down from a full test-suite epic given the
  time-box — resist the temptation to build broad coverage here; three
  focused integration tests plus whatever unit tests already exist from
  prior specs is the target, not a rewrite.
- If time allows after MEDGENT-025, deeper coverage can be revisited, but
  it is not part of this spec's acceptance criteria.
