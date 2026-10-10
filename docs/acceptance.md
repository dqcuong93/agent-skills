# Acceptance results

Headless runs of the working copy (`--plugin-dir`), model Claude Sonnet, against real or cloned projects with planted bugs, compared with the in-repo skill each one replaces. One to a few runs per case. Treat the numbers as indicative, not as rates. No project names, hosts, or business rules here.

`v0.4.1` later tightened the docs and frontend checks after a separate side-by-side run on three real changes (documented behaviour checked against the code, a changed contract searched across docs, and unresolved-state, failed-check, expired-session, role-aware-copy, and stale-value checks on the frontend). That run found the same important defects as the in-repo skills at about half the tokens. It is not in the tables below.

## Wave 1 — `/qa:review` (2026-10-05)

Backend test suites were not run (no database). Lint, format, and frontend tests were. About 20 runs, $0.17–0.50 each.

| Check | Result |
|---|---|
| `validate --strict` (marketplace and plugin), `check-plugin.py` | pass |
| `/qa:init-profile` on both source projects stops for confirmation and writes nothing until approved | pass. After approval every non-database command ran and passed |
| Side by side, 2 commits per project, old skills vs `/qa:review` | After one wording pass: every old CRITICAL/WARNING found or argued. No CRITICAL false positives. One extra WARNING on a past commit came from judging it against the current tree; the rule was added and not re-run |
| Drift reports manifests, not `none`; a pack written for an older major emits `PACK … may be stale` | `none` on correctly listed stacks (3 runs). Stale detection needed three wording passes; the final run emits the line (1 run). `Packs:` still shows `?` for some frontend packs whose version is in a nested `package.json` |
| No profile: ask and stop | 3/3 asked with the detected stacks, no Verdict |
| `--no-ask` without a profile | Verdict, no question, layers `assumed` |
| Severity override | 2/2 graded the finding at the override level |
| Overlapping layout (repo root plus a frontend directory) | `.vue` files reviewed as frontend |
| Nothing deleted from the projects | pass |

Wording fixed during these runs: tests-can-fail (backend, frontend); accessibility examples and a no-downgrade rule; keys already in `stacks` are never drift; keys without a pack are listed in `stacks`; lookups check the installed package first and never trust project docs about a library; a commit is judged at its own tree; drift ends with a `Packs:` line and checks lockfiles for transitive versions.

## Layout confirmation (2026-10-06)

Two headless attempts per scenario. `--resume` carries a pending question across turns.

| Test | Result |
|---|---|
| First run, turn 1 | pass 2/2: odd paths on their own lines; no profile written; turn ended with the question |
| First run, later turns | layout pass 2/2 (invariants question, nothing written). The write itself could not be tested: headless `Write` to `.claude/project-profile.md` is denied |
| Update, nothing new | pass 2/2: `layout unchanged`, no layout question |
| Update, one new directory | pass 2/2: the question listed only that directory |
| Review of unmapped and ignored paths | pass 2/2: `LAYOUT … (unmapped)` with the `/qa:init-profile` action; ignored files under Not checked, not reviewed |
| Glob longer than its directory | pass 4/4 |
| Profile with no `ignore:` line | pass 2/2: no error; the directory reported as unmapped |

A defect found in these runs is fixed: `.claude/project-profile.md` itself no longer produces `LAYOUT .claude (unmapped)`.

Still open: the write step. A `tests` line that joins two paths with `·`, or whose parenthetical notes contain commas, only counts the first path; the second would be asked about again on an update (read, not run).

## `infra` (2026-10-06)

Scratch clone, profile extended with `docker` and `caddy`. Ground truth: `caddy validate` and `docker compose config -q` both pass on the planted tree, so the bugs are only visible by reading. Two runs each. New skill 10–12 turns ($0.25–0.28); the old infra skill 4 turns ($0.17) and ran no validator.

| Planted bug | New | Old |
|---|---|---|
| Route shadowed by a broader matcher | CRITICAL / CRITICAL | found / found |
| Duplicate response header | CRITICAL / CRITICAL | found / found |
| Password literal in compose `environment:` | CRITICAL / CRITICAL | found (merged with the next) / found |
| Variable missing from the example env file | WARNING / WARNING | found (merged with the previous) / found |
| `restart:` removed from a service | WARNING / WARNING | found / found |

A mixed backend-and-infra diff reported the backend CRITICAL and the infra findings in one report. A Dockerfile inside a backend directory was not reviewed until the profile assigned it to `infra` (secret CRITICAL, `USER root` WARNING, missing `.dockerignore` WARNING). Routing followed the profile.

Caveats: one run listed `docker` and `caddy` on `Packs:` without reading the reference files (the line is what should be loaded, not proof it was). Severity of the shadowed route was CRITICAL here and WARNING in an earlier run on another tree, unless the profile overrides it. `caddy validate` also passes on the shadowed-route tree. `k8s` was out of scope.

## `docs` (2026-10-07)

Scratch clone. On the clean tree the link checker exits 0 and the strict build succeeds. On the planted tree the link checker reports the broken links from a deleted page and the strict build aborts. A wrong route name, a pasted context block, and an untouched doc after a rename are invisible to both tools. Two runs each. New skill $0.29–0.32, 11–17 turns; old skill about $0.21, 5–6 turns.

| Planted bug | New, default | Old |
|---|---|---|
| Doc names a route the code does not serve | WARNING / WARNING | CRITICAL / CRITICAL |
| New doc, no index row, no nav entry | WARNING / WARNING | WARNING / WARNING |
| Deleted page still linked | CRITICAL / WARNING | CRITICAL / CRITICAL |
| Context block pasted into an adapter file | WARNING / WARNING | WARNING / CRITICAL |
| Route renamed in code, docs untouched | CRITICAL / CRITICAL | CRITICAL / CRITICAL |

The lower default grades match the design: the layer adds no default override. With three profile overrides (wrong doc contract, link to a deleted doc, context copied into an adapter: CRITICAL), two further runs graded the first, third, fourth, and fifth CRITICAL, and the index bug WARNING in one run and CRITICAL in the other.

Docs-only and mixed diffs behaved as specified. A doc that sits inside a backend path was reviewed as backend until its path was listed under `docs:`.

Caveats: `Packs:` does not prove the model read the pack (one run said the read was refused and still listed `mkdocs`). Grades move between runs even with overrides. The strict build was used for ground truth; the reviews inferred nav and index errors from the files and the link checker. Whole-repo orphan links were not tested; they belong to `all`.

## `/qa:perf` (2026-10-06)

Six planted problems (unbounded query, N+1, `len()` over a queryset per row, a 3000-item list with an O(n²) label and no virtualisation, `client:load` on that island, an image without dimensions). Two runs each. Neither skill could measure anything (no `node_modules`, no database).

| | New | Old |
|---|---|---|
| Planted problems | 6/6 / 6/6 | 6/6 / 6/6 |
| Evidence labelled | yes (`reasoned` or `pattern`) | no |
| Says nothing was measured | yes, with why | no |
| Cost, turns | $0.24–0.27, 13–16 | $0.06–0.20, 5–9 |

The old runs wrote unlabeled estimates and disagreed with each other on the O(n²) count. The new skill's count matched the code, and it refused to invent a measurement.

Not tested: a run where a measurement command can execute (the `measured` label), `--no-ask` without a profile, and Cursor.

## `/qa:review all` (2026-10-06)

Backend only, seven planted bugs committed so there was no diff: three in critical units (removed row lock, `AllowAny` on a user view, `AllowAny` on a paid view) and four in the rest (`AllowAny` on a notifications view, a hard-coded vendor token, `eval` on user input, `shell=True` with concatenated input). Runs that hit the monthly spend limit were discarded.

| Arm | Runs | Planted bugs | Cost |
|---|---|---|---|
| Orchestrator and reviewers (`all backend --units everything`) | 1 | 7 of 7, all CRITICAL; 17 units, 12 reviewers, 3 critical units included | $5.0 |
| Same skill, no Agent tool (sequential, stop after six) | 1 | 3 of 7 (the critical units; the rest listed as not reached) | $1.15 |
| Old backend skill asked to review the whole backend | 2 | 4 of 7 and 2 of 7, no coverage line | $0.36–0.45 |

The spread between the two old runs is as large as the gap to the sequential arm, so this is not a recall rate. Cost is about 4× to 14× a diff review on a backend of about 230 Python files. `--units critical` was not run. A unit that is too large was not tested. Frontend, infra, and docs in `all` mode were not tested.

## Profile lifecycle (2026-10-06)

`scripts/test_drift.py`: 12 tests pass, including no `confirmed` date, a date past `review-after-days`, a date inside the limit, an older `plugin:` version, the current version, a layer with neither checklist nor profile checks, the same layer with checks, and `tests` / `ignore` exempt. On one real profile the script reports `PROFILE (no confirmed date)` and nothing else, because `/qa:init-profile` has not been run since the fields were added. The write step that sets `confirmed:` and `plugin:` was not tested (headless runs cannot write under `.claude/`).

## `/qa:finish` (2026-10-06)

`--no-ask`, on a ticket branch, profile with a `Finish` section.

- Needs-decision (a permission class changed to `AllowAny`, one doc line edited): two runs. Both called `/qa:review`, found the broken contract, the failing test, the stale schema and docs, and the throttle and CSRF consequences, left them unfixed, and printed a Conventional Commits message with the ticket from the branch name. Neither ran `git commit` or `git push`. Commands that were not allowed were reported as `not run`.
- Auto-fix (a debug `print` of the request body and an unused import): one run. Both lines removed, lint, format, and the touched app's tests run (18 passed), test-writing skipped because the diff was empty, nothing left to commit. No `git commit` or `git push`. That run used services already on the machine (separate test database, shared cache).

Not tested: the interactive question, writing a missing test, `reviewers:` lines, and the `/qa:perf` offer.

## `backend-pyqt` pack (2026-10-10)

Scratch clone of a desktop PyQt5 app, profile with `python` and `pyqt` packs, three uncommitted planted bugs. `/qa:review uncommitted --no-ask`, one headless run, model Claude Sonnet. Tests, ruff, and drift ran.

| Planted bug | Result |
|---|---|
| Resume query dropped the `processing` status | CRITICAL, tied to the profile invariant; named the lost files on resume; two failing tests |
| `import sqlite3` in the UI layer | CRITICAL, tied to the profile invariant; failing layer-boundary test, ruff F401/I001 |
| `QMessageBox` called inside `QThread.run()` | CRITICAL, tied to the pack rule "Widgets on the main thread only"; also found the duplicate error display and the raw exception text in the dialog |

Extra WARNING: stale docstring after the first change (correct). No false positives. `Packs:` showed `python 3/3, pyqt 5/5`, `Drift: none`.

One run, so indicative only.

Profile write step (`/qa:init-profile`, update path, profile deleted from the worktree), two turns with `--resume`: turn 1 checked stacks, doc pointers and commands, said `layout unchanged`, and ended with the confirmation question without writing. Turn 2 ("ok") was denied under `acceptEdits` (both `Write` and `Bash` to `.claude/project-profile.md`; Claude did not work around it). With `--permission-mode bypassPermissions`, run by the user in the scratch clone, it wrote the 120-line file with `confirmed:` set to the run date and `plugin:` to the installed version, then ran lint, format, and tests (all passed). So the write works, but headless needs `bypassPermissions` (or an interactive permission prompt) because `.claude/` is protected.

## Still open

- `/qa:init-profile` write step: tested once on the update path only (see `backend-pyqt` section); a first-run write from scratch is untested.
- A `tests` (or other) layout line that joins paths with `·`, or whose notes contain commas: only the first path counts.
- `/qa:review all` on frontend, infra, and docs; `--units critical`; a unit that is too large.
- `/qa:finish`: interactive question, writing a missing test, `reviewers:`, the `/qa:perf` offer.
- `/qa:perf`: a run that can actually measure (`measured`), `--no-ask` without a profile, Cursor.
- `Packs:` names packs to load. It does not prove they were read. Some frontend packs show `?` when the version is in a nested `package.json`.
- `pyqt`: one headless run only (see above). `nuxt` and `k8s` are not written.
- Cursor does not read Claude plugins. `npx skills add dqcuong93/agent-skills -a cursor` is untested.
