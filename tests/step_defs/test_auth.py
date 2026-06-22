"""pytest-bdd step definitions for the Login feature (tests/features/auth/login.feature).

Steps are thin: interaction logic lives in LoginPage. Case IDs (AUTH-NNN) live in the
scenario names for traceability to test_cases/auth.md and Allure.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

import pytest
from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from src.pages.login_page import LoginPage

scenarios("../features/auth/login.feature")

HOME_RE = re.compile(r"https?://[^/]+/?$")


@pytest.fixture
def bag() -> dict:
    """Cross-step scratch state (typed password, captured dialogs, etc.)."""
    return {"dialogs": []}


def _resolve(token: str, creds) -> str:
    return {"VALID_EMAIL": creds.email, "VALID_PASSWORD": creds.password}.get(token, token)


# --------------------------------------------------------------------------- #
# Given
# --------------------------------------------------------------------------- #
@given("the login page is open")
def open_login(login_page: LoginPage, bag: dict):
    login_page.page.on("dialog", lambda d: (bag["dialogs"].append(d.message), d.dismiss()))
    login_page.open()
    login_page.dismiss_cookie_banner()


# --------------------------------------------------------------------------- #
# When
# --------------------------------------------------------------------------- #
@when("I log in with valid credentials")
def login_valid(login_page: LoginPage, creds):
    login_page.login(creds.email, creds.password)


@when("I log in with valid credentials clicking submit twice")
def login_valid_double(login_page: LoginPage, creds):
    login_page.fill("email_input", creds.email)
    login_page.fill("password_input", creds.password)
    btn = login_page.find("submit_button")
    btn.click()
    try:
        btn.click(timeout=800)  # second rapid click; may be detached post-nav
    except Exception:
        pass


@when("I log in with the valid email and a wrong password")
def login_wrong_pw(login_page: LoginPage, creds):
    login_page.login(creds.email, "WrongPass!" + "123")


@when("I log in with the valid email and a wrong-case password")
def login_wrong_case_pw(login_page: LoginPage, creds):
    login_page.login(creds.email, creds.password.swapcase())


@when("I log in with the valid email in uppercase")
def login_upper_email(login_page: LoginPage, creds):
    login_page.login(creds.email.upper(), creds.password)


@when("I log in with the valid email wrapped in whitespace")
def login_ws_email(login_page: LoginPage, creds):
    login_page.login(f"   {creds.email}   ", creds.password)


@when("I submit very long credentials")
def login_long(login_page: LoginPage):
    login_page.login("a" * 300 + "@example.com", "b" * 300)


@when(parsers.re(r'I submit the login form with email "(?P<email>[^"]*)" and password "(?P<password>[^"]*)"'))
def submit_form(login_page: LoginPage, creds, email: str, password: str):
    login_page.fill("email_input", _resolve(email, creds))
    login_page.fill("password_input", _resolve(password, creds))
    login_page.submit_only()


@when("I click the sign-up link")
def click_signup(login_page: LoginPage):
    login_page.click("signup_link")


@when("I click the forgot-password link")
def click_forgot(login_page: LoginPage):
    login_page.click("forgot_password_link")
    login_page.page.wait_for_timeout(1500)


@when("I type a password into the password field")
def type_pw(login_page: LoginPage):
    login_page.fill("password_input", "Sample-Pw-123")  # arbitrary; only exercises the show/hide toggle


@when("I toggle password visibility")
def toggle_pw(login_page: LoginPage):
    login_page.toggle_password_visibility()


@when("I reload the page")
def reload_page(login_page: LoginPage):
    login_page.page.reload(wait_until="networkidle")


# --------------------------------------------------------------------------- #
# Then
# --------------------------------------------------------------------------- #
@then("the login form shows the email, password fields and the Log In button")
def form_renders(login_page: LoginPage):
    assert login_page.is_visible("email_input"), "email field missing"
    assert login_page.is_visible("password_input"), "password field missing"
    assert login_page.is_visible("submit_button"), "Log In button missing"


@then("the signup and forgot-password links are visible")
def links_visible(login_page: LoginPage):
    assert login_page.is_visible("signup_link"), "sign-up link missing"
    assert login_page.is_visible("forgot_password_link"), "forgot-password link missing"


@then("I land on the home page")
def on_home(login_page: LoginPage):
    expect(login_page.page).to_have_url(HOME_RE, timeout=15000)


@then("I am logged in")
def is_logged_in(login_page: LoginPage, creds):
    assert login_page.wait_until_logged_in(), "still see logged-out nav (Login link) after login"
    if creds.first_name:
        assert login_page.account_name_visible(creds.first_name), \
            f"account name '{creds.first_name}' not visible in nav"


@then("I am not logged in")
def not_logged_in(login_page: LoginPage):
    assert not login_page.is_logged_in(), "appears logged in but should not be"


@then("I remain on the login page")
def remain_login(login_page: LoginPage):
    assert urlparse(login_page.current_url).path.rstrip("/") in ("/login", "/login"), \
        f"expected to stay on /login, was {login_page.current_url}"


@then("I see the invalid-credentials error")
def invalid_error(login_page: LoginPage):
    text = login_page.error_toast_text()
    assert re.search(r"invalid email or password", text, re.I), f"unexpected error text: {text!r}"


@then(parsers.parse('the URL path is "{path}"'))
def url_path_is(login_page: LoginPage, path: str):
    expect(login_page.page).to_have_url(re.compile(rf"{re.escape(path)}/?$"), timeout=10000)


@then("the password is shown as plain text")
def pw_text(login_page: LoginPage):
    assert login_page.password_field_type() == "text", "password not revealed as text"


@then("the password is masked")
def pw_masked(login_page: LoginPage):
    assert login_page.password_field_type() == "password", "password not re-masked"


@then(parsers.parse('the email field has type "{t}"'))
def email_type(login_page: LoginPage, t: str):
    assert login_page.email_field_type() == t, f"email type was {login_page.email_field_type()!r}"


@then("the app responds without a crash")
def no_crash(login_page: LoginPage):
    assert login_page.page.title(), "page has no title (possible crash)"
    # either we logged in OR the login form is still usable — both are non-crash states
    assert login_page.is_logged_in() or login_page.is_visible("email_input"), \
        "neither logged-in nor a usable login form — possible crash"


@then("no browser dialog appears")
def no_dialog(bag: dict):
    assert not bag["dialogs"], f"unexpected browser dialog(s): {bag['dialogs']}"


@then("I am taken away from the login form to a password reset flow")
def reset_flow(login_page: LoginPage):
    path = urlparse(login_page.current_url).path.rstrip("/")
    assert path not in ("", "/login"), \
        f"Forgot Password did not lead to a reset flow — still at {login_page.current_url!r}"
