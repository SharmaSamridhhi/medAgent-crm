from typing import Any

from langchain_core.messages import BaseMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

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
