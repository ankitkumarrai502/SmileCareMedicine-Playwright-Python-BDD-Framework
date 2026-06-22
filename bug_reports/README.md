# Bug House — persistent defect log

This folder holds **`bug_house.xlsx`**, the cumulative bug report maintained by the
`bug-house` pipeline agent (stage 6). It is intentionally **tracked in git** (not gitignored)
so the defect history survives across runs, machines, and CI — it is the project's bug memory.

## Format
- **One worksheet per module** (`auth`, `products`, `cart`, …) plus a rolled-up **`Summary`**
  sheet (totals per module + severity breakdown + open/closed).
- Standard senior-QA bug-report columns:

  | Bug ID | Module | Title | Severity | Priority | Status | Test Case ID | Environment | Steps to Reproduce | Test Data | Expected Result | Actual Result | Evidence | First Seen | Last Seen | Occurrences | Reported By | Notes |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

- **Bug ID** is stable: `BUG-<MODULE>-NNN` (e.g. `BUG-AUTH-001`).
- **Severity**: Critical / Major / Minor / Trivial — impact on the product.
- **Priority**: P1–P4 — urgency to fix.
- **Status**: New / Open / Reopened / Retest / Closed / Deferred.

## How rows are written
Never edit the `.xlsx` by hand from an agent — writes go through the deterministic logger so
the format stays consistent and bugs de-duplicate by ID:

```bash
python -m src.utils.bug_logger --add-many bugs.json   # batch of bug dicts
python -m src.utils.bug_logger --add bug.json          # single bug dict
python -m src.utils.bug_logger --summary               # rebuild Summary only
```

The logger **upserts**: a re-seen Bug ID bumps `Occurrences` + `Last Seen` (keeps `First Seen`);
a bug seen again after `Closed` is auto-flagged `Reopened`. Existing entries are never wiped.
