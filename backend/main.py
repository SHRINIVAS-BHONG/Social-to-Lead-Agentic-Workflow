"""
main.py – FastAPI application entry point for the AutoStream AI Agent.

Endpoints:
  POST /chat    → Main chat endpoint; maintains session state across turns
  GET  /health  → Health check
  GET  /leads   → View all captured leads (admin/debug)
  WS   /ws      → WebSocket for streaming + social media posting simulation
"""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json

from backend.agent.graph import agent_graph
from backend.agent.state import AgentState
from backend.agent.tools import get_all_leads
from backend.agent.social_media_agent import run_social_media_agent
from backend.auth.store import (
    create_pending_user, complete_registration, login_user,
    get_user_by_token, user_exists, get_registration_token_email, get_user_by_email
)
from backend.config.logging_config import setup_logging, get_logger
from backend.config.settings import settings

setup_logging(level=settings.LOG_LEVEL, use_json=settings.LOG_JSON_FORMAT)
logger = get_logger(__name__)

try:
    settings.validate()
    logger.info("Configuration validated successfully", extra={"config": settings.get_info()})
except ValueError as e:
    logger.error(f"Configuration validation failed: {e}")
    raise

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


class RegisterRequest(BaseModel):
    token: str
    password: str
    social_accounts: dict = {}


class LoginRequest(BaseModel):
    email: str
    password: str


class ConnectSocialRequest(BaseModel):
    session_token: str
    platform: str
    username: str
    password: str


# ─────────────────────────────────────────────────────────────────────────────
# Helper – init session state
# ─────────────────────────────────────────────────────────────────────────────

def _init_session(session_id: str) -> AgentState:
    return AgentState(
        messages=[],
        intent="",
        retrieved_docs=[],
        lead_info={},
        is_ready_for_tool=False,
        tool_executed=False,
        response="",
        session_id=session_id,
        posting_triggered=False,
        posting_platform="",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running",
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        session_id = request.session_id or str(uuid.uuid4())

        if session_id not in sessions:
            sessions[session_id] = _init_session(session_id)
        state = sessions[session_id]
        state["messages"].append({"role": "user", "content": request.message})

        result: AgentState = agent_graph.invoke(state)
        sessions[session_id] = {**state, **result, "session_id": session_id}

        agent_response = result.get("response", "I'm sorry, I couldn't process that.")
        sessions[session_id]["messages"].append({"role": "assistant", "content": agent_response})

        lead_info = result.get("lead_info", {})
        lead_captured = bool(
            lead_info.get("name") and lead_info.get("email") and lead_info.get("platform")
            and result.get("tool_executed") is False
        )

        return ChatResponse(
            response=agent_response,
            session_id=session_id,
            intent=result.get("intent", ""),
            lead_info=lead_info,
            lead_captured=lead_captured,
        )

    except Exception as exc:
        logger.error("Error in /chat endpoint", extra={"error": str(exc)}, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.API_TITLE, "version": settings.API_VERSION}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint handling:
      1. Real-time streaming chat responses (word-by-word)
      2. Social media posting simulation (stage-by-stage) after lead capture
    """
    await websocket.accept()
    session_id = None

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            user_message = message_data.get("message", "")
            session_id = message_data.get("session_id") or str(uuid.uuid4())

            if not user_message:
                continue

            # ── Init session ──────────────────────────────────────────
            if session_id not in sessions:
                sessions[session_id] = _init_session(session_id)

            state = sessions[session_id]
            state["messages"].append({"role": "user", "content": user_message})

            # ── Typing indicator ──────────────────────────────────────
            await websocket.send_text(json.dumps({"type": "typing", "session_id": session_id}))

            # ── Run LangGraph agent ───────────────────────────────────
            result: AgentState = agent_graph.invoke(state)
            sessions[session_id] = {**state, **result, "session_id": session_id}

            agent_response = result.get("response", "I'm sorry, I couldn't process that.")
            sessions[session_id]["messages"].append({"role": "assistant", "content": agent_response})

            lead_info = result.get("lead_info", {})
            lead_captured = bool(
                lead_info.get("name") and lead_info.get("email") and lead_info.get("platform")
                and result.get("tool_executed") is False
            )

            # ── Stream response word-by-word ──────────────────────────
            words = agent_response.split()
            streamed_text = ""
            for i, word in enumerate(words):
                streamed_text += word + " "
                await websocket.send_text(json.dumps({
                    "type": "stream",
                    "content": streamed_text.strip(),
                    "session_id": session_id,
                    "intent": result.get("intent", ""),
                    "lead_info": lead_info,
                    "lead_captured": lead_captured,
                    "is_complete": False,
                }))
                await asyncio.sleep(0.05)

            # ── Complete signal ───────────────────────────────────────
            await websocket.send_text(json.dumps({
                "type": "complete",
                "content": agent_response,
                "session_id": session_id,
                "intent": result.get("intent", ""),
                "lead_info": lead_info,
                "lead_captured": lead_captured,
                "posting_triggered": result.get("posting_triggered", False),
                "posting_platform": result.get("posting_platform", ""),
                "is_complete": True,
            }))

            # ── Social media posting — REAL AGENT ────────────────────
            if result.get("posting_triggered") and result.get("posting_platform"):
                platform = result["posting_platform"]
                lead_name = result.get("lead_info", {}).get("name", "Creator")
                logger.info(f"Starting real social media agent for {platform}")

                await websocket.send_text(json.dumps({
                    "type": "agent_start",
                    "platform": platform,
                    "session_id": session_id,
                    "message": f"🤖 Launching autonomous agent for {platform}...",
                }))

                async for event in run_social_media_agent(platform, lead_name):
                    await websocket.send_text(json.dumps({
                        **event,
                        "session_id": session_id,
                    }))
                    await asyncio.sleep(0.1)

                sessions[session_id]["posting_triggered"] = False

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", extra={"session_id": (session_id or "")[:8]})
    except Exception as exc:
        logger.error("WebSocket error", extra={"error": str(exc)}, exc_info=True)
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "An error occurred while processing your message.",
            }))
        except Exception:
            pass


@app.get("/leads")
async def list_leads():
    leads = get_all_leads()
    return {"leads": leads, "total": len(leads)}


# ─────────────────────────────────────────────────────────────────────────────
# Auth Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/auth/check-token/{token}")
async def check_registration_token(token: str):
    """Check if a registration token is valid and return user info."""
    email = get_registration_token_email(token)
    if not email:
        raise HTTPException(status_code=404, detail="Invalid or expired registration link")
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "valid": True,
        "name": user["name"],
        "email": user["email"],
        "platform": user["platform"],
        "plan": user["plan"],
    }


@app.post("/auth/register")
async def register(request: RegisterRequest):
    """Complete registration — set password and connect social accounts."""
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    user = complete_registration(request.token, request.password, request.social_accounts)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired registration link")

    return {"success": True, "user": user, "message": "Account activated successfully!"}


@app.post("/auth/login")
async def login(request: LoginRequest):
    """Login with email and password."""
    result = login_user(request.email, request.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"success": True, "user": result["user"], "token": result["token"]}


@app.get("/auth/profile")
async def get_profile(session_token: str):
    """Get user profile by session token."""
    user = get_user_by_token(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    return {"user": user}


@app.post("/auth/connect-social")
async def connect_social(request: ConnectSocialRequest):
    """Connect a social media account to the user's profile."""
    from backend.auth.store import update_social_accounts, sessions
    email = sessions.get(request.session_token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid session")

    social_data = {
        request.platform: {
            "username": request.username,
            "connected": True,
            "connected_at": datetime.now().isoformat(),
        }
    }
    user = update_social_accounts(email, social_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"success": True, "user": user, "message": f"{request.platform} connected successfully"}


@app.get("/auth/check-user/{email}")
async def check_user_exists(email: str):
    """Check if a user with this email is already registered."""
    exists = user_exists(email)
    return {"exists": exists}
