# medAgent-CRM

AI-first CRM HCP (Healthcare Professional) module for a pharmaceutical
sales representative. Core deliverable is the **Log Interaction Screen**:
a single screen with a structured form panel and an AI Assistant
(LangGraph) chat panel side by side, backed by a shared FastAPI + Postgres
backend.

See `specs/README.md` for the full spec index and build order, and
`steering/` for the project's development rules.

## Running locally with Docker (recommended)

```bash
cp .env.example .env
docker compose up
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000/health`
- Postgres: `localhost:5432` (credentials from `.env`)

Source is bind-mounted into both the `backend` and `frontend` containers,
so edits on your host hot-reload inside the containers. `docker compose
down` stops everything; add `-v` to also drop the Postgres volume.

## Running locally without Docker

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/health` — should return `{"status": "ok"}`.

Lint/type-check:

```bash
ruff check .
ruff format --check .
mypy app tests
pytest
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`.

Lint/format:

```bash
npm run lint
npm run format:check
```
