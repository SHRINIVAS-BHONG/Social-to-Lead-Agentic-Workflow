"""
main.py – FastAPI application entry point for the AutoStream AI Agent.

Endpoints:
  POST /chat    → Main chat endpoint; maintains session state across turns
  GET  /health  → Health check
  GET  /leads   → View all captured leads (admin/debug)
"""

import logging
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.graph import agent_graph
from agent.state import AgentState
from agent.tools import get_all_leads

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AutoStream AI Agent",
    description="Social-to-Lead Agentic Workflow powered by LangGraph + Claude",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# In-memory session store
# In production replace with Redis or a database.
# ─────────────────────────────────────────────────────────────────────────────
sessions: dict[str, AgentState] = {}


# ─────────────────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: str
    lead_info: dict
    lead_captured: bool


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.

    Maintains full conversation history and agent state per session_id.
    Calls the LangGraph agent and returns the structured response.
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        logger.info(f"[Session {session_id[:8]}] User: {request.message!r}")

        # ── Get or initialise session state ──────────────────────────
        if session_id not in sessions:
            sessions[session_id] = AgentState(
                messages=[],
                intent="",
                retrieved_docs=[],
                lead_info={},
                is_ready_for_tool=False,
                tool_executed=False,
                response="",
                session_id=session_id,
            )

        state = sessions[session_id]

        # ── Append user message ───────────────────────────────────────
        state["messages"].append({"role": "user", "content": request.message})

        # ── Run the LangGraph agent ───────────────────────────────────
        result: AgentState = agent_graph.invoke(state)

        # ── Merge result back into session ────────────────────────────
        sessions[session_id] = {**state, **result, "session_id": session_id}

        # Append assistant reply to message history
        agent_response = result.get("response", "I'm sorry, I couldn't process that.")
        sessions[session_id]["messages"].append(
            {"role": "assistant", "content": agent_response}
        )

        lead_info = result.get("lead_info", {})
        lead_captured = bool(
            lead_info.get("name")
            and lead_info.get("email")
            and lead_info.get("platform")
            and result.get("tool_executed") is False  # tool just finished
        )

        logger.info(
            f"[Session {session_id[:8]}] Intent={result.get('intent')} | "
            f"Lead={lead_info} | Captured={lead_captured}"
        )

        return ChatResponse(
            response=agent_response,
            session_id=session_id,
            intent=result.get("intent", ""),
            lead_info=lead_info,
            lead_captured=lead_captured,
        )

    except Exception as exc:
        logger.exception(f"Error in /chat: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AutoStream AI Agent", "version": "1.0.0"}


@app.get("/leads")
async def list_leads():
    """Return all captured leads (for demo / admin purposes)."""
    return {"leads": get_all_leads(), "total": len(get_all_leads())}
