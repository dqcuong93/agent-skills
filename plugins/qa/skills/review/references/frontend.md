# Frontend checklist

Framework-agnostic. Report only items the change affects.

## 1. Structure

- [ ] **Placement**: Pages, layouts, components, composables/hooks, and utilities live in the folders the profile's `Layout` and project conventions name.
- [ ] **Size**: No component past ~300 lines or doing more than one job; split by responsibility.
- [ ] **Imports**: The project's path alias is used instead of deep relative paths (`../../..`).
- [ ] **Naming**: Components PascalCase, functions and variables camelCase, constants UPPER_SNAKE; domain names, not `data`/`temp`/`x`.

## 2. Data and state

- [ ] **One API client**: Requests go through the project's shared client or helper; no ad-hoc `fetch`/`axios` that re-implements base URL, auth, or error handling.
- [ ] **No duplicate or waterfall requests**: Independent calls run in parallel; the same data is not fetched twice for one view.
- [ ] **Errors handled**: A failed request shows a user-facing message and leaves the UI usable; no unhandled promise rejection.
- [ ] **Loading and empty states**: Async views show a loading indicator and an empty state with a next action.
- [ ] **Unresolved state**: Content that depends on state fetched at load (session, user, permissions, a flag) shows neutral content or a skeleton until that state is known. A `v-else` or default branch that also covers "not loaded yet" flashes the wrong content (a signed-in user sees the guest copy first), and a placeholder that grows when the state arrives shifts the layout.
- [ ] **Failed check is not "no"**: A request that fails (network, 5xx) is not treated as a negative answer (not signed in, no permission). Show an error or retry, not the restricted view.
- [ ] **Expired session**: When the server rejects a request for auth after the page loaded (401), the user sees a clear message and a way to sign in again, not the raw framework error text or a generic failure.
- [ ] **Copy matches the user**: Text, hints, and counts name only what the current user can do or see. A notice that lists categories or features the user's role cannot reach is wrong for that user.
- [ ] **Values captured once**: A date, time, or other value read once at setup or module scope and used on a page that stays open (presets, "today", ranges) goes stale; compute it where it is used.
- [ ] **Double submit**: Submit buttons are disabled while a request is in flight and re-enabled on both success and failure.

## 3. Accessibility

- [ ] **Labels**: Every form input has a `<label>` (`for`/`id` or wrapping).
- [ ] **Names**: Icon-only buttons have `aria-label`; decorative icons have `aria-hidden="true"`.
- [ ] **Keyboard**: Interactive elements are reachable and operable by keyboard, with a visible `:focus-visible` style; tab order follows reading order.
- [ ] **Alt text**: Meaningful images have descriptive `alt`; decorative images `alt=""`.
- [ ] **Semantics**: `<button>`, `<a>`, `<nav>`, `<main>`, `<form>` used for their roles, not clickable `<div>`s.
- [ ] **Colour**: Colour is not the only signal of state; text contrast at least 4.5:1 in every theme the project ships.

## 4. Styling and motion

- [ ] **Interaction states**: Interactive elements have hover and focus feedback and a pointer cursor.
- [ ] **Responsive**: Works at 375, 768, 1024, and 1440 px wide with no horizontal scroll on mobile.
- [ ] **Animation cost**: Only `transform` and `opacity` are animated; no animating `width`/`height`/`top`/`left`/`box-shadow`.
- [ ] **Reduced motion**: `prefers-reduced-motion` handling is kept and covers new animation.

## 5. Security

- [ ] **XSS**: No `v-html`, `set:html`, `innerHTML`, or `dangerouslySetInnerHTML` with content a user or external system controls, unless sanitised.
- [ ] **Secrets**: No API keys, tokens, or private URLs in client code or in build-time variables exposed to the browser.
- [ ] **CSRF**: The framework's CSRF mechanism is not bypassed or stripped from requests.
- [ ] **External links**: `target="_blank"` links carry `rel="noopener noreferrer"`.
- [ ] **Sensitive data**: Tokens and personal data are not logged to the console or kept in persistent browser storage beyond need.
- [ ] **Uploads**: Client-side type and size checks in addition to the server's.

## 6. Performance

- [ ] **Lazy loading**: Large, rarely used, or below-the-fold components and routes load on demand.
- [ ] **Images**: Modern format where possible, explicit dimensions, lazy below the fold.
- [ ] **Bundle**: No large dependency added for a small use; check build output when dependencies change.
- [ ] **Derived values**: Computed once, not recalculated in templates on every render.

## 7. Code quality and tests

- [ ] **Leftovers**: No `console.*`, commented-out code, or unused imports in merge-ready code.
- [ ] **Lint/format**: The profile's lint and format commands pass on changed files.
- [ ] **Comments**: Explain why, not what. A comment or JSDoc that still describes the old behaviour after the change is a contract bug (WARNING).
- [ ] **Tests**: Changed utilities, stores, and composables have unit tests; a bug fix has a regression test.
- [ ] **Tests can fail**: Each new test would fail if the behaviour it covers were removed. An assertion that holds either way (`not.toThrow()` on code that cannot throw, checking a mock's return) proves nothing (WARNING).
