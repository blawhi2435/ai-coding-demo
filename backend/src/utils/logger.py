"""Structured JSON logging utility for backend service."""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage(),
            "context": {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName,
            },
        }

        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_data["context"]["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["context"]["user_id"] = record.user_id

        # Add exception info if present
        if record.exc_info:
            log_data["error"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance with JSON formatting.

    Args:
        name: Logger name (e.g., "backend.api", "backend.startup")
        log_file: Optional path to log file. If None, logs to stderr.

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    # Create handler
    if log_file:
        handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler(sys.stderr)

    # Set formatter
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    return logger


# Create default logger instance
logger = get_logger("backend")
