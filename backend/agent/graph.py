"""
graph.py – Assembles the LangGraph StateGraph for the AutoStream AI Agent.

Graph topology:

    START
      │
      ▼
  classify_intent
      │
      ├─[inquiry / greeting]──► retrieve_docs ──► generate_response ──► END
      │
      └─[high_intent]──────────► qualify_lead
                                      │
                                      ├─[all fields ready]──► execute_tool ──► generate_response ──► END
                                      │
                                      └─[fields missing]────► generate_response ──► END
"""

from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes import (
    intent_classifier_node,
    lead_qualification_node,
    rag_retrieval_node,
    response_generator_node,
    tool_execution_node,
)


# ─────────────────────────────────────────────────────────────────────────────
# Conditional edge routing functions
# ─────────────────────────────────────────────────────────────────────────────

def route_by_intent(state: AgentState) -> str:
    """Route after intent classification."""
    if state.get("intent") == "high_intent":
        return "qualify_lead"
    return "retrieve_docs"


def route_after_qualification(state: AgentState) -> str:
    """Route after lead qualification — tool only fires when all fields exist."""
    if state.get("is_ready_for_tool"):
        return "execute_tool"
    return "generate_response"


# ─────────────────────────────────────────────────────────────────────────────
# Graph construction
# ─────────────────────────────────────────────────────────────────────────────

def build_graph():
    """Build and compile the LangGraph StateGraph."""
    workflow = StateGraph(AgentState)

    # ── Register nodes ────────────────────────────────────────────────
    workflow.add_node("classify_intent",   intent_classifier_node)
    workflow.add_node("retrieve_docs",     rag_retrieval_node)
    workflow.add_node("qualify_lead",      lead_qualification_node)
    workflow.add_node("execute_tool",      tool_execution_node)
    workflow.add_node("generate_response", response_generator_node)

    # ── Entry point ───────────────────────────────────────────────────
    workflow.set_entry_point("classify_intent")

    # ── Edges ─────────────────────────────────────────────────────────
    workflow.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "retrieve_docs": "retrieve_docs",
            "qualify_lead":  "qualify_lead",
        },
    )

    # RAG path → straight to response
    workflow.add_edge("retrieve_docs", "generate_response")

    # Lead qualification path → tool or response
    workflow.add_conditional_edges(
        "qualify_lead",
        route_after_qualification,
        {
            "execute_tool":      "execute_tool",
            "generate_response": "generate_response",
        },
    )

    # Tool always flows to response generator (which passes through)
    workflow.add_edge("execute_tool",      "generate_response")
    workflow.add_edge("generate_response", END)

    return workflow.compile()


# ── Singleton compiled graph ──────────────────────────────────────────────────
agent_graph = build_graph()
