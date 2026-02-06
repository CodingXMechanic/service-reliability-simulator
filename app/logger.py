# app/logger.py
import logging
import os
import json
from datetime import datetime
from logging import Logger, LogRecord

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "service.log")

# Reserved LogRecord attributes that must NEVER appear in extra
_RESERVED_LOG_RECORD_KEYS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "message",  # <-- the one that caused your crash
}


class JSONFormatter(logging.Formatter):
    """Formatter that emits a compact JSON object per log line."""

    def format(self, record: LogRecord) -> str:
        payload = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Attach structured fields if present
        if hasattr(record, "endpoint"):
            payload["endpoint"] = record.endpoint
        if hasattr(record, "error_reason"):
            payload["error_reason"] = record.error_reason

        # Add exception info if present
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


class SafeLoggerAdapter(logging.LoggerAdapter):
    """
    LoggerAdapter that strips illegal keys from 'extra'
    to prevent LogRecord overwrite crashes.
    """

    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        if extra:
            safe_extra = {
                k: v for k, v in extra.items()
                if k not in _RESERVED_LOG_RECORD_KEYS
            }
            kwargs["extra"] = safe_extra
        return msg, kwargs


def get_logger(name: str = "service") -> Logger:
    os.makedirs(LOG_DIR, exist_ok=True)

    base_logger = logging.getLogger(name)
    if base_logger.handlers:
        return base_logger  # avoid duplicate handlers

    base_logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(JSONFormatter())
    base_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(JSONFormatter())
    base_logger.addHandler(console_handler)

    base_logger.propagate = False

    # Wrap with SafeLoggerAdapter
    return SafeLoggerAdapter(base_logger, {})


logger = get_logger()