"""
main.py – FastAPI application entry point for the AutoStream AI Agent.

Endpoints:
  POST /chat    → Main chat endpoint; maintains session state across turns
  GET  /health  → Health check
  GET  /leads   → View all captured leads (admin/debug)
"""

import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agent.graph import agent_graph
from backend.agent.state import AgentState
from backend.agent.tools import get_all_leads
from backend.config.logging_config import setup_logging, get_logger
from backend.config.settings import settings

# ─────────────────────────────────────────────────────────────────────────────
# Logging Configuration
# ─────────────────────────────────────────────────────────────────────────────
setup_logging(level=settings.LOG_LEVEL, use_json=settings.LOG_JSON_FORMAT)
logger = get_logger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Validate Configuration
# ─────────────────────────────────────────────────────────────────────────────
try:
    settings.validate()
    logger.info(
        "Configuration validated successfully",
        extra={"config": settings.get_info()}
    )
except ValueError as e:
    logger.error(f"Configuration validation failed: {e}")
    raise

# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "endpoints": {
            "POST /chat": "Main chat endpoint - send messages to the AI agent",
            "GET /health": "Health check endpoint",
            "GET /leads": "View all captured leads",
            "GET /docs": "Interactive API documentation (Swagger UI)"
        },
        "status": "running"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.

    Maintains full conversation history and agent state per session_id.
    Calls the LangGraph agent and returns the structured response.
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        logger.info(
            "Chat request received",
            extra={
                "session_id": session_id[:8],
                "message_preview": request.message[:60],
            }
        )

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
            logger.info(
                "New session initialized",
                extra={"session_id": session_id[:8]}
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
            "Chat response generated",
            extra={
                "session_id": session_id[:8],
                "intent": result.get("intent"),
                "lead_info": lead_info,
                "lead_captured": lead_captured,
            }
        )

        return ChatResponse(
            response=agent_response,
            session_id=session_id,
            intent=result.get("intent", ""),
            lead_info=lead_info,
            lead_captured=lead_captured,
        )

    except Exception as exc:
        logger.error(
            "Error in /chat endpoint",
            extra={"error": str(exc)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
async def health():
    """Health check endpoint."""
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
    }


@app.get("/leads")
async def list_leads():
    """Return all captured leads (for demo / admin purposes)."""
    leads = get_all_leads()
    logger.info(
        "Leads list requested",
        extra={"total_leads": len(leads)}
    )
    return {"leads": leads, "total": len(leads)}
