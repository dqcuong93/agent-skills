---
name: review-backend
description: Use when reviewing backend or core-layer code (Python services, APIs, ORM/DB code, background jobs, CLI/core libraries) for correctness, security, performance, test gaps, or adherence to project invariants — on a diff, branch, file, or before merging.
argument-hint: "[path | branch | 'staged']"
allowed-tools: Bash(cat *) Bash(git status *) Bash(git diff *) Bash(git log *)
---

# Backend QA/QC review

Generic backend review. Project-specific rules come from the project profile below; stack rules come from `references/`.

## Project profile

!`cat "${CLAUDE_PROJECT_DIR}/.claude/project-profile.md" 2>/dev/null || echo "NO_PROFILE"`

## Change scope

!`git status --short --untracked-files=normal`

Requested scope: `$ARGUMENTS` (empty = uncommitted changes; if none, ask what to review).

## Steps

1. **Profile.** If the profile above is `NO_PROFILE`, say so in one line, suggest `/qa:init-profile`, and continue with the generic checklist only.
2. **Stack drift.** Skipped when the profile is `NO_PROFILE`. Read the project's dependency manifests (`pyproject.toml`, `requirements*.txt`, `package.json`) and `${CLAUDE_PLUGIN_ROOT}/stack-signals.md`. For each stack key whose signals match and that is missing from the profile's `stacks`, record one mismatch: `pack available` when a `<key>.md` exists under `${CLAUDE_PLUGIN_ROOT}/skills/*/references/`, otherwise `no pack`. Also record each profile `stacks` key that matches no signal and has no pack file as `unknown key`. Report mismatches only; never edit the profile.
3. **Scope.** List the backend files in scope (use the profile's `Layout`). Ignore files of other layers.
4. **Load checklists.** Read `${CLAUDE_SKILL_DIR}/references/common.md`, then `${CLAUDE_SKILL_DIR}/references/<stack>.md` for each key in the profile's `stacks` that has a file there.
5. **Invariants first.** For every profile invariant the change touches, verify it holds by reading the code that enforces it. An invariant break is CRITICAL.
6. **Checklists.** Walk common → stack packs → profile `Backend checks`. Only report items the change actually affects.
7. **Run, don't guess.** Run the profile's `lint`, `typecheck`, and `test` commands scoped to the change when they exist. Report the exact command and result. If a command can't run (missing DB, service), say which and why.
8. **Docs drift.** If changed behavior is described in a file under the profile's `Docs to keep in sync`, or in a docstring/comment of the changed code, check they still match.

## Output

Return exactly these parts, in order:

1. **Verdict** — one line: `PASS`, `PASS WITH WARNINGS`, or `FAIL` (any CRITICAL).
2. **Findings** — grouped by severity, most severe first. One finding per line:
   `SEVERITY path:line — problem. Why it matters. Fix.` Cite `INV-xxx` or the checklist item when one applies.
3. **Profile drift** — one line per mismatch from step 2, in the form
   `STACK <key> (<pack available | no pack | unknown key>): <what to do>`; write `none` when there are none.
   `pack available` → add the key to `stacks` (or run `/qa:init-profile`). `no pack` → add its rules to the profile's `Backend checks`, or write a pack. `unknown key` → fix the typo or remove it.
4. **Commands run** — each command with pass/fail.
5. **Not checked** — anything in scope you could not verify, and why.

## Severity

Grade each finding in this order:

1. If a line in the profile's `Severity overrides` matches the finding, use that level exactly. Do not re-grade it, up or down.
2. Otherwise use the table row that describes it.

| Level | Meaning |
|---|---|
| CRITICAL | Invariant broken, data loss/corruption, security hole (secret leak, auth bypass, injection, cross-tenant access), crash on a normal path |
| WARNING | Wrong behavior on an edge case, missing transaction/idempotency where retry happens, N+1 or unbounded load on a real path, missing test for a changed critical path, docs drift |
| SUGGESTION | Readability, naming, missing docstring, minor duplication |
