from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    """
    Structured state object maintained across all conversation turns.
    LangGraph merges returned dicts from each node into this shared state.
    """
    messages: List[dict]           # Full conversation history [{role, content}]
    intent: str                    # greeting | inquiry | high_intent
    retrieved_docs: List[str]      # RAG results from vector store
    lead_info: dict                # Collected lead fields: name, email, platform
    is_ready_for_tool: bool        # True only when all 3 lead fields are present
    tool_executed: bool            # Flag to prevent response_generator overwriting tool response
    response: str                  # Final agent response for this turn
    session_id: str                # Unique session identifier
