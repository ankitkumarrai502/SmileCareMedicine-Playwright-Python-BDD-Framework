# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is
An enterprise **Playwright + Python (pytest-bdd)** E2E automation framework for the **customer-facing
SmileCareMedicine website**. It is built incrementally, **one module at a time**, via a fixed
six-agent pipeline. The framework currently exists as a **scaffold** — most module code is written
on demand.

## Hard rules
- **Customer-facing site ONLY.** Never write or run tests against the admin dashboard or
  `/admin-login`. Excluded routes: `/admin`, `/admin-login`.
- **Do not implement module tests unless the user asks for a specific module.** When they do, run the
  pipeline below.
- **Never modify the app under test (AUT).** Treat it as a black box.

## The per-module agent pipeline (run in order)
Invoked via `/test-module <module>` (see `.claude/commands/test-module.md`). Agents live in
`.claude/agents/`:
1. **planner** → `docs/<module>-test-plan.md`
2. **manual-test-case-writer** → `test_cases/<module>.md` (positive / negative / edge, SDET mindset)
3. **generator** → `tests/features/<module>/`, `tests/step_defs/`, `src/pages/` (production-grade)
4. **browser-runner** → headed run so the user can watch; trace/video to `reports/`
5. **healer** → repairs broken locators in `config/locators/` (deterministic + optional Claude)
6. **bug-house** → triages genuine product defects (not test/locator issues) and logs them to
   `bug_reports/bug_house.xlsx` — one sheet per module, cumulative across runs (upsert by Bug ID
   via `src/utils/bug_logger.py`; never overwritten)
7. **coverage-metrics** → Allure + appends to `metrics/` (this run + prior runs)

## App under test — how to run it
Sibling repo `..\SmileCareMedicine Development Code`. From its root: `npm install` then
`npm run dev` (Vite `:3000` + PocketBase `:8090`). Tests target `http://localhost:3000`. PocketBase
is proxied at `/hcgi/platform`. Seed data: 8 categories + 40 products auto-seeded; reset by deleting
`apps/pocketbase/pb_data/`.

## Discovery stance: GREY-BOX (live-site-first)
Build tests the way an external SDET handed only the URL would: **discover each module by exploring
the running site** (`http://localhost:3000`) — navigate routes, inspect the live DOM, probe
behavior. Consult the sibling AUT source (`..\SmileCareMedicine Development Code`) **only to confirm
hard-to-see backend quirks**, never as the design starting point. The framework also never *imports*
AUT code — it interacts purely through the browser + public API. Document anything not inferable
from the UI as an explicit assumption in the module's test plan.

## Playwright MCP — DISCOVERY ONLY, token-disciplined
A Playwright MCP server is configured in `.mcp.json`, scoped tightly on purpose. Rules:
- **Use it only for DISCOVERY** — exploring the live site to author/confirm locators and probe
  behavior during the planner / generator / healer stages. It is an authoring aid, not a runtime.
- **NEVER in CI, never in the test path.** The pytest suite and `.github/workflows/e2e.yml` must
  never depend on or invoke the MCP. (CI doesn't run Claude, so the server can't start there — keep
  it that way: no test code references MCP tools.)
- **Snapshots stay narrow (token discipline is the whole point):** the config already forces
  `--image-responses=omit` (no screenshot bytes), no `vision` capability (text accessibility tree
  only), a small viewport, and `--allowed-origins` pinned to the AUT so the browser can't wander.
  On top of that, BY HABIT: navigate → snapshot **once** → extract the locators you need → move on.
  Do not re-snapshot an unchanged page, don't loop full-page snapshots, and `browser_close` when
  done. Prefer reading one element's ref over dumping the whole tree repeatedly.
- **Even tighter levers if a page is huge:** add `--snapshot-mode=none` (suppress auto post-action
  snapshots) or `--output-mode=file` (write snapshots/console/network to disk, then Grep only the
  slice you need) to `.mcp.json` args. Off by default because they make discovery clunkier.
- First browser launch downloads a chromium build for node-playwright (one-time).

## Confirmed quirks to watch for (verify against the live site)
These were observed during initial exploration. Treat them as things to confirm/handle, not as
ground truth to design around blindly:
- Almost **no `data-testid`s** — rely on input `id`s (`#email`, `#password`, `#fullName`, `#phone`,
  `#name`, `#message`), nav `href`s, ARIA roles, visible text. This is why locators are self-healing.
- **Packed fields** (decode via `src/data/encoders.py`):
  - product `strength` = `strength || packaging || JSON(additionalCategories)`
  - review `userLocation` = `Name ||| Location`
  - order status is JSON inside `shippingAddress` (pending→confirmed→shipped→delivered), not `orderStatus`.
- **Coupon** `SMILECAREFREE` needs subtotal > $500 → free shipping; base shipping $35 (<500 pills) / $65 (≥500).
- **Mock** Web3Forms (`api.web3forms.com`), `ipapi.co`, `open.er-api.com`; pin currency for price asserts.
- User auth = plain email+password on `users` collection (UI never triggers the DB-level OTP).

## Commands
- `make install` — deps + Playwright browsers
- `make test` / `make test-smoke` / `make test-headed`
- `pytest -m <marker>` — markers per module (see `pytest.ini`): `auth home products cart checkout
  orders track_order my_orders reviews contact`, plus `smoke regression needs_auth mocks_network`
- `make report` — open Allure (`reports/allure-results`)

## Conventions
- Page Objects extend `src/core/base_page.py` and locate elements through the healing layer
  (`src/core/healing_locator.py`) using logical keys backed by `config/locators/<page>.yaml`.
- Fixtures live only in `tests/conftest.py`; keep steps/pages free of setup wiring.
- Prefer the PocketBase API (`src/api/pocketbase_client.py`) for arrange/cleanup; assert through the UI.
