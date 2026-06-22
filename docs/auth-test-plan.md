# Test Plan — Auth / **Login** (SmileCareMedicine)

> Pipeline stage 1 (Planner). Module: `auth` — **Login flow only** (Sign Up is the next auth flow).
> Environment: **Production** `https://www.smilecaremedicine.com`. Discovery: grey-box, live-site-first
> (DOM + behavior probed directly; sibling source consulted only to confirm quirks).

## 1. Scope

**In scope (this run):** the customer Login journey at `/login` — rendering, field validation,
authentication success/failure, post-login session state, navigation to/from signup & forgot-password,
and the password show/hide control.

**Out of scope:** Sign Up (`/signup`, next flow), admin login (excluded entirely), password-reset
*completion*, and any destructive action. No account creation on production.

## 2. Preconditions & Data

| Item | Value |
|------|-------|
| Login URL | `https://www.smilecaremedicine.com/login` |
| Valid account (positive) | existing user; credentials from `.env` (`SMILECARE_USER` / `SMILECARE_PASS`) + GitHub Secrets — never committed |
| Invalid account (negative) | non-existent email + any password |
| Cookie banner | A consent banner (Accept / Reject) appears on first load — **must be dismissed** before interacting |
| Auth mechanism | Plain email + password (PocketBase `users` collection via `/hcgi/platform`). DB-level OTP exists but the UI never triggers it — **not tested**. |

**Stable selectors (confirmed on live DOM):**
- Email: `#email` (type=email, label "Email Address", placeholder `name@example.com`)
- Password: `#password` (type=password) + a show/hide **eye** toggle button inside the field
- Submit: button with text **"Log In"**
- Links: "Forgot Password?" (currently `href=/login`), "Sign up here" → `/signup`
- Logged-in oracle: nav shows the user's first name (**"vaibhav"**) + "Orders"; Login/Sign Up disappear
- Error oracle: a transient red toast **"Invalid email or password. Please try again."** (bottom-right; short-lived — capture immediately / poll, do not wait 4s+)

## 3. Test Conditions

### Positive
- P1. Page renders: heading "Welcome Back", email & password fields, Log In button, links present.
- P2. Valid email + valid password → authenticates, redirects to `/`, nav shows first name + Orders.
- P3. Session persists on full page reload after login (still logged in).
- P4. "Sign up here" navigates to `/signup`.
- P5. Password show/hide toggle reveals then re-masks the typed password (`type` flips text↔password).
- P6. Email field is `type=email` (gets native email keyboard/validation affordance).

### Negative
- N1. Valid email + **wrong** password → stays on `/login`, shows "Invalid email or password" toast, not logged in.
- N2. **Unregistered** email + any password → same invalid-credentials toast, not logged in.
- N3. Submit with **both fields empty** → blocked (HTML5 required / no navigation), not logged in.
- N4. Submit with **email only** (no password) → blocked / validation.
- N5. Submit with **password only** (no email) → blocked / validation.
- N6. **Malformed email** (e.g. `foo@`, `foo.com`) → HTML5 email validation prevents submit.
- N7. Protected route while logged out (e.g. `/my-orders` or Orders) → redirected to login / blocked. *(boundary with other modules; verify-only)*

### Edge
- E1. Leading/trailing **whitespace** around a valid email → does it trim and authenticate, or fail? (document actual behavior).
- E2. **Wrong case** email (`VAIBHAVDADA@GMAIL.COM`) → does login still succeed (email case-insensitivity)?
- E3. Password **case-sensitivity** (wrong-case variant of the correct password) → must fail.
- E4. **Very long** inputs (e.g. 256+ char email/password) → graceful handling, no crash.
- E5. Injection-style strings (`' OR 1=1 --`, `<script>`) in fields → safely rejected, no error leak.
- E6. **Forgot Password?** link → record where it actually goes (observed `href=/login`; likely a gap — flag as a finding, not an assumption).
- E7. **Double-click / rapid submit** of Log In → no duplicate side effects, no UI break.
- E8. Repeated invalid attempts → watch for rate-limiting / lockout behavior (and the production risk it implies).

## 4. Oracles (what proves pass/fail)
- **Auth success:** URL becomes `/` AND nav contains the account first name (Login/Sign Up gone).
- **Auth failure:** URL stays `/login` AND the "Invalid email or password. Please try again." toast appears AND not logged in.
- **Client validation:** form does not submit (URL unchanged, no network auth call) for empty/malformed input.

## 5. Risks & flakiness sources
- **Production data-safety:** login is read-only (safe), but repeated negative attempts may trigger rate-limiting — keep negative volume modest; no account creation here.
- **Transient toast:** the error toast is short-lived → assert with a fast/polling wait, not a fixed sleep.
- **SPA timing:** client-rendered; use Playwright auto-wait / network-idle, never hard sleeps.
- **Cookie banner** can overlay controls → dismiss in a fixture before each test.
- **Third-party noise:** geo/FX (ipapi.co, open.er-api.com) calls fire on load; irrelevant to login but may slow first paint — allow generous nav timeout (20s, per `production.yaml`).
- **Shared live account:** the positive account is real and shared; tests must not mutate its data.

## 6. Out-of-scope notes / assumptions
- OTP/2FA not exercised (UI never triggers it).
- Password-reset completion not tested (only the link's destination is observed).
- "Orders" appears in nav even when logged out — its auth-gating is verified at the boundary (N7) but full order journeys belong to the `my_orders` module.

---
*Next stage:* Manual Test Case Writer expands these conditions into `test_cases/auth.md` with concrete steps, data, and expected results, using stable IDs `AUTH-NNN`.
