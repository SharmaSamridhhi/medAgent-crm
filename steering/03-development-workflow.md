# Development Workflow (Strict)

## Picking up a spec

1. Read `specs/README.md` to find the next spec whose `Depends on` list is
   fully `Done` and merged to `main`.
2. Check that spec's `Priority` field. This project is time-boxed against
   a real deadline (see `CLAUDE.md` and `docs/med-agent-crm.pdf`): **every
   `Priority: MVP` spec must be `Done` before any `Priority: Stretch` spec
   is started**, regardless of what looks interesting or what a
   dependency graph would otherwise allow. If asked to work on a Stretch
   spec while MVP specs remain, say so and confirm before proceeding.
3. Read the spec file fully (user story, context, acceptance criteria,
   technical details).
4. `git pull origin main`, then branch per [[01-git-workflow]].
5. Edit the spec's `Status` to `In Progress` as your first change.
6. Implement against the acceptance criteria only — resist adding anything
   the spec doesn't ask for (see the project's general scope discipline).

## Definition of Ready

A spec may move to `In Progress` only when every spec listed in its
`Depends on` field is `Status: Done` on `main`, **and** — per the MVP/
Stretch rule above — it isn't a Stretch spec while MVP work remains. If a
dependency is still `In Progress` or `To Do`, stop and tell the user
instead of starting anyway or "temporarily" stubbing the dependency.

## Definition of Done

All of the following before a spec's `Status` becomes `Done`:

- Every acceptance criterion in the spec is met.
- Lint, type-check, and tests pass per [[02-code-quality]].
- No secrets, debug prints, or commented-out code left in the diff.
- The spec file's `Status` is updated to `Done`.
- The matching row in `specs/README.md` is updated to `Done`.
- Changes are staged (`git add`) but **not committed** — see
  [[01-git-workflow]].

## Local dev loop

- Once [[EPIC-01-foundation]] lands, bring up the stack with
  `docker compose up`. Postgres, backend, and frontend run as services;
  don't install/run Postgres natively on the host.
- Any new environment variable a spec introduces must be added to
  `.env.example` in the same branch.
- Alembic migrations are generated and reviewed locally
  (`alembic revision --autogenerate`) and committed as part of the spec
  branch — never applied ad hoc against a shared database.

## Sequencing across epics

Rough build order (exact gating is always the `Depends on` field, this is
just the intended shape):

1. **Foundation** (monorepo, Docker, DB schema, CI) unblocks everything else.
2. **Backend Core** and **Frontend Core** can proceed in parallel once
   Foundation is done.
3. **AI Agent & Tools** needs Backend Core's data models to persist against.
4. **Log Interaction Screen** needs both the AI Agent (for the chat path)
   and Frontend Core (for the shell/state).
5. **Quality & Deployment** specs are written to run throughout, but are
   formalized/finished last.

## Ending a work session on a spec

When a spec reaches `Done`:

- Summarize what changed and which files were touched.
- Remind the user of their steps: review the staged diff, commit (suggested
  message format in [[01-git-workflow]]), push, open a PR against `main`,
  merge, then tell you it's merged.
- Offer the two continuation options: keep going on the next ready spec in
  this same session, or start a new session for it — recommend based on how
  large this session's context has already grown.

## Handling scope changes and new specs mid-session

- If the user pivots requirements mid-spec, update the spec's acceptance
  criteria / technical details in place rather than leaving stale text and
  bolting on new criteria.
- If you discover a gap that deserves its own spec, propose the new
  `MEDGENT-XXX` to the user (title, user story, rough acceptance criteria,
  dependencies) before adding it to `specs/` — don't silently expand the
  backlog.
