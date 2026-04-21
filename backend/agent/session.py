"""
session.py - Session management utilities for LangGraph integration.

This module provides utilities for managing conversation sessions including:
- Session initialization with proper state setup
- Session cleanup and memory management
- State merging logic for LangGraph workflow integration
- Session storage and retrieval

Validates: Requirements 5.7, 5.9
"""

from typing import Dict, Optional
import logging
from datetime import datetime, timedelta

from .state import AgentState, create_initial_state, validate_agent_state

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages conversation sessions with proper initialization, cleanup, and state merging.
    
    This class provides a centralized interface for session management that integrates
    with LangGraph's state management system. It handles:
    - Creating new sessions with initialized state
    - Retrieving existing sessions
    - Merging LangGraph results back into session state
    - Cleaning up expired or inactive sessions
    
    Validates: Requirements 5.7, 5.9
    """
    
    def __init__(self, session_timeout_minutes: int = 60):
        """
        Initialize the SessionManager.
        
        Args:
            session_timeout_minutes: Minutes of inactivity before session cleanup (default: 60)
        """
        self._sessions: Dict[str, AgentState] = {}
        self._last_activity: Dict[str, datetime] = {}
        self._session_timeout = timedelta(minutes=session_timeout_minutes)
        logger.info(f"SessionManager initialized with {session_timeout_minutes}min timeout")
    
    def get_or_create_session(self, session_id: str) -> AgentState:
        """
        Get an existing session or create a new one if it doesn't exist.
        
        This method ensures that every session_id has a valid AgentState, creating
        a new initialized state if the session doesn't exist yet.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            AgentState: The session's current state (existing or newly created)
            
        Validates: Requirements 5.7, 5.9
        """
        if session_id not in self._sessions:
            logger.info(f"Creating new session: {session_id[:8]}...")
            self._sessions[session_id] = create_initial_state(session_id)
            self._last_activity[session_id] = datetime.now()
        else:
            logger.debug(f"Retrieved existing session: {session_id[:8]}...")
            self._last_activity[session_id] = datetime.now()
        
        return self._sessions[session_id]
    
    def update_session(self, session_id: str, state: AgentState) -> None:
        """
        Update an existing session with new state.
        
        Args:
            session_id: Unique identifier for the session
            state: Updated AgentState to store
            
        Validates: Requirements 5.7, 5.9
        """
        if session_id not in self._sessions:
            logger.warning(f"Updating non-existent session: {session_id[:8]}...")
        
        self._sessions[session_id] = state
        self._last_activity[session_id] = datetime.now()
        logger.debug(f"Session updated: {session_id[:8]}...")
    
    def merge_graph_result(
        self, 
        session_id: str, 
        current_state: AgentState, 
        graph_result: AgentState
    ) -> AgentState:
        """
        Merge LangGraph execution result back into session state.
        
        This method implements the state merging logic required for LangGraph integration.
        It combines the current session state with the results from a graph execution,
        ensuring that all updates are properly preserved while maintaining state consistency.
        
        The merging strategy:
        1. Start with the current session state as the base
        2. Overlay all fields from the graph result
        3. Ensure session_id is preserved
        4. Validate the merged state for consistency
        
        Args:
            session_id: Unique identifier for the session
            current_state: The session state before graph execution
            graph_result: The state returned by LangGraph after execution
            
        Returns:
            AgentState: Merged state combining current state and graph results
            
        Validates: Requirements 5.7, 5.9
        """
        logger.debug(f"Merging graph result for session: {session_id[:8]}...")
        
        # Start with current state as base
        merged_state = dict(current_state)
        
        # Overlay graph result fields
        for key, value in graph_result.items():
            merged_state[key] = value
        
        # Ensure session_id is preserved
        merged_state["session_id"] = session_id
        
        # Validate the merged state
        validated_state = validate_agent_state(merged_state)
        
        logger.debug(
            f"State merged successfully for session: {session_id[:8]}...",
            extra={
                "intent": validated_state.get("intent"),
                "message_count": len(validated_state.get("messages", [])),
                "lead_fields": list(validated_state.get("lead_info", {}).keys()),
            }
        )
        
        return validated_state
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove sessions that have been inactive beyond the timeout period.
        
        This method performs garbage collection on the session store, removing
        sessions that haven't been accessed within the configured timeout period.
        This prevents unbounded memory growth in long-running applications.
        
        Returns:
            int: Number of sessions cleaned up
            
        Validates: Requirements 5.7, 5.9
        """
        now = datetime.now()
        expired_sessions = [
            session_id
            for session_id, last_activity in self._last_activity.items()
            if now - last_activity > self._session_timeout
        ]
        
        for session_id in expired_sessions:
            logger.info(f"Cleaning up expired session: {session_id[:8]}...")
            del self._sessions[session_id]
            del self._last_activity[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_session_count(self) -> int:
        """
        Get the current number of active sessions.
        
        Returns:
            int: Number of active sessions
        """
        return len(self._sessions)
    
    def clear_session(self, session_id: str) -> bool:
        """
        Explicitly clear a specific session.
        
        Args:
            session_id: Unique identifier for the session to clear
            
        Returns:
            bool: True if session was found and cleared, False otherwise
        """
        if session_id in self._sessions:
            logger.info(f"Clearing session: {session_id[:8]}...")
            del self._sessions[session_id]
            del self._last_activity[session_id]
            return True
        
        logger.warning(f"Attempted to clear non-existent session: {session_id[:8]}...")
        return False
    
    def clear_all_sessions(self) -> int:
        """
        Clear all sessions (useful for testing or maintenance).
        
        Returns:
            int: Number of sessions cleared
        """
        count = len(self._sessions)
        self._sessions.clear()
        self._last_activity.clear()
        logger.info(f"Cleared all {count} sessions")
        return count


# ─────────────────────────────────────────────────────────────────────────────
# Standalone utility functions for simple use cases
# ─────────────────────────────────────────────────────────────────────────────

def initialize_session(session_id: str) -> AgentState:
    """
    Initialize a new session with default state.
    
    This is a convenience function for creating a new session state without
    using the SessionManager class. Useful for simple applications or testing.
    
    Args:
        session_id: Unique identifier for the session
        
    Returns:
        AgentState: Newly initialized session state
        
    Validates: Requirements 5.7
    """
    logger.info(f"Initializing new session: {session_id[:8]}...")
    return create_initial_state(session_id)


def merge_state(base_state: AgentState, updates: AgentState) -> AgentState:
    """
    Merge state updates into a base state.
    
    This function implements the core state merging logic used by LangGraph.
    It takes a base state and overlays updates from a graph execution result.
    
    Args:
        base_state: The starting state
        updates: State updates to merge in
        
    Returns:
        AgentState: Merged and validated state
        
    Validates: Requirements 5.9
    """
    merged = dict(base_state)
    merged.update(updates)
    return validate_agent_state(merged)


def append_message_to_state(
    state: AgentState, 
    role: str, 
    content: str
) -> AgentState:
    """
    Append a message to the conversation history in the state.
    
    This is a helper function for adding messages to the state's message list
    while maintaining immutability principles.
    
    Args:
        state: Current agent state
        role: Message role ("user" or "assistant")
        content: Message content
        
    Returns:
        AgentState: Updated state with new message appended
        
    Validates: Requirements 5.1, 5.2
    """
    updated_state = dict(state)
    updated_state["messages"] = list(state["messages"])
    updated_state["messages"].append({"role": role, "content": content})
    return validate_agent_state(updated_state)
