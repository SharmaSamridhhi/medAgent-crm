import uuid
from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.agent.tools.flag_compliance_risks import FlagComplianceRisksOutput
from app.agent.tools.log_interaction import (
    ExtractedFields,
    LogInteractionInput,
    log_interaction,
)
from app.core.config import DEFAULT_DEMO_REP_ID
from app.core.db import SessionLocal
from app.main import app
from app.models import HCP, Interaction
from app.schemas.interaction import ComplianceFlag

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

    with (
        patch(
            "app.agent.tools.log_interaction.extract_structured",
            return_value=extraction,
        ),
        patch(
            "app.agent.tools.log_interaction.flag_compliance_risks",
            return_value=FlagComplianceRisksOutput(flags=[]),
        ),
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
    assert result.compliance_flags == []


def test_log_interaction_persists_and_surfaces_compliance_flags(
    hcp_id: str,
) -> None:
    extraction = ExtractedFields(
        hcp_name="Priya Shah",
        interaction_type="Call",
        topics_discussed="Patient reported a rash after taking CardioX",
    )
    flagged = FlagComplianceRisksOutput(
        flags=[
            ComplianceFlag(
                category="adverse_event_mention",
                excerpt="reported a rash",
                rationale="Possible adverse event.",
            )
        ]
    )

    with (
        patch(
            "app.agent.tools.log_interaction.extract_structured",
            return_value=extraction,
        ),
        patch(
            "app.agent.tools.log_interaction.flag_compliance_risks",
            return_value=flagged,
        ),
    ):
        with SessionLocal() as db:
            result = log_interaction(
                LogInteractionInput(
                    rep_utterance="Dr. Shah's patient had a rash on CardioX.",
                    rep_id=DEFAULT_DEMO_REP_ID,
                ),
                db,
            )

    assert result.status == "created"
    assert len(result.compliance_flags) == 1
    assert result.compliance_flags[0].category == "adverse_event_mention"
    assert "adverse event" in result.message

    get_response = client.get(f"/api/v1/interactions/{result.interaction_id}")
    body = get_response.json()
    assert body["has_compliance_flags"] is True
    assert len(body["compliance_flags"]) == 1


def test_log_interaction_creates_new_hcp_when_not_found() -> None:
    extraction = ExtractedFields(
        hcp_name="Dr. Nobody",
        hcp_specialty="Cardiology",
        interaction_type="Call",
        topics_discussed="Generic follow-up",
    )

    result = None
    try:
        with (
            patch(
                "app.agent.tools.log_interaction.extract_structured",
                return_value=extraction,
            ),
            patch(
                "app.agent.tools.log_interaction.flag_compliance_risks",
                return_value=FlagComplianceRisksOutput(flags=[]),
            ),
        ):
            with SessionLocal() as db:
                result = log_interaction(
                    LogInteractionInput(
                        rep_utterance="Called Dr. Nobody about something.",
                        rep_id=DEFAULT_DEMO_REP_ID,
                    ),
                    db,
                )

        assert result.status == "created"
        assert result.hcp_created is True
        assert result.hcp_id is not None
        assert result.interaction_id is not None
        assert "wasn't on file" in result.message

        with SessionLocal() as db:
            created = db.get(HCP, result.hcp_id)
            assert created is not None
            assert created.name == "Dr. Nobody"
            assert created.specialty == "Cardiology"
    finally:
        if result is not None and result.hcp_id is not None:
            with SessionLocal() as db:
                db.execute(
                    delete(Interaction).where(Interaction.hcp_id == result.hcp_id)
                )
                db.execute(delete(HCP).where(HCP.id == result.hcp_id))
                db.commit()


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
