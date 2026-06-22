"""Hybrid self-healing locator.

A logical key (e.g. ``"email_input"``) maps to a RANKED list of candidate selectors in
``config/locators/<page>.yaml`` (most stable first: id > role > text > structural). At runtime
the resolver tries each candidate in order and returns the first that actually matches an element
on the page. When a lower-ranked candidate wins, that is a *heal signal* — recorded so the Healer
agent can promote it.

This is the deterministic layer. The optional AI layer (``src/core/ai_healer.py``) is consulted
only when every deterministic candidate fails and AI healing is enabled.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml
from playwright.sync_api import Locator, Page

from src.utils.logger import get_logger

log = get_logger("heal")
_LOCATOR_DIR = Path(__file__).resolve().parents[2] / "config" / "locators"
_HEAL_LOG = Path(__file__).resolve().parents[2] / "reports" / "heal_events.json"


@dataclass
class HealEvent:
    page: str
    key: str
    used_selector: str
    rank: int           # 0 = top candidate (no heal); >0 = a fallback won
    candidates: list[str] = field(default_factory=list)


class LocatorRepository:
    """Loads and caches the ranked candidate selectors for a page."""

    def __init__(self) -> None:
        self._cache: dict[str, dict[str, list[str]]] = {}

    def candidates(self, page_name: str, key: str) -> list[str]:
        data = self._cache.get(page_name)
        if data is None:
            path = _LOCATOR_DIR / f"{page_name}.yaml"
            if not path.exists():
                raise FileNotFoundError(f"No locator file for page '{page_name}': {path}")
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            self._cache[page_name] = data
        if key not in data:
            raise KeyError(f"Locator key '{key}' not defined for page '{page_name}'")
        cands = data[key]
        return cands if isinstance(cands, list) else [cands]


_REPO = LocatorRepository()


def resolve(page: Page, page_name: str, key: str, *, timeout_ms: int = 5000) -> Locator:
    """Return a Locator for the logical key, trying ranked candidates until one matches.

    Records a heal event when a non-top candidate is used. Raises ``LookupError`` if none match.
    """
    candidates = _REPO.candidates(page_name, key)
    last_error: Optional[Exception] = None
    for rank, selector in enumerate(candidates):
        try:
            loc = page.locator(selector).first
            loc.wait_for(state="attached", timeout=timeout_ms if rank == 0 else 1500)
            if rank > 0:
                _record(HealEvent(page_name, key, selector, rank, candidates))
                log.warning("HEAL: '%s.%s' used fallback #%d (%s)", page_name, key, rank, selector)
            return loc
        except Exception as exc:  # noqa: BLE001 - intentionally try the next candidate
            last_error = exc
            continue
    raise LookupError(
        f"All {len(candidates)} candidate selectors failed for '{page_name}.{key}'. "
        f"Candidates: {candidates}. Last error: {last_error}"
    )


def _record(event: HealEvent) -> None:
    _HEAL_LOG.parent.mkdir(parents=True, exist_ok=True)
    history = []
    if _HEAL_LOG.exists():
        try:
            history = json.loads(_HEAL_LOG.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            history = []
    history.append(event.__dict__)
    _HEAL_LOG.write_text(json.dumps(history, indent=2), encoding="utf-8")
