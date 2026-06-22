"""BasePage — shared Page Object behavior over Playwright + the healing locator.

Concrete page objects in ``src/pages/`` subclass this and declare a ``PAGE_NAME`` that maps
to ``config/locators/<PAGE_NAME>.yaml``. They locate elements by logical key via ``self.find``,
so selectors live in YAML (and can self-heal), never hard-coded in page logic.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from src.core import healing_locator
from src.utils.logger import get_logger

log = get_logger("page")


class BasePage:
    PAGE_NAME: str = ""          # subclasses set this (e.g. "login")
    PATH: str = "/"              # route relative to base_url

    def __init__(self, page: Page) -> None:
        self.page = page

    # --- navigation -------------------------------------------------------
    def open(self) -> "BasePage":
        log.info("navigate -> %s", self.PATH)
        self.page.goto(self.PATH, wait_until="domcontentloaded")
        self.page.wait_for_load_state("networkidle")
        return self

    @property
    def current_url(self) -> str:
        return self.page.url

    # --- element access (healing) ----------------------------------------
    def find(self, key: str, *, timeout_ms: int = 5000) -> Locator:
        return healing_locator.resolve(self.page, self.PAGE_NAME, key, timeout_ms=timeout_ms)

    # --- interactions -----------------------------------------------------
    def click(self, key: str) -> None:
        log.info("click %s.%s", self.PAGE_NAME, key)
        self.find(key).click()

    def fill(self, key: str, value: str) -> None:
        log.info("fill %s.%s", self.PAGE_NAME, key)
        loc = self.find(key)
        loc.fill(value)

    def text(self, key: str) -> str:
        return (self.find(key).inner_text() or "").strip()

    def is_visible(self, key: str, *, timeout_ms: int = 3000) -> bool:
        try:
            return self.find(key, timeout_ms=timeout_ms).is_visible()
        except Exception:
            return False
