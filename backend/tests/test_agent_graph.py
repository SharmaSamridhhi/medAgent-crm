import uuid
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage

from app.agent.graph import build_graph


def test_graph_returns_llm_response() -> None:
    fake_llm = MagicMock()
    fake_llm.invoke.return_value = AIMessage(content="mocked response")

    with patch("app.agent.graph.get_default_llm", return_value=fake_llm):
        graph = build_graph()
        result = graph.invoke(
            {
                "messages": [HumanMessage(content="hello")],
                "rep_id": uuid.uuid4(),
                "active_hcp_id": None,
                "draft_interaction": None,
            }
        )

    assert result["messages"][-1].content == "mocked response"
    fake_llm.invoke.assert_called_once()
