# `/qa:perf` — design (wave 2, cycle 3)

Status: implemented; accepted with the caveats under Results. Date: 2026-10-06. The plan is folded into this spec.

## Goal

Port Project A's in-repo `performance-optimization` skill into the plugin as its own skill. It is an analysis, not a diff review: it asks what is slow and why, measures when it can, and keeps measured results apart from reasoning.

## Decisions

- **Own skill, `/qa:perf`**, in `plugins/qa/skills/perf/` with its own references (`backend.md`, `frontend.md`, packs `backend-django.md`, `frontend-astro.md`, `frontend-vue.md`). It shares the profile and the stack keys with `/qa:review` but not its workflow.
- **Scope**: an argument (path, endpoint, page), else the profile's hot paths, else the changed files.
- **Measure first**: the profile's `perf` command (new `- perf:` line under `Commands`) and a production build for frontends. Without a runnable measurement the output says `not measured (<why>)` and what to run. A number that no command produced is never written.
- **Evidence labels**: every finding is `measured`, `reasoned` (mechanism from the code, no number), or `pattern` (costly pattern, effect unknown until measured). Findings are ranked by expected effect on the user's wait.
- **Profile**: a `## Performance` section (budgets, hot paths, known traps) and the `perf:` command. Project rules such as critical-CSS scope stay there.
- **No edits** unless the user asks.
- `check-plugin.py` checks that each perf reference is linked from `perf/SKILL.md` and that a pack has `Written for:` on line 3 and a row in `stack-signals.md`. `drift.py` reads only the review references; perf packs are not part of the `Packs:` line.

## Results

Clone of Project A, profile extended with a `perf` command and a `Performance` section, six planted problems: an unbounded list query, an N+1 on a foreign key, a `len()` over a filtered queryset per row, a 3000-item list with an O(n²) label function and no virtualisation, `client:load` on that island, and an unoptimised public image without dimensions. Two runs each of `/qa:perf --no-ask` and the old skill, Sonnet, same tools.

| | New, run 1 / run 2 | Old `performance-optimization`, run 1 / run 2 |
|---|---|---|
| Planted problems found | 6/6 / 6/6 | 6/6 / 6/6 |
| Evidence labelled | yes (reasoned or pattern) | no |
| States that nothing was measured | yes, with why | no |
| Cost, turns | $0.24–0.27, 13–16 turns | $0.06–0.20, 5–9 turns |

Neither could measure anything in the clone (no `node_modules`, no database). The new skill said so and listed the commands to run; the old one wrote estimates such as "about 2001 queries for 1000 rows" without a label, and the two old runs disagreed on the comparison count of the O(n²) function (4.5 million and 9 million; the new skill's 9 million is the right count for the code). The new runs also noted, outside the performance scope, that the planted view exposes every user's email to any signed-in user and that the view was not wired to a route.

Not tested: a run where a measurement command can execute (the label `measured` has not been exercised), the `--no-ask` path without a profile, and the Cursor side.
