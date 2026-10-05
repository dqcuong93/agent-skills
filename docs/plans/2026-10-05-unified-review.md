# Unified `/qa:review` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `/qa:review-backend` with one `/qa:review` skill that reviews backend and frontend changes, routed by the project profile, and prove it on two real projects while their old skills keep running.

**Architecture:** One skill (`plugins/qa/skills/review/`) with a short `SKILL.md` (workflow, routing table, finding rules, severity, output) and flat reference files named `<layer>.md` / `<layer>-<stack>.md`. `stack-signals.md` maps dependencies to stack keys and lists manifests. A stdlib Python check script enforces the structural rules; behaviour is verified by headless `claude -p` runs.

**Tech Stack:** Claude Code plugin (Markdown skills), Python 3 stdlib (check script), GitHub Actions.

**Spec:** `docs/specs/2026-10-05-unified-review-design.md`

## Global Constraints

- Public repo: no project names, client names, domains, hosts, machine paths, credentials, or business rules in any tracked file. Spec calls the source projects "Project A" and "Project B".
- Never run `git commit`, `git push`, or `git tag`. Each "Commit" step prints the command for the owner to run.
- Plugin version becomes `0.2.0` (breaking rename).
- References are one level deep: `SKILL.md` links every reference file; reference files link to nothing.
- Every `<layer>-<stack>.md` pack starts with `Written for: <stack> <major>` on line 3.
- `!` injection lines contain no `|`, `||`, `&&`, `;`, or `( … )`.
- Nothing is deleted from Project A or Project B in this wave; the only file written there is `.claude/project-profile.md`, and only after the owner approves it.
- Shell is zsh: in commands use `printf`, not `echo =====`; quote globs.
- In commands, `<agent-skills>` is the path to this repo's checkout and `$SCRATCH` a scratch directory outside both repos; never write a real machine path into a tracked file.

## Review Focus

1. **Overlapping layout paths** (Project B: backend `.`, frontend `frontend/`): a `.vue` file under `frontend/` must route to frontend, not backend. Pinned in Task 8 Step 4.
2. **No-profile question skipped:** the model must stop after asking, not ask and review in one turn. Pinned in Task 7 Step 3 (3 runs).
3. **Single-layer diff:** a frontend-only change must not load or cite `backend*.md`. Pinned in Task 9 Step 2.
4. **`--no-ask` without a profile:** must finish a review with no question and mark layers "assumed". Pinned in Task 7 Step 4.
5. **Severity override vs merge/table:** an override line must fix the level exactly. Pinned in Task 9 Step 4.

---

### Task 1: Structural check script

**Files:**
- Create: `scripts/check-plugin.py`
- Modify: `.github/workflows/validate.yml`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `python3 scripts/check-plugin.py` → exit 0 and prints `OK (<n> checks)`, or exit 1 and prints one `FAIL <rule>: <detail>` line per problem. Later tasks run it after every change.

- [ ] **Step 1: Write the script**

```python
#!/usr/bin/env python3
"""Structural checks for the qa plugin that `claude plugin validate` does not cover."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "qa"
REVIEW = PLUGIN / "skills" / "review"
REFS = REVIEW / "references"
SIGNALS = PLUGIN / "stack-signals.md"
BANNED = ROOT / ".banned-words"  # gitignored, one word per line, optional

WRITTEN_FOR = re.compile(r"^Written for: \S.* \d+$")
INJECTION = re.compile(r"!`([^`]*)`")
SHELL_OPS = ("|", "&&", ";", "(", ")")


def main() -> int:
    fails: list[str] = []
    checks = 0

    skill = REVIEW / "SKILL.md"
    if not skill.is_file():
        print(f"FAIL structure: {skill.relative_to(ROOT)} missing")
        return 1
    skill_text = skill.read_text()

    refs = sorted(REFS.glob("*.md"))
    if not refs:
        fails.append("structure: no reference files")

    signal_text = SIGNALS.read_text() if SIGNALS.is_file() else ""
    for ref in refs:
        name = ref.name
        text = ref.read_text()
        checks += 1
        if f"references/{name}" not in skill_text:
            fails.append(f"linked: references/{name} not linked from SKILL.md")
        checks += 1
        if re.search(r"\]\([^)]*\.md\)|references/", text):
            fails.append(f"one-level: {name} links to another file")
        if "-" in ref.stem:
            key = ref.stem.split("-", 1)[1]
            lines = text.splitlines()
            checks += 1
            if len(lines) < 3 or not WRITTEN_FOR.match(lines[2]):
                fails.append(f"written-for: {name} line 3 is not 'Written for: <stack> <major>'")
            checks += 1
            if f"| `{key}` |" not in signal_text:
                fails.append(f"signals: stack key `{key}` has no row in stack-signals.md")

    for skill_md in sorted(PLUGIN.glob("skills/*/SKILL.md")):
        for cmd in INJECTION.findall(skill_md.read_text()):
            checks += 1
            if any(op in cmd for op in SHELL_OPS):
                fails.append(f"injection: {skill_md.relative_to(ROOT)} runs `{cmd}`")

    if BANNED.is_file():
        words = [w.strip().lower() for w in BANNED.read_text().splitlines() if w.strip()]
        tracked = subprocess.run(
            ["git", "ls-files", "-co", "--exclude-standard"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.split()
        for rel in tracked:
            path = ROOT / rel
            if path.suffix not in {".md", ".json", ".yml", ".py", ".excalidraw"} or not path.is_file():
                continue
            low = path.read_text(errors="ignore").lower()
            for word in words:
                checks += 1
                if word in low:
                    fails.append(f"public: {rel} contains a banned word")

    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print(f"OK ({checks} checks)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Ignore the local banned-word list and create it**

Append to `.gitignore`:

```text
# local list of project/client names that must never be committed (read by scripts/check-plugin.py)
.banned-words
```

Create `.banned-words` (untracked) with the owner's project and client names, one per line. Ask the owner for the list; do not invent it.

- [ ] **Step 3: Run it to verify it fails on the current tree**

Run: `python3 scripts/check-plugin.py`
Expected: exit 1, `FAIL structure: plugins/qa/skills/review/SKILL.md missing`

- [ ] **Step 4: Add it to CI**

In `.github/workflows/validate.yml`, after the `Validate plugins` step, add:

```yaml
      - name: Structural checks
        run: python3 scripts/check-plugin.py
```

- [ ] **Step 5: Commit (print only)**

```bash
git add scripts/check-plugin.py .github/workflows/validate.yml .gitignore
git commit -m "chore: add structural check script for the qa plugin"
```

---

### Task 2: Move backend references and update stack signals

**Files:**
- Move: `plugins/qa/skills/review-backend/references/common.md` → `plugins/qa/skills/review/references/backend.md`
- Move: `…/references/python.md` → `…/review/references/backend-python.md`
- Move: `…/references/django.md` → `…/review/references/backend-django.md`
- Move: `…/references/sqlalchemy.md` → `…/review/references/backend-sqlalchemy.md`
- Move: `…/references/fastapi.md` → `…/review/references/backend-fastapi.md`
- Modify: `plugins/qa/stack-signals.md`

**Interfaces:**
- Produces: pack file names `backend-<key>.md`; stack keys `python`, `django`, `sqlalchemy`, `fastapi`, `inertia`, `vue`, `astro`, `tailwind` all have rows in `stack-signals.md`; `## Manifests` section that Tasks 3 and 5 read.

- [ ] **Step 1: Move the files**

```bash
mkdir -p plugins/qa/skills/review/references
git mv plugins/qa/skills/review-backend/references/common.md plugins/qa/skills/review/references/backend.md
git mv plugins/qa/skills/review-backend/references/python.md plugins/qa/skills/review/references/backend-python.md
git mv plugins/qa/skills/review-backend/references/django.md plugins/qa/skills/review/references/backend-django.md
git mv plugins/qa/skills/review-backend/references/sqlalchemy.md plugins/qa/skills/review/references/backend-sqlalchemy.md
git mv plugins/qa/skills/review-backend/references/fastapi.md plugins/qa/skills/review/references/backend-fastapi.md
```

- [ ] **Step 2: Retitle `backend.md` and add `Written for` to each pack**

`backend.md` line 1 becomes `# Backend checklist` (was `# Common backend checklist`); keep the rest.

Make lines 1–3 of each pack exactly:

```text
# Python stack pack

Written for: Python 3
```

```text
# Django / DRF stack pack

Written for: Django 6
```

```text
# SQLAlchemy stack pack

Written for: SQLAlchemy 2
```

```text
# FastAPI / Pydantic v2 stack pack

Written for: FastAPI 0
```

Each pack already has its title on line 1 and a blank line 2: replace line 1 with the title above, then insert `Written for: …` and one blank line after line 2. Everything else is kept.

- [ ] **Step 3: Remove the project-specific item from `backend-django.md`**

Delete these two lines (the section and its only item):

```text
## i18n / <language> data
- [ ] **Slugs for closed sets**: <the existing item about diacritic-stripped slugs colliding>
```

Note the removed text in the Task 8 handoff: it goes into Project A's profile under `Backend checks`.

- [ ] **Step 4: Rewrite `stack-signals.md`**

```markdown
# Stack signals

Single source for mapping a project's dependencies to stack keys. Used by `init-profile` (to draft `stacks`) and `review` (layout question and drift).

A stack key has a **pack** when a file `references/<layer>-<key>.md` exists under `skills/review/`. Keys without a pack are still reported by name so the user knows they are unreviewed.

## Manifests

Read these files to find dependencies. Search the project root and each `Layout` path from the profile; without a profile, the root and one directory down.

- `pyproject.toml` (`[project] dependencies`, `[tool.poetry.dependencies]`, `[dependency-groups]`)
- `requirements*.txt`
- `setup.cfg` (`install_requires`)
- `package.json` (`dependencies`, `devDependencies`)

## Signals

Match a signal case-insensitively against dependency names. Ignore dependencies that match no row.

| Stack key | Layer | Signals (dependency names) |
|---|---|---|
| `python` | backend | any Python manifest above |
| `django` | backend | `django`, `djangorestframework`, `drf-spectacular` |
| `fastapi` | backend | `fastapi`, `starlette` |
| `sqlalchemy` | backend | `sqlalchemy`, `sqlmodel` |
| `pydantic` | backend | `pydantic`, `pydantic-settings` |
| `celery` | backend | `celery` |
| `temporal` | backend | `temporalio` |
| `pgvector` | backend | `pgvector` |
| `pyqt` | backend | `pyqt5`, `pyqt6`, `pyside2`, `pyside6` |
| `inertia` | frontend | `@inertiajs/vue3`, `@inertiajs/react`, `inertia-django`, `django-inertia` |
| `vue` | frontend | `vue` |
| `nuxt` | frontend | `nuxt` |
| `astro` | frontend | `astro` |
| `tailwind` | frontend | `tailwindcss` |
| `docker` | infra | a `Dockerfile` or `docker-compose*.yml` / `compose*.yaml` at the project root |
```

- [ ] **Step 5: Run the check**

Run: `python3 scripts/check-plugin.py`
Expected: still `FAIL structure: …/review/SKILL.md missing` (SKILL.md comes in Task 3).

- [ ] **Step 6: Commit (print only)**

```bash
git add -A plugins/qa
git commit -m "refactor(qa): move backend packs under review/ and add stack layers"
```

---

### Task 3: `/qa:review` SKILL.md

**Files:**
- Create: `plugins/qa/skills/review/SKILL.md`
- Delete: `plugins/qa/skills/review-backend/SKILL.md` (directory becomes empty and goes away)

**Interfaces:**
- Consumes: `references/*.md` names from Task 2 and Task 4; `stack-signals.md` sections `## Manifests`, `## Signals`.
- Produces: `/qa:review [backend|frontend] [--no-ask] [path | branch | commit | range | staged]`; output sections Verdict, Findings, Profile drift, Commands run, Not checked.

- [ ] **Step 1: Write `SKILL.md`**

````markdown
---
name: review
description: Use when reviewing backend or frontend code (services, APIs, ORM/DB, jobs, components, pages, styling) for correctness, security, performance, test gaps, or project invariants — on uncommitted changes, a branch, a commit range, staged files, or a path, or before merging.
argument-hint: "[backend|frontend] [--no-ask] [path | branch | commit | range | staged]"
allowed-tools: Bash(git status *) Bash(git diff *) Bash(git log *) Bash(git show *) Read Glob Grep
---

# QA review

Generic review workflow. Project facts come from `.claude/project-profile.md`. Layer and stack rules come from the reference files below.

## Change scope

!`git status --short --untracked-files=normal`

Arguments: `$ARGUMENTS`

- `backend` or `frontend`: review only that layer.
- `--no-ask`: never stop to ask. Used by headless runs and other skills.
- `staged`, a branch, a commit, a range (`A..B`), or a path: what to review. Empty: uncommitted changes. If there are none, ask what to review; with `--no-ask`, report `Nothing to review` and stop.

## Reference files

Load only what step 4 selects. A pack's stack key is the part of its name after the layer.

| File | Load when |
|---|---|
| [references/backend.md](references/backend.md) | a backend file is in scope |
| [references/backend-python.md](references/backend-python.md) | backend in scope and `python` in stacks |
| [references/backend-django.md](references/backend-django.md) | backend in scope and `django` in stacks |
| [references/backend-sqlalchemy.md](references/backend-sqlalchemy.md) | backend in scope and `sqlalchemy` in stacks |
| [references/backend-fastapi.md](references/backend-fastapi.md) | backend in scope and `fastapi` in stacks |
| [references/frontend.md](references/frontend.md) | a frontend file is in scope |
| [references/frontend-vue.md](references/frontend-vue.md) | frontend in scope and `vue` in stacks |
| [references/frontend-inertia.md](references/frontend-inertia.md) | frontend in scope and `inertia` in stacks |
| [references/frontend-astro.md](references/frontend-astro.md) | frontend in scope and `astro` in stacks |
| [references/frontend-tailwind.md](references/frontend-tailwind.md) | frontend in scope and `tailwind` in stacks |

Stack signals and the manifest list: `${CLAUDE_PLUGIN_ROOT}/stack-signals.md`.

## Steps

1. **Profile.** Read `.claude/project-profile.md`. If it does not exist, the profile is `NO_PROFILE`.

2. **Layout.**
   - **With a profile:** assign each changed file to the layer whose `Layout` path contains it. When several match, the longest path wins (`frontend/` beats `.`).
   - **`NO_PROFILE`, no `--no-ask`:** do not guess layers from file extensions. Read the manifests listed in `stack-signals.md` at the root and one directory down, map their dependencies to stack keys, then ask the user in the conversation's language, filled in with what you found:

     > This repo has no `.claude/project-profile.md`, so I need to know how it is laid out.
     > I found:
     > - `pyproject.toml` → Python, Django
     > - `fe/package.json` → Vue, Astro, Tailwind
     >
     > Is this right?
     > 1. Yes: `.` is backend, `fe/` is frontend. Review with these stacks.
     > 2. Partly: tell me what to change (e.g. "`fe/` is Nuxt", "`scripts/` is backend too").
     > 3. Create a profile first with `/qa:init-profile` so I don't ask again.

     **End the turn with this question. Do not start the review in the same turn.** On the reply, use the confirmed layout and stacks for this run only; write nothing.
   - **`NO_PROFILE` with `--no-ask`:** a directory holding a Python manifest is backend; a directory whose `package.json` matches a frontend stack key is frontend. Load only `backend.md` and `frontend.md`. Every file's layer is listed as `assumed` under **Not checked**.
   - Files in no layer go under **Not checked**. Never review them with another layer's checklist.
   - A `backend` or `frontend` argument drops the other layer.

3. **Drift.** Skip with `NO_PROFILE`. Read the manifests at the root and in each `Layout` path, and map them through `stack-signals.md`. Record, never fix:
   - `STACK <key> (pack available)`: signal matched, key missing from `stacks`, a `references/*-<key>.md` exists.
   - `STACK <key> (no pack)`: signal matched, key missing from `stacks`, no pack file.
   - `STACK <key> (unknown key)`: key in `stacks` matches no signal and has no pack file.
   - `STACK ? (no manifest found in <paths>)`: no manifest anywhere searched.
   - `PACK <key> (written for <n>, project uses <m>): may be stale`: for each pack you load, the dependency's major version in the manifest (pinned or lower bound) is greater than the pack's `Written for` major.

4. **Load checklists.** For each layer in scope, read `references/<layer>.md`, then `references/<layer>-<key>.md` for each key in `stacks` (or the confirmed stacks) that has one.

5. **Invariants first.** For every profile invariant the change touches, read the code that enforces it and verify it holds. A break is CRITICAL.

6. **Checklists.** Walk the layer file, then its packs, then the profile's `<Layer> checks`. Report only items the change affects.

7. **Run, don't guess.** Run the profile's `lint`, `typecheck`, and `test` commands, scoped to the change when the tool allows. Report each exact command and its result. If one cannot run (missing database, service, tool), say which and why. Silent output is not a pass; check the exit code.

8. **Look up only with a reason.** Consult sources only when the diff adds or upgrades a dependency, a finding depends on version-specific behaviour, or you are unsure an API behaves as assumed. Order: official docs (context7 when available), then changelog or migration guide, then community posts only to corroborate. A finding that relies on a lookup cites the URL.

9. **Docs drift.** If changed behaviour is described in a file under the profile's `Docs to keep in sync`, or in a docstring or comment of the changed code, check they still match.

10. **Grade** each finding (see Severity), then write the output.

## Finding rules

1. **Evidence.** A finding names the changed line and either the concrete failure or the rule it breaks (checklist item, `INV-xxx`, profile check). If you cannot name both, drop it.
2. **Merge.** The same `file:line` and problem flagged by two checklists is one finding, at the higher level, citing both.

## Severity

Grade in this order:

1. **Overrides first.** Before grading anything else, list each profile `Severity overrides` line that matches a finding. Those findings take exactly that level. Do not re-grade them up or down; the merge rule does not change them.
2. Grade the rest with this table.

| Level | Meaning |
|---|---|
| CRITICAL | Invariant broken, data loss or corruption, security hole (secret leak, auth or CSRF bypass, injection, XSS, cross-tenant access), crash or broken primary flow on a normal path |
| WARNING | Wrong behaviour on an edge case, missing transaction or idempotency where retry happens, N+1 or unbounded load on a real path, missing loading/error state, accessibility failure, missing test for a changed critical path, docs drift |
| SUGGESTION | Readability, naming, missing docstring, minor duplication, minor performance |

## Output

Return exactly these parts, in order:

1. **Verdict**: one line, `PASS`, `PASS WITH WARNINGS`, or `FAIL` (any CRITICAL).
2. **Findings**: CRITICAL, then WARNING, then SUGGESTION. One per line: `SEVERITY path:line — problem. Why it matters. Fix.` Cite the `INV-xxx`, checklist item, or URL that applies.
3. **Profile drift**: one line per record from step 3, with what to do (`pack available` → add the key to `stacks` or run `/qa:init-profile`; `no pack` → add its rules to the profile's checks; `unknown key` → fix or remove it; `may be stale` → tell the plugin owner). `none` when there are none.
4. **Commands run**: each command with `ran ✓`, `ran ✗`, or `not run (<why>)`.
5. **Not checked**: files outside every layer, `assumed` layers, and anything in scope you could not verify, with why.
````

- [ ] **Step 2: Delete the old skill file**

```bash
git rm plugins/qa/skills/review-backend/SKILL.md
```

- [ ] **Step 3: Run the check**

Run: `python3 scripts/check-plugin.py`
Expected: exit 1 with exactly one line, `FAIL injection: plugins/qa/skills/init-profile/SKILL.md runs ...` (fixed in Task 5). Any `linked`, `one-level`, `written-for`, or `signals` line is a real problem; fix it now.

`claude plugin validate` runs after Task 4, once the frontend files SKILL.md links to exist.

- [ ] **Step 4: Commit (print only)**

```bash
git add -A plugins/qa
git commit -m "feat(qa)!: replace review-backend with layer-routed /qa:review"
```

---

### Task 4: Frontend reference files

**Files:**
- Create: `plugins/qa/skills/review/references/frontend.md`
- Create: `plugins/qa/skills/review/references/frontend-vue.md`
- Create: `plugins/qa/skills/review/references/frontend-inertia.md`
- Create: `plugins/qa/skills/review/references/frontend-astro.md`
- Create: `plugins/qa/skills/review/references/frontend-tailwind.md`

**Interfaces:**
- Consumes: file names linked from `SKILL.md` (Task 3); keys `vue`, `inertia`, `astro`, `tailwind` in `stack-signals.md` (Task 2).

- [ ] **Step 1: Write `frontend.md`**

```markdown
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
```

- [ ] **Step 2: Write `frontend-vue.md`**

```markdown
# Vue stack pack

Written for: Vue 3

- [ ] **`<script setup>`** with the Composition API in new and changed components.
- [ ] **Typed props and emits**: `defineProps<{…}>()` / `defineEmits<{…}>()` (or runtime validators); props are never mutated.
- [ ] **List keys**: `v-for` has a unique, stable `:key` (an id, not the index); `v-if` is not on the same element as `v-for`.
- [ ] **Reactivity**: `ref` for primitives and replaced values, `reactive` only for objects kept by reference; no destructuring of reactive objects without `toRefs`.
- [ ] **`computed` over `watch`** for derived state; a `watch` exists only for side effects.
- [ ] **Cleanup**: Listeners, intervals, observers, and manual subscriptions are removed in `onUnmounted` (or the composable's scope).
- [ ] **`v-show` vs `v-if`**: `v-show` for frequent toggles, `v-if` for rarely shown content.
- [ ] **Async components**: `defineAsyncComponent()` for large or rarely rendered components.
- [ ] **Composables**: Return refs, not raw values, so callers stay reactive; one concern per composable.
```

- [ ] **Step 3: Write `frontend-inertia.md`**

```markdown
# Inertia stack pack

Written for: Inertia 2

- [ ] **Page names**: The page file path matches the name the backend passes to `render(...)`; a mismatch is a 404/blank page on a normal path (CRITICAL).
- [ ] **Forms**: `useForm()` for forms with several fields, validation errors, or file uploads; `router.post()` / `router.visit()` for simple actions with no user input. No manual `axios`/`fetch` to Inertia routes.
- [ ] **Button state**: Async actions re-enable controls in `onFinish`, not only `onSuccess`.
- [ ] **Uploads**: Requests with files are sent as `FormData` automatically; `forceFormData: true` is only for forcing multipart when no file is present. Do not flag its absence on file uploads.
- [ ] **Navigation**: `<Link>` or `router.visit()` for internal routes, not bare `<a href>`.
- [ ] **Partial reloads**: `only: [...]` when one section of a page refreshes; `preserveScroll`/`preserveState` where losing them hurts the user (filters, long lists).
- [ ] **Props**: Serialisable and minimal; no ORM objects, secrets, or data the page does not render.
- [ ] **Shared data**: Added through middleware only when every page needs it.
- [ ] **CSRF**: Inertia's CSRF headers are left intact.
```

- [ ] **Step 4: Write `frontend-astro.md`**

```markdown
# Astro stack pack

Written for: Astro 6

- [ ] **Static by default**: Components ship no JS unless they need it; `client:*` only on islands that must hydrate.
- [ ] **Directive choice**: `client:visible` or `client:idle` for below-the-fold or non-urgent islands; `client:load` only for what must work immediately.
- [ ] **Island props**: Serialisable (no functions, class instances, or circular data).
- [ ] **Prerender vs SSR**: On prerendered routes, `Astro.cookies`, request headers, and per-request data are build-time only; code that depends on them belongs on an SSR route.
- [ ] **`set:html`**: Only with trusted or sanitised content.
- [ ] **Images**: Content images go through `astro:assets` (`<Image />`) with dimensions; files in `public/` are served unoptimised.
- [ ] **Env**: `PUBLIC_*` variables are exposed to the browser and fixed at build time; secrets never use that prefix.
- [ ] **Styles**: Component `<style>` stays scoped unless a global rule is intended and placed in a global stylesheet.
```

- [ ] **Step 5: Write `frontend-tailwind.md`**

```markdown
# Tailwind CSS stack pack

Written for: Tailwind 4

- [ ] **Tokens**: Colours, fonts, and spacing come from the project's theme tokens (`@theme` variables / configured scale); no arbitrary hex values like `text-[#a1b2c3]`.
- [ ] **Inline style**: Only for values computed at runtime; static styling uses utilities.
- [ ] **Responsive**: Mobile-first; larger breakpoints added with `sm:`/`md:`/`lg:` prefixes, not by overriding desktop styles down.
- [ ] **States**: `hover:`, `focus-visible:`, `disabled:` variants present on interactive elements.
- [ ] **Dark mode**: Uses the project's dark-mode mechanism consistently, not a mix of strategies.
- [ ] **Class conflicts**: No contradictory utilities on one element (`p-2 p-4`); conditional classes merge predictably.
- [ ] **Custom CSS**: Kept to the project's stylesheet location; `@apply` only for repeated, named patterns.
```

- [ ] **Step 6: Run the checks**

Run: `python3 scripts/check-plugin.py`
Expected: only the `init-profile` injection line from Task 3 (fixed in Task 5).

Run: `claude plugin validate . --strict && claude plugin validate ./plugins/qa --strict`
Expected: both pass.

- [ ] **Step 7: Commit (print only)**

```bash
git add plugins/qa/skills/review/references
git commit -m "feat(qa): add frontend, vue, inertia, astro and tailwind checklists"
```

---

### Task 5: `init-profile` updates

**Files:**
- Modify: `plugins/qa/skills/init-profile/SKILL.md`
- Modify: `plugins/qa/skills/init-profile/profile-template.md`

**Interfaces:**
- Consumes: pack naming `references/<layer>-<key>.md` under `skills/review/` (Task 2), `## Manifests` and `## Signals` in `stack-signals.md`.
- Produces: profiles whose `stacks` keys match pack file suffixes and whose `Layout` paths are matched longest-first by `/qa:review`.

- [ ] **Step 1: Replace the profile injection and pack lookup**

In `init-profile/SKILL.md`:

Change the frontmatter line to:

```yaml
allowed-tools: Bash(ls *) Glob Read
```

Replace the `## Current profile` section (heading and the `!` line under it) with:

```markdown
## Current profile

Read `.claude/project-profile.md`. If it does not exist, there is no profile yet; draft a new one.
```

Replace the `Available stack packs:` paragraph with:

```markdown
Available stack packs: Glob `${CLAUDE_PLUGIN_ROOT}/skills/review/references/*-*.md`. The stack key is the part of the file name after the first `-` (`frontend-vue.md` → `vue`). Files without a `-` (`backend.md`, `frontend.md`) are layer checklists, always loaded, never listed in `stacks`.
```

- [ ] **Step 2: Update steps 1–2 and add the no-pack research step**

Replace steps 1 and 2 with:

```markdown
1. **Detect.** Read the manifests listed in `${CLAUDE_PLUGIN_ROOT}/stack-signals.md` § Manifests at the root and one directory down, plus compose files, `Makefile` targets, and `AGENTS.md`/`CLAUDE.md`. Derive: stacks, layout per layer (backend, frontend, infra, tests), and the exact lint/format/typecheck/test commands.
2. **Map stacks.** Match dependencies against `stack-signals.md` § Signals. Set `stacks` to the matched keys that have a pack. For each matched key with no pack, research it: official docs first (context7 when available), then the changelog or migration guide; community posts only to corroborate. Keep only pitfalls Claude would otherwise miss, and put them under the profile's `<Layer> checks` with the source URL. Mark these as researched in the step-5 summary.
```

- [ ] **Step 3: Update the template**

In `profile-template.md`, replace the frontmatter comment with:

```yaml
---
# Stack packs to load. Each key matches a file named <layer>-<key>.md in the review
# skill's references/ (e.g. backend-django.md → django). Unknown keys are reported as drift.
stacks: []
---
```

Replace the `## Layout` comment with:

```markdown
<!-- Where each layer lives, as paths from the repo root. Reviews assign a changed file to the
     layer whose path contains it; the longest path wins (`frontend/` beats `.`). -->
```

- [ ] **Step 4: Run the checks**

Run: `python3 scripts/check-plugin.py && claude plugin validate ./plugins/qa --strict`
Expected: `OK (…)` and pass. The `injection` rule must not flag `init-profile` (only `ls -a` remains).

- [ ] **Step 5: Commit (print only)**

```bash
git add plugins/qa/skills/init-profile
git commit -m "feat(qa): init-profile reads review packs and researches stacks without one"
```

---

### Task 6: Repo docs, version, diagram

**Files:**
- Modify: `plugins/qa/.claude-plugin/plugin.json`
- Modify: `README.md`
- Modify: `CLAUDE.md`
- Modify: `docs/architecture.excalidraw`, regenerate `docs/architecture.png`

- [ ] **Step 1: Version and keywords**

`plugin.json`: `"version": "0.2.0"`, and

```json
"keywords": ["qa", "code-review", "checklist", "django", "fastapi", "sqlalchemy", "python", "vue", "inertia", "astro", "tailwind", "frontend"]
```

- [ ] **Step 2: README**

- Plugins table row: `qa` | `/qa:review`, `/qa:init-profile`.
- Replace "Stack packs for `review-backend`: …" with: "Layers: `backend`, `frontend`. Stack packs: `python`, `django`, `sqlalchemy`, `fastapi`, `vue`, `inertia`, `astro`, `tailwind`."
- "Use in a project" block: `/qa:review          # review uncommitted changes (or: backend|frontend, --no-ask, path / branch / range / staged)`.
- "What a review does": steps become 1 profile (none → asks how the repo is laid out; `--no-ask` skips the question), 2 layout routing (longest path wins), 3 drift incl. stale packs, 4 layer checklist + packs, 5 invariants first, 6 run commands, 7 lookups only with a reason, 8 report.
- "Keeping a project current" table: add row `A pack is older than the project's major version` | `Review reports PACK <key> … may be stale` | `Refresh the pack here, bump the version`.
- Status: `v0.2.0`, not tagged; replace the known gap "Only backend review exists" with "Infra and docs review, `finish-change`, and Nuxt/k8s packs are not written"; keep the Cursor gap.
- Rules for this repo: change "`references/common.md`" → "`references/<layer>.md`" and "`references/<stack>.md`" → "`references/<layer>-<stack>.md`".

- [ ] **Step 3: CLAUDE.md**

- Layout block: `plugins/qa/skills/review/   SKILL.md + references/{backend,frontend}.md + <layer>-<stack>.md packs`; add `scripts/check-plugin.py   structural checks (also in CI)`.
- Replace "Local state: git initialised, remote `origin` set, **nothing committed or pushed yet**." with "Released from `main` on GitHub; no tags yet."
- "Before changing a skill" step 1: add `python3 scripts/check-plugin.py`.
- Testing section: replace `/qa:review-backend` with `/qa:review`; add the plugin-conflict note from Task 7 Step 1.
- Open work: rewrite to the spec's out-of-scope list (remove old in-repo skills after Cursor check; infra/docs layers; performance; finish-change; Nuxt and k8s packs; community release).

- [ ] **Step 4: Diagram**

In `docs/architecture.excalidraw` change texts:

- `review-backend\n/qa:review-backend` → `review\n/qa:review`
- `references/\n  common.md  (always)\n  python.md\n  django.md\n  sqlalchemy.md\n  fastapi.md` → `references/\n  backend.md · frontend.md\n  backend-{python,django,\n    sqlalchemy,fastapi}.md\n  frontend-{vue,inertia,\n    astro,tailwind}.md`
- `/qa:review-backend flow` → `/qa:review flow`
- `3. Load common.md + stack packs` → `3. Route files by Layout, load layer + packs`
- `## Backend checks` (inside the profile text) → `## Backend / Frontend checks`

Render:

```bash
cd ../diagram-drawing-skill/skills/diagram-drawing-skill/references && uv run python render_excalidraw.py ../../../../agent-skills/docs/architecture.excalidraw --output ../../../../agent-skills/docs/architecture.png
```

Open the PNG and check no text overflows its box (the references box grew to 5 lines). If it overflows, widen/heighten that rectangle in the JSON and re-render. If the renderer cannot run, keep the JSON change and report the PNG as stale.

- [ ] **Step 5: Run the checks**

Run: `python3 scripts/check-plugin.py && claude plugin validate . --strict && claude plugin validate ./plugins/qa --strict`
Expected: all pass. `grep -rn 'review-backend' --include='*.md' --include='*.json' --include='*.excalidraw' .` returns only `docs/specs/` and `docs/plans/` hits.

- [ ] **Step 6: Commit (print only)**

```bash
git add plugins/qa/.claude-plugin/plugin.json README.md CLAUDE.md docs/architecture.excalidraw docs/architecture.png
git commit -m "docs: describe /qa:review and bump qa to 0.2.0"
```

---

### Task 7: No-profile behaviour on Project A (acceptance 6)

Runs before any profile exists. Uses the working copy, not the installed plugin.

**Files:** none changed. Results go into the run log (Task 9 Step 5).

- [ ] **Step 1: Avoid two `qa` plugins in one session**

Run: `claude plugin list`
If `qa@dqcuong93` is enabled, ask the owner before running `claude plugin disable qa@dqcuong93` (changes their user config). Re-enable it after Task 9: `claude plugin enable qa@dqcuong93`.

- [ ] **Step 2: Pick a recent Project A commit that touches backend and frontend**

Run (in Project A): `git log --oneline -30 --name-only | head -120` and choose a commit `<A1>` whose files include both backend and `fe/` paths.

- [ ] **Step 3: Question gate, 3 runs**

Run 3 times (in Project A, no profile present):

```bash
claude -p "/qa:review <A1>~1..<A1>" --model sonnet --plugin-dir <agent-skills>/plugins/qa --allowedTools "Read,Glob,Grep,Bash(git *)" --output-format json < /dev/null > $SCRATCH/qa-a-noprofile-<n>.json
```

Pass when every run's final text: names the root `pyproject.toml` (Python, Django) and `fe/package.json` (Vue, Astro, Tailwind), offers the three choices, and contains no `Verdict` line. Any run with a `Verdict` is a fail: strengthen the "End the turn" wording in SKILL.md step 2 and re-run all 3.

- [ ] **Step 4: `--no-ask`, 1 run**

```bash
claude -p "/qa:review --no-ask <A1>~1..<A1>" --model sonnet --plugin-dir <agent-skills>/plugins/qa --allowedTools "Read,Glob,Grep,Bash(git *)" --output-format json < /dev/null > $SCRATCH/qa-a-noask.json
```

Pass when the output has a `Verdict`, no question, and **Not checked** lists the layers as `assumed`.

---

### Task 8: Profiles for Project A and B (acceptance 2, 5)

Interactive with the owner, inside each project, using `claude --plugin-dir <agent-skills>/plugins/qa`.

**Files:**
- Create (in Project A, after approval): `.claude/project-profile.md`
- Create (in Project B, after approval): `.claude/project-profile.md`

- [ ] **Step 1: Project A profile**

Run `/qa:init-profile`. Check the draft stops for confirmation and writes nothing. Before approving, make sure it contains (add if missing):

- `stacks: [python, django, vue, astro, tailwind]`
- Layout: backend `be/`, frontend `fe/`, infra `infras/`, tests `be/app/**/tests`, `fe/src/**/*.test.ts`
- Commands from the project's AGENTS verification section (FE lint/test/build, BE `manage.py check`, `spectacular --validate`, pytest)
- Backend checks: the closed-set slug rule removed in Task 2 Step 3; the project's OpenAPI date bump
- Frontend checks: the Project A list in spec D9
- Invariants and severity overrides harvested from the project's agent instructions (gotchas section)
- Under ~150 lines

After the owner approves, it writes the file and runs each `Commands` entry once; record which ran.

- [ ] **Step 2: Project B profile**

Same in Project B. Must contain:

- `stacks: [python, django, inertia, vue, tailwind]`
- Layout: backend `.`, frontend `frontend/`, tests per its testing doc
- Commands: `make dev-test` / `uv run python manage.py test`, `pnpm run lint`, `pnpm run check`
- Backend checks: POST bodies via `get_post_data(request)`; smoke modules from its testing doc
- Frontend checks: icon library rule (inline SVG only for spinners or icons with no library match, with a comment), palette/font tokens, pages path, `defineOptions({ name })` on pages

- [ ] **Step 3: Drift and stale pack (acceptance 5)**

In Project A run `/qa:review backend <A1>~1..<A1>` and check **Profile drift** is `none` (or lists only real gaps), not `STACK ? (no manifest …)`.

Then temporarily change `backend-django.md` line 3 to `Written for: Django 5`, re-run, and check for `PACK django (written for 5, project uses 6): may be stale`. Restore line 3 and run `python3 scripts/check-plugin.py`.

- [ ] **Step 4: Overlapping layout (Review Focus 1)**

In Project B pick a commit `<B1>` touching `frontend/**/*.vue`. Run `/qa:review <B1>~1..<B1>`. Pass when the `.vue` files are reviewed under frontend (frontend checklist items cited) and no `backend*.md` item is cited for them.

---

### Task 9: Side-by-side comparison (acceptance 3, 4) and overrides

- [ ] **Step 1: Pick commits**

Project A: `<A1>` and one more `<A2>` touching backend and frontend. Project B: `<B1>` and `<B2>` touching backend and `frontend/`.

- [ ] **Step 2: Run both skills on each commit**

For each commit `<C>` in its project, two headless runs, same model:

```bash
claude -p "/qa:review <C>~1..<C>" --model sonnet --plugin-dir <agent-skills>/plugins/qa --allowedTools "Read,Glob,Grep,Bash(git *),Bash(uv run *),Bash(pnpm *),Bash(make *)" --output-format json < /dev/null > $SCRATCH/qa-new-<C>.json
claude -p "Use the qa-qc-backend and qa-qc-frontend skills to review the changes in commit <C> (git show <C>)." --model sonnet --allowedTools "Read,Glob,Grep,Bash(git *),Bash(uv run *),Bash(pnpm *),Bash(make *)" --output-format json < /dev/null > $SCRATCH/qa-old-<C>.json
```

For a commit that touches only `frontend/` (Review Focus 3), confirm the new output cites no backend checklist item.

About 8 runs; each earlier run cost roughly $0.2–0.35.

- [ ] **Step 3: Read and score by hand**

For each commit, list every CRITICAL/WARNING from the old run and mark it found / missed / argued wrong in the new run. Count new CRITICAL false positives. Compare CRITICAL + WARNING counts. Pass per project: no unexplained miss, no new CRITICAL false positive, new count ≤ old count.

On a fail, change the relevant checklist or SKILL.md wording, re-run that commit only, and note the change.

- [ ] **Step 4: Severity override (Review Focus 5)**

Take one WARNING the new skill reported in Project A. Add a matching line to Project A's profile under `Severity overrides`, e.g. `- SUGGESTION: <that condition>`. Re-run that commit twice. Pass when both runs report it as SUGGESTION. Remove the line afterwards (the profile is the owner's).

- [ ] **Step 5: Run log and wrap-up**

Write the results (no project names) into `docs/specs/2026-10-05-unified-review-design.md` under a new `## Results` section: per acceptance item, runs, pass/fail, and any wording changes made. Re-enable the installed plugin if it was disabled. Print the final commands for the owner:

```bash
git add -A && git commit -m "test(qa): record /qa:review acceptance results"
git push && git tag v0.2.0 && git push origin v0.2.0
claude plugin marketplace update dqcuong93 && claude plugin update qa@dqcuong93
```
