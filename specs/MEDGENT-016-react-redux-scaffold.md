# MEDGENT-016: React + Redux app scaffold

**Status:** To Do
**Priority:** MVP — required for the 36-hour submission
**Epic:** [EPIC-04: Frontend Core](epics/EPIC-04-frontend-core.md)
**Branch:** `MEDGENT-016-react-redux-scaffold`
**Depends on:** MEDGENT-001

## User story

As a developer, I want the Redux store, routing, and design tokens (Inter
font, base theme) wired into the placeholder frontend from MEDGENT-001, so
that later screens are built inside a consistent shell instead of ad hoc.

## Context

MEDGENT-001 created a bare Vite/React/TS app. This spec adds the Redux
Toolkit store, React Router, and the Inter font/design-token setup that the
whole app will use — no product screens yet, just the shell.

## Acceptance criteria

- [ ] Redux Toolkit store configured (`configureStore`) with a `store.ts`
      and typed hooks (`useAppDispatch`, `useAppSelector`).
- [ ] React Router set up with at least a placeholder home route and a
      not-found route.
- [ ] Google Inter loaded once at the app root (self-hosted `@font-face` or
      Google Fonts link — pick one and document it) and set as the default
      font in a base stylesheet/theme.
- [ ] A minimal design-tokens file (colors, spacing, font sizes) exists so
      later screens don't hardcode raw values inline.
- [ ] ESLint/Prettier from MEDGENT-001 still pass clean.
- [ ] A render test confirms the app shell mounts without error.

## Technical details

- Prefer CSS variables or a small `theme.ts` module for tokens — don't pull
  in a full component library (MUI, Chakra, etc.) unless the user
  explicitly asks for one; keep this lightweight per the fixed stack in
  `steering/04-architecture-tech-stack.md`.
- No API calls yet — that's MEDGENT-017.
- No real screen content yet — the app's single route is the Log
  Interaction Screen (EPIC-05); there is no separate navigation shell or
  HCP list page in this build (the HCP picker lives inline on that screen,
  matching the reference mockup in `docs/med-agent-crm.pdf`).
