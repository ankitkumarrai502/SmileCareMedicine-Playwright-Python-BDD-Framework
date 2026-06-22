# SmileCareMedicine — E2E Automation Framework

Enterprise-grade **Playwright + Python (pytest-bdd)** end-to-end test framework for the
**customer-facing** SmileCareMedicine website. Built to demonstrate full-lifecycle SDET practice —
requirements analysis → BDD test design → automation → execution → debugging → **auto-healing** →
reporting → CI/CD — driven by a Claude AI agent pipeline, one module at a time.

> **Scope:** customer-facing journeys only. The admin dashboard is intentionally **out of scope**.

## Tech
- **pytest-bdd** (Gherkin) + Page Object Model
- **Playwright** (chromium/firefox/webkit, tracing, video)
- **Hybrid self-healing locators** — ranked candidate selectors + optional Claude AI healer
- **Allure** reporting + run **metrics** history
- **GitHub Actions** CI

## App under test
React + Vite front end on `:3000` talking to PocketBase on `:8090` via `/hcgi/platform`, in a
sibling repo (`SmileCareMedicine Development Code`). Start it with `npm install && npm run dev`
in that repo before running tests. Base URL: `http://localhost:3000`.

## Quick start
```bash
python -m venv .venv && . .venv/Scripts/activate   # Windows: .venv\Scripts\activate
make install            # deps + playwright browsers
cp .env.example .env    # fill in test user creds
make test-smoke         # once modules are automated
make report             # open Allure
```

## CI/CD (GitHub Actions)
`.github/workflows/e2e.yml` runs the suite against **production**, generates the Allure report,
and publishes it to **GitHub Pages**.

- **Triggers:** manual (`Actions → E2E Tests (Production) → Run workflow`) + weekly (Mon 06:00 UTC).
  Not on every push — each run does real logins against the live shared account.
- **Secrets required** (Settings → Secrets and variables → Actions): `SMILECARE_USER`,
  `SMILECARE_PASS`, `SMILECARE_USER_FIRSTNAME`.
- **Published report:** `https://ankitkumarrai502.github.io/SmileCareMedicine-Playwright-Python-BDD-Framework/`
  (live after the first successful run with Pages enabled).

## Reports & metrics
Test runs emit **Allure** results to `reports/allure-results/`. To view the HTML dashboard
(Overview, Suites, Graphs, **Categories** = tracked bugs, **Environment** = base URL/browser):

```bash
# one-time tooling (Allure needs Java):
winget install Microsoft.OpenJDK.17      # JRE/JDK
npm install -g allure-commandline        # Allure CLI
# then, after a test run:
make report          # quick: temp report, opens browser at http://127.0.0.1:<port>
make report-html     # persistent site in reports/allure-report/, opens browser
```
> Java's PATH applies to **new** shells only. The generated report must be **served**
> (`allure open`/`serve`) — opening `index.html` over `file://` fails (browser CORS).

Other metrics: `metrics/history.json` (per-run history), `docs/<module>-coverage.md`
(coverage dashboard), `bug_reports/bug_house.xlsx` (defect log), `reports/traces/*.zip`
(open with `playwright show-trace <file>`).

## Layout
| Path | Purpose |
|------|---------|
| `tests/features/` | Gherkin features (customer modules) |
| `tests/step_defs/` | pytest-bdd step implementations |
| `src/pages/` | Page Objects |
| `src/core/` | browser factory, base page, **healing locator**, AI healer |
| `src/api/` | PocketBase setup/teardown |
| `src/data/` | factories + encoders for packed fields |
| `config/locators/` | ranked candidate selectors per page (YAML) |
| `test_cases/` | manual test cases (pos/neg/edge) |
| `docs/test-strategy.md` | strategy & traceability |
| `metrics/` | per-run results history |
| `bug_reports/` | **Bug House** Excel defect log (`bug_house.xlsx`) |
| `.claude/` | the 7-agent QA pipeline |

## The AI agent pipeline (per module, on request)
`Planner` → `Manual Test Case Writer` → `Generator` → `Browser` → `Healer` → `Bug House` → `QA Coverage & Metrics`.
Kick it off with the `/test-module <name>` command (see `.claude/commands/test-module.md`).

> **Status:** engine implemented; first module **auth/login** automated end-to-end against
> production (17 passed, 2 tracked product bugs). Subsequent modules reuse the engine.
