from typing import TypedDict, List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """
    Structured state object maintained across all conversation turns.
    LangGraph merges returned dicts from each node into this shared state.
    
    Fields:
        messages: Full conversation history [{role, content}]
        intent: Current intent classification (greeting | inquiry | high_intent)
        retrieved_docs: RAG results from vector store
        lead_info: Collected lead fields {name, email, platform}
        is_ready_for_tool: True only when all 3 lead fields are present
        tool_executed: Flag to prevent response_generator overwriting tool response
        response: Final agent response for this turn
        session_id: Unique session identifier
    """
    messages: List[dict]
    intent: str
    retrieved_docs: List[str]
    lead_info: dict
    is_ready_for_tool: bool
    tool_executed: bool
    response: str
    session_id: str


def create_initial_state(session_id: str) -> AgentState:
    """
    Create a new AgentState with default values for a new session.
    
    Args:
        session_id: Unique identifier for the session
        
    Returns:
        AgentState: Initialized state with empty values
    """
    return AgentState(
        messages=[],
        intent="",
        retrieved_docs=[],
        lead_info={},
        is_ready_for_tool=False,
        tool_executed=False,
        response="",
        session_id=session_id
    )


def validate_agent_state(state: Dict[str, Any]) -> AgentState:
    """
    Validate and sanitize agent state, fixing common issues.
    
    This function ensures state consistency by:
    - Validating all required fields exist
    - Ensuring correct types for each field
    - Sanitizing invalid values to safe defaults
    - Preserving valid data while fixing corrupted fields
    
    Args:
        state: Raw state dictionary to validate
        
    Returns:
        AgentState: Validated and sanitized state
        
    Validates: Requirements 5.1, 5.2, 5.8
    """
    validated_state: Dict[str, Any] = {}
    
    # Validate messages field
    if not isinstance(state.get("messages"), list):
        logger.warning("Invalid messages field, initializing to empty list")
        validated_state["messages"] = []
    else:
        # Ensure each message is a dict with role and content
        valid_messages = []
        for msg in state["messages"]:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                valid_messages.append(msg)
            else:
                logger.warning(f"Skipping invalid message: {msg}")
        validated_state["messages"] = valid_messages
    
    # Validate intent field
    valid_intents = ["greeting", "inquiry", "high_intent", ""]
    intent = state.get("intent", "")
    if intent not in valid_intents:
        logger.warning(f"Invalid intent '{intent}', resetting to empty string")
        validated_state["intent"] = ""
    else:
        validated_state["intent"] = intent
    
    # Validate retrieved_docs field
    if not isinstance(state.get("retrieved_docs"), list):
        logger.warning("Invalid retrieved_docs field, initializing to empty list")
        validated_state["retrieved_docs"] = []
    else:
        # Ensure all docs are strings
        valid_docs = [doc for doc in state["retrieved_docs"] if isinstance(doc, str)]
        validated_state["retrieved_docs"] = valid_docs
    
    # Validate lead_info field
    if not isinstance(state.get("lead_info"), dict):
        logger.warning("Invalid lead_info field, initializing to empty dict")
        validated_state["lead_info"] = {}
    else:
        # Sanitize lead_info to only contain valid fields
        lead_info = state["lead_info"]
        sanitized_lead_info = {}
        
        if "name" in lead_info and isinstance(lead_info["name"], str):
            sanitized_lead_info["name"] = lead_info["name"]
        
        if "email" in lead_info and isinstance(lead_info["email"], str):
            sanitized_lead_info["email"] = lead_info["email"]
        
        if "platform" in lead_info and isinstance(lead_info["platform"], str):
            # Validate platform against allowed list
            valid_platforms = [
                "YouTube", "Instagram", "TikTok", "Twitter", 
                "Facebook", "LinkedIn", "Twitch", "Other"
            ]
            if lead_info["platform"] in valid_platforms:
                sanitized_lead_info["platform"] = lead_info["platform"]
            else:
                logger.warning(f"Invalid platform '{lead_info['platform']}', omitting from lead_info")
        
        validated_state["lead_info"] = sanitized_lead_info
    
    # Validate is_ready_for_tool field
    if not isinstance(state.get("is_ready_for_tool"), bool):
        logger.warning("Invalid is_ready_for_tool field, initializing to False")
        validated_state["is_ready_for_tool"] = False
    else:
        validated_state["is_ready_for_tool"] = state["is_ready_for_tool"]
    
    # Validate tool_executed field
    if not isinstance(state.get("tool_executed"), bool):
        logger.warning("Invalid tool_executed field, initializing to False")
        validated_state["tool_executed"] = False
    else:
        validated_state["tool_executed"] = state["tool_executed"]
    
    # Validate response field
    if not isinstance(state.get("response"), str):
        logger.warning("Invalid response field, initializing to empty string")
        validated_state["response"] = ""
    else:
        validated_state["response"] = state["response"]
    
    # Validate session_id field
    if not isinstance(state.get("session_id"), str):
        logger.warning("Invalid session_id field, initializing to empty string")
        validated_state["session_id"] = ""
    else:
        validated_state["session_id"] = state["session_id"]
    
    return AgentState(**validated_state)


def sanitize_lead_info(lead_info: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """
    Sanitize lead information to ensure data integrity.
    
    Args:
        lead_info: Raw lead information dictionary
        
    Returns:
        dict: Sanitized lead info with only valid fields
    """
    valid_platforms = [
        "YouTube", "Instagram", "TikTok", "Twitter", 
        "Facebook", "LinkedIn", "Twitch", "Other"
    ]
    
    sanitized = {}
    
    # Sanitize name
    if "name" in lead_info and isinstance(lead_info["name"], str) and lead_info["name"].strip():
        sanitized["name"] = lead_info["name"].strip()
    
    # Sanitize email
    if "email" in lead_info and isinstance(lead_info["email"], str) and lead_info["email"].strip():
        sanitized["email"] = lead_info["email"].strip()
    
    # Sanitize platform
    if "platform" in lead_info and lead_info["platform"] in valid_platforms:
        sanitized["platform"] = lead_info["platform"]
    
    return sanitized


def is_lead_complete(lead_info: Dict[str, Any]) -> bool:
    """
    Check if all required lead fields are present and valid.
    
    Args:
        lead_info: Lead information dictionary
        
    Returns:
        bool: True if all three fields (name, email, platform) are present
        
    Validates: Requirement 3.7
    """
    required_fields = ["name", "email", "platform"]
    return all(
        field in lead_info and 
        isinstance(lead_info[field], str) and 
        lead_info[field].strip()
        for field in required_fields
    )


def get_missing_lead_fields(lead_info: Dict[str, Any]) -> List[str]:
    """
    Get list of missing lead fields.
    
    Args:
        lead_info: Lead information dictionary
        
    Returns:
        List[str]: List of missing field names
    """
    required_fields = ["name", "email", "platform"]
    return [
        field for field in required_fields
        if field not in lead_info or not lead_info[field]
    ]


def limit_conversation_history(messages: List[dict], max_turns: int = 6) -> List[dict]:
    """
    Limit conversation history to the last N turns for LLM context.
    
    Args:
        messages: Full conversation history
        max_turns: Maximum number of turns to keep (default: 6)
        
    Returns:
        List[dict]: Truncated conversation history
        
    Validates: Requirement 5.6
    """
    if len(messages) <= max_turns * 2:  # Each turn has user + assistant message
        return messages
    
    # Keep the last max_turns * 2 messages (user + assistant pairs)
    return messages[-(max_turns * 2):]
