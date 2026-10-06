---
name: perf
description: Use when asked why a page, endpoint, query, job, or bundle is slow, to find bottlenecks, to optimize before shipping, or to check performance of a path; it measures first and keeps measured results apart from reasoning.
argument-hint: "[backend|frontend] [--no-ask] [path | endpoint | page]"
allowed-tools: Bash(git status *) Bash(git diff *) Bash(git log *) Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/drift.py *) Read Glob Grep
---

# Performance analysis

Generic workflow. Project facts come from `.claude/project-profile.md`. Layer and stack rules come from the reference files below. This skill explains and recommends; it changes code only when the user asks.

## Change scope

!`git status --short --untracked-files=normal`

Arguments: `$ARGUMENTS`

- `backend` or `frontend`: analyse only that layer.
- `--no-ask`: never stop to ask; used by headless runs and other skills.
- A path, endpoint, or page: the thing to analyse. Empty: the profile's hot paths (`## Performance`), else the changed files above. If there is nothing to analyse, ask what is slow; with `--no-ask`, report `Nothing to analyse` and stop.

## Reference files

Load only what step 4 selects. A pack's stack key is the part of its name after the layer.

| File | Load when |
|---|---|
| [references/backend.md](references/backend.md) | a backend path is in scope |
| [references/backend-django.md](references/backend-django.md) | backend in scope and `django` in stacks |
| [references/frontend.md](references/frontend.md) | a frontend path is in scope |
| [references/frontend-astro.md](references/frontend-astro.md) | frontend in scope and `astro` in stacks |
| [references/frontend-vue.md](references/frontend-vue.md) | frontend in scope and `vue` in stacks |

## Steps

1. **Profile.** Read `.claude/project-profile.md`. With no profile, ask for the layout (or, with `--no-ask`, say the layers are assumed from the manifests) and continue without commands.
2. **Scope.** Assign the target to a layer by the profile's `Layout` (the entry with the longest literal prefix wins). A target outside every layer goes under **Not measured**.
3. **Measure first.** Run the profile's `perf` command and any command the user names; for a frontend, the production build output is a measurement. Record each number with the exact command. If nothing can be measured (no `perf` command, no running service, no tooling), say so and give the measurement the user should take (command, tool, what to record). Never state a latency, size, or count that no command produced.
4. **Load references.** For each layer in scope read `references/<layer>.md`, then `references/<layer>-<key>.md` for each key in the profile's `stacks` that has one, then the profile's `## Performance` section (budgets, hot paths, known traps).
5. **Analyse.** Read the code on the path. Trace the work one request or one page load does. Look for the items in the references that the path can reach.
6. **Rank.** Order findings by expected effect on the user's wait, not by how easy the fix is. Label every finding's evidence:
   - `measured`: a command in this run produced the number.
   - `reasoned`: derived from the code, with the mechanism stated and no number.
   - `pattern`: matches a known costly pattern; effect unknown until measured.
7. **Verify plan.** For each finding, say how to measure before and after (command, metric, the value to compare).

## Finding rules

1. **Evidence.** A finding names the file and line (or the page and element), the mechanism, and its evidence label. If you cannot name the mechanism, drop it.
2. **No invented numbers.** An estimate is written as an estimate with the assumption behind it.
3. **Trade-offs.** When the fix costs memory, freshness, or complexity, say what is given up.
4. **Merge.** The same location and cause reported twice is one finding.

## Output

Return exactly these parts, in order:

1. **Baseline**: each measurement with its command, or `not measured (<why>)` and what to run.
2. **Findings**: ordered by expected effect. One per line: `IMPACT path:line — mechanism. Evidence: measured|reasoned|pattern. Fix and trade-off. Verify: <command and metric>.` Impact is `high`, `medium`, or `low`.
3. **Not measured**: paths, layers, or claims you could not measure or read, with why. When the owner's answer would change a finding or its rank, write the item as a question and say where the answer belongs (which profile section); do not guess.
4. **Next measurement**: the one measurement that would most change the ranking.
