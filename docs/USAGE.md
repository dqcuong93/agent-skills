# Using the `qa` plugin

The plugin reviews code for you. It knows how to review (workflow, severity, checklists per layer and stack). Your project tells it what to review and what must never break, through one file: `.claude/project-profile.md`.

## What you get

| Command | Use it when | What it does | Typical cost* |
|---|---|---|---|
| `/qa:init-profile` | A project has no profile, or its layout, stack, or rules changed | Detects the stack, asks you to confirm the layout, drafts the profile, asks before writing it | one short session |
| `/qa:review` | You are coding and want a review of what changed | Reviews uncommitted changes (or a commit, range, branch, path) against the layer checklists, stack packs, and your project's invariants; runs your lint and tests | $0.2–0.3 |
| `/qa:finish` | Coding is done and you are about to commit | Runs the review, the full verification commands, fixes clear-cut findings, checks for missing tests and stale docs, and prints a commit message. Never commits | $0.3–0.4 |
| `/qa:perf` | Something is slow, or you want a performance check | Measures first, then explains the likely causes and how to verify each fix | $0.2–0.3 |
| `/qa:review all` | Before a big release, or as a periodic audit | Reviews whole layers, not a diff, with one fresh reviewer per area | several dollars for a large backend |

\* Measured on small diffs with Claude Sonnet; yours will differ with diff size and model.

The review covers four layers: `backend`, `frontend`, `infra`, `docs`. Stack packs add rules for `python`, `django`, `sqlalchemy`, `fastapi`, `pyqt`, `vue`, `inertia`, `astro`, `tailwind`, `docker`, `caddy`, `mkdocs`. Desktop Qt UIs (`pyqt`) are reviewed as `backend`; `frontend` is for web pages.

## Install and update

```bash
claude plugin marketplace add dqcuong93/agent-skills
claude plugin install qa@dqcuong93
```

To make everyone on a repo use the same version, put this in the repo's `.claude/settings.json` and pin a tag:

```json
{
  "extraKnownMarketplaces": {
    "dqcuong93": { "source": { "source": "github", "repo": "dqcuong93/agent-skills", "ref": "v0.4.1" } }
  },
  "enabledPlugins": { "qa@dqcuong93": true }
}
```

Update with `claude plugin marketplace update dqcuong93`, then `claude plugin update qa@dqcuong93`. Check with `claude plugin list` (the `qa` entry shows its version). If you also load a working copy with `--plugin-dir`, disable the installed one first or two `qa` plugins load.

## First time in a project

1. Run `/qa:init-profile`. It reads your manifests, `AGENTS.md`/`CLAUDE.md`, docs, and compose files.
2. It first asks about the layout: one numbered line per path or file with the role it proposes (`backend`, `frontend`, `infra`, `docs`, `tests`, or `ignore`). Odd cases (a `Dockerfile` inside the backend folder, a `scripts/` folder) get their own line. Answer `ok`, or e.g. `3 infra, 5 ignore`.
3. It then shows the draft profile with the invariants and critical areas it inferred, where each came from, and asks you to confirm or edit. Nothing is written before you confirm.
4. After you confirm it writes `.claude/project-profile.md`, stamps `confirmed:` and `plugin:`, and runs each command once to check it works.

If your setup protects `.claude/` and the write is refused, copy the draft into the file by hand.

Commit the profile. It is the only project-specific input the plugin reads.

## Daily use

### Review

```
/qa:review                      # uncommitted changes; on a clean branch, the branch against its base
/qa:review staged               # staged files
/qa:review feature/x            # a branch
/qa:review abc123               # a commit (judged as it was at that commit)
/qa:review main..HEAD           # a range
/qa:review be/app/billing       # a path
/qa:review backend              # only one layer: backend | frontend | infra | docs
/qa:review --no-ask             # never stop to ask (headless runs, other skills)
```

The report has five parts, always in this order:

1. **Verdict**: `PASS`, `PASS WITH WARNINGS`, or `FAIL` (any CRITICAL).
2. **Findings**: CRITICAL, WARNING, SUGGESTION, one per line as `SEVERITY path:line — problem. Why it matters. Fix.` A finding cites the invariant, checklist item, or doc it comes from.
3. **Profile drift**: records that the profile or the plugin needs attention (see below), then a `Packs:` line listing the packs the review should load.
4. **Commands run**: each command as `ran ✓`, `ran ✗`, or `not run (why)`. Silence is never a pass.
5. **Not checked**: files outside every layer, ignored files, layers it only assumed, anything it could not verify, and questions only you can answer.

How findings are graded: your profile's `Severity overrides` come first and fix the level; everything else uses the shared table (CRITICAL for broken invariants, data loss, security holes, broken main flows; WARNING for edge cases, missing tests or states, accessibility, docs drift; SUGGESTION for readability).

### Finish

```
/qa:finish                      # review, verify, fix, test gaps, docs, commit message
/qa:finish --no-ask             # leave decisions unfixed and list them instead of asking
```

It runs `/qa:review --no-ask` once for the whole scope, then runs your lint, format, typecheck, and test commands in full (not scoped to the diff, so it takes longer than a review). Clear-cut findings are fixed with the smallest edit. Anything that changes behavior or an API contract, touches money or irreversible data, or is a trade-off between valid designs is asked in one batch (or listed with `--no-ask`). Then it checks that changed code has tests (writing missing ones in the style of the nearest test), walks `Docs to keep in sync`, and prints one commit message in the profile's `commit-format`, with the ticket taken from the branch name by `ticket-from-branch`. It never runs `git commit`, `git push`, or `git tag`.

The `reviewers:` line of the profile's `Finish` section lets a project add other skills, such as an external UI review for the frontend.

### Performance

```
/qa:perf                        # the profile's hot paths, else the changed files
/qa:perf backend be/app/billing # a layer and a path
/qa:perf frontend /pricing      # a page
```

The report has **Baseline** (measurements with the exact commands, or `not measured` and what to run), **Findings** ranked by expected effect with an evidence label (`measured`, `reasoned`, or `pattern`), **Not measured**, and the **Next measurement** that would most change the ranking. It never states a number no command produced, and it changes no code unless you ask. Put the measuring commands on the profile's `perf:` line.

### Review a whole layer

```
/qa:review all backend                         # asks which areas to review
/qa:review all backend --units critical        # only the profile's Critical areas (the default with --no-ask)
/qa:review all --units everything              # every unit of every layer
```

This is a different job from a diff review: bugs that never showed up in a diff are found by reading the code itself. The work is split into units (your `Critical areas` first, then one unit per remaining top-level directory) and one reviewer per unit runs in a fresh context, because one long pass reads the end of the code worse than the start. The report adds a **Coverage** line (units and files reviewed), and units not chosen or not reached are listed under **Not checked**.

It costs several times more than the alternatives. Start with `--units critical`. It needs the Agent tool; without it the review runs unit by unit in one context and stops after six units.

## The profile

One file per project, facts only. Documentation stays the source of truth: **point to it, do not copy it.** An invariant is one line plus the place that enforces it and the doc section that explains it.

```markdown
---
stacks: [python, django, vue]
confirmed: 2026-10-06        # set by /qa:init-profile
plugin: 0.4.1                # plugin version it was written with
review-after-days: 180
---

# Project profile

## Layout
- backend: be/ (Django, DRF)
- frontend: fe/
- infra: infras/, be/Dockerfile*      # paths or globs; the longest literal prefix wins
- docs: docs/, AGENTS.md
- tests: be/*/tests/, fe/src/**/*.test.ts
- ignore: scripts/legacy/             # never reviewed

## Commands
- lint: `cd be && uv run ruff check app`
- test: `cd be && uv run pytest app/`
- perf: `cd fe && pnpm build`
- extra: `python3 scripts/check-doc-links.py`

## Invariants
- INV-001: No network I/O under `select_for_update()` — enforced by billing/services.py · docs/features/BILLING.md § Locks

## Critical areas
- be/app/billing/ — money, locks, refunds — INV-001

## Backend checks      # project-specific items added to the generic checklist
## Docs checks         # same, for documentation
## Performance         # budgets, hot paths, known traps (used by /qa:perf)
## Finish              # reviewers, commit-format, ticket-from-branch (used by /qa:finish)
## Severity overrides
- CRITICAL: doc in docs/features/ states a route the code does not serve
## Docs to keep in sync
- billing, refunds — docs/features/BILLING.md
```

The full template is [`plugins/qa/skills/init-profile/profile-template.md`](../plugins/qa/skills/init-profile/profile-template.md). Keep the profile short (about 150 lines); a long one usually means generic rules or copied documentation leaked in. Rules that two or more projects need belong in a pack in this repo, not in profiles.

## Keeping a project current

The review reports drift and never fixes it. Each record in **Profile drift** says what to do:

| Record | Meaning | What to do |
|---|---|---|
| `STACK <key> (pack available)` | The project uses a stack that has a pack but `stacks` lacks it | Add the key, or re-run `/qa:init-profile` |
| `STACK <key> (no pack)` | A stack with no pack here | Add the key and put its rules under the profile's checks |
| `STACK <key> (unknown key)` | A key in `stacks` matches nothing | Fix or remove it |
| `PACK <key> (written for <n>, project uses <m>): may be stale` | The project is on a newer major version than the pack | Tell the plugin owner (or refresh the pack) |
| `LAYOUT <dir> (unmapped)` | Changed files that match no `Layout` or `ignore` entry | Run `/qa:init-profile` and assign or ignore them |
| `PROFILE (…)` | Never confirmed, confirmed too long ago, or written with an older plugin | Run `/qa:init-profile` to re-confirm |
| `GAP layer <role>` | A layer with neither a plugin checklist nor profile checks | Add checks to the profile |

`/qa:init-profile` on an existing profile updates it in place, keeps your invariants, and asks only about paths that are new or changed.

## Headless and CI

```bash
claude -p "/qa:review --no-ask" --model sonnet \
  --allowedTools "Read,Glob,Grep,Bash(git *)" --output-format json < /dev/null
```

Put the prompt first, then the flags, and redirect stdin. Grant only the commands you want run; any profile command that is not allowed is reported as `not run`, never as a pass. Add `Agent` to the allowed tools for `all`. The review reads the profile from the working directory.

## When it is unsure

It asks you, or, when it cannot ask (`--no-ask`, headless), it does not guess: the item goes under **Not checked** as a question that names the profile section where your answer belongs. The `Packs:` line says which packs a review should load, not that the model read them; if a review says it could not read a reference file, treat that review as weaker.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `/qa:review` not found | The plugin is not installed or enabled: `claude plugin list` |
| Two `qa` plugins loaded | A `--plugin-dir` copy plus the installed one; disable one |
| Version did not change after `update` | Run `claude plugin marketplace update dqcuong93` first; if still stale, uninstall and reinstall |
| Every review says `PROFILE (no confirmed date)` | The profile predates the field; run `/qa:init-profile` once |
| Commands show `not run (permission)` | Allow them (`--allowedTools` or your settings), or accept that they are unchecked |
| zsh breaks on `echo =====` or `${PIPESTATUS[0]}` | Known zsh quirks; the skills avoid them, so avoid them in your own profile commands |
| Cursor ignores the skills | Cursor does not read Claude plugins; `npx skills add dqcuong93/agent-skills -a cursor` is an untested option |

## Reporting a gap

If your project needs a stack, layer, or rule the plugin does not have, put it in your profile first. Open an issue or a pull request here once two projects need the same thing. This repo is public: no project names, hosts, credentials, or business rules in anything you contribute.
