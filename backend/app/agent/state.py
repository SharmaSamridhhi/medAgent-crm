import uuid
from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    rep_id: uuid.UUID
    active_hcp_id: uuid.UUID | None
    draft_interaction: dict[str, Any] | None
