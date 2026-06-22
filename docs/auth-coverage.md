# Coverage & Metrics — Auth / Login (Run 1)

> Pipeline stage 7. Environment: **production** `https://www.smilecaremedicine.com`.
> Run timestamp: see `metrics/history.json`. Authoritative run: headless full pass after healing.

## Module dashboard

| Module | Authored | Automated | Passing | Known-bug (xfail) | Failed | Deferred | Pass rate* |
|--------|---------:|----------:|--------:|------------------:|-------:|---------:|-----------:|
| auth (login) | 20 | 19 | 17 | 2 | 0 | 1 | 100% |

\* Pass rate = passed / (passed + hard-failed). The 2 known bugs are tracked as `xfail`, not failures.

## This run — per-case status

| Result | Cases |
|--------|-------|
| ✅ Passed (17) | AUTH-001..012, AUTH-014, AUTH-016, AUTH-017, AUTH-018, AUTH-020 |
| 🐞 xfail / known bug (2) | AUTH-015 → BUG-AUTH-002 (case-sensitive email) · AUTH-019 → BUG-AUTH-001 (Forgot Password dead link) |
| ⏸️ Deferred (1) | AUTH-013 (protected-route redirect — verified at the `my_orders` boundary, not in this flow) |

## Defects filed (Bug House → `bug_reports/bug_house.xlsx`)
- **BUG-AUTH-001** — *Major / P2* — Forgot Password link is a dead link; no password recovery flow. (AUTH-019)
- **BUG-AUTH-002** — *Minor / P3* — Login email is case-sensitive; uppercase email of a valid account is rejected. (AUTH-015)

## Healing / stabilization this run
- Fixed step matcher to accept empty fields (test-code): AUTH-009/010/011 (`parsers.re`).
- Hardened the invalid-credentials toast wait (short-lived, server round-trip): AUTH-008.
- 0 locator heals required — ranked candidate selectors all resolved on the top candidate.

## Trends
- First run for this project — no historical baseline yet. `metrics/history.json` now seeded;
  subsequent runs/modules will accumulate pass-rate, flaky, slowest, and heal-frequency trends.

## Reports & evidence
- Allure results: `reports/allure-results/` (541 files). View with `allure serve reports/allure-results`
  *(requires the Allure CLI + Java; not installed in this run).*
- Playwright traces: `reports/traces/*.zip` (18) — incl. evidence for both filed bugs.
  View with `playwright show-trace reports/traces/<name>.zip`.
- Videos: `reports/videos/` · failure screenshots: `reports/screenshots/`.
