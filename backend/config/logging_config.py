"""
logging_config.py – Structured JSON logging configuration for the AutoStream AI Agent.

Provides structured logging with JSON output for production monitoring and debugging.
Includes correlation IDs, timestamps, and sanitization of sensitive data.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs log records as structured JSON.
    
    Each log entry includes:
    - timestamp: ISO format timestamp
    - level: Log level (INFO, WARNING, ERROR, etc.)
    - logger: Logger name (module path)
    - message: Log message
    - Additional fields from extra parameter
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields passed via extra parameter
        # Filter out standard LogRecord attributes
        standard_attrs = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName',
            'levelname', 'levelno', 'lineno', 'module', 'msecs',
            'message', 'pathname', 'process', 'processName', 'relativeCreated',
            'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info'
        }
        
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith('_'):
                log_data[key] = value
        
        return json.dumps(log_data)


def sanitize_sensitive_data(data: Any) -> Any:
    """
    Sanitize sensitive information from log data.
    
    Replaces API keys, passwords, and other sensitive fields with [REDACTED].
    
    Args:
        data: Data to sanitize (dict, list, str, or other)
    
    Returns:
        Sanitized copy of the data
    """
    sensitive_keys = {
        'api_key', 'apikey', 'password', 'secret', 'token',
        'authorization', 'auth', 'anthropic_api_key'
    }
    
    if isinstance(data, dict):
        return {
            key: "[REDACTED]" if key.lower() in sensitive_keys else sanitize_sensitive_data(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [sanitize_sensitive_data(item) for item in data]
    elif isinstance(data, str):
        # Check if string looks like an API key (starts with sk- or contains key patterns)
        if any(pattern in data.lower() for pattern in ['sk-', 'api_key=', 'token=']):
            return "[REDACTED]"
    
    return data


def setup_logging(level: str = "INFO", use_json: bool = True) -> None:
    """
    Configure application-wide logging with structured JSON output.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: If True, use JSON formatter; if False, use standard text format
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create handler for stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Set formatter based on configuration
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )
    
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    
    root_logger.info(
        "Logging configured",
        extra={
            "log_level": level,
            "json_format": use_json,
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__ from the calling module)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
