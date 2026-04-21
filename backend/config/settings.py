"""
settings.py – Application configuration and environment variables.

Centralizes all configuration settings for the AutoStream AI Agent.
Loads from environment variables with sensible defaults.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # ── LLM Configuration ────────────────────────────────────────────
    # HuggingFace Inference API (free with generous limits)
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # Model selection - HuggingFace Inference API models
    # Popular free models: 
    # - meta-llama/Meta-Llama-3-8B-Instruct (WORKING, recommended)
    # - microsoft/DialoGPT-large (specialized for conversations)
    # - HuggingFaceH4/zephyr-7b-beta (good for chat)
    LLM_MODEL: str = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.5"))
    
    # ── Logging Configuration ────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_JSON_FORMAT: bool = os.getenv("LOG_JSON_FORMAT", "true").lower() == "true"
    
    # ── RAG Configuration ────────────────────────────────────────────
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "3"))
    
    # ── API Configuration ────────────────────────────────────────────
    API_TITLE: str = "AutoStream AI Agent"
    API_DESCRIPTION: str = "Social-to-Lead Agentic Workflow powered by LangGraph + HuggingFace"
    API_VERSION: str = "1.0.0"
    
    # CORS settings
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # ── Conversation Configuration ───────────────────────────────────
    MAX_CONVERSATION_TURNS: int = int(os.getenv("MAX_CONVERSATION_TURNS", "6"))
    RESPONSE_WORD_LIMIT: int = int(os.getenv("RESPONSE_WORD_LIMIT", "120"))
    
    # ── Lead Validation ──────────────────────────────────────────────
    VALID_PLATFORMS: list[str] = [
        "YouTube", "Instagram", "TikTok", "Twitter", 
        "Facebook", "LinkedIn", "Twitch", "Other"
    ]
    
    @classmethod
    def validate(cls) -> None:
        """
        Validate required configuration settings.
        
        Raises:
            ValueError: If required settings are missing or invalid
        """
        if not cls.HUGGINGFACE_API_KEY:
            raise ValueError(
                "HUGGINGFACE_API_KEY is required. "
                "Get a free API key at https://huggingface.co/settings/tokens"
            )
        
        if cls.LLM_TEMPERATURE < 0 or cls.LLM_TEMPERATURE > 1:
            raise ValueError(
                f"LLM_TEMPERATURE must be between 0 and 1, got {cls.LLM_TEMPERATURE}"
            )
        
        if cls.RAG_TOP_K < 1:
            raise ValueError(
                f"RAG_TOP_K must be at least 1, got {cls.RAG_TOP_K}"
            )
    
    @classmethod
    def get_info(cls) -> dict:
        """
        Get non-sensitive configuration information for logging/debugging.
        
        Returns:
            Dictionary of configuration settings (sensitive values redacted)
        """
        return {
            "llm_model": cls.LLM_MODEL,
            "llm_temperature": cls.LLM_TEMPERATURE,
            "log_level": cls.LOG_LEVEL,
            "log_json_format": cls.LOG_JSON_FORMAT,
            "embedding_model": cls.EMBEDDING_MODEL,
            "rag_top_k": cls.RAG_TOP_K,
            "max_conversation_turns": cls.MAX_CONVERSATION_TURNS,
            "response_word_limit": cls.RESPONSE_WORD_LIMIT,
            "api_key_configured": bool(cls.HUGGINGFACE_API_KEY),
        }


# Create singleton instance
settings = Settings()
