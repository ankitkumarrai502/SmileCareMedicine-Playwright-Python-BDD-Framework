# Manual Test Cases — Auth / **Login**

> Pipeline stage 2 (Manual Test Case Writer). Module `auth`, Login flow. Source: `docs/auth-test-plan.md`.
> Environment: production `https://www.smilecaremedicine.com/login`. IDs `AUTH-NNN` are the
> traceability key to automated scenarios and Allure results.
>
> **Shared preconditions (all cases):** browser open; navigate to `/login`; cookie consent banner
> dismissed (Accept). Valid account credentials come from `.env` (`SMILECARE_USER` /
> `SMILECARE_PASS`) and GitHub Secrets — never committed. Placeholders below: `<valid email>`, `<valid password>`.

| ID | Title | Type | Priority | Preconditions | Steps | Test Data | Expected Result |
|----|-------|------|----------|---------------|-------|-----------|-----------------|
| AUTH-001 | Login page renders all elements | Pos | P2 | On `/login` | 1. Observe the login card | — | Heading "Welcome Back", Email Address field, Password field with eye toggle, "Log In" button, "Forgot Password?" and "Sign up here" links all visible |
| AUTH-002 | Successful login with valid credentials | Pos | P1 | On `/login` | 1. Enter valid email 2. Enter valid password 3. Click Log In | `<valid email>` / `<valid password>` | Redirects to `/`; nav shows first name "vaibhav" + Orders; Login/Sign Up links no longer shown |
| AUTH-003 | Session persists after page reload | Pos | P2 | Logged in (AUTH-002) | 1. Reload the page (F5) | — | User remains logged in; nav still shows the account name |
| AUTH-004 | "Sign up here" navigates to signup | Pos | P3 | On `/login` | 1. Click "Sign up here" | — | URL becomes `/signup`; signup form shown |
| AUTH-005 | Password show/hide toggle works | Pos | P3 | On `/login` | 1. Type a password 2. Click the eye toggle 3. Click it again | `<valid password>` | After 1st click password is visible as text; after 2nd click it is masked again |
| AUTH-006 | Email field uses type=email | Pos | P4 | On `/login` | 1. Inspect the email input | — | Input `type=email` (native email semantics/validation) |
| AUTH-007 | Wrong password rejected | Neg | P1 | On `/login` | 1. Enter valid email 2. Enter wrong password 3. Click Log In | `<valid email>` / `WrongPass!` | Stays on `/login`; toast "Invalid email or password. Please try again."; not logged in |
| AUTH-008 | Unregistered email rejected | Neg | P1 | On `/login` | 1. Enter non-existent email 2. Enter any password 3. Click Log In | `nouser-xyz@example.com` / `Whatever1!` | Stays on `/login`; same invalid-credentials toast; not logged in |
| AUTH-009 | Submit with both fields empty blocked | Neg | P2 | On `/login` | 1. Leave both fields empty 2. Click Log In | (empty) | Form does not submit (HTML5 required); URL unchanged; not logged in |
| AUTH-010 | Submit with email only blocked | Neg | P2 | On `/login` | 1. Enter valid email 2. Leave password empty 3. Click Log In | `<valid email>` / (empty) | Password required; no submit/auth; URL unchanged |
| AUTH-011 | Submit with password only blocked | Neg | P2 | On `/login` | 1. Leave email empty 2. Enter a password 3. Click Log In | (empty) / `<valid password>` | Email required; no submit/auth; URL unchanged |
| AUTH-012 | Malformed email rejected by validation | Neg | P2 | On `/login` | 1. Enter malformed email 2. Enter any password 3. Click Log In | `foo@` / `<valid password>` | HTML5 email validation blocks submit; no auth call; URL unchanged |
| AUTH-013 | Protected route redirects when logged out | Neg | P2 | Logged OUT | 1. Navigate directly to a protected area (Orders / `/my-orders`) | — | Redirected to login or access blocked (not shown order history) |
| AUTH-014 | Email leading/trailing whitespace | Edge | P3 | On `/login` | 1. Enter valid email wrapped in spaces 2. Valid password 3. Log In | `"  <valid email>  "` / `<valid password>` | Document actual: either trims & logs in, or shows invalid-credentials. Record observed behavior |
| AUTH-015 | Email case-insensitivity | Edge | P3 | On `/login` | 1. Enter uppercase email 2. Valid password 3. Log In | `<VALID EMAIL UPPERCASED>` / `<valid password>` | Document actual: login succeeds if email is case-insensitive (expected), else flag |
| AUTH-016 | Password is case-sensitive | Edge | P2 | On `/login` | 1. Valid email 2. Wrong-case password 3. Log In | `<valid email>` / `<valid password, wrong case>` | Login fails; invalid-credentials toast; not logged in |
| AUTH-017 | Very long inputs handled gracefully | Edge | P3 | On `/login` | 1. Enter 256+ char email & password 2. Log In | 300-char strings | No crash/500; invalid-credentials or validation; app stays responsive |
| AUTH-018 | Injection strings safely rejected | Edge | P2 | On `/login` | 1. Enter SQL/script payloads 2. Log In | `' OR 1=1 --` / `<script>alert(1)</script>` | Treated as invalid credentials; no error leak, no script execution, no login |
| AUTH-019 | Forgot Password link destination | Edge | P3 | On `/login` | 1. Click "Forgot Password?" | — | Record where it leads. Expected: a reset page. Observed `href=/login` → if it does NOT lead to a reset flow, raise as a defect |
| AUTH-020 | Double / rapid submit | Edge | P3 | On `/login` | 1. Enter valid creds 2. Click Log In twice rapidly | valid creds | Single login; no duplicate requests breaking UI; no error |

**Counts:** 20 total — Positive: 6 (AUTH-001..006), Negative: 7 (AUTH-007..013), Edge: 7 (AUTH-014..020).

*Path written:* `test_cases/auth.md`. Next stage: Generator turns these into `.feature` + step defs + page object + ranked locators (1:1 with these IDs).
