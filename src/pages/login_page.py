"""Login Page Object for SmileCareMedicine (/login)."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from src.core.base_page import BasePage
from src.utils.logger import get_logger

log = get_logger("login")


class LoginPage(BasePage):
    PAGE_NAME = "login"
    PATH = "/login"

    # --- setup -----------------------------------------------------------
    def dismiss_cookie_banner(self) -> "LoginPage":
        """Accept the cookie consent banner if it is showing (it overlays controls)."""
        try:
            btn = self.find("cookie_accept", timeout_ms=3000)
            if btn.is_visible():
                btn.click()
                self.page.wait_for_timeout(400)
        except Exception:
            pass  # banner not present (already dismissed for this context)
        return self

    # --- actions ---------------------------------------------------------
    def login(self, email: str, password: str) -> None:
        self.fill("email_input", email)
        self.fill("password_input", password)
        self.click("submit_button")

    def submit_only(self) -> None:
        self.click("submit_button")

    def toggle_password_visibility(self) -> None:
        self.click("password_toggle")

    def password_field_type(self) -> str:
        return self.find("password_input").get_attribute("type") or ""

    def email_field_type(self) -> str:
        return self.find("email_input").get_attribute("type") or ""

    # --- oracles ---------------------------------------------------------
    def error_toast_text(self, *, timeout_ms: int = 10000) -> str:
        """Return the invalid-credentials toast text.

        The toast is short-lived AND can appear only after a server round-trip, so we give
        the top (text-based) candidate a generous window and let Playwright auto-retry to
        catch it as soon as it renders.
        """
        loc = self.find("error_toast", timeout_ms=timeout_ms)
        expect(loc).to_be_visible(timeout=timeout_ms)
        return (loc.inner_text() or "").strip()

    def is_logged_in(self) -> bool:
        """Quick snapshot oracle: the logged-out 'Login' nav link is not visible."""
        return not self.is_visible("login_nav_link", timeout_ms=3000)

    def wait_until_logged_in(self, *, timeout_ms: int = 12000) -> bool:
        """Robust positive oracle: poll until the logged-out 'Login' nav link disappears.

        Production redirect + header re-render can lag behind the click, so we wait
        (auto-retrying) rather than snapshotting once — this kills the P1 smoke flake.
        """
        try:
            expect(self.page.locator("header a[href='/login']").first).to_be_hidden(timeout=timeout_ms)
            return True
        except Exception:
            return not self.is_visible("login_nav_link", timeout_ms=1000)

    def account_name_visible(self, name: str) -> bool:
        try:
            return self.page.get_by_text(name, exact=False).first.is_visible(timeout=4000)
        except Exception:
            return False

    def native_validation_message(self, field_key: str) -> str:
        """Read the HTML5 validation message for a required/invalid field."""
        loc = self.find(field_key)
        return loc.evaluate("el => el.validationMessage") or ""
