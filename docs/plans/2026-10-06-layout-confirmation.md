# Layout Confirmation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `/qa:init-profile` ask the owner to confirm the role of every path and file (first run and updates), store "not a layer" answers in an `ignore:` line, and make `/qa:review` report changed files that have no role.

**Architecture:** Edits to three existing files (`init-profile/SKILL.md`, `profile-template.md`, `review/SKILL.md`) and one check added to `scripts/check-plugin.py`. No new files in the plugin. Behaviour is verified by multi-turn headless `claude -p` runs on a fake project.

**Tech Stack:** Markdown skills, Python 3 stdlib check script, `claude -p` with `--resume`.

**Spec:** `docs/specs/2026-10-06-layout-confirmation-design.md`

## Global Constraints

- Public repo: no project names, domains, hosts, machine paths, credentials, or business rules in any tracked file. The source project is "Project A".
- Never run `git commit`, `git push`, or `git tag`. Each "Commit" step prints the command for the owner to run.
- Plugin version stays `0.2.0` (not tagged yet).
- The plugin assumes no directory names and no file placement; the profile's `Layout` is the only router.
- `!` injection lines contain no `|`, `||`, `&&`, `;`, or `( … )`.
- A profile without an `ignore:` line stays valid and behaves as before.
- Shell is zsh: use `printf`, not `echo =====`; quote globs; do not chain `; echo $?`.
- In commands, `<agent-skills>` is this repo's checkout and `$SCRATCH` a scratch directory outside it; never write a real machine path into a tracked file.
- Tasks 2 and 3 of the `infra` plan edit the same step-2 sentence as Task 2 below; this plan runs first, and the `infra` plan's replacement strings then start from the text this plan leaves.

## Review Focus

1. **Skipped gate:** the model continues to invariants or writes the profile in the same turn as the layout question. Pinned in Task 4 Step 3 (turn 1 must leave no profile file) and Step 4.
2. **Glob tie-break:** `be/Dockerfile*` must beat `be/` for `be/Dockerfile`. Pinned in Task 4 Step 6.
3. **Update re-asks settled paths:** a path already in `Layout` or `ignore` must not be asked about again. Pinned in Task 4 Step 5.
4. **Ignored file reviewed anyway:** a changed file under `ignore` must be listed under **Not checked** and not reviewed. Pinned in Task 4 Step 7.
5. **Profile without `ignore:`:** review output must not change. Pinned in Task 4 Step 8.

---

### Task 1: `ignore:` in the template, with a check

**Files:**
- Modify: `scripts/check-plugin.py` (before the `if BANNED.is_file():` block)
- Modify: `plugins/qa/skills/init-profile/profile-template.md`
- Test: `scripts/check-plugin.py`

**Interfaces:**
- Produces: the profile line `- ignore:` under `## Layout`, which Tasks 2 and 3 refer to.

- [ ] **Step 1: Add the failing check**

In `scripts/check-plugin.py`, immediately before `if BANNED.is_file():` insert:

```python
    template = PLUGIN / "skills" / "init-profile" / "profile-template.md"
    checks += 1
    layout = re.search(r"^## Layout\n(.*?)^## ", template.read_text(), re.S | re.M)
    if not layout or "- ignore:" not in layout.group(1):
        fails.append("template: profile-template.md has no '- ignore:' line under Layout")
```

- [ ] **Step 2: Run the check to see it fail**

Run: `python3 scripts/check-plugin.py`
Expected: `FAIL template: profile-template.md has no '- ignore:' line under Layout`

- [ ] **Step 3: Edit the template**

In `profile-template.md`, replace the Layout comment and list with:

```markdown
<!-- Where each layer lives, as paths or globs from the repo root, comma-separated, each
     optionally followed by a note in parentheses. Reviews assign a changed file to the layer
     whose entry matches it; with several matches the entry with the longest literal prefix
     (the text before the first `*`) wins (`frontend/` beats `.`, `be/Dockerfile*` beats `be/`).
     `ignore` lists paths the owner said belong to no layer; they are never reviewed. -->
- backend:
- frontend:
- infra:
- tests:
- ignore:
```

- [ ] **Step 4: Run the check to see it pass**

Run: `python3 scripts/check-plugin.py`
Expected: `OK` with one more check than before (39 if run before the infra plan).

- [ ] **Step 5: Commit**

```bash
git add scripts/check-plugin.py plugins/qa/skills/init-profile/profile-template.md
git commit -m "feat(qa): add ignore line to the profile template"
```

Print this command; do not run it.

---

### Task 2: `/qa:review` tie-break, `ignore`, and `LAYOUT` records

**Files:**
- Modify: `plugins/qa/skills/review/SKILL.md` (step 2 line 46, step 3 drift list, Output parts 3 and 5)
- Test: `scripts/check-plugin.py`, `claude plugin validate`

**Interfaces:**
- Consumes: the `ignore:` line from Task 1.
- Produces: drift record `LAYOUT <directory> (unmapped): <n> changed files`; Not-checked label `ignored by profile`.

- [ ] **Step 1: Edit step 2**

Replace `When several match, the longest path wins (`frontend/` beats `.`).` with:

`When several match, the entry with the longest literal prefix (the text before the first `*`) wins (`frontend/` beats `.`, `be/Dockerfile*` beats `be/`). A file under an `ignore` entry is not reviewed; list it under **Not checked** as `ignored by profile`.`

- [ ] **Step 2: Edit step 3**

After the `STACK ? (no manifest found in <paths>)` bullet, insert:

```markdown
   - `LAYOUT <directory> (unmapped): <n> changed files`: with a profile only. Changed files that match no `Layout` entry and no `ignore` entry. One record per top-level directory of those files (a root-level file uses `.`). Build it from the changed files only; never scan the repo for it.
```

- [ ] **Step 3: Edit the Output**

In part 3, replace `` `may be stale` → tell the plugin owner), then`` with `` `may be stale` → tell the plugin owner; `LAYOUT … (unmapped)` → run `/qa:init-profile` to give the directory a role or ignore it), then``.

In part 5, replace `files outside every layer, `assumed` layers,` with `files outside every layer, files under `ignore` (`ignored by profile`), `assumed` layers,`.

- [ ] **Step 4: Run the checks**

Run: `python3 scripts/check-plugin.py` then `claude plugin validate ./plugins/qa --strict`
Expected: `OK` and `validation passed`.

- [ ] **Step 5: Commit**

```bash
git add plugins/qa/skills/review/SKILL.md
git commit -m "feat(qa): review reports unmapped and ignored files"
```

Print this command; do not run it.

---

### Task 3: `init-profile` layout confirmation

**Files:**
- Modify: `plugins/qa/skills/init-profile/SKILL.md` (steps 3–7 renumbered, step 2 reference)
- Test: `scripts/check-plugin.py`, `claude plugin validate`

**Interfaces:**
- Consumes: the `ignore:` line from Task 1.
- Produces: the layout question and the rule that `ignore` answers are written under `Layout`.

- [ ] **Step 1: Insert the new step 3**

After step 2 (`Map stacks`), insert:

```markdown
3. **Confirm layout.** Build the candidates: each directory holding a manifest from `stack-signals.md` § Manifests at the root and one directory down; each infra file found by name anywhere in the repo (`Dockerfile*`, `docker-compose*.yml`, `compose*.yaml`, `Caddyfile*`), shown as one line per directory and as its own line only when its directory is assigned another role; each directory holding tests; on an update, every top-level directory or manifest not covered by the profile. A candidate is already settled when it appears as an entry in a `Layout` line (a path or glob, comma-separated, optionally followed by a note in parentheses, including `ignore`) or lies under one. Ask only about candidates that are not settled, and about any whose detected role differs from its assigned one (show both roles; never change it silently). If there are none, say `layout unchanged` and go on. Otherwise ask in the conversation's language, one numbered line per candidate with the path, the proposed role, and the evidence, and offer the roles `backend`, `frontend`, `infra`, `tests`, `ignore`, or a name the user gives. **End the turn with the question; draft nothing and write nothing this turn.** If the reply leaves a line unassigned, ask again for that line only. Use the answers for the rest of the run and record `ignore` answers on the `ignore:` line under `Layout`.

   Example:

   > I found these paths. Tell me which are wrong; reply "ok" if all are right.
   >
   > 1. `be/` — backend (pyproject.toml: Django)
   > 2. `be/Dockerfile` — infra? (it sits inside `be/`, so it could be backend)
   > 3. `scripts/` — unclear: backend, infra, or ignore?
```

- [ ] **Step 2: Renumber the remaining steps**

`Harvest invariants and rules` becomes 4, `Draft` 5, `Present and end the turn` 6, `Write after confirmation` 7, `Verify commands` 8. In step 2, change `in the step-5 summary` to `in the step-6 summary`. In the renumbered step 6, change `the file is written in step 6` to `the file is written in step 7`. In step 4 (Harvest), add at the start: `Use the layout confirmed in step 3.`

- [ ] **Step 3: Run the checks**

Run: `python3 scripts/check-plugin.py` then `claude plugin validate ./plugins/qa --strict`
Expected: both pass. Then run `grep -n "step-5\|step 5\|step 6" plugins/qa/skills/init-profile/SKILL.md`; every hit refers to the new numbering.

- [ ] **Step 4: Commit**

```bash
git add plugins/qa/skills/init-profile/SKILL.md
git commit -m "feat(qa): init-profile confirms the layout with the user"
```

Print this command; do not run it.

---

### Task 4: Acceptance tests

**Files:**
- Modify: `docs/specs/2026-10-06-layout-confirmation-design.md` (add `## Results`)
- No other tracked file changes; all test material lives in `$SCRATCH`.

**Interfaces:**
- Consumes: Tasks 1–3.

- [ ] **Step 1: Check that `--resume` keeps a pending question**

```bash
mkdir -p $SCRATCH/resume-probe && cd $SCRATCH/resume-probe && git init -q
claude -p "Ask me which colour I like, then stop and wait for my answer." --model sonnet --output-format json < /dev/null > $SCRATCH/probe-1.json
python3 -c "import json;d=json.load(open('$SCRATCH/probe-1.json'));r=[e for e in d if e.get('type')=='result'][-1];print(r['session_id'])"
claude -p "blue" --resume <session_id> --model sonnet --output-format json < /dev/null > $SCRATCH/probe-2.json
python3 -c "import json;d=json.load(open('$SCRATCH/probe-2.json'));print([e for e in d if e.get('type')=='result'][-1]['result'])"
```

Expected: the second answer refers to "blue", so the session carries over. If not, stop and change the test method in the spec before continuing.

- [ ] **Step 2: Build the fake project**

```bash
mkdir -p $SCRATCH/fake && cd $SCRATCH/fake && git init -q
mkdir -p be/tests fe infras scripts
printf '[project]\nname = "demo"\ndependencies = ["django>=5"]\n' > pyproject.toml
printf 'def f():\n    return 1\n' > be/app.py
printf 'FROM python:3.12\nCOPY . .\n' > be/Dockerfile
printf 'def test_f():\n    assert True\n' > be/tests/test_app.py
printf '{"name":"fe","dependencies":{"vue":"^3.5.0"}}\n' > fe/package.json
printf 'services:\n  web:\n    image: caddy:2\n' > infras/docker-compose.yml
printf ':80 {\n  respond "ok"\n}\n' > infras/Caddyfile
printf '#!/bin/sh\nexit 0\n' > scripts/run.sh
git add -A && git -c user.name=t -c user.email=t@t commit -q -m init
```

(The git identity is passed per command; nothing is configured globally.)

Disable the installed copy so only the working copy loads: `claude plugin disable qa@dqcuong93` (re-enable it in Step 10). Review runs below use these flags, called `REVIEW_FLAGS`: `--model sonnet --plugin-dir <agent-skills>/plugins/qa --allowedTools "Read,Glob,Grep,Bash(git *)" --output-format json < /dev/null`.

- [ ] **Step 3: First run, turn 1 (twice, in two fresh copies)**

```bash
cd $SCRATCH/fake
claude -p "/qa:init-profile" --model sonnet --plugin-dir <agent-skills>/plugins/qa --allowedTools "Read,Glob,Write,Bash(ls *)" --output-format json < /dev/null > $SCRATCH/init-1-t1.json
ls .claude/project-profile.md
```

Expected: `ls` reports `No such file`. Read the result: the question lists `be/Dockerfile` and `scripts/` as separate lines and has no invariants or draft yet. For the second attempt, `rm -rf .claude` and repeat into `init-2-t1.json`.

- [ ] **Step 4: First run, turns 2 and 3**

Answer with `--resume <session_id>`: `be/Dockerfile infra, scripts ignore, rest ok`. Expected: turn 2 ends with the invariants question and `.claude/project-profile.md` still does not exist. Then reply `ok, no invariants`; expected: the profile exists with `be/Dockerfile` under `infra:` and `scripts/` under `ignore:`. Read the file.

- [ ] **Step 5: Update runs**

Without changes, run `/qa:init-profile` again from a new session: expected `layout unchanged`, no layout question. Then `mkdir tools && printf '{"name":"tools"}\n' > tools/package.json`, run again: expected a question listing only `tools/`.

- [ ] **Step 6: Glob tie-break**

Read the written profile. Run `claude -p "/qa:review --no-ask" $REVIEW_FLAGS` (flags as defined in Step 2) after editing `be/Dockerfile` (append a comment line). Expected: the report treats `be/Dockerfile` under infra, not backend. (If the profile lists `be/` as backend and `be/Dockerfile` under `infra`, the longer literal prefix must win.)

- [ ] **Step 7: Review reports `LAYOUT` and `ignored by profile`**

Make uncommitted changes to `scripts/run.sh` and to a new file `newdir/x.py`. Run `/qa:review --no-ask` with `REVIEW_FLAGS`. Expected: a `LAYOUT newdir/ (unmapped): 1 changed files` record with the `/qa:init-profile` action, `scripts/run.sh` under **Not checked** as `ignored by profile`, and neither file reviewed.

- [ ] **Step 8: Regression without `ignore:`**

Copy the profile, delete the `- ignore:` line and the `scripts/` entry, and run `/qa:review --no-ask` with `REVIEW_FLAGS` after appending a comment line to `be/app.py` and a line to `scripts/run.sh`. Expected: no error; `scripts/run.sh` appears in a `LAYOUT scripts/ (unmapped)` record instead of `ignored by profile`.

- [ ] **Step 9: Judge and record**

For each run record pass or fail, read each transcript for the skipped-gate risk, and write the table, model, tools, and run counts under `## Results` in the spec. Set the spec status to `accepted` only if every Acceptance bullet passes. If one fails, fix the file that caused it, re-run only that step twice, and record both attempts.

- [ ] **Step 10: Commit**

```bash
git add docs/specs/2026-10-06-layout-confirmation-design.md
git commit -m "docs(qa): record layout confirmation acceptance results"
```

Print this command; do not run it. Re-enable `qa@dqcuong93` if it was disabled; tell the owner nothing was tagged.
