import uuid
from typing import Any, cast

from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agent.graph import build_agent_graph_with_tools
from app.agent.state import AgentState
from app.core.db import get_db
from app.core.dependencies import get_current_rep
from app.models import Rep

router = APIRouter(prefix="/agent", tags=["agent"])

# In-memory only — restarting the backend drops in-flight conversations.
# Acceptable for this project's scope (single-process demo); see
# MEDGENT-015's technical details.
_SESSIONS: dict[str, AgentState] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ToolSideEffect(BaseModel):
    tool: str
    output: dict[str, Any]


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    side_effects: list[ToolSideEffect]


def _new_state(rep_id: uuid.UUID) -> AgentState:
    return AgentState(
        messages=[], rep_id=rep_id, active_hcp_id=None, draft_interaction=None
    )


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_rep: Rep = Depends(get_current_rep),
) -> ChatResponse:
    session_id = payload.session_id or str(uuid.uuid4())
    state = _SESSIONS.get(session_id) or _new_state(current_rep.id)
    state["messages"] = [*state["messages"], HumanMessage(content=payload.message)]

    side_effects: list[dict[str, Any]] = []
    graph = build_agent_graph_with_tools(db, current_rep.id, side_effects)
    result_state = cast("AgentState", graph.invoke(state))

    _SESSIONS[session_id] = result_state

    reply = str(result_state["messages"][-1].content)

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        side_effects=[ToolSideEffect(**effect) for effect in side_effects],
    )
