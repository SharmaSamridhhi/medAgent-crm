import uuid
from collections.abc import Generator
from datetime import date
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.agent.tools.schedule_follow_up import (
    FollowUpExtraction,
    ScheduleFollowUpInput,
    schedule_follow_up,
)
from app.core.config import DEFAULT_DEMO_REP_ID
from app.core.db import SessionLocal
from app.main import app
from app.models import HCP, FollowUp, Interaction

client = TestClient(app)

_PATCH_TARGET = "app.agent.tools.schedule_follow_up.extract_structured"


@pytest.fixture
def hcp_id() -> Generator[str, None, None]:
    response = client.post("/api/v1/hcps", json={"name": "Dr. Priya Shah"})
    assert response.status_code == 201
    created_id: str = response.json()["id"]

    yield created_id

    with SessionLocal() as db:
        db.execute(delete(FollowUp).where(FollowUp.hcp_id == uuid.UUID(created_id)))
        db.execute(
            delete(Interaction).where(Interaction.hcp_id == uuid.UUID(created_id))
        )
        db.execute(delete(HCP).where(HCP.id == uuid.UUID(created_id)))
        db.commit()


def test_schedule_follow_up_relative_date_resolves(hcp_id: str) -> None:
    extraction = FollowUpExtraction(
        due_date=date(2026, 8, 14), note="Send Phase III data"
    )

    with patch(_PATCH_TARGET, return_value=extraction):
        with SessionLocal() as db:
            result = schedule_follow_up(
                ScheduleFollowUpInput(
                    rep_utterance="Remind me to follow up in a month with data.",
                    rep_id=DEFAULT_DEMO_REP_ID,
                    hcp_id=uuid.UUID(hcp_id),
                ),
                db,
            )

    assert result.status == "scheduled"
    assert result.due_date == date(2026, 8, 14)

    list_response = client.get("/api/v1/follow-ups")
    assert list_response.status_code == 200
    assert any(f["id"] == str(result.follow_up_id) for f in list_response.json())


def test_schedule_follow_up_tied_to_interaction(hcp_id: str) -> None:
    interaction_response = client.post(
        "/api/v1/interactions",
        json={
            "hcp_id": hcp_id,
            "interaction_type": "Meeting",
            "occurred_at": "2026-07-14T10:00:00Z",
        },
    )
    assert interaction_response.status_code == 201
    interaction_id = interaction_response.json()["id"]

    extraction = FollowUpExtraction(
        due_date=date(2026, 7, 28), note="Follow up on dosing data"
    )

    with patch(_PATCH_TARGET, return_value=extraction):
        with SessionLocal() as db:
            result = schedule_follow_up(
                ScheduleFollowUpInput(
                    rep_utterance="Remind me to follow up in two weeks.",
                    rep_id=DEFAULT_DEMO_REP_ID,
                    hcp_id=uuid.UUID(hcp_id),
                    interaction_id=uuid.UUID(interaction_id),
                ),
                db,
            )

    assert result.status == "scheduled"
    with SessionLocal() as db:
        follow_up = db.get(FollowUp, result.follow_up_id)
        assert follow_up is not None
        assert follow_up.interaction_id == uuid.UUID(interaction_id)


def test_schedule_follow_up_hcp_only_no_interaction(hcp_id: str) -> None:
    extraction = FollowUpExtraction(
        hcp_name="Priya Shah", due_date=date(2026, 9, 1), note="Check in"
    )

    with patch(_PATCH_TARGET, return_value=extraction):
        with SessionLocal() as db:
            result = schedule_follow_up(
                ScheduleFollowUpInput(
                    rep_utterance="Remind me to check in with Dr. Shah next month.",
                    rep_id=DEFAULT_DEMO_REP_ID,
                ),
                db,
            )

    assert result.status == "scheduled"
    with SessionLocal() as db:
        follow_up = db.get(FollowUp, result.follow_up_id)
        assert follow_up is not None
        assert follow_up.interaction_id is None
        assert follow_up.hcp_id == uuid.UUID(hcp_id)
