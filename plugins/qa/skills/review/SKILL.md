---
name: review
description: Use when reviewing backend or frontend code (services, APIs, ORM/DB, jobs, components, pages, styling) for correctness, security, performance, test gaps, or project invariants — on uncommitted changes, a branch, a commit range, staged files, or a path, or before merging.
argument-hint: "[backend|frontend] [--no-ask] [path | branch | commit | range | staged]"
allowed-tools: Bash(git status *) Bash(git diff *) Bash(git log *) Bash(git show *) Bash(git branch *) Bash(git symbolic-ref *) Read Glob Grep
---

# QA review

Generic review workflow. Project facts come from `.claude/project-profile.md`. Layer and stack rules come from the reference files below.

## Change scope

!`git status --short --untracked-files=normal`

Arguments: `$ARGUMENTS`

- `backend` or `frontend`: review only that layer.
- `--no-ask`: never stop to ask. Used by headless runs and other skills.
- `staged`, a branch, a commit, a range (`A..B`), or a path: what to review. For a commit or range, judge the code as it was at that commit (`git show <commit>:<path>`), not the working tree. Empty: uncommitted changes. If there are none and the current branch is not the default branch, review the branch against its base (`git diff <default>...HEAD`; find `<default>` with `git symbolic-ref --short refs/remotes/origin/HEAD`, else `main`, else `master`) and say which base you used. On the default branch with a clean tree, ask what to review; with `--no-ask`, report `Nothing to review` and stop.

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
   - **With a profile:** assign each changed file to the layer whose `Layout` path contains it (a path with `*` matches as a glob). When several match, the longest path wins (`frontend/` beats `.`). `tests` paths are not a layer of their own: a test file goes to the layer it tests (backend or frontend) by the same rule with `tests` left out. Layers with no checklist yet (e.g. `infra`) go under **Not checked**.
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

3. **Drift (required with a profile; do not skip it to save turns).** Skip only with `NO_PROFILE`. Open `stack-signals.md`, then open a manifest in the root and in every `Layout` path of the profile (Glob for it; never guess a path such as `be/pyproject.toml`), and map them through it. Write `none` only after both were opened in this run. Record, never fix:
   - `STACK <key> (pack available)`: signal matched, key missing from `stacks`, a `references/*-<key>.md` exists.
   - `STACK <key> (no pack)`: signal matched, key missing from `stacks`, no pack file.
   - `STACK <key> (unknown key)`: key in `stacks` matches no signal and has no pack file.
   - `STACK ? (no manifest found in <paths>)`: no manifest anywhere searched.
   - A key already listed in `stacks` is never reported as `pack available` or `no pack`.
   - `PACK <key> (written for <n>, project uses <m>): may be stale`: emit exactly this line when the project's major version of a loaded pack's dependency is greater than the pack's `Written for` major. To find the project's version, read every manifest you read above, including `requirements*.txt` inside `Layout` paths (pinned `==`, or the lower bound of `>=`, `^`, `~`); if none names it directly, Grep the root lockfile (`uv.lock`, `poetry.lock`, `pnpm-lock.yaml`, `package-lock.json`) for its resolved version.
   - Always end the drift record with one line listing every pack loaded in step 4 (a pack not opened is not listed): `Packs: <key> <written-for major>/<project major or ?>`; `?` only after the manifests and the lockfile were opened and name no version, e.g. `Packs: django 6/6, vue 3/3, astro 6/?`.

4. **Load checklists.** For each layer in scope, read `references/<layer>.md`, then `references/<layer>-<key>.md` for each key in `stacks` (or the confirmed stacks) that has one. Load every such pack even when the diff seems not to touch it: its items are skipped later if the change does not affect them, but the `Packs:` line and the stale check need them loaded.

5. **Invariants first.** For every profile invariant the change touches, read the code that enforces it and verify it holds. A break is CRITICAL.

6. **Checklists.** Walk the layer file, then its packs, then the profile's `<Layer> checks`. Report only items the change affects.

7. **Run, don't guess.** Run the profile's `lint`, `typecheck`, and `test` commands, scoped to the change when the tool allows. Report each exact command and its result. If one cannot run (missing database, service, tool), say which and why. Silent output is not a pass; check the exit code. The shell may be zsh: do not use `echo =====` or `PIPESTATUS`, and do not chain `; echo $?` (headless permission checks reject it). Run each command on its own: the Bash tool reports a non-zero exit itself, so no error line means exit 0.

8. **Look up only with a reason.** Consult sources only when the diff adds or upgrades a dependency, a finding depends on version-specific behaviour, or you are unsure an API behaves as assumed or a library provides something (e.g. whether an icon or helper exists). Order: for whether a library provides something, the installed package first (`node_modules/`, the virtualenv); otherwise official docs (context7 when available), then changelog or migration guide, then community posts only to corroborate. Project docs that describe a library are not a source for it. A finding that relies on a lookup cites the URL.

9. **Docs drift.** If changed behaviour is described in a file under the profile's `Docs to keep in sync`, or in a docstring or comment of the changed code, check they still match.

10. **Grade** each finding (see Severity), then write the output.

## Finding rules

1. **Evidence.** A finding names the changed line and either the concrete failure or the rule it breaks (checklist item, `INV-xxx`, profile check). If you cannot name both, drop it.
2. **Merge.** The same `file:line` and problem flagged by two checklists is one finding, at the higher level, citing both.

## Severity

Grade in this order:

1. **Overrides first.** Before grading anything else, list each profile `Severity overrides` line that matches a finding. Those findings take exactly that level. Do not re-grade them up or down; the merge rule does not change them.
2. Grade the rest with this table, by effect on the user or the data. A finding is not downgraded because the code predates the commit or because it breaks a convention rather than a rule; say which in the finding instead.

| Level | Meaning |
|---|---|
| CRITICAL | Invariant broken, data loss or corruption, security hole (secret leak, auth or CSRF bypass, injection, XSS, cross-tenant access), crash or broken primary flow on a normal path |
| WARNING | Wrong behaviour on an edge case, missing transaction or idempotency where retry happens, N+1 or unbounded load on a real path, missing loading/error state, accessibility failure (wrong role or ARIA state, control not reachable or operable by keyboard, missing label), a test that cannot fail, missing test for a changed critical path, docs drift |
| SUGGESTION | Readability, naming, missing docstring, minor duplication, minor performance |

## Output

Return exactly these parts, in order:

1. **Verdict**: one line, `PASS`, `PASS WITH WARNINGS`, or `FAIL` (any CRITICAL).
2. **Findings**: CRITICAL, then WARNING, then SUGGESTION. One per line: `SEVERITY path:line — problem. Why it matters. Fix.` Cite the `INV-xxx`, checklist item, or URL that applies.
3. **Profile drift**: one line per record from step 3, with what to do (`pack available` → add the key to `stacks` or run `/qa:init-profile`; `no pack` → add the key to `stacks` and its rules to the profile's checks; `unknown key` → fix or remove it; `may be stale` → tell the plugin owner), then the `Packs:` line. Write `none` before it when there are no records. With a profile this part is mandatory: an output without a `Packs:` line is invalid, so go back and finish steps 3 and 4 first.
4. **Commands run**: each command with `ran ✓`, `ran ✗`, or `not run (<why>)`.
5. **Not checked**: files outside every layer, `assumed` layers, and anything in scope you could not verify, with why.
