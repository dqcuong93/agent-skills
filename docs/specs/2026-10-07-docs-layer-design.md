# `docs` layer for `/qa:review` — design (wave 2, cycle 2)

Status: implemented; acceptance passed with the caveats under Results. Date: 2026-10-07.

## Goal

Add a `docs` layer to `/qa:review` so it covers what Project A's in-repo `qa-qc-docs-ai` skill covers: system documentation (feature specs, indexes, architecture notes) and multi-AI configuration (canonical context file, tool adapters, skills list), driven by the project profile. When it passes the acceptance tests below, that in-repo skill can be removed. The model and the infra cycle are in `2026-10-05-unified-review-design.md` and `2026-10-06-infra-layer-design.md`.

Out of scope: whole-repo audits (orphan links across every file, every `@see` path in the codebase). They belong to the `all` scope (cycle 4). In diff mode the layer reviews the changed docs and the docs a change should have updated.

## Decisions

### D1. Files and routing

No new skill. New reference files under `skills/review/references/`:

| File | Holds |
|---|---|
| `docs.md` | Rules true for any project's documentation and AI configuration |
| `docs-mkdocs.md` | MkDocs rules (`Written for: MkDocs 1`) |

`SKILL.md` changes: routing table rows for both files (the pack loads when `docs` is in scope and `mkdocs` is in `stacks`); the argument becomes `[backend|frontend|infra|docs]`; the profile section `Docs checks` is walked in step 6 like the other layers' checks. `stack-signals.md` gains `| mkdocs | docs | a mkdocs.yml anywhere in the repo |`; `drift.py` gets a file-signal entry for it.

The profile template gains a `- docs:` line under `Layout` and a `## Docs checks` section. Routing is by `Layout` only (no routing by file name): a project lists `docs/`, `AGENTS.md`, `.cursor/` and so on under `docs`, and the longest literal prefix wins. A change to a doc that sits inside another layer's path (a backend `README`) goes to that layer; the docs-drift step (step 9) still compares it with the code.

### D2. Where each old rule goes

| Old rule | Goes to |
|---|---|
| Feature spec states the contract (rules, integration points, live vs backlog) | `docs.md` |
| Routes, endpoints, env vars, and ports in docs match the shipped code | `docs.md` (the check names the failure: a reader follows a dead route) |
| Links resolve; no link to a deleted or ephemeral file | `docs.md` |
| New doc has an index row and a nav entry | `docs.md` (index) and `docs-mkdocs.md` (nav, `mkdocs build --strict`) |
| Names, routes, or fields the diff removed or renamed are searched for in docs and comments | `docs.md` |
| Docstrings and comments that encode a contract match the code | already in the backend and frontend checklists; `docs.md` points at neither, it does not repeat them |
| One canonical AI context file; adapters only point to it or import it | `docs.md` |
| Adapter files stay short; no domain content copied into them or into always-on rules | `docs.md` |
| Skills list in the context file matches the skills on disk | `docs.md` |
| Teaching diagrams still argue the same fact as the doc they illustrate | `docs.md` generic part: "a diagram or figure the change falsifies is updated"; which diagrams exist stays in the profile |
| The `git grep` lines (orphan `superpowers/specs` links, deprecated mirror files, `@see` existence, `AGENTS.md § Gotchas` pointers) | profile `Docs checks` (they name project paths) |
| Update order (docs first, context file only for new routes/gotchas), ephemeral specs deleted after the branch | profile |
| Pre-commit hooks (markdownlint, links, mkdocs) | profile `extra` commands |

Anything the profile already holds is not copied into the plugin.

### D3. Severity

The shared table already grades docs drift WARNING. A project that treats a wrong documented contract as CRITICAL says so under its profile `Severity overrides`, as for any other rule; the layer adds no default override. The old skill's CRITICAL cases (wrong contract, orphan link in shipped docs, duplicate AI context causing drift) move to Project A's profile.

### D4. Commands

Doc checks that need a tool come from the profile's `extra` commands (link checker, markdown lint, `mkdocs build --strict`). If a tool is missing or not allowed, the report says `not run (<why>)` and the finding is judged from the text.

### D5. `check-plugin.py`, `drift.py`

`check-plugin.py` needs no change beyond the new files being linked from `SKILL.md`. `drift.py` gets one entry in `FILE_SIGNALS` (`mkdocs`: `mkdocs.yml`) and a unit test for it; `CLAUDE.md` already says to change the script and its tests together with `stack-signals.md`.

## Tests

Clone Project A, extend its profile (`docs:` layout line, `mkdocs` in `stacks`, `Docs checks` carried over from the old skill's grep lines, doc checks under `extra`), and plant uncommitted edits. Ground truth first: record what the project's link checker and `mkdocs build --strict` say on the clean clone and on the planted tree.

1. A feature doc states a route the code does not serve (change the doc, not the code).
2. A new doc file with no index row and no nav entry.
3. A doc linking to a file that the change deletes.
4. A paragraph of domain content copied into an adapter file that should only import the canonical context.
5. A renamed route in code with the old route left in a doc the diff does not touch.
6. A change touching docs and backend together (routing across layers).
7. A doc inside a backend path (checks that routing follows the profile; run once as is, once with it listed under `docs`).

Run `/qa:review` and the old `qa-qc-docs-ai` twice each, same model, tools, and prompt.

## Acceptance

- Planted bugs 1, 2, 3 and 5 are reported in both runs; bug 4 in at least one; none graded above WARNING unless the profile says so.
- Every finding is checked against the files by hand; none contradicts them.
- Run 6 reports backend and docs findings in one report, each under its layer's rules; run 7 follows the profile in both cases.
- On the same diff, `/qa:review` finds everything the old skill found; extra findings are judged by hand.
- `Packs:` lists `mkdocs` when it is in `stacks`; the output is valid; `check-plugin.py`, the script tests, and `claude plugin validate --strict` pass.

## Risks

- **Over-reach into whole-repo audits.** Grep lines that scan every file are tempting to put in `docs.md`; they stay in the profile and in the `all` scope.
- **Generic rules that are really one project's habits** (for example "context file only for new routes"). Each `docs.md` item names the failure it prevents; project habits stay in the profile.
- **Overlap with step 9** (docs drift against the profile's `Docs to keep in sync`). The layer reviews docs that changed; step 9 reviews docs the change should have updated. A finding reported by both is merged under the finding rules.

## Results

Model Sonnet, headless, working copy via `--plugin-dir` (old skill: its in-repo copy), two runs per scenario, on a scratch clone of Project A. The clone's profile got `docs`, `mkdocs`, `docker`, `caddy` in `stacks`/`Layout`, the old skill's grep lines as `Docs checks`, and the link checker plus a strict docs build under `extra`.

Ground truth. On the clean clone the link checker exits 0 and the strict build succeeds. On the planted tree the link checker reports the six broken links caused by the deleted page (bug 3) and the strict build aborts (bug 2, and bug 3 through the nav); bugs 1, 4 and 5 are invisible to both tools.

Scenario A (bugs 1–5; bug 5 is a backend route rename, so the diff spans docs and backend):

| Planted bug | New skill, run 1 / run 2 | Old `qa-qc-docs-ai`, run 1 / run 2 |
|---|---|---|
| 1 doc names a route the code does not serve | WARNING / WARNING | CRITICAL / CRITICAL |
| 2 new doc, no index row, no nav entry | WARNING / WARNING | WARNING / WARNING |
| 3 deleted page still linked from many files | CRITICAL / WARNING | CRITICAL / CRITICAL |
| 4 context block pasted into the adapter file | WARNING / WARNING | WARNING / CRITICAL |
| 5 route renamed in code, docs untouched | CRITICAL (callers and 6–7 doc mentions listed) / CRITICAL | CRITICAL / CRITICAL |

The default grading is lower than the old skill's on bugs 1, 3 and 4, as the spec says (D3: the layer adds no default override). After adding three overrides to Project A's profile (doc contract wrong, link to a deleted doc, context copied into an adapter file: CRITICAL), two more new-skill runs graded 1, 3, 4 and 5 CRITICAL and bug 2 WARNING in one run and CRITICAL in the other.

Scenario B (docs-only diff, 2 runs): findings the same as above minus bug 5. Run 1 read `docs.md` and `docs-mkdocs.md` and no backend, frontend, or infra reference. Run 2 tried to read the references through `cat`, which the permission check refused; it said so and reviewed from the profile's `Docs checks`, yet its `Packs:` line still listed `mkdocs`.

Scenario C (docs plus backend in one report): scenario A already covers it; both new runs reported the backend route finding and the docs findings together, with `Packs: python 3/3, django 6/6, mkdocs 1/?`.

Scenario D (a doc inside a backend path, 2 runs each): with the profile unchanged the file was reviewed under backend (`Packs:` limited to python and django; the finding on the stale route was the same); with its path under `docs:` it was reviewed under docs (`--layers docs`, `docs-mkdocs.md` read, `Packs: mkdocs 1/?`). Routing followed the profile in all four runs. A first attempt at D used a profile reset by a stray `git checkout`, so it tested nothing and was discarded.

Findings were read against the files; none contradicted them.

Caveats:

- The `Packs:` line says which packs the review should load, not that the model read them (scenario B, run 2).
- Grading beyond the overrides varies: bug 3 was CRITICAL in one run and WARNING in the other; with the overrides, bug 2 went CRITICAL in one of two runs.
- The strict docs build ran only for the ground truth; in the reviews the model inferred nav and index errors from the files and the link checker.
- The new skill costs more than the old one ($0.29–0.32 against about $0.21) and takes 11–17 turns against 5–6.
- Whole-repo audits (orphan links outside the diff's reach) were not tested; they belong to the `all` scope.
