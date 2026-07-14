import uuid
from typing import Any

from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from sqlalchemy.orm import Session

from app.agent.graph_tools import build_tools
from app.agent.llm import get_default_llm
from app.agent.state import AgentState


def _call_llm(state: AgentState) -> dict[str, list[BaseMessage]]:
    llm = get_default_llm()
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def build_graph() -> CompiledStateGraph[AgentState, Any, AgentState, AgentState]:
    graph = StateGraph(AgentState)
    graph.add_node("llm", _call_llm)
    graph.set_entry_point("llm")
    graph.add_edge("llm", END)
    return graph.compile()


_SYSTEM_PROMPT = (
    "You are an AI CRM assistant helping a pharmaceutical sales rep log "
    "and manage their interactions with healthcare professionals (HCPs). "
    "You have five tools: log_interaction, edit_interaction, "
    "retrieve_hcp_history, schedule_follow_up, flag_compliance_risks.\n\n"
    "Guidelines:\n"
    "- As soon as you know which HCP the rep is discussing (by name or "
    "id), call retrieve_hcp_history proactively, even if the rep didn't "
    "ask for it — it grounds the rest of the conversation. Do this once "
    "per HCP per conversation, not on every turn.\n"
    "- Reuse ids (hcp_id, interaction_id) from earlier tool results in "
    "this conversation when calling later tools, instead of re-resolving "
    "by name every time.\n"
    "- If a tool returns status='needs_clarification', relay its message "
    "to the rep in your own words and wait for their answer — never "
    "guess or proceed without it.\n"
    "- flag_compliance_risks already runs automatically inside "
    "log_interaction; only call it directly if the rep explicitly asks "
    "you to check some other text.\n"
    "- Keep replies brief and conversational."
)


def build_agent_graph_with_tools(
    db: Session, rep_id: uuid.UUID, side_effects: list[dict[str, Any]]
) -> CompiledStateGraph[AgentState, Any, AgentState, AgentState]:
    """The real, multi-tool conversational graph — see MEDGENT-015."""
    tools = build_tools(db, rep_id, side_effects)
    llm_with_tools = get_default_llm().bind_tools(tools)

    def agent_node(state: AgentState) -> dict[str, list[BaseMessage]]:
        messages = [SystemMessage(content=_SYSTEM_PROMPT), *state["messages"]]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent", tools_condition, {"tools": "tools", "__end__": END}
    )
    graph.add_edge("tools", "agent")
    return graph.compile()
