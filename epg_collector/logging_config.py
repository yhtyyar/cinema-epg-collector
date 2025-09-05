from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(level: str = "INFO") -> None:
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(level.upper())

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level.upper())
    ch.setFormatter(formatter)

    # # File handler
    # fh = RotatingFileHandler(logs_dir / "app.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    # fh.setLevel(level.upper())
    # fh.setFormatter(formatter)

    # # Avoid duplicate handlers in repeated setups
    # if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
    #     logger.addHandler(fh)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(ch)
