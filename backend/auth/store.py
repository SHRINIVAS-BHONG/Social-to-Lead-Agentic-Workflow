"""
store.py – In-memory user store for AutoStream.

Stores registered users, their plans, and connected social media accounts.
In production this would be a real database (PostgreSQL, MongoDB, etc.)
"""

import uuid
import hashlib
from datetime import datetime
from typing import Optional
from backend.config.logging_config import get_logger

logger = get_logger(__name__)

# ── In-memory stores ──────────────────────────────────────────────────────────
users: dict[str, dict] = {}          # email → user record
tokens: dict[str, str] = {}          # registration_token → email
sessions: dict[str, str] = {}        # session_token → email


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _make_token() -> str:
    return str(uuid.uuid4()).replace("-", "")


# ── User operations ───────────────────────────────────────────────────────────

def create_pending_user(name: str, email: str, platform: str) -> str:
    """
    Create a pending user record after lead capture.
    Returns a registration token to embed in the welcome email link.
    """
    token = _make_token()
    tokens[token] = email

    if email not in users:
        users[email] = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "platform": platform,
            "plan": "AutoStream Pro",
            "plan_activated": False,
            "password_hash": None,
            "social_accounts": {},
            "created_at": datetime.now().isoformat(),
            "registered_at": None,
        }
        logger.info(f"Pending user created: {email}")

    return token


def complete_registration(token: str, password: str, social_accounts: dict) -> Optional[dict]:
    """
    Complete registration when user clicks 'Get Started' and sets up their account.
    Returns the user record or None if token is invalid.
    """
    email = tokens.get(token)
    if not email or email not in users:
        return None

    user = users[email]
    user["password_hash"] = _hash_password(password)
    user["plan_activated"] = True
    user["social_accounts"] = social_accounts
    user["registered_at"] = datetime.now().isoformat()

    # Remove used token
    del tokens[token]

    logger.info(f"User registration completed: {email}")
    return _safe_user(user)


def login_user(email: str, password: str) -> Optional[dict]:
    """Authenticate user. Returns user + session token or None."""
    user = users.get(email)
    if not user:
        return None
    if not user.get("plan_activated"):
        return None
    if user.get("password_hash") != _hash_password(password):
        return None

    session_token = _make_token()
    sessions[session_token] = email

    logger.info(f"User logged in: {email}")
    return {"user": _safe_user(user), "token": session_token}


def get_user_by_token(session_token: str) -> Optional[dict]:
    """Get user by session token."""
    email = sessions.get(session_token)
    if not email:
        return None
    user = users.get(email)
    return _safe_user(user) if user else None


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user record by email (safe version)."""
    user = users.get(email)
    return _safe_user(user) if user else None


def update_social_accounts(email: str, social_accounts: dict) -> Optional[dict]:
    """Update connected social media accounts for a user."""
    user = users.get(email)
    if not user:
        return None
    user["social_accounts"].update(social_accounts)
    logger.info(f"Social accounts updated for: {email}")
    return _safe_user(user)


def user_exists(email: str) -> bool:
    """Check if a registered (activated) user exists."""
    user = users.get(email)
    return bool(user and user.get("plan_activated"))


def get_registration_token_email(token: str) -> Optional[str]:
    """Get email associated with a registration token."""
    return tokens.get(token)


def _safe_user(user: dict) -> dict:
    """Return user dict without sensitive fields."""
    return {k: v for k, v in user.items() if k != "password_hash"}
