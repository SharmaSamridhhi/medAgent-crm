import uuid
from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.agent.tools.log_interaction import (
    ExtractedFields,
    LogInteractionInput,
    log_interaction,
)
from app.core.config import DEFAULT_DEMO_REP_ID
from app.core.db import SessionLocal
from app.main import app
from app.models import HCP, Interaction

client = TestClient(app)


@pytest.fixture
def hcp_id() -> Generator[str, None, None]:
    response = client.post("/api/v1/hcps", json={"name": "Dr. Priya Shah"})
    assert response.status_code == 201
    created_id = response.json()["id"]

    yield created_id

    with SessionLocal() as db:
        db.execute(
            delete(Interaction).where(Interaction.hcp_id == uuid.UUID(created_id))
        )
        db.execute(delete(HCP).where(HCP.id == uuid.UUID(created_id)))
        db.commit()


def test_log_interaction_creates_success(hcp_id: str) -> None:
    extraction = ExtractedFields(
        hcp_name="Priya Shah",
        interaction_type="Meeting",
        topics_discussed="Discussed CardioX dosing data",
        materials_shared=["CardioX brochure"],
        samples_distributed=["CardioX 10mg x2"],
        sentiment="positive",
        outcomes="Agreed to follow up next month",
        suggested_follow_ups=[
            "Schedule follow-up meeting in 2 weeks",
            "Send CardioX Phase III data sheet",
        ],
    )

    with patch(
        "app.agent.tools.log_interaction.extract_structured",
        return_value=extraction,
    ):
        with SessionLocal() as db:
            result = log_interaction(
                LogInteractionInput(
                    rep_utterance="Met Dr. Shah, discussed CardioX dosing.",
                    rep_id=DEFAULT_DEMO_REP_ID,
                ),
                db,
            )

    assert result.status == "created"
    assert result.interaction_id is not None
    assert result.hcp_id == uuid.UUID(hcp_id)
    assert result.sentiment == "positive"
    assert result.materials_shared == ["CardioX brochure"]
    assert len(result.suggested_follow_ups) == 2


def test_log_interaction_unresolvable_hcp() -> None:
    extraction = ExtractedFields(
        hcp_name="Dr. Nobody",
        interaction_type="Call",
        topics_discussed="Generic follow-up",
    )

    with patch(
        "app.agent.tools.log_interaction.extract_structured",
        return_value=extraction,
    ):
        with SessionLocal() as db:
            result = log_interaction(
                LogInteractionInput(
                    rep_utterance="Called Dr. Nobody about something.",
                    rep_id=DEFAULT_DEMO_REP_ID,
                ),
                db,
            )

    assert result.status == "needs_clarification"
    assert result.interaction_id is None
    assert result.candidate_hcps == []


def test_log_interaction_ambiguous_hcp(hcp_id: str) -> None:
    second_response = client.post("/api/v1/hcps", json={"name": "Dr. Priya Kapoor"})
    assert second_response.status_code == 201
    second_id = second_response.json()["id"]

    extraction = ExtractedFields(
        hcp_name="Priya",
        interaction_type="Call",
        topics_discussed="Quick check-in",
    )

    try:
        with patch(
            "app.agent.tools.log_interaction.extract_structured",
            return_value=extraction,
        ):
            with SessionLocal() as db:
                result = log_interaction(
                    LogInteractionInput(
                        rep_utterance="Called Priya about something.",
                        rep_id=DEFAULT_DEMO_REP_ID,
                    ),
                    db,
                )

        assert result.status == "needs_clarification"
        assert len(result.candidate_hcps) == 2
    finally:
        with SessionLocal() as db:
            db.execute(
                delete(Interaction).where(Interaction.hcp_id == uuid.UUID(second_id))
            )
            db.execute(delete(HCP).where(HCP.id == uuid.UUID(second_id)))
            db.commit()


def test_log_interaction_missing_topic(hcp_id: str) -> None:
    extraction = ExtractedFields(hcp_name="Priya Shah", interaction_type="Call")

    with patch(
        "app.agent.tools.log_interaction.extract_structured",
        return_value=extraction,
    ):
        with SessionLocal() as db:
            result = log_interaction(
                LogInteractionInput(
                    rep_utterance="Talked to Dr. Shah briefly.",
                    rep_id=DEFAULT_DEMO_REP_ID,
                ),
                db,
            )

    assert result.status == "needs_clarification"
    assert result.interaction_id is None
    assert result.hcp_id == uuid.UUID(hcp_id)
