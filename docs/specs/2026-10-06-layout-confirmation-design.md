# Layout confirmation in `init-profile` — design (wave 2, cycle 0)

Status: implemented; accepted for the layout question, update and review behaviour. The profile write step could not be tested headless (see Results). Date: 2026-10-06.

## Goal

The plugin must not impose where a project keeps its files. Today `/qa:init-profile` infers the `Layout` from manifests and shows it inside the full draft; the owner is asked to confirm invariants and severity overrides, not the layout. A project that keeps a `Dockerfile` inside its backend directory, or a `scripts/` directory of unclear purpose, gets a guessed role. This cycle makes the owner confirm every path-to-role assignment, on first run and on every update, and lets `/qa:review` say when a changed file has no role.

Cycle 1 (`2026-10-06-infra-layer-design.md`) depends on this: infra rules apply only to files the profile assigns to `infra`.

## Decisions

### D1. A separate layout question, before invariants

`skills/init-profile/SKILL.md` steps become:

1. Detect (unchanged).
2. Map stacks (unchanged).
3. **Confirm layout** (new). Ends the turn with the question below; nothing is drafted or written in this turn.
4. Harvest invariants and rules, using the confirmed layout.
5. Draft.
6. Present and end the turn (invariants, severity overrides, as today).
7. Write after confirmation.
8. Verify commands.

The question is asked in the conversation's language. Layout comes first because the layer decides which rules apply to a path, so harvesting checks before the layout is settled would attach them to the wrong layer.

### D2. What the question lists

Every candidate path or file gets one numbered line: path, proposed role, the evidence. Candidates are:

- each directory holding a manifest from `stack-signals.md` § Manifests, at the root and one directory down;
- each infra file found by name anywhere in the repo (`Dockerfile*`, `docker-compose*.yml`, `compose*.yaml`, `Caddyfile*`), listed as its own line even when its directory is already assigned to another layer;
- each directory holding tests;
- on an update, every top-level directory or manifest not covered by an existing `Layout` path or `ignore` entry.

Roles offered: `backend`, `frontend`, `infra`, `tests`, `ignore`, or a new role the owner names (recorded under `Layout` with that name; reviews report it under **Not checked** until a checklist exists). Example:

```text
I found these paths. Tell me which are wrong; reply "ok" if all are right.

1. `be/` — backend (pyproject.toml: Django)
2. `fe/` — frontend (package.json: Vue, Astro)
3. `be/Dockerfile` — infra? (it sits inside `be/`, so it could be backend)
4. `infras/` — infra (docker-compose.yml, Caddyfile)
5. `scripts/` — unclear: backend, infra, or ignore?
```

Replies: `ok`, `3 backend`, `5 ignore`, `5 tests`, or free text. A reply that assigns nothing for an unclear line is not an answer; ask again for that line only.

### D3. Update asks only what changed

On an existing profile, step 1 compares what it detects with `Layout` and `ignore`. A path already listed (assigned or ignored) is not asked about again. If nothing new is found, step 3 states "layout unchanged" and continues without ending the turn. A path whose detected role disagrees with its assigned role is asked once, with both roles shown, and never silently changed.

### D4. `ignore` in the profile

The profile template gains one line under `Layout`:

```markdown
- ignore:
```

It holds comma-separated paths or globs the owner said belong to no layer (`scripts/legacy/`, `vendor/**`). A path may be a glob everywhere in `Layout`. Entries are comma-separated paths, each optionally followed by a parenthetical note, as in Project A's profile; a path already "listed" means it appears in that position on any `Layout` line. When several entries match a file, the one with the longest literal prefix (the text before the first `*`) wins, so `be/Dockerfile*` beats `be/`. Review's step 2 (`SKILL.md`) is reworded to say this; today it says only "longest path wins". A changed file under `ignore` is reported under **Not checked** as `ignored by profile`, never reviewed. Profiles without the line stay valid; it is added the first time the owner ignores something.

### D5. `/qa:review` reports unmapped files

Step 3 (Drift) gains one record type, only with a profile:

- `LAYOUT <directory> (unmapped): <n> changed files`: changed files that match no `Layout` path and no `ignore` entry. One record per top-level directory of those files.

Output part 3 gives the action: `LAYOUT … (unmapped)` → run `/qa:init-profile` to assign or ignore it. Review reads and reports; it does not ask or edit. These files stay under **Not checked** as today. Records are built from changed files only, so a review never scans the whole repo for them.

### D6. Check script

`scripts/check-plugin.py` gains one check: the profile template has an `ignore:` line under `Layout`. `review/SKILL.md` step 2 changes its tie-break wording as D4 says. No other code change.

## Tests

Fake project in a scratch directory (`git init`, uncommitted): `be/` (`pyproject.toml` with Django), `be/Dockerfile`, `fe/` (`package.json` with Vue), `infras/docker-compose.yml` and `infras/Caddyfile`, an unclear `scripts/` directory, tests under `be/tests/`. Headless init runs take up to three turns (layout question, invariants question, then the write): run `/qa:init-profile`, read `session_id` from the JSON, then answer each question with `--resume <session_id>`. Confirm first that `--resume` keeps the pending question; if it does not, change the test method before running anything. Allow `Read,Glob,Write,Bash(ls *)`.

1. **First run, turn 1:** the question lists `be/Dockerfile` and `scripts/` as separate lines; `.claude/project-profile.md` does not exist yet; the turn ends with the question.
2. **First run, turns 2 and 3:** answer `3 infra`, `5 ignore`. Turn 2 must end with the invariants question and still write nothing; after the confirming reply in turn 3 the profile exists, with `be/Dockerfile` under `infra` and `scripts/` under `ignore`.
3. **Update, nothing new:** re-run on the same tree; no layout question, no change to `Layout`.
4. **Update, new directory:** add `tools/` with a `package.json`; the question lists only `tools/`.
5. **Review:** change a file under a new, unlisted directory and one under `scripts/`; `/qa:review --no-ask` reports `LAYOUT <dir> (unmapped)` for the first and `ignored by profile` for the second, and reviews neither.
6. **Regression:** `/qa:review --no-ask` on a profile without `ignore:` behaves as before.

Each run twice, same model (Sonnet), same tools.

## Acceptance

- Runs 1, 3, 4, 5 pass in both attempts; run 2 passes in both attempts for the layout part.
- In run 1 the model does not write the profile or start drafting invariants before the answer (the known weakness of "ask the user" gates; read each transcript).
- `check-plugin.py` and `claude plugin validate ./plugins/qa --strict` pass.
- The existing profile of Project A is still valid without edits.

## Risks

- **Question fatigue:** a repo with many infra files makes a long list. Mitigation: show one line per directory (`infras/`: compose file, Caddyfile) and a separate line for an infra file only when its directory is assigned another role; the first question lists top-level directories plus those exceptions, not every file.
- **Skipped gate:** the model may continue past the question. Mitigation: the "ends the turn" wording used by the other gates, and two runs per test.
- **Profile growth:** `ignore` can grow. The existing ~150-line guidance applies; globs keep it short.

## Results

Model Sonnet, headless, working copy via `--plugin-dir`, two attempts per scenario (fake projects `a` and `b`; `c` and `d` for the no-`ignore` regression). `--resume` was confirmed to carry a pending question across turns before testing.

| Test | Result |
|---|---|
| 1. First run, turn 1 | pass 2/2: `be/Dockerfile` and `scripts/` on separate lines; no profile file written; turn ended with the question |
| 2. First run, turns 2 and 3 | layout part pass 2/2 (turn 2 ended with the invariants question and wrote nothing; the draft had `be/Dockerfile` under `infra` and `scripts/` under `ignore`). The write itself could not be tested: headless `Write` to `.claude/project-profile.md` is denied as a sensitive path, even with `acceptEdits`; the model reported it and did not work around it. The profile used by later runs was built by hand from the drafts. |
| 3. Update, nothing new | pass 2/2: `layout unchanged`, no layout question (the run then continued to the invariants question, as the step says) |
| 4. Update, new `tools/` | pass 2/2: the question listed only `tools/` |
| 5. Review `LAYOUT` / `ignored by profile` | pass 2/2: `LAYOUT newdir (unmapped)` and `LAYOUT tools (unmapped)` with the `/qa:init-profile` action; `scripts/run.sh` under Not checked as `ignored by profile`; neither reviewed |
| 6. Glob tie-break | pass 4/4 (`be/Dockerfile` entry or `be/Dockerfile*` glob beat `be/`; file treated as infra) |
| 7. Regression without `ignore:` | pass 2/2: no error; `scripts` reported as `LAYOUT scripts (unmapped)` |

Defect found and fixed during the runs: the profile file itself (`.claude/project-profile.md`, untracked in the test projects) produced `LAYOUT .claude (unmapped)` in 4/4 runs. `review/SKILL.md` now exempts it; two re-runs showed no such record.

Not verified:

- The profile write step in headless runs (above).
- Project A's own profile: its `tests` line uses `·` between two paths and notes in parentheses contain commas, which the D4 entry format does not describe. Only its first path per line counts as an entry; the second `tests` path would be asked about again on an update. Read, not run.
- Run `b` of the first review reported `STACK docker (unknown key)` because the `docker` signal row still says "at the project root" while the Dockerfile sits in `be/`; run `d` accepted it. This is the existing row, changed by the `infra` plan (Task 3), not by this cycle.
- Run `d` claimed `infras/` does not exist when it does; it never listed the directory. Unrelated to this change; a reminder that "Not checked" claims need a check of their own.
