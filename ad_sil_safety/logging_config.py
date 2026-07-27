#!/usr/bin/env python3
"""Unified logging configuration for ad-sil-safety.

Provides a single setup function that configures both console and file
logging with rotation. All modules in this package should use this instead of
bare print() statements.

Usage:
    from ad_sil_safety.logging_config import setup_logging, get_logger

    setup_logging(level="INFO", log_dir="data/logs")
    logger = get_logger(__name__)
    logger.info("Simulation started")
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Optional


logger = logging.getLogger(__name__)

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized = False


def setup_logging(
    level: str = "INFO",
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    console: bool = True,
) -> Optional[Path]:
    """Setup unified logging for ad-sil-safety.

    Configures the root logger with both console and rotating file handlers.
    Safe to call multiple times — subsequent calls are no-ops unless force=True.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        max_bytes: Max size per log file before rotation (default 10MB)
        backup_count: Number of rotated log files to keep
        console: Whether to also log to stdout

    Returns:
        Path to the log file, or None if setup failed
    """
    global _initialized
    if _initialized:
        return None

    log_path = Path(log_dir)
    try:
        log_path.mkdir(parents=True, exist_ok=True)
    except OSError:
        logger.warning("[logging_config] Cannot create log directory: %s, falling back to console-only", log_dir, exc_info=True)
        log_path = None

    log_level = getattr(logging, level.upper(), logging.INFO)

    # Build handlers
    handlers = []

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
        handlers.append(console_handler)

    log_file = None
    if log_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_path / f"compliance_{timestamp}.log"
        try:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
            handlers.append(file_handler)
        except OSError:
            logger.warning("[logging_config] Cannot create log file: %s", log_file, exc_info=True)
            log_file = None

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers to avoid duplicates
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    for h in handlers:
        root_logger.addHandler(h)

    _initialized = True
    return log_file


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.

    If setup_logging() has not been called yet, configures a basic
    console-only logger automatically.

    Args:
        name: Logger name, typically __name__ of the calling module

    Returns:
        A configured logging.Logger instance
    """
    if not _initialized:
        setup_logging()
    return logging.getLogger(name)


def reset_logging():
    """Reset logging state (useful for testing)."""
    global _initialized
    root_logger = logging.getLogger()
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
        h.close()
    _initialized = False
