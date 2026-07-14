# Architecture & Tech Stack (Fixed)

These decisions are settled for the project. Don't introduce alternatives
(a different state library, a different LLM provider, a different ORM,
etc.) without raising it with the user first.

## Stack

| Layer            | Choice                                                        |
|------------------|----------------------------------------------------------------|
| Frontend         | React (Vite) + Redux Toolkit                                   |
| Frontend font    | Google Inter                                                    |
| Backend          | Python + FastAPI                                                |
| AI agent runtime | LangGraph                                                       |
| LLM provider     | Groq — `gemma2-9b-it` (default/fast), `llama-3.3-70b-versatile` (heavier extraction/summarization, config-selectable) |
| Database         | PostgreSQL (SQLAlchemy 2.0 + Alembic migrations)                |
| Containerization | Docker + Docker Compose (monorepo, single compose file at root)|

## Monorepo layout

```
medAgent-crm/
├── frontend/              # React + Redux app
│   ├── src/
│   └── ...
├── backend/                # FastAPI app + LangGraph agent
│   ├── app/
│   │   ├── api/            # FastAPI routers
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── agent/          # LangGraph graph + tools
│   │   └── core/           # config, db session, logging
│   └── alembic/
├── docker/                  # extra Dockerfiles / compose overrides
├── docker-compose.yml
├── specs/
├── steering/
└── CLAUDE.md
```

Exact directory names are finalized in MEDGENT-001; this is the intended
shape all later specs should conform to.

## Identity

This build has no authentication system. It's a single-rep demo project
built against a time-boxed assignment (see `CLAUDE.md`,
`docs/med-agent-crm.pdf`) — a real login/session/auth spec is explicitly
out of scope. MEDGENT-005 establishes a `get_current_rep` dependency that
resolves to one hardcoded, seeded demo rep. Don't reintroduce header
tokens, JWTs, or a login flow unless the user asks for a new spec.

## LLM usage pattern

- Groq API key is read from an environment variable (`GROQ_API_KEY`), never
  hardcoded.
- Model name is also environment/config-driven (`GROQ_MODEL_DEFAULT`,
  `GROQ_MODEL_HEAVY`) so swapping models doesn't require a code change.
- `gemma2-9b-it` is the default for latency-sensitive conversational turns;
  `llama-3.3-70b-versatile` is reserved for steps that need stronger
  reasoning (e.g. structured entity extraction from a long free-form note,
  compliance flagging) and is invoked explicitly by the tool that needs it.

## LangGraph agent contract

- The agent is a single LangGraph state graph per conversation session,
  keyed by rep + HCP + in-progress interaction (if any).
- Every tool is a plain function with:
  - a Pydantic input model (what the agent must supply),
  - a Pydantic output model (what comes back into agent state),
  - no hidden global state or side effects beyond its declared DB writes.
- Tool routing/decisioning is the graph's job, not embedded ad hoc in
  individual tools.
- See [[EPIC-03-ai-agent]] and its child specs for the concrete tool list.

## API conventions

- REST endpoints under `/api/v1/...`, versioned from the start.
- Resource-oriented routes (`/api/v1/hcps`, `/api/v1/interactions`), not
  RPC-style action endpoints, except for the agent's conversational endpoint
  which is inherently action-shaped (e.g. `/api/v1/agent/chat`).
- New endpoints are documented in the owning spec's technical details
  before/while being implemented, so the spec stays the source of truth for
  the contract.

## Docker Compose services (target shape)

- `postgres` — database
- `backend` — FastAPI app (includes the LangGraph agent, same process)
- `frontend` — Vite dev server in development; static build served
  separately in a prod-style compose profile
- Additional services (e.g. `adminer` for DB inspection) may be added by a
  spec but should stay optional/dev-profile only.
