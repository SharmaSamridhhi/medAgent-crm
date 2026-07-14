import uuid
from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.db import SessionLocal
from app.main import app
from app.models import HCP, Interaction

client = TestClient(app)


@pytest.fixture
def hcp_id() -> Generator[str, None, None]:
    response = client.post("/api/v1/hcps", json={"name": "Dr. Interaction Fixture"})
    assert response.status_code == 201
    created_id = response.json()["id"]

    yield created_id

    with SessionLocal() as db:
        db.execute(
            delete(Interaction).where(Interaction.hcp_id == uuid.UUID(created_id))
        )
        db.execute(delete(HCP).where(HCP.id == uuid.UUID(created_id)))
        db.commit()


@pytest.fixture
def interaction_factory(hcp_id: str) -> Generator[Any, None, None]:
    created_ids: list[uuid.UUID] = []

    def _create(**overrides: Any) -> dict[str, Any]:
        payload = {
            "hcp_id": hcp_id,
            "interaction_type": "Meeting",
            "occurred_at": "2026-07-14T10:00:00Z",
            **overrides,
        }
        response = client.post("/api/v1/interactions", json=payload)
        assert response.status_code == 201
        data: dict[str, Any] = response.json()
        created_ids.append(uuid.UUID(data["id"]))
        return data

    yield _create

    with SessionLocal() as db:
        db.execute(delete(Interaction).where(Interaction.id.in_(created_ids)))
        db.commit()


def test_create_and_get_interaction(interaction_factory: Any, hcp_id: str) -> None:
    created = interaction_factory(
        topics_discussed="Discussed CardioX dosing",
        materials_shared=["CardioX brochure"],
        samples_distributed=["CardioX 10mg x2"],
        sentiment="positive",
        outcomes="Agreed to follow up next month",
    )

    response = client.get(f"/api/v1/interactions/{created['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["hcp_id"] == hcp_id
    assert body["interaction_type"] == "Meeting"
    assert body["sentiment"] == "positive"
    assert body["materials_shared"] == ["CardioX brochure"]
    assert body["source"] == "form"
    assert body["is_active"] is True


def test_create_missing_required_field(hcp_id: str) -> None:
    response = client.post(
        "/api/v1/interactions",
        json={"hcp_id": hcp_id, "occurred_at": "2026-07-14T10:00:00Z"},
    )
    assert response.status_code == 422


def test_create_invalid_hcp_id() -> None:
    response = client.post(
        "/api/v1/interactions",
        json={
            "hcp_id": str(uuid.uuid4()),
            "interaction_type": "Call",
            "occurred_at": "2026-07-14T10:00:00Z",
        },
    )
    assert response.status_code == 422


def test_create_invalid_sentiment(hcp_id: str) -> None:
    response = client.post(
        "/api/v1/interactions",
        json={
            "hcp_id": hcp_id,
            "interaction_type": "Call",
            "occurred_at": "2026-07-14T10:00:00Z",
            "sentiment": "ecstatic",
        },
    )
    assert response.status_code == 422


def test_get_not_found() -> None:
    response = client.get(f"/api/v1/interactions/{uuid.uuid4()}")
    assert response.status_code == 404


def test_update_interaction(interaction_factory: Any) -> None:
    created = interaction_factory()

    response = client.patch(
        f"/api/v1/interactions/{created['id']}",
        json={"outcomes": "Rescheduled for next week", "sentiment": "neutral"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["outcomes"] == "Rescheduled for next week"
    assert body["sentiment"] == "neutral"


def test_update_not_found() -> None:
    response = client.patch(
        f"/api/v1/interactions/{uuid.uuid4()}", json={"outcomes": "X"}
    )
    assert response.status_code == 404


def test_delete_interaction_soft_deletes(interaction_factory: Any) -> None:
    created = interaction_factory()

    delete_response = client.delete(f"/api/v1/interactions/{created['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/interactions/{created['id']}")
    assert get_response.status_code == 404


def test_list_filters_by_hcp_id(interaction_factory: Any, hcp_id: str) -> None:
    interaction_factory()

    response = client.get("/api/v1/interactions", params={"hcp_id": hcp_id})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["hcp_id"] == hcp_id
