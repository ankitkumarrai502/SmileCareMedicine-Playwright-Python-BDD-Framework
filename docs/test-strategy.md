# Test Strategy — SmileCareMedicine (Customer-Facing E2E)

> Skeleton. Filled in incrementally as modules are planned by the Planner agent.

## 1. Scope
**In scope (customer-facing only):** home, products (catalog/search/filter/detail), cart,
checkout, order-confirmation, track-order, my-orders, reviews, contact, auth (login/signup).
**Out of scope:** the admin dashboard and admin-login — explicitly excluded.

## 2. Objectives
End-to-end validation of customer journeys with positive, negative, and edge coverage; resilient
to a UI that lacks `data-testid`s (hybrid self-healing locators); fast feedback in CI.

## 3. Approach
- BDD with **pytest-bdd**; Gherkin features double as living requirements.
- Page Object Model over a self-healing locator layer.
- API (PocketBase) for fast arrange/cleanup; UI for the actual assertions.
- Third-party calls (Web3Forms, geo, FX) mocked for determinism.

## 4. Per-module workflow (AI agent pipeline)
Planner → Manual Test Case Writer (pos/neg/edge) → Generator (Python+Playwright) →
Browser (headed run) → Healer (on demand) → QA Coverage & Metrics. Run one module at a time.

## 5. Risks
- No stable test ids → mitigated by ranked candidate locators + healing.
- Geo/currency variability → pinned via mocks.
- Encoded fields (`strength||`, `userLocation|||`, status JSON) → centralized in `src/data/encoders.py`.

## 6. Entry / Exit criteria
TBD per module.

## 7. Traceability
Each feature scenario ↔ manual test case in `test_cases/<module>.md` ↔ Allure result.
