# EPIC-07: HCP Admin Tooling

**Status:** Done

## Goal

A minimal in-app screen to create and browse HCPs directly against the
existing `hcpsApi` (MEDGENT-017), so manual testing of the Log Interaction
Screen doesn't require `curl`-ing the backend to seed data.

## Why this exists / how it relates to EPIC-04 and EPIC-05

EPIC-04's scope note says: "There is no separate navigation shell or HCP
list page in this build: the app has one route (the Log Interaction
Screen itself), with HCP search/select handled inline on that screen per
the reference mockup." That's still true for the **graded deliverable** —
the mockup in `docs/med-agent-crm.pdf` has no HCP admin surface, and nothing
here changes the Log Interaction Screen itself.

This epic exists purely as developer/tester tooling, added out of the
normal MVP-before-Stretch order at the user's explicit request (see
session history) to unblock manual testing of MEDGENT-021/022 before
EPIC-06's smoke tests and docs. It is not part of the assignment's
required deliverable and doesn't need to be demoed in the submission
video, though it doesn't hurt if it is.

## Specs in this epic

| Spec | Title | Status |
|------|-------|--------|
| [MEDGENT-027](../MEDGENT-027-hcp-admin-screen.md) | HCP admin screen (list + create) | Done |

## Notes

Depends on EPIC-04 (`hcpsApi`'s `listHcps`/`createHcp` endpoints,
MEDGENT-017) — already `Done` and merged to `main`.

**Branching exception:** normally every spec branches fresh from `main`
(`steering/01-git-workflow.md`). This one doesn't — `EPIC-05` (the Log
Interaction Screen) is finished but not yet merged, and the entire point
of this tool is to make manual testing of *that* work easier. Branching
from `main` would put the admin screen on a branch that can't see
EPIC-05's screen at all, defeating the purpose. So MEDGENT-027 is
implemented as an additional commit on the existing
`EPIC-05-log-interaction-screen` branch instead. Once both are reviewed
together and merged, this is a one-off; it doesn't change how future
epics branch.
