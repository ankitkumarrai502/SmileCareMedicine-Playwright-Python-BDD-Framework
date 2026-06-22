"""Playwright browser/context lifecycle, driven by config.settings."""

from __future__ import annotations

from playwright.sync_api import Browser, BrowserContext, Playwright

from config.settings import Settings


def launch_browser(pw: Playwright, settings: Settings) -> Browser:
    launcher = getattr(pw, settings.browser)
    return launcher.launch(
        headless=not settings.headed,
        slow_mo=250 if settings.headed else 0,  # visible pacing for the Browser agent
    )


def new_context(browser: Browser, settings: Settings, *, record_video_dir: str | None = None) -> BrowserContext:
    ctx = browser.new_context(
        base_url=settings.base_url,
        viewport={"width": 1366, "height": 850},
        record_video_dir=record_video_dir if settings.video != "off" else None,
        ignore_https_errors=False,
    )
    ctx.set_default_timeout(settings.default_timeout_ms)
    ctx.set_default_navigation_timeout(settings.default_timeout_ms + 15000)
    return ctx
