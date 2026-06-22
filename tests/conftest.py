"""pytest fixtures for the SmileCareMedicine customer-facing suite.

Single wiring point: settings -> playwright -> browser -> context (trace/video) -> page,
plus credentials, page objects, Allure attachments on failure, and a metrics hook that
appends per-test results to ``metrics/`` for the Coverage & Metrics agent.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import allure
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from config.settings import Settings, get_settings
from src.core.browser_factory import launch_browser, new_context
from src.pages.login_page import LoginPage

load_dotenv()

_ROOT = Path(__file__).resolve().parents[1]
_REPORTS = _ROOT / "reports"
_ALLURE = _REPORTS / "allure-results"
_TRACES = _REPORTS / "traces"
_SHOTS = _REPORTS / "screenshots"
_VIDEOS = _REPORTS / "videos"
_METRICS = _ROOT / "metrics"
for _d in (_ALLURE, _TRACES, _SHOTS, _VIDEOS, _METRICS):
    _d.mkdir(parents=True, exist_ok=True)

_RESULTS: list[dict] = []


def _safe(name: str) -> str:
    """Filesystem/artifact-safe name. Scenario names can contain <, >, ', etc. (e.g. the
    injection-payload case), which are invalid in Windows filenames AND rejected by the
    GitHub upload-artifact action — sanitize before using a node name as a file path."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)[:80]

# Confirmed PRODUCT defects (filed in bug_reports/bug_house.xlsx). The tests assert the
# CORRECT expected behavior, so they stay red against the live bug — we mark them xfail
# (non-strict) so the suite is green while the defect is tracked; an xpass signals a fix.
KNOWN_BUGS = {
    "auth015": "BUG-AUTH-002 — login email is case-sensitive (uppercase email rejected)",
    "auth019": "BUG-AUTH-001 — Forgot Password link is a dead link; no password recovery",
}


def pytest_collection_modifyitems(items):
    for item in items:
        name = item.name.lower()
        for key, reason in KNOWN_BUGS.items():
            if key in name:
                item.add_marker(pytest.mark.xfail(reason=reason, strict=False))


def pytest_sessionstart(session):
    """Seed the Allure results dir with the Environment widget + defect Categories."""
    s = get_settings()
    env = {
        "Base.URL": s.base_url,
        "Environment": os.getenv("SMILECARE_ENV", "production"),
        "Browser": s.browser,
        "Headed": str(s.headed),
        "Run.Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    (_ALLURE / "environment.properties").write_text(
        "\n".join(f"{k}={v}" for k, v in env.items()), encoding="utf-8")

    # Buckets shown in Allure's "Categories" tab.
    categories = [
        {"name": "Known product bugs (tracked)",
         "matchedStatuses": ["skipped"], "messageRegex": ".*BUG-AUTH.*"},
        {"name": "Product defects (failures)", "matchedStatuses": ["failed"]},
        {"name": "Test infrastructure / locator issues",
         "matchedStatuses": ["broken"]},
    ]
    (_ALLURE / "categories.json").write_text(json.dumps(categories, indent=2), encoding="utf-8")


@dataclass(frozen=True)
class Credentials:
    email: str
    password: str
    first_name: str


# --------------------------------------------------------------------------- #
# session-scoped
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def creds() -> Credentials:
    email = os.getenv("SMILECARE_USER")
    password = os.getenv("SMILECARE_PASS")
    if not email or not password:
        pytest.skip("SMILECARE_USER / SMILECARE_PASS not set in .env")
    return Credentials(email, password, os.getenv("SMILECARE_USER_FIRSTNAME", ""))


@pytest.fixture(scope="session")
def _playwright():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(_playwright, settings: Settings) -> Browser:
    b = launch_browser(_playwright, settings)
    yield b
    b.close()


# --------------------------------------------------------------------------- #
# function-scoped
# --------------------------------------------------------------------------- #
@pytest.fixture
def context(browser: Browser, settings: Settings, request: pytest.FixtureRequest) -> BrowserContext:
    ctx = new_context(browser, settings, record_video_dir=str(_VIDEOS))
    if settings.trace != "off":
        ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield ctx

    name = _safe(request.node.name)
    if settings.trace != "off":
        try:
            ctx.tracing.stop(path=str(_TRACES / f"{name}.zip"))
        except Exception:
            pass
    ctx.close()


@pytest.fixture
def page(context: BrowserContext, request: pytest.FixtureRequest) -> Page:
    pg = context.new_page()
    yield pg
    if getattr(request.node, "_failed", False):
        try:
            shot = pg.screenshot(full_page=True)
            pg.screenshot(path=str(_SHOTS / f"{_safe(request.node.name)}.png"), full_page=True)
            allure.attach(shot, name="failure-screenshot",
                          attachment_type=allure.attachment_type.PNG)
            allure.attach(pg.url, name="final-url", attachment_type=allure.attachment_type.TEXT)
        except Exception:
            pass


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture(autouse=True)
def _allure_meta(request: pytest.FixtureRequest):
    """Tag every test with Allure feature/story/severity + link known-bug tests to their Bug ID."""
    allure.dynamic.feature("Auth")
    allure.dynamic.story("Login")
    marker_names = [m.name for m in request.node.iter_markers()]
    if "smoke" in marker_names:
        allure.dynamic.severity(allure.severity_level.CRITICAL)
    name = request.node.name.lower()
    for key, reason in KNOWN_BUGS.items():
        if key in name:
            bug_id = reason.split(" ")[0]
            allure.dynamic.issue(bug_id, f"{bug_id} (see bug_reports/bug_house.xlsx)")
            allure.dynamic.severity(allure.severity_level.MINOR
                                    if bug_id == "BUG-AUTH-002" else allure.severity_level.NORMAL)
    yield


# --------------------------------------------------------------------------- #
# hooks: mark failures + accumulate metrics
# --------------------------------------------------------------------------- #
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        item._failed = report.failed
        _RESULTS.append({
            "test": item.name,
            "outcome": report.outcome,
            "duration_s": round(report.duration, 2),
            "markers": [m.name for m in item.iter_markers()],
        })


def pytest_sessionfinish(session, exitstatus):
    if not _RESULTS:
        return
    payload = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total": len(_RESULTS),
        "passed": sum(r["outcome"] == "passed" for r in _RESULTS),
        "failed": sum(r["outcome"] == "failed" for r in _RESULTS),
        "skipped": sum(r["outcome"] == "skipped" for r in _RESULTS),
        "tests": _RESULTS,
    }
    (_METRICS / "last_run.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
