import uuid
from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.agent.tools.edit_interaction import (
    EditExtraction,
    EditInteractionInput,
    HCPNameHint,
    edit_interaction,
)
from app.agent.tools.flag_compliance_risks import FlagComplianceRisksOutput
from app.core.config import DEFAULT_DEMO_REP_ID
from app.core.db import SessionLocal
from app.main import app
from app.models import HCP, Interaction

client = TestClient(app)

_PATCH_TARGET = "app.agent.tools.edit_interaction.extract_structured"


@pytest.fixture(autouse=True)
def _no_real_compliance_screening() -> Generator[None, None, None]:
    # edit_interaction() calls update_interaction(), which re-screens
    # topics_discussed/outcomes edits for compliance risk (MEDGENT-022) —
    # stub it out here so these tests never hit the real Groq API.
    with patch(
        "app.api.v1.interactions.flag_compliance_risks",
        return_value=FlagComplianceRisksOutput(flags=[]),
    ):
        yield


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


@pytest.fixture
def interaction_id(hcp_id: str) -> str:
    response = client.post(
        "/api/v1/interactions",
        json={
            "hcp_id": hcp_id,
            "interaction_type": "Meeting",
            "occurred_at": "2026-07-14T10:00:00Z",
            "samples_distributed": ["CardioX 10mg x2"],
        },
    )
    assert response.status_code == 201
    result: str = response.json()["id"]
    return result


def test_edit_interaction_unambiguous_by_id(interaction_id: str) -> None:
    extraction = EditExtraction(samples_distributed=["CardioX 10mg x3"])

    with patch(_PATCH_TARGET, return_value=extraction):
        with SessionLocal() as db:
            result = edit_interaction(
                EditInteractionInput(
                    rep_utterance="Actually it was 3 samples, not 2.",
                    rep_id=DEFAULT_DEMO_REP_ID,
                    interaction_id=uuid.UUID(interaction_id),
                ),
                db,
            )

    assert result.status == "updated"
    assert result.interaction_id == uuid.UUID(interaction_id)
    assert len(result.changes) == 1
    change = result.changes[0]
    assert change.field == "samples_distributed"
    assert change.old_value == ["CardioX 10mg x2"]
    assert change.new_value == ["CardioX 10mg x3"]

    get_response = client.get(f"/api/v1/interactions/{interaction_id}")
    assert get_response.json()["samples_distributed"] == ["CardioX 10mg x3"]


def test_edit_interaction_resolves_via_recency_when_unambiguous(
    interaction_id: str,
) -> None:
    extraction = EditExtraction(outcomes="Agreed to a trial order")

    with patch(_PATCH_TARGET, return_value=extraction):
        with SessionLocal() as db:
            result = edit_interaction(
                EditInteractionInput(
                    rep_utterance="For the one with Dr. Shah, she agreed to order.",
                    rep_id=DEFAULT_DEMO_REP_ID,
                ),
                db,
            )

    assert result.status == "updated"
    assert result.interaction_id == uuid.UUID(interaction_id)
    assert result.changes[0].field == "outcomes"


def test_edit_interaction_ambiguous_multiple_recent(hcp_id: str) -> None:
    other_hcp = client.post("/api/v1/hcps", json={"name": "Dr. Rohan Mehta"})
    assert other_hcp.status_code == 201
    other_hcp_id = other_hcp.json()["id"]

    first = client.post(
        "/api/v1/interactions",
        json={
            "hcp_id": hcp_id,
            "interaction_type": "Call",
            "occurred_at": "2026-07-14T09:00:00Z",
        },
    )
    second = client.post(
        "/api/v1/interactions",
        json={
            "hcp_id": other_hcp_id,
            "interaction_type": "Call",
            "occurred_at": "2026-07-14T11:00:00Z",
        },
    )
    assert first.status_code == 201
    assert second.status_code == 201

    hint = HCPNameHint(target_hcp_name=None)

    try:
        with patch(_PATCH_TARGET, return_value=hint):
            with SessionLocal() as db:
                result = edit_interaction(
                    EditInteractionInput(
                        rep_utterance="It went well.",
                        rep_id=DEFAULT_DEMO_REP_ID,
                    ),
                    db,
                )

        assert result.status == "needs_clarification"
        assert len(result.candidate_interactions) == 2
    finally:
        with SessionLocal() as db:
            db.execute(
                delete(Interaction).where(Interaction.hcp_id == uuid.UUID(other_hcp_id))
            )
            db.execute(delete(HCP).where(HCP.id == uuid.UUID(other_hcp_id)))
            db.commit()


def test_edit_interaction_disambiguated_by_hcp_name(hcp_id: str) -> None:
    other_hcp = client.post("/api/v1/hcps", json={"name": "Dr. Rohan Mehta"})
    assert other_hcp.status_code == 201
    other_hcp_id = other_hcp.json()["id"]

    first = client.post(
        "/api/v1/interactions",
        json={
            "hcp_id": hcp_id,
            "interaction_type": "Call",
            "occurred_at": "2026-07-14T09:00:00Z",
        },
    )
    second = client.post(
        "/api/v1/interactions",
        json={
            "hcp_id": other_hcp_id,
            "interaction_type": "Call",
            "occurred_at": "2026-07-14T11:00:00Z",
        },
    )
    assert first.status_code == 201
    assert second.status_code == 201
    first_id = first.json()["id"]

    hint = HCPNameHint(target_hcp_name="Priya Shah")
    diff = EditExtraction(outcomes="Went well")

    try:
        with patch(_PATCH_TARGET, side_effect=[hint, diff]):
            with SessionLocal() as db:
                result = edit_interaction(
                    EditInteractionInput(
                        rep_utterance="The one with Dr. Shah went well.",
                        rep_id=DEFAULT_DEMO_REP_ID,
                    ),
                    db,
                )

        assert result.status == "updated"
        assert result.interaction_id == uuid.UUID(first_id)
        assert result.changes[0].field == "outcomes"
    finally:
        with SessionLocal() as db:
            db.execute(
                delete(Interaction).where(Interaction.hcp_id == uuid.UUID(other_hcp_id))
            )
            db.execute(delete(HCP).where(HCP.id == uuid.UUID(other_hcp_id)))
            db.commit()


def test_edit_interaction_no_recognizable_change(interaction_id: str) -> None:
    with patch(_PATCH_TARGET, return_value=EditExtraction()):
        with SessionLocal() as db:
            result = edit_interaction(
                EditInteractionInput(
                    rep_utterance="Actually that was on a different date entirely.",
                    rep_id=DEFAULT_DEMO_REP_ID,
                    interaction_id=uuid.UUID(interaction_id),
                ),
                db,
            )

    assert result.status == "needs_clarification"
    assert result.changes == []
