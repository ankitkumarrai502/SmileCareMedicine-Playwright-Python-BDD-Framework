"""Structured logging for the framework (console + file under reports/)."""

from __future__ import annotations

import logging
from pathlib import Path

_LOG_DIR = Path(__file__).resolve().parents[2] / "reports"
_CONFIGURED = False


def get_logger(name: str = "smilecare") -> logging.Logger:
    global _CONFIGURED
    logger = logging.getLogger(name)
    if not _CONFIGURED:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        fh = logging.FileHandler(_LOG_DIR / "run.log", encoding="utf-8")
        fh.setFormatter(fmt)
        root = logging.getLogger("smilecare")
        root.setLevel(logging.INFO)
        root.addHandler(sh)
        root.addHandler(fh)
        root.propagate = False
        _CONFIGURED = True
    return logger if name.startswith("smilecare") else logging.getLogger(f"smilecare.{name}")
