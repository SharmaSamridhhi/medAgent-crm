import uuid
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.agent.tools.retrieve_hcp_history import (
    RetrieveHCPHistoryInput,
    retrieve_hcp_history,
)
from app.core.db import SessionLocal
from app.main import app
from app.models import HCP, Interaction

client = TestClient(app)

_PATCH_TARGET = "app.agent.tools.retrieve_hcp_history.get_default_llm"


@pytest.fixture
def hcp_id() -> Generator[str, None, None]:
    response = client.post("/api/v1/hcps", json={"name": "Dr. Priya Shah"})
    assert response.status_code == 201
    created_id: str = response.json()["id"]

    yield created_id

    with SessionLocal() as db:
        db.execute(
            delete(Interaction).where(Interaction.hcp_id == uuid.UUID(created_id))
        )
        db.execute(delete(HCP).where(HCP.id == uuid.UUID(created_id)))
        db.commit()


def _mock_llm(content: str) -> MagicMock:
    llm = MagicMock()
    llm.invoke.return_value = MagicMock(content=content)
    return llm


def test_retrieve_hcp_history_with_history(hcp_id: str) -> None:
    for occurred_at, topic in [
        ("2026-07-01T10:00:00Z", "Discussed CardioX dosing"),
        ("2026-07-10T10:00:00Z", "Follow-up on trial order"),
    ]:
        response = client.post(
            "/api/v1/interactions",
            json={
                "hcp_id": hcp_id,
                "interaction_type": "Meeting",
                "occurred_at": occurred_at,
                "topics_discussed": topic,
                "sentiment": "positive",
            },
        )
        assert response.status_code == 201

    with patch(_PATCH_TARGET, return_value=_mock_llm("Two positive meetings.")):
        with SessionLocal() as db:
            result = retrieve_hcp_history(
                RetrieveHCPHistoryInput(hcp_id=uuid.UUID(hcp_id)), db
            )

    assert result.status == "found"
    assert result.hcp_name == "Dr. Priya Shah"
    assert len(result.interactions) == 2
    # most recent first
    assert result.interactions[0].topics_discussed == "Follow-up on trial order"
    assert result.summary == "Two positive meetings."


def test_retrieve_hcp_history_no_prior_interactions(hcp_id: str) -> None:
    mock_llm = _mock_llm("should not be called")

    with patch(_PATCH_TARGET, return_value=mock_llm):
        with SessionLocal() as db:
            result = retrieve_hcp_history(
                RetrieveHCPHistoryInput(hcp_id=uuid.UUID(hcp_id)), db
            )

    assert result.status == "found"
    assert result.interactions == []
    assert result.summary == "No prior interactions on file yet."
    mock_llm.invoke.assert_not_called()


def test_retrieve_hcp_history_ambiguous_name(hcp_id: str) -> None:
    second = client.post("/api/v1/hcps", json={"name": "Dr. Priya Kapoor"})
    assert second.status_code == 201
    second_id = second.json()["id"]

    try:
        with SessionLocal() as db:
            result = retrieve_hcp_history(RetrieveHCPHistoryInput(hcp_name="Priya"), db)

        assert result.status == "needs_clarification"
        assert len(result.candidate_hcps) == 2
    finally:
        with SessionLocal() as db:
            db.execute(delete(HCP).where(HCP.id == uuid.UUID(second_id)))
            db.commit()
