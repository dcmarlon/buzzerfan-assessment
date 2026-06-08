# Auth/Login/WebApp/utils/logger.py
"""Centralized logging for the Web Login test.

Provides a single configured logger that writes to BOTH the console (stdout)
and a timestamped file under ``logs/``. Routing all output through one factory
keeps formatting consistent and removes the need for bare ``print()`` calls.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

# Directory (relative to this feature folder) where log files are written.
_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def get_logger(name: str = "web_login") -> logging.Logger:
    """Return a logger that streams to stdout and a timestamped log file.

    The logger is configured only once per name; repeated calls return the
    same instance without attaching duplicate handlers.

    Args:
        name: Logical name for the logger (also shown in each log line).

    Returns:
        A ready-to-use :class:`logging.Logger`.
    """
    logger = logging.getLogger(name)

    # If handlers already exist, the logger was configured earlier — reuse it.
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Ensure logs/ exists before the file handler tries to open a file in it.
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = _LOG_DIR / f"{name}_{timestamp}.log"

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler -> stdout.
    console = logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    # File handler -> logs/<name>_<timestamp>.log.
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    logger.info("Logging initialized. Writing to %s", log_file)
    return logger
