"""Configuración de logging de SisAlmacen."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(logs_dir: Path) -> None:
    """Configura logging rotativo sin exponer datos sensibles."""

    logs_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("sisalmacen")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = RotatingFileHandler(
        logs_dir / "sisalmacen.log",
        maxBytes=1_048_576,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.propagate = False
