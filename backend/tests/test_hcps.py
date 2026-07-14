import uuid
from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.db import SessionLocal
from app.main import app
from app.models import HCP

client = TestClient(app)


@pytest.fixture
def hcp_factory() -> Generator[Any, None, None]:
    created_ids: list[uuid.UUID] = []

    def _create(**overrides: Any) -> dict[str, Any]:
        payload = {"name": "Dr. Test Rep", **overrides}
        response = client.post("/api/v1/hcps", json=payload)
        assert response.status_code == 201
        data: dict[str, Any] = response.json()
        created_ids.append(uuid.UUID(data["id"]))
        return data

    yield _create

    with SessionLocal() as db:
        db.execute(delete(HCP).where(HCP.id.in_(created_ids)))
        db.commit()


def test_create_and_get_hcp(hcp_factory: Any) -> None:
    created = hcp_factory(name="Dr. Priya Shah", specialty="Cardiology")

    response = client.get(f"/api/v1/hcps/{created['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Dr. Priya Shah"
    assert body["specialty"] == "Cardiology"
    assert body["is_active"] is True


def test_create_validation_error_missing_name() -> None:
    response = client.post("/api/v1/hcps", json={"specialty": "Oncology"})
    assert response.status_code == 422


def test_get_not_found() -> None:
    response = client.get(f"/api/v1/hcps/{uuid.uuid4()}")
    assert response.status_code == 404


def test_update_hcp(hcp_factory: Any) -> None:
    created = hcp_factory(name="Dr. Amit Rao")

    response = client.patch(
        f"/api/v1/hcps/{created['id']}", json={"specialty": "Neurology"}
    )

    assert response.status_code == 200
    assert response.json()["specialty"] == "Neurology"


def test_update_not_found() -> None:
    response = client.patch(f"/api/v1/hcps/{uuid.uuid4()}", json={"specialty": "X"})
    assert response.status_code == 404


def test_delete_hcp_soft_deletes(hcp_factory: Any) -> None:
    created = hcp_factory(name="Dr. Kavita Nair")

    delete_response = client.delete(f"/api/v1/hcps/{created['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/hcps/{created['id']}")
    assert get_response.status_code == 404


def test_list_search_filters_by_name(hcp_factory: Any) -> None:
    hcp_factory(name="Dr. Zsuzsanna Filtermatch")
    hcp_factory(name="Dr. Someone Else")

    response = client.get("/api/v1/hcps", params={"search": "Filtermatch"})

    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert "Dr. Zsuzsanna Filtermatch" in names
    assert "Dr. Someone Else" not in names
