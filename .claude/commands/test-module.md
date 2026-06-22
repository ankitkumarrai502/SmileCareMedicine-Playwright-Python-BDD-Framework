---
description: Run the full 6-agent QA pipeline for ONE customer-facing module of SmileCareMedicine.
argument-hint: <module> (e.g. auth | home | products | cart | checkout | orders | track_order | my_orders | reviews | contact)
---

Run the SmileCareMedicine QA pipeline for the module: **$ARGUMENTS**

Hard rules:
- Customer-facing site ONLY. If the module is admin-related, refuse — it is out of scope.
- Execute the stages **in order**, passing each stage's output file to the next. Pause and show the
  user the result after each stage; do not silently chain past a failure.

Stages (use the matching subagent for each):
1. **planner** — produce `docs/$ARGUMENTS-test-plan.md`.
2. **manual-test-case-writer** — produce `test_cases/$ARGUMENTS.md` (positive / negative / edge).
3. **generator** — write the feature files, step defs, page objects, and ranked locators for
   `$ARGUMENTS` (and, if this is the first module, the shared engine). Confirm `pytest --collect-only`.
4. **browser-runner** — run the `$ARGUMENTS` tests headed so the user can watch; capture artifacts.
5. **healer** — ONLY if stage 4 reports a locator/brittleness failure; repair and re-verify.
6. **bug-house** — triage this run's genuine product defects (not locator/test issues) with a
   senior-QA mindset and record them in `bug_reports/bug_house.xlsx` (per-module sheets,
   cumulative across runs). Skip only if no real app defects were found.
7. **coverage-metrics** — update `metrics/` and present this-run + historical coverage and the Allure report.

Before stage 4, verify the AUT is running on http://localhost:3000 (and :8090). If not, tell the
user to start it (`npm install && npm run dev` in the sibling `SmileCareMedicine Development Code`
repo) before continuing.
