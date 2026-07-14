# Code Quality Standards (Strict)

## Frontend (React + Redux, `frontend/`)

- TypeScript in strict mode (`strict: true` in `tsconfig.json`). No new `any`
  without a one-line comment explaining why it's unavoidable.
- Redux Toolkit only — no hand-written reducers/action-type constants, no
  legacy `redux` boilerplate, no other state library introduced without the
  user's sign-off.
- Lint with ESLint (`react-hooks`, `react-refresh`, `@typescript-eslint`
  plugins) and format with Prettier. Both must run clean before a spec is
  marked `Done`.
- Naming: `PascalCase` for components and their files, `camelCase` for
  functions/variables/hooks, `useX` prefix for custom hooks, one Redux slice
  per domain feature (e.g. `interactionsSlice`).
- Font: Google Inter is the only body/UI font. Load it once at the app shell
  level (see [[04-architecture-tech-stack]]) — do not re-import fonts per
  component.

## Backend (FastAPI + LangGraph, `backend/`)

- Python 3.11+. Use Ruff for both linting and formatting (`ruff check`,
  `ruff format`) — no separate Black/isort/Flake8 config.
- Type hints are mandatory on every function signature (params + return).
  Run mypy on `backend/` and fix new errors before marking a spec `Done`;
  don't silence with blanket `# type: ignore`.
- All request/response payloads are Pydantic v2 models — no raw dicts across
  API boundaries.
- Schema changes only via Alembic migrations, generated and committed to
  `backend/alembic/versions/` — never a manual `ALTER TABLE` against a shared
  database.
- LangGraph tools are pure, typed functions: a Pydantic input model, a
  Pydantic output model, no hidden global state. See
  [[04-architecture-tech-stack]] for the tool contract shape.

## Testing minimums (both sides)

- Every new API endpoint: at least one happy-path test and one failure-path
  test (validation error, not-found, etc.).
- Every new LangGraph tool: a unit test with the LLM call mocked — never hit
  the real Groq API in automated tests.
- Every new Redux slice: reducer/selector tests for its core actions.
- Every new screen/critical component (especially anything under the Log
  Interaction Screen epic): at least a render/interaction test.
- A spec is not `Done` if it introduces failing or skipped tests.

## Secrets and configuration

- The Groq API key, database credentials, and any other secret live only in
  environment variables, never in source code, fixtures, or test files.
- `.env` is git-ignored. `.env.example` must be kept up to date with every
  new environment variable a spec introduces (name + placeholder value +
  one-line comment), so the next person can `cp .env.example .env`.
- Never log secrets, even at debug level.

## General hygiene

- No commented-out code left behind.
- No `TODO` without a linked spec key (`# TODO(MEDGENT-014): ...`) — an
  unlinked TODO is scope that isn't tracked anywhere.
- Comments explain non-obvious *why*, never restate the *what*. Prefer
  clear naming over comments.
- Don't introduce a new library, framework, or architectural pattern beyond
  what a spec's technical details call for without flagging it to the user
  first.
