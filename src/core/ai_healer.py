"""Optional Claude-backed locator healer.

When the deterministic ranked candidates in ``healing_locator.py`` are exhausted,
this module sends the failing logical key + a trimmed DOM snapshot to Claude
(via the ``anthropic`` SDK) and asks for a repaired selector.

Design notes (to be implemented later):
  - Reads ``ANTHROPIC_API_KEY`` from the environment.
  - If the key is absent, this healer is a no-op so the suite still runs deterministically.
  - Proposed selectors are logged, attached to the Allure report, and optionally written
    back to the relevant ``config/locators/<page>.yaml`` as a new top-ranked candidate.

Stub for now — implemented when first needed by the Healer agent.
"""

# TODO: implement AIHealer.propose_selector(logical_key, dom_snapshot) -> str | None
