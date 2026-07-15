# EPIC-04: Frontend Core

**Status:** Done

## Goal

Stand up the React + Redux application shell — build tooling, design tokens
(Inter font), Redux store, and a typed API client — that the Log
Interaction Screen is built inside of. There is no separate navigation
shell or HCP list page in this build: the app has one route (the Log
Interaction Screen itself), with HCP search/select handled inline on that
screen per the reference mockup (`docs/med-agent-crm.pdf`).

## Specs in this epic

| Spec | Title | Status |
|------|-------|--------|
| [MEDGENT-016](../MEDGENT-016-react-redux-scaffold.md) | React + Redux app scaffold | Done |
| [MEDGENT-017](../MEDGENT-017-api-client-redux-slices.md) | API client & Redux slices for HCP/Interaction | Done |

## Notes

Depends on EPIC-01. Can proceed in parallel with EPIC-02, except
MEDGENT-017 which needs the HCP/Interaction API contracts from EPIC-02 to
be defined (MEDGENT-006, MEDGENT-007).
