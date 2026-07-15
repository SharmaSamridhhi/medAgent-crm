# MEDGENT-027: HCP admin screen (list + create)

**Status:** Done
**Priority:** Dev tooling — not part of the graded deliverable; built out of
normal MVP/Stretch order at the user's explicit request to unblock manual
testing before EPIC-06.
**Epic:** [EPIC-07: HCP Admin Tooling](epics/EPIC-07-hcp-admin-tooling.md)
**Branch:** bundled into `EPIC-05-log-interaction-screen` (not a fresh
`main`-based branch — this exists to test EPIC-05's not-yet-merged work,
so it needs to live alongside it; see the epic file's note)
**Depends on:** MEDGENT-017

## User story

As whoever is manually testing the Log Interaction Screen, I want a simple
screen to see which HCPs already exist and add new ones, so that I don't
have to `curl` the backend just to get a name into the HCP picker.

## Context

`hcpsApi` (MEDGENT-017) already has `listHcps` and `createHcp` RTK Query
endpoints wired up; nothing backend-side is missing. This is purely a
small new frontend route and two components on top of what already
exists.

## Acceptance criteria

- [x] A new route (`/hcps`) renders a table of existing HCPs (name,
      specialty, institution, contact info, active status), backed by
      `useListHcpsQuery`.
- [x] A search box filters the table by name (reuses the `search` query
      param `listHcps` already supports).
- [x] A create form (name required; specialty, institution, contact info
      optional) adds a new HCP via `useCreateHcpMutation` and the new row
      appears in the table without a manual refresh (cache invalidation
      already exists in `hcpsApi`).
- [x] A small link between this screen and the Log Interaction Screen
      (`/`) so both are reachable without typing the URL by hand.
- [x] Render/interaction tests: table renders existing HCPs, search
      filters the list, creating an HCP adds it to the table.

## Technical details

- Component(s) under `frontend/src/features/hcpAdmin/` (e.g.
  `HcpAdminPage.tsx`), added as a second entry in `frontend/src/app/router.tsx`.
- List-only + create — no edit/delete UI. `hcpsApi` already exposes
  `updateHcp`/`deleteHcp` if that's wanted later; out of scope for this
  spec unless asked.
- No design-system work beyond reusing the existing tokens from
  MEDGENT-016 (`theme.css`) — this is a utility screen, not part of the
  mockup.

**Verified live** against the real backend (`docker compose up`): created
an HCP through the form, confirmed it appeared in the table immediately
(no manual refresh), and confirmed the search box filters correctly.
