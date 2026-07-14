import uuid
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage
from sqlalchemy import delete

from app.agent.tools.edit_interaction import EditExtraction, HCPNameHint
from app.agent.tools.flag_compliance_risks import FlagComplianceRisksOutput
from app.agent.tools.log_interaction import ExtractedFields
from app.core.db import SessionLocal
from app.main import app
from app.models import HCP, Interaction

client = TestClient(app)


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


def _heavy_llm_mock(
    extracted_fields: ExtractedFields, edit_extraction: EditExtraction
) -> MagicMock:
    def with_structured_output(schema: type) -> MagicMock:
        mock = MagicMock()
        if schema is ExtractedFields:
            mock.invoke.return_value = extracted_fields
        elif schema is FlagComplianceRisksOutput:
            mock.invoke.return_value = FlagComplianceRisksOutput(flags=[])
        elif schema is EditExtraction:
            mock.invoke.return_value = edit_extraction
        elif schema is HCPNameHint:
            mock.invoke.return_value = HCPNameHint(target_hcp_name=None)
        else:
            raise AssertionError(f"Unexpected structured-output schema: {schema}")
        return mock

    heavy = MagicMock()
    heavy.with_structured_output.side_effect = with_structured_output
    return heavy


def _routing_llm_mock(replies: list[AIMessage]) -> MagicMock:
    bound = MagicMock()
    bound.invoke.side_effect = replies
    routing = MagicMock()
    routing.bind_tools.return_value = bound
    return routing


def _tool_call(name: str, args: dict[str, Any], call_id: str) -> AIMessage:
    return AIMessage(
        content="", tool_calls=[{"name": name, "args": args, "id": call_id}]
    )


def test_multi_turn_log_then_edit_then_history(hcp_id: str) -> None:
    extracted_fields = ExtractedFields(
        hcp_name="Priya Shah",
        interaction_type="Call",
        topics_discussed="Discussed CardioX dosing data",
        samples_distributed=["2 packs of CardioX"],
        sentiment="positive",
    )
    edit_extraction = EditExtraction(samples_distributed=["3 packs of CardioX"])

    routing_replies = [
        # Turn 1: decide to log, then respond
        _tool_call("log_interaction", {"rep_utterance": "Met Dr. Shah, CardioX."}, "1"),
        AIMessage(content="Logged the interaction with Dr. Shah."),
        # Turn 2: decide to edit (no interaction_id — relies on recency), then respond
        _tool_call(
            "edit_interaction", {"rep_utterance": "Actually it was 3, not 2."}, "2"
        ),
        AIMessage(content="Updated the interaction."),
        # Turn 3: decide to look up history, then respond
        _tool_call("retrieve_hcp_history", {"hcp_name": "Priya Shah"}, "3"),
        AIMessage(content="Here's the history with Dr. Shah."),
    ]

    with (
        patch(
            "app.agent.tools._extraction.get_heavy_llm",
            return_value=_heavy_llm_mock(extracted_fields, edit_extraction),
        ),
        patch(
            "app.agent.tools.retrieve_hcp_history.get_default_llm",
            return_value=MagicMock(
                invoke=MagicMock(return_value=MagicMock(content="Positive history."))
            ),
        ),
        patch(
            "app.agent.graph.get_default_llm",
            return_value=_routing_llm_mock(routing_replies),
        ),
    ):
        turn1 = client.post(
            "/api/v1/agent/chat", json={"message": "Met Dr. Shah, CardioX."}
        )
        assert turn1.status_code == 200
        body1 = turn1.json()
        session_id = body1["session_id"]
        log_effect = next(
            e for e in body1["side_effects"] if e["tool"] == "log_interaction"
        )
        assert log_effect["output"]["status"] == "created"
        interaction_id = log_effect["output"]["interaction_id"]

        turn2 = client.post(
            "/api/v1/agent/chat",
            json={
                "session_id": session_id,
                "message": "Actually it was 3, not 2.",
            },
        )
        assert turn2.status_code == 200
        body2 = turn2.json()
        edit_effect = next(
            e for e in body2["side_effects"] if e["tool"] == "edit_interaction"
        )
        assert edit_effect["output"]["status"] == "updated"
        assert edit_effect["output"]["interaction_id"] == interaction_id
        assert edit_effect["output"]["changes"][0]["new_value"] == [
            "3 packs of CardioX"
        ]

        turn3 = client.post(
            "/api/v1/agent/chat",
            json={
                "session_id": session_id,
                "message": "What's the history with Dr. Shah?",
            },
        )
        assert turn3.status_code == 200
        body3 = turn3.json()
        history_effect = next(
            e for e in body3["side_effects"] if e["tool"] == "retrieve_hcp_history"
        )
        assert history_effect["output"]["status"] == "found"
        assert len(history_effect["output"]["interactions"]) == 1
        # reflects turn 2's edit, confirming state carried correctly
        assert history_effect["output"]["interactions"][0]["id"] == interaction_id
