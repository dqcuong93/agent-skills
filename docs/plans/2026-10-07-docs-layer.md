# `docs` Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `docs` layer to `/qa:review` (generic `docs.md` plus a `mkdocs` pack) and prove it against Project A's in-repo `qa-qc-docs-ai` skill with planted bugs.

**Architecture:** Two flat reference files linked from `SKILL.md`; one new row in `stack-signals.md`; one new file-signal entry in `drift.py` with a unit test; `docs` added to the profile template and to the `init-profile` layout question. Project-specific rules stay in the profile. Behaviour is verified by headless `claude -p` runs on a clone of Project A.

**Tech Stack:** Markdown skills, Python 3 stdlib (drift script and its tests), `claude -p`.

**Spec:** `docs/specs/2026-10-07-docs-layer-design.md`

## Global Constraints

- Public repo: no project names, client names, domains, hosts, machine paths, credentials, or business rules in any tracked file. The source project is "Project A".
- Never run `git commit`, `git push`, or `git tag`. Each "Commit" step prints the command for the owner to run.
- Plugin version stays `0.3.0` (not tagged yet).
- The plugin assumes no directory names and no file placement; the profile's `Layout` is the only router.
- References are one level deep: `SKILL.md` links every reference file; reference files link to nothing.
- Every `<layer>-<stack>.md` pack has `Written for: <stack> <major>` on line 3 (line 1 title, line 2 blank).
- `!` injection lines contain no `|`, `||`, `&&`, `;`, or `( … )`.
- Nothing is changed in Project A except uncommitted edits inside a scratch clone; the real checkout is never modified.
- Shell is zsh: use `printf`, not `echo =====`; quote globs; do not chain `; echo $?`.
- In commands, `<agent-skills>` is this repo's checkout, `<project-a>` the real Project A checkout, and `$SCRATCH` a scratch directory outside both; never write a real machine path into a tracked file.
- Do not start the project's stack or touch a shared database.
- When `stack-signals.md` or a pack's `Written for:` line changes, `plugins/qa/scripts/drift.py` and `scripts/test_drift.py` change in the same task (they parse both).

## Review Focus

1. **Doc inside another layer's path** (a backend `README`): with the profile unchanged it is reviewed under backend; with its path listed under `docs` it is reviewed under docs. Pinned in Task 4 Step 6 (scenario D).
2. **Adapter duplication** needs both files read: the model must open the canonical context file as well as the adapter. Pinned in Task 4 Step 4 (bug 4).
3. **Docs-only diff loads no backend, frontend, or infra reference.** Pinned in Task 4 Step 5.
4. **Double report with step 9** (docs drift against the profile's `Docs to keep in sync`) merges into one finding. Pinned in Task 4 Step 5 (read the findings for duplicates).
5. **`mkdocs.yml` exists but `mkdocs` is not in `stacks`:** the drift output has `STACK mkdocs (pack available)`. Pinned in Task 2 Step 1 (test) and Step 5 (run).
6. **Renamed route left in an untouched doc** (bug 5): the model must grep the repo for the old name, not only read the diff. Pinned in Task 4 Step 4.

---

### Task 1: `docs.md`, `SKILL.md` wiring, profile template, `init-profile` question

**Files:**
- Create: `plugins/qa/skills/review/references/docs.md`
- Modify: `plugins/qa/skills/review/SKILL.md` (frontmatter lines 3–4, layer-argument line, routing table, `NO_PROFILE` line)
- Modify: `plugins/qa/skills/init-profile/profile-template.md`
- Modify: `plugins/qa/skills/init-profile/SKILL.md` (step 3)
- Test: `scripts/check-plugin.py` (existing)

**Interfaces:**
- Produces: layer name `docs`; file `references/docs.md`; table rows that Task 2 completes with `docs-mkdocs.md`; the profile line `- docs:` and section `## Docs checks`.

- [ ] **Step 1: Run the checks to confirm the baseline**

Run: `python3 scripts/check-plugin.py` and `python3 -m unittest discover -s scripts -p 'test_*.py'`
Expected: `OK (50 checks)` and `OK`.

- [ ] **Step 2: Create `references/docs.md`**

```markdown
# Docs checklist

Tool-agnostic. Covers documentation and AI-tool configuration. Report only items the change affects. Site-generator rules are in the `docs-<stack>.md` packs; rules for one project (file names, update order, grep audits) are in the profile's `Docs checks`.

## 1. Contract accuracy

- [ ] **States the contract**: A feature or spec document gives the rules, the integration points, and what is live versus planned, so a reader can use the feature from it.
- [ ] **Matches shipped code**: Routes, endpoints, environment variables, ports, and commands in the text exist in the code or config. Grep when unsure; a reader who follows a dead route loses time and trust.
- [ ] **No stale labels**: A removed route, a wrong port, or a cancelled feature is not presented as live.
- [ ] **Renames followed**: A name, route, or field the diff removed or renamed is searched for in docs and comments (grep the old name); every hit is updated or deleted.

## 2. Links and navigation

- [ ] **Links resolve**: Relative links point to files and anchors that exist. No link points to a deleted file or to a temporary draft that will be removed.
- [ ] **Index and nav**: A new document has a row in the project's docs index, and in the site navigation when one exists.
- [ ] **Deleted pages**: When the change deletes or moves a page, links to it are retargeted to the page that now holds the content.

## 3. AI-tool configuration

- [ ] **One canonical context file**: The shared agent context (domain, commands, conventions) lives in one file. Files for other tools import it or point to it.
- [ ] **Adapters stay thin**: A tool-specific file holds only what is specific to that tool. A paragraph copied from the canonical file is a second source of truth that will drift.
- [ ] **No always-on domain copy**: Rules that load for every request do not restate the product or domain brief.
- [ ] **Skills list matches disk**: The list of skills or commands in the context file equals the ones that exist.
- [ ] **Read order consistent**: Docs that explain how the tools load context (which file first, what is ignored) match the files and ignore lists in the repo.

## 4. Figures

- [ ] **Figures follow the text**: A diagram, screenshot, or figure that the change makes false is updated or marked outdated. The text is the source of truth; the figure is a view of it.
```

- [ ] **Step 3: Edit `review/SKILL.md`**

Frontmatter line 3: replace `Use when reviewing backend, frontend, or infrastructure code (` with `Use when reviewing backend, frontend, infrastructure, documentation, or AI-configuration changes (`, and replace `proxy config, deploy scripts)` with `proxy config, deploy scripts, feature docs, agent context files)`.

Frontmatter line 4: replace `[backend|frontend|infra]` with `[backend|frontend|infra|docs]`.

Layer argument line: replace `` - `backend`, `frontend`, or `infra`: review only that layer. `` with `` - `backend`, `frontend`, `infra`, or `docs`: review only that layer. ``

Routing table: after the `infra-caddy.md` row add

```markdown
| [references/docs.md](references/docs.md) | a docs file is in scope |
| [references/docs-mkdocs.md](references/docs-mkdocs.md) | docs in scope and `mkdocs` in stacks |
```

`NO_PROFILE` with `--no-ask` line: replace `Infra manifests found this way are listed as `assumed` under **Not checked**; infra is not reviewed without a profile or a confirmed layout.` with `Infra manifests and docs files found this way are listed as `assumed` under **Not checked**; infra and docs are not reviewed without a profile or a confirmed layout.`

- [ ] **Step 4: Edit the profile template**

In `profile-template.md`, after the `- infra:` line insert `- docs:`; after the `## Infra checks` heading's section (before `## Severity overrides`) insert:

```markdown
## Docs checks

<!-- Project-specific items appended to the generic docs checklist: doc paths that must be updated for a given change, grep audits, update order. -->
```

(Keep a blank line after every heading and before every list.)

- [ ] **Step 5: Edit `init-profile/SKILL.md` step 3**

Replace `each directory holding tests;` with `each directory holding tests; each documentation directory and each agent context file (`AGENTS.md`, `CLAUDE.md`, `.cursor/`);`. Replace `offer the roles `backend`, `frontend`, `infra`, `tests`, `ignore`,` with `offer the roles `backend`, `frontend`, `infra`, `docs`, `tests`, `ignore`,`.

- [ ] **Step 6: Run the checks**

Run: `python3 scripts/check-plugin.py`, then `claude plugin validate ./plugins/qa --strict`
Expected: `OK` and `Validation passed`. (The table links `docs-mkdocs.md`, which Task 2 creates; the check does not follow links to missing files.)

- [ ] **Step 7: Commit**

```bash
git add plugins/qa
git commit -m "feat(qa): add docs layer checklist and routing"
```

Print this command; do not run it.

---

### Task 2: `docs-mkdocs.md`, the `mkdocs` signal, and `drift.py`

**Files:**
- Modify: `scripts/test_drift.py` (fixture and one test, written first)
- Modify: `plugins/qa/scripts/drift.py` (`FILE_SIGNALS`)
- Create: `plugins/qa/skills/review/references/docs-mkdocs.md`
- Modify: `plugins/qa/stack-signals.md` (manifest bullet, signals table)

**Interfaces:**
- Produces: stack key `mkdocs` (layer `docs`), pack file `docs-mkdocs.md` with `Written for: MkDocs 1`.
- Consumes: `FILE_SIGNALS` in `drift.py` (key to glob list).

- [ ] **Step 1: Write the failing test**

In `scripts/test_drift.py`, add the row `| `mkdocs` | docs | a `mkdocs.yml` anywhere in the repo |` to the `SIGNALS` table, add `write(refs / "docs-mkdocs.md", "# M\n\nWritten for: MkDocs 1\n")` to `setUp`, and add:

```python
    def test_mkdocs_file_signal_and_loaded_pack(self) -> None:
        self.profile("python", "- backend: .\n- docs: docs/\n")
        write(self.proj / "pyproject.toml", "[project]\n")
        write(self.proj / "mkdocs-config" / "mkdocs.yml", "site_name: x\n")
        out = self.run_drift()
        self.assertIn("STACK mkdocs (pack available)", out)
        self.profile("python, mkdocs", "- backend: .\n- docs: docs/\n")
        out = self.run_drift("--layers", "docs")
        self.assertEqual(out, ["none", "Packs: mkdocs 1/?"])
```

- [ ] **Step 2: Run it to see it fail**

Run: `python3 -m unittest discover -s scripts -p 'test_*.py' 2>&1 | tail -8`
Expected: FAIL on `test_mkdocs_file_signal_and_loaded_pack` (no `STACK mkdocs` record yet).

- [ ] **Step 3: Implement**

In `drift.py`, change `FILE_SIGNALS` to:

```python
FILE_SIGNALS = {
    "docker": ["Dockerfile*", "docker-compose*.yml", "compose*.yaml"],
    "caddy": ["Caddyfile*"],
    "mkdocs": ["mkdocs.yml"],
}
```

In `stack-signals.md`, extend the file-name manifest bullet with `` `mkdocs.yml` `` and add after the `caddy` row: `` | `mkdocs` | docs | a `mkdocs.yml` anywhere in the repo | ``.

- [ ] **Step 4: Create the pack**

```markdown
# MkDocs stack pack

Written for: MkDocs 1

- [ ] **Nav entry**: A new page appears in `nav` of the MkDocs config, unless the project's config turns omitted files into errors (then the strict build catches it).
- [ ] **Strict build**: `mkdocs build --strict` passes (or the project's wrapper for it); run it when the profile or the environment allows, otherwise say `not run`.
- [ ] **Relative links**: Links between pages use relative paths that resolve from the page's own location; anchors exist.
- [ ] **Assets**: Images and files a page references exist under the docs directory and are not excluded by the config.
- [ ] **Config in step**: A new top-level docs folder, a renamed page, or a moved file updates the config (nav, `exclude_docs`, plugins) in the same change.
```

- [ ] **Step 5: Run the tests and checks**

Run: `python3 -m unittest discover -s scripts -p 'test_*.py' 2>&1 | tail -3`, `python3 scripts/check-plugin.py`, `claude plugin validate ./plugins/qa --strict`
Expected: `OK`, `OK (…checks)`, `Validation passed`.

- [ ] **Step 6: Commit**

```bash
git add plugins/qa/scripts/drift.py plugins/qa/stack-signals.md plugins/qa/skills/review/references/docs-mkdocs.md scripts/test_drift.py
git commit -m "feat(qa): add mkdocs stack pack and signal"
```

Print this command; do not run it.

---

### Task 3: Sync the docs that list layers

**Files:**
- Modify: `README.md` (layer and pack lists, the known-gaps line)
- Modify: `CLAUDE.md` (Open work, cycle 2 line)
- Modify: `plugins/qa/.claude-plugin/plugin.json` (keywords)

- [ ] **Step 1: Edit**

README: `layer checklists (`backend.md`, `frontend.md`, `infra.md`)` becomes `layer checklists (`backend.md`, `frontend.md`, `infra.md`, `docs.md`)`; `Layers: `backend`, `frontend`, `infra`.` becomes `Layers: `backend`, `frontend`, `infra`, `docs`.`; add `mkdocs` to the pack list; in the known-gaps line, change `Docs review, `/qa:perf`,` to `` `/qa:perf`, `` and add the sentence `The `docs` layer (`mkdocs` pack) is checked on one real project with planted bugs, two runs per case.`

`CLAUDE.md` Open work: change `2 `docs` layer; 3 `/qa:perf` as its own skill: no spec yet.` into two lines: `2 `docs` layer (`mkdocs` pack): implemented and accepted (results in `docs/specs/2026-10-07-docs-layer-design.md`); not committed until the owner commits it.` and `3 `/qa:perf` as its own skill: no spec yet.`

`plugin.json` keywords: append `"docs"`, `"mkdocs"`.

- [ ] **Step 2: Check**

Run: `python3 scripts/check-plugin.py`, `claude plugin validate ./plugins/qa --strict`, `claude plugin validate . --strict`
Expected: all pass.

- [ ] **Step 3: Commit**

```bash
git add README.md CLAUDE.md plugins/qa/.claude-plugin/plugin.json
git commit -m "docs: list docs layer and mkdocs pack"
```

Print this command; do not run it. (Mark the Open work line as accepted only after Task 4 passes; if Task 4 fails, change it back to `implemented; acceptance tests pending.`)

---

### Task 4: Acceptance tests on a clone of Project A

**Files:**
- Modify: `docs/specs/2026-10-07-docs-layer-design.md` (add `## Results`)
- No other tracked file changes; all planting happens in `$SCRATCH`.

- [ ] **Step 1: Clone and prepare**

```bash
git clone --no-hardlinks -q <project-a> $SCRATCH/docs-clone
cd $SCRATCH/docs-clone
git status --short
```

Expected: no output. Extend the clone's `.claude/project-profile.md` (then `git update-index --assume-unchanged .claude/project-profile.md`): add `mkdocs` to `stacks`; add a `- docs:` layout line listing the documentation directory, the agent context files, and the editor-rules directory; move the old skill's grep lines (orphan links to deleted specs, deprecated mirror files, `@see` existence, the adapter-size guard) into a new `## Docs checks` section; add the project's link checker and a strict docs build to `extra` (try the docs image already present locally, read-only mount; write `not run (<why>)` if it cannot run). Disable the installed plugin: `claude plugin disable qa@dqcuong93`; re-enable it in Step 8.

- [ ] **Step 2: Ground truth**

Run the link checker and the strict docs build on the clean clone and record both outputs in `$SCRATCH/docs-ground-truth.txt`. After Step 3, run them again on the planted tree and record what they report (some planted bugs may be caught by them; note which).

- [ ] **Step 3: Plant bugs as uncommitted edits**

By hand (Edit tool), list each in `$SCRATCH/docs-planted.txt`:

1. In a feature doc, change a route to one the code does not serve.
2. Create a new document with no index row and no nav entry.
3. Delete a document that another document links to (leave the link).
4. Paste a paragraph of domain content from the canonical context file into an adapter file that should only import it.
5. Rename a route in code (a URL pattern) and leave the old route in a doc the diff does not touch.
6. (Scenario C) In the same tree, also change a backend file (remove a permission class from a small view) so the diff spans docs and backend.

- [ ] **Step 4: Run scenario A (bugs 1–5) twice per skill**

```bash
cd $SCRATCH/docs-clone
for n in 1 2; do claude -p "/qa:review --no-ask" --model sonnet --plugin-dir <agent-skills>/plugins/qa --allowedTools "Read,Glob,Grep,Bash(git *),Bash(docker run *)" --output-format json < /dev/null > $SCRATCH/docs-A-new-$n.json 2>/dev/null &
claude -p "Use the qa-qc-docs-ai skill to review the uncommitted changes (git diff)." --model sonnet --allowedTools "Skill,Read,Glob,Grep,Bash(git *),Bash(docker run *)" --output-format json < /dev/null > $SCRATCH/docs-A-old-$n.json 2>/dev/null & done; wait
```

Use a small viewer that prints, per run, the turns, the cost, the reference files read, and the first part of the result. Judge each run against the planted list by hand. Pin Review Focus 2 (both files opened) and 6 (the old route found by grep) here.

- [ ] **Step 5: Scenario B (docs-only diff) and double-report check**

Revert bug 6 and any backend edit so the diff is docs only, run the new skill twice, and print the references read. Expected: only `docs.md` and `docs-mkdocs.md` among `docs`/`backend`/`frontend`/`infra` references. Read the findings for the same problem reported twice (step 9 and the layer).

- [ ] **Step 6: Scenario C (cross-layer) and D (doc inside a backend path)**

Scenario C: restore bug 6; run the new skill twice; expect backend and docs findings in one report with `Packs:` listing `python`, `django`, `mkdocs`.

Scenario D: copy a documentation file into a backend directory and edit it to contain a stale route. Run twice with the profile unchanged (expect it reviewed under backend, no docs rules), then twice after adding that path to the profile's `docs:` line (expect docs rules, `Packs:` includes `mkdocs`).

- [ ] **Step 7: Judge and record**

For each run record the planted bugs found (level), false findings (read each against the files), the `Packs:` line, the commands run, and Review Focus 1–6. Append `## Results` to the spec with the table, model, tools, and run counts. Set the spec status to `accepted` only if every Acceptance bullet passes; otherwise fix the reference file that caused the miss, re-run only the affected scenario twice, and record both attempts.

- [ ] **Step 8: Restore and commit**

```bash
claude plugin enable qa@dqcuong93
git add docs/specs/2026-10-07-docs-layer-design.md
git commit -m "docs(qa): record docs layer acceptance results"
```

Print the commit command; do not run it. Tell the owner the plugin is re-enabled and nothing was tagged.
