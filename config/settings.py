"""Typed framework settings — loads `config/environments/<env>.yaml` + `.env`.

Select the environment with the ``SMILECARE_ENV`` env var (default ``production`` for this
suite, since the live site is the agreed target). Any field can be overridden by an env var
of the same name (e.g. ``BASE_URL``, ``HEADED``, ``BROWSER``).
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_DIR = Path(__file__).resolve().parent / "environments"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    base_url: str = "https://www.smilecaremedicine.com"
    pocketbase_proxy: str = "/hcgi/platform"
    pocketbase_direct: Optional[str] = None

    browser: Literal["chromium", "firefox", "webkit"] = "chromium"
    headed: bool = True
    default_timeout_ms: int = 20000

    # artifact policy (Playwright-friendly strings)
    trace: str = "on"
    video: str = "retain-on-failure"
    screenshot: str = "only-on-failure"

    healing_enabled: bool = True
    ai_healing_enabled: bool = False
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")

    # production data-safety guardrails
    allow_destructive: bool = False
    cleanup_via_api: bool = False

    @property
    def pocketbase_url(self) -> str:
        return self.base_url.rstrip("/") + self.pocketbase_proxy


def _load_env_yaml(env: str) -> dict:
    path = _ENV_DIR / f"{env}.yaml"
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    flat: dict = {}
    for key, val in data.items():
        if key == "artifacts" and isinstance(val, dict):
            flat.update({k: v for k, v in val.items()})
        elif key == "healing" and isinstance(val, dict):
            flat["healing_enabled"] = val.get("enabled", True)
            flat["ai_healing_enabled"] = val.get("ai_enabled", False)
        elif key == "data_safety" and isinstance(val, dict):
            flat["allow_destructive"] = val.get("allow_destructive", False)
            flat["cleanup_via_api"] = val.get("cleanup_via_api", False)
        else:
            flat[key] = val
    return flat


@lru_cache
def get_settings() -> Settings:
    env = os.getenv("SMILECARE_ENV", "production")
    yaml_values = _load_env_yaml(env)
    # env vars (already read by BaseSettings) win over yaml defaults
    return Settings(**yaml_values)
