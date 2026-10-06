---
name: finish
description: Use when coding is done and a change needs its last pass before the owner commits: review, verify, fix, test gaps, stale docs, and a ready commit message.
argument-hint: "[--no-ask] [path | branch | range]"
disable-model-invocation: true
allowed-tools: Bash(git status *) Bash(git diff *) Bash(git log *) Bash(git branch *) Bash(git symbolic-ref *) Bash(git merge-base *) Bash(date *) Read Glob Grep Edit Write
---

# Finish a change

Runs after coding. Execute the steps in order, inline. Project facts come from `.claude/project-profile.md`.

**Hard rule:** never run `git commit`, `git push`, `git tag`, or anything that rewrites history. Print the commit message and stop.

## Change scope

!`git status --short --untracked-files=normal`

Arguments: `$ARGUMENTS`

- `--no-ask`: never stop to ask. Items that need a decision stay unfixed and are listed in the report.
- A path, branch, or range limits the scope. Empty: uncommitted changes plus the current branch against its base (`git diff <default>...HEAD --name-only`; find `<default>` with `git symbolic-ref --short refs/remotes/origin/HEAD`, else `main`, else `master`).

## Steps

1. **Scope and reviewers.** List the changed files. Read the profile. Invoke `/qa:review --no-ask` once through the `Skill` tool for the whole scope (it routes by layer). Then, for each profile `Finish` line under `reviewers:` whose path matches a changed file, invoke the skill or command it names through the `Skill` tool. For a hot path named in the profile's `## Performance`, offer `/qa:perf`. Nothing matched and nothing changed: say so and stop.
2. **Verify.** Run the profile's `lint`, `format-check`, `typecheck`, `test`, and the `extra` commands the scope needs, in full, not scoped to the diff. A command that cannot run (no database, tool missing, not allowed) is `not run (<why>)`; silent output is not a pass, check the exit code. End the report with one line per command: `ran ✓`, `ran ✗`, or `not run (<why>)`.
3. **Triage.** Merge all findings into one list graded CRITICAL, WARNING, SUGGESTION, each `path:line — problem — fix`. Split it into two buckets: **auto-fix** (clear-cut) and **needs decision** (behaviour or API contract change, money or irreversible data, a trade-off between valid designs, deleting code or data, anything a reviewer marked "depends").
4. **Fix.** Apply every auto-fix with the smallest edit that does what the finding says. If the needs-decision bucket is not empty and `--no-ask` is not set, ask once, in one `AskUserQuestion` batch, with a recommendation first, then apply the answers. With `--no-ask`, leave them and list them.
5. **Tests.** For each changed code file find its tests (same module or directory) and check that the new or changed behaviour is covered: the happy path, each new error or edge branch, permission and auth paths, and a regression test for a bug fix. Write the missing tests in the style of the nearest existing test, mocking external services. Skip, and say why, for docs-only, comment-only, config-only, rename-only, and generated files. Then re-run the step 2 commands for the touched areas so the new tests execute.
6. **Stale docs.** Walk the profile's `Docs to keep in sync` against the diff. Rewrite docstrings and comments the change made false. Grep the repository for each name, route, or field the diff removed or renamed. Update an index, a navigation entry, or an OpenAPI/version stamp when the profile says the change requires it.
7. **Report and commit message.** Report briefly: what was fixed, what the owner decided, what was not verified, what stays open. For each open item that only the owner can settle, write it as a question and say where the answer belongs (which profile section); do not guess. Then print one commit message for the whole change, ready to paste, in the profile's `commit-format` (default: Conventional Commits, `type(scope): subject`, subject at most 72 characters, a one or two sentence body only for the why). Take the ticket from the branch name with the profile's `ticket-from-branch` pattern and add it as the profile says; omit it when there is none. Append any attribution line the session's instructions require. Print it and stop.
