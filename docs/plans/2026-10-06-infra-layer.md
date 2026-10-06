# `infra` Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an `infra` layer to `/qa:review` (generic `infra.md` plus `docker` and `caddy` packs) and prove it against Project A's in-repo `qa-qc-infra` skill with planted bugs.

**Architecture:** Three flat reference files under `skills/review/references/`, linked from `SKILL.md`; one new row in `stack-signals.md`; project-specific rules stay in the profile. No new skill. Behaviour is verified by headless `claude -p` runs on a clone of Project A.

**Tech Stack:** Markdown skills, Python 3 stdlib check script (unchanged), `claude -p` for tests.

**Spec:** `docs/specs/2026-10-06-infra-layer-design.md`

## Global Constraints

- Public repo: no project names, client names, domains, hosts, vendor account ids, machine paths, credentials, or business rules in any tracked file. Source project is "Project A".
- Never run `git commit`, `git push`, or `git tag`. Each "Commit" step prints the command for the owner to run.
- Plugin version stays `0.2.0` (v0.2.0 is not tagged yet; the owner decides when to tag).
- References are one level deep: `SKILL.md` links every reference file; reference files link to nothing.
- Every `<layer>-<stack>.md` pack has `Written for: <stack> <major>` on line 3 (line 1 title, line 2 blank).
- `!` injection lines contain no `|`, `||`, `&&`, `;`, or `( … )`.
- Nothing is changed in Project A except uncommitted edits inside a scratch clone; the real checkout is never modified.
- Shell is zsh: use `printf`, not `echo =====`; quote globs; do not chain `; echo $?`.
- In commands, `<agent-skills>` is this repo's checkout, `<project-a>` the real Project A checkout, and `$SCRATCH` a scratch directory outside both; never write a real machine path into a tracked file.
- Do not touch a shared dev database or start the project's stack.

## Review Focus

1. **Layer routing with overlapping paths** (Project A: backend `be/`, infra `infras/`; a project may list backend as `.`): an infra file must route to infra by longest path, not to backend. Pinned in Task 5 Step 4 (scenario B).
2. **Infra-only diff loads no backend or frontend reference.** Pinned in Task 5 Step 5.
3. **Pack key missing from `stacks`:** a profile that lists no `docker` or `caddy` while infra files exist gets `STACK docker (pack available)` and `STACK caddy (pack available)` drift records. Pinned in Task 2 Step 4 and Task 3 Step 4.
4. **Validator not runnable:** if `caddy validate` or `docker compose config -q` cannot run (image missing, tool not allowed), the report says `not run (<why>)` and the finding is marked as text-only, never `ran ✓`. With the local image it should run; if it does, the planted Caddy bugs also get a `ran` result to compare against. Pinned in Task 5 Step 3.
5. **Infra file inside another layer's directory, declared by glob:** a profile that lists `infra: infras/, be/Dockerfile*` routes `be/Dockerfile` to infra (longest match beats `be/`); a profile that does not list it leaves the file in backend. Pinned in Task 5 Step 4 (scenario C).

## Decision D7 (dropped): no file-name routing

An earlier draft routed `Dockerfile*`, `docker-compose*.yml`, `Caddyfile` to `infra` whatever their directory. That forces one repo layout on every project, so it is dropped. Routing stays exactly as it is: the profile's `Layout` decides, and a layout path may be a glob (`be/Dockerfile*`). A project that keeps a Dockerfile inside its backend directory lists that file under `infra`; the longest matching path wins. The plugin assumes no directory names and no file placement. Stack detection (`stack-signals.md`) finds infra files by name anywhere in the repo, only to suggest `stacks` keys.

---

### Task 1: `infra.md` and `SKILL.md` wiring

**Files:**
- Create: `plugins/qa/skills/review/references/infra.md`
- Modify: `plugins/qa/skills/review/SKILL.md` (frontmatter lines 3–4, line 18, routing table, step 2 lines 46 and 60, step 6)
- Test: `scripts/check-plugin.py` (existing)

**Interfaces:**
- Produces: layer name `infra`; file `references/infra.md`; table rows that Task 2 and Task 3 extend with `infra-docker.md` and `infra-caddy.md`.

- [ ] **Step 1: Run the check to confirm the baseline**

Run: `python3 scripts/check-plugin.py`
Expected: `OK (38 checks)`

- [ ] **Step 2: Create `references/infra.md`**

```markdown
# Infra checklist

Tool-agnostic. Report only items the change affects. Tool-specific rules are in the `infra-<stack>.md` packs; rules for one project are in the profile's `Infra checks`.

## 1. Secrets and env

- [ ] **No secret literals**: No credential, token, key, or password value in any tracked file (compose `environment:`, scripts, Dockerfile `ENV`/`ARG`, CI files). Values come from untracked env files or a secret store.
- [ ] **Env files untracked**: Real `.env*` files are gitignored; only `*.example` files are tracked, with placeholder values.
- [ ] **Env example in sync**: Every variable the config reads exists in the example env file; a variable the change removes is removed there too.

## 2. Change safety

- [ ] **Validated before reload**: The config is checked with the tool's own validator before a reload or deploy. If the profile names the command, run it.
- [ ] **Reload, not restart**: Where the tool supports a graceful reload, the procedure uses it instead of a restart that drops connections.
- [ ] **Revertible**: The change is undone by reverting one commit. No step depends on an edit made by hand on the host.
- [ ] **Scripts fail loudly**: Shell scripts stop on error (`set -e` or `set -euo pipefail`), quote variable expansions, and never run `rm -rf` on a path built from an unchecked variable. Running the script twice is safe.

## 3. Exposure

- [ ] **Published ports**: Only the public entrypoint publishes a port. Databases and caches stay on the internal network or bind to `127.0.0.1`.
- [ ] **Privilege**: No `privileged: true`, no container-runtime socket mounted into an app container without a restricting proxy, no root user without a reason in a comment.
- [ ] **Logs**: Config does not log request bodies, tokens, or other secrets; log rotation or a size limit exists for long-running services.
```

- [ ] **Step 3: Edit `SKILL.md`**

Frontmatter line 3: replace `Use when reviewing backend or frontend code (services, APIs, ORM/DB, jobs, components, pages, styling)` with `Use when reviewing backend, frontend, or infrastructure code (services, APIs, ORM/DB, jobs, components, pages, styling, Dockerfiles, compose files, proxy config, deploy scripts)`.

Frontmatter line 4: replace `[backend|frontend]` with `[backend|frontend|infra]`.

Line 18: replace
`` - `backend` or `frontend`: review only that layer. ``
with
`` - `backend`, `frontend`, or `infra`: review only that layer. ``

Routing table: add after the `frontend-tailwind.md` row

```markdown
| [references/infra.md](references/infra.md) | an infra file is in scope |
| [references/infra-docker.md](references/infra-docker.md) | infra in scope and `docker` in stacks |
| [references/infra-caddy.md](references/infra-caddy.md) | infra in scope and `caddy` in stacks |
```

Step 2, line 46: no change. The sentence about layers with no checklist already says that a layer with profile checks is reviewed by them; `infra` now has a reference file, so nothing refers to it by name. Add no rule that assigns a file to a layer by its name; the profile's `Layout` (paths and globs) is the only router.

Step 2, line 60 (`NO_PROFILE` with `--no-ask`): append the sentence `Infra manifests found this way are listed as `assumed` under **Not checked**; infra is not reviewed without a profile or a confirmed layout.`

Line 62 (`A `backend` or `frontend` argument drops the other layer.`): replace with `A layer argument drops the other layers.`

- [ ] **Step 4: Run the check**

Run: `python3 scripts/check-plugin.py`
Expected: `OK` with a check count higher than 38; no `FAIL` lines.

- [ ] **Step 5: Commit**

```bash
git add plugins/qa/skills/review/references/infra.md plugins/qa/skills/review/SKILL.md
git commit -m "feat(qa): add infra layer checklist and routing"
```

Print this command; do not run it.

---

### Task 2: `infra-docker.md`

**Files:**
- Create: `plugins/qa/skills/review/references/infra-docker.md`
- Test: `scripts/check-plugin.py`

**Interfaces:**
- Consumes: routing row for `infra-docker.md` from Task 1; the `docker` row already in `stack-signals.md`.

- [ ] **Step 1: Run the check to see the pack is not yet linked**

Run: `python3 scripts/check-plugin.py`
Expected: `OK` (the table row exists but the file does not; a link to a missing file is not checked, so also run `ls plugins/qa/skills/review/references/infra-docker.md` and expect `No such file`).

- [ ] **Step 2: Create the pack**

```markdown
# Docker and Compose stack pack

Written for: Docker Compose 2

## Compose

- [ ] **Health checks**: A service that others wait on has a `healthcheck`, and dependents use `depends_on` with `condition: service_healthy`. A service that is the only instance behind a proxy has none, because a flaky check would mark the only upstream down.
- [ ] **Restart policy**: Long-running production services set `restart: unless-stopped` or `always`; one-shot jobs set `"no"` or `on-failure`.
- [ ] **Resource limits**: Production services that can grow (workers, renderers, databases) set memory and CPU limits so one container cannot starve the others.
- [ ] **Volumes**: Persistent data lives on a named volume or bind mount, not the container layer. Services that share files mount the same source at the paths their configs expect. A mount the service never writes to is `:ro`.
- [ ] **Networks**: Services reach each other by service name on the compose network, not through published host ports.
- [ ] **Image tags**: Images are pinned to at least a major version; `latest` is not used for anything that gets deployed.
- [ ] **Validation**: `docker compose config -q` passes for every compose file the change touches (run it when the profile allows).

## Dockerfile

- [ ] **Layer cache**: Dependency manifests are copied and installed before the source is copied, so a source edit does not reinstall dependencies.
- [ ] **Multi-stage**: Build tools and dev dependencies stay out of the final image.
- [ ] **Non-root**: The final stage sets a non-root `USER`.
- [ ] **No secrets in layers**: No secret in `ENV`, `ARG`, or a copied file; `.dockerignore` excludes env files, VCS data, and local dependency directories.
- [ ] **Reproducible base**: The base image tag is pinned to at least a major version.
```

- [ ] **Step 3: Run the check**

Run: `python3 scripts/check-plugin.py`
Expected: `OK`, no `FAIL` lines (the pack is linked from `SKILL.md`, has `Written for:` on line 3, and `docker` has a signals row).

- [ ] **Step 4: Check the drift record by reading**

Open `plugins/qa/stack-signals.md` and confirm the `docker` row says `infra`. A profile without `docker` in `stacks` and a `Dockerfile` at the root gives `STACK docker (pack available)` under step 3 of `SKILL.md`; confirm the pack file name `infra-docker.md` matches the glob `references/*-docker.md` that step uses.

- [ ] **Step 5: Commit**

```bash
git add plugins/qa/skills/review/references/infra-docker.md
git commit -m "feat(qa): add docker and compose stack pack"
```

Print this command; do not run it.

---

### Task 3: `infra-caddy.md` and the `caddy` signal

**Files:**
- Create: `plugins/qa/skills/review/references/infra-caddy.md`
- Modify: `plugins/qa/stack-signals.md` (manifest list, signals table)
- Test: `scripts/check-plugin.py`

**Interfaces:**
- Consumes: routing row for `infra-caddy.md` from Task 1.
- Produces: stack key `caddy` (layer `infra`).

- [ ] **Step 1: Run the check**

Run: `python3 scripts/check-plugin.py`
Expected: `OK`.

- [ ] **Step 2: Edit `stack-signals.md`**

In `## Manifests`, add after the `package.json` line:

```markdown
- `Dockerfile*`, `docker-compose*.yml`, `compose*.yaml`, `Caddyfile*`: found by file name anywhere in the repo (Glob `**/<name>`), not only at the root. Nothing is parsed. They only suggest stack keys; where a file belongs is decided by the profile's `Layout`.
```

In the signals table, replace the `docker` row's Signals cell `a `Dockerfile` or `docker-compose*.yml` / `compose*.yaml` at the project root` with `a `Dockerfile*` or `docker-compose*.yml` / `compose*.yaml` anywhere in the repo`, and add after it:

```markdown
| `caddy` | infra | a `Caddyfile*` anywhere in the repo |
```

- [ ] **Step 3: Create the pack**

```markdown
# Caddy stack pack

Written for: Caddy 2

## Routing

- [ ] **Route order**: Within a site block, `handle` blocks are tried in the order written. A narrow path must come before a broad one (`/api/special` before `/api/*`), or the broad block shadows it.
- [ ] **No duplicate handlers**: The same path is not matched by two blocks with conflicting behaviour.
- [ ] **Snippets**: Repeated `reverse_proxy` options are factored into a `(snippet)` and imported, not pasted per route.
- [ ] **Single upstream health checks**: A route with one upstream has no active health check; a flaky check would take the only instance out of rotation.

## Headers

- [ ] **One owner per header**: A top-level `header` directive runs before `reverse_proxy` and sets a value; the proxy then adds the upstream's own value for the same name, so the client sees two. Pick one place to own each header.
- [ ] **Override upstream values**: To force a value regardless of what the upstream sends, use `header_down <Name> "<value>"` inside `reverse_proxy`; it runs after the response arrives and replaces the value.
- [ ] **Verified, not assumed**: When a header changes, check it with `curl -sS -D - -o /dev/null <url>`: each header name appears once. Two lines of the same name is this bug.

## Caching

- [ ] **Hashed assets**: Content-hashed file names get a long `max-age` plus `immutable`.
- [ ] **Unhashed static files**: A moderate `max-age`, optionally with `stale-while-revalidate`; never `immutable`.
- [ ] **HTML and CDNs**: Many CDNs do not cache HTML unless a rule says so, whatever `Cache-Control` the origin sends. A change that expects HTML to be edge-cached needs that rule, not only a header.
- [ ] **Purge after deploy**: If anything caches the output (browser, CDN, proxy), the deploy procedure names the purge step.

## TLS and clients

- [ ] **Site addresses**: Production site blocks name explicit hostnames. `auto_https off` and `tls internal` need a comment saying why.
- [ ] **Ports**: 80 and 443 (TCP, and UDP for HTTP/3) are reachable for certificate issuance and renewal.
- [ ] **Client IP behind a proxy or CDN**: When another proxy sits in front, `trusted_proxies` is set deliberately; otherwise the upstream sees the edge address and per-client throttling or attribution is wrong.

## Validation

- [ ] **Validated**: `caddy validate --config <Caddyfile>` passes (or the containerised equivalent); run it when the profile or the environment allows, otherwise say `not run`.
- [ ] **Formatted**: `caddy fmt --diff` shows no change for the touched file.
```

- [ ] **Step 4: Run the check**

Run: `python3 scripts/check-plugin.py`
Expected: `OK`, no `FAIL` (the new pack needs the `caddy` row in `stack-signals.md`; Step 2 added it). Also confirm by reading that a profile without `caddy` in `stacks` and a `Caddyfile` in an infra Layout path yields `STACK caddy (pack available)` (Review Focus 3).

- [ ] **Step 5: Validate the plugin**

Run: `claude plugin validate ./plugins/qa --strict`
Expected: `validation passed`.

- [ ] **Step 6: Commit**

```bash
git add plugins/qa/skills/review/references/infra-caddy.md plugins/qa/stack-signals.md
git commit -m "feat(qa): add caddy stack pack and signal"
```

Print this command; do not run it.

---

### Task 4: Sync the docs that list layers

**Files:**
- Modify: `README.md` (the `Layers:` line and the tier-1 bullet)
- Modify: `CLAUDE.md` (Open work item 3)
- Modify: `plugins/qa/.claude-plugin/plugin.json` (keywords)
- Modify: `docs/specs/2026-10-06-infra-layer-design.md` (status line, after Task 5)

- [ ] **Step 1: Find every place that lists layers or packs**

Run: `grep -rn "backend\.md\|Layers:\|Stack packs" README.md CLAUDE.md plugins docs/specs --include=*.md --include=*.json`
Expected: `README.md` lines naming `Layers: backend, frontend` and the pack list; list them all before editing.

- [ ] **Step 2: Edit**

README `Layers:` line becomes `Layers: `backend`, `frontend`, `infra`. Stack packs: `python`, `django`, `sqlalchemy`, `fastapi`, `vue`, `inertia`, `astro`, `tailwind`, `docker`, `caddy`.`

README tier-1 bullet: `layer checklists (`backend.md`, `frontend.md`)` becomes `layer checklists (`backend.md`, `frontend.md`, `infra.md`)`.

`CLAUDE.md` Open work item 3: replace `infra (`docker`, `caddy`, `k8s`)` with `infra `k8s` pack` and keep the rest of the line.

`plugin.json` keywords: append `"infra"`, `"docker"`, `"caddy"`.

- [ ] **Step 3: Check**

Run: `python3 scripts/check-plugin.py` and `claude plugin validate ./plugins/qa --strict`
Expected: both pass.

- [ ] **Step 4: Commit**

```bash
git add README.md CLAUDE.md plugins/qa/.claude-plugin/plugin.json
git commit -m "docs: list infra layer and docker/caddy packs"
```

Print this command; do not run it.

---

### Task 5: Acceptance tests on a clone of Project A

**Files:**
- Modify: `docs/specs/2026-10-06-infra-layer-design.md` (add `## Results`)
- No other tracked file changes; all planting happens in `$SCRATCH`.

**Interfaces:**
- Consumes: the three reference files and `SKILL.md` wiring from Tasks 1–3.

- [ ] **Step 1: Clone and prepare**

```bash
git clone --no-hardlinks -q <project-a> $SCRATCH/infra-clone
cd $SCRATCH/infra-clone
git status --short
```

Expected: no output. Copy in the profile if it is not committed (`cp <project-a>/.claude/project-profile.md .claude/`). Disable the installed copy of the plugin for the test: `claude plugin disable qa@dqcuong93`; re-enable at the end of Task 5.

- [ ] **Step 2: Ground truth**

Record what the project's own tools say on the clean clone. Caddy runs from the local `caddy:alpine` image (already present, no pull; the binary is not installed on the host), mounted read-only: `docker run --rm -v "$PWD/infras/caddy:/etc/caddy:ro" caddy:alpine caddy validate --config /etc/caddy/Caddyfile` (expect `Valid configuration` on the clean clone). Also `docker compose -f infras/docker-compose.yml config -q` (write `not run (<why>)` if the compose plugin is absent). Save the outputs in `$SCRATCH/ground-truth.txt`. Never exec into or restart the running dev containers; use only `docker run --rm` with a read-only mount. In the clone's `.claude/project-profile.md`, add both commands to `extra` so the review runs them.

- [ ] **Step 3: Plant bugs as uncommitted edits**

In the clone, edit by hand (Edit tool) and keep a list in `$SCRATCH/planted.txt`:

1. Caddyfile: move one narrow path `handle` below the broad `/api/*` handle.
2. Caddyfile: add a top-level `header` setting `Cache-Control` for a path whose upstream also sends `Cache-Control`.
3. `infras/docker-compose.yml`: put a password literal (`PLANTED_SECRET_123`) in a service's `environment:`.
4. `infras/docker-compose.yml`: read a new variable `${PLANTED_NEW_VAR}` that is not added to `infras/.env.example`.
5. `infras/docker-compose.yml`: delete the `restart:` line of one production service.

Run the clean-tree check first: `git diff --stat` shows only these edits.

- [ ] **Step 4: Run the new skill twice per scenario**

Scenario A (bugs 1–5, uncommitted, infra only):

```bash
cd $SCRATCH/infra-clone
for n in 1 2; do claude -p "/qa:review --no-ask" --model sonnet --plugin-dir <agent-skills>/plugins/qa --allowedTools "Read,Glob,Grep,Bash(git *),Bash(docker compose *),Bash(docker run *)" --output-format json < /dev/null > $SCRATCH/infra-new-A-$n.json 2> $SCRATCH/infra-new-A-$n.err & done; wait
```

Scenario B (spec run 6, cross-layer): revert nothing; additionally plant one backend bug (remove an `IsAuthenticated` permission class from a small view). Run the same command into `infra-new-B-$n.json`.

Scenario C (glob routing): copy a `Dockerfile` into a backend directory with a planted `USER root` and a secret in `ENV`. Run twice with the profile unchanged (expect the file reviewed under backend, no Docker rules) and twice with the clone's profile `infra:` line extended by that file's glob (expect infra rules, `Packs:` includes `docker`). Outputs go to `infra-new-C0-$n.json` and `infra-new-C1-$n.json`.

Print each result with:

```bash
python3 -c "import json;d=json.load(open('$SCRATCH/infra-new-A-1.json'));print([e for e in d if e.get('type')=='result'][-1]['result'])"
```

- [ ] **Step 5: Run the old skill twice on scenario A**

```bash
for n in 1 2; do claude -p "Use the qa-qc-infra skill to review the uncommitted changes (git diff)." --model sonnet --allowedTools "Skill,Read,Glob,Grep,Bash(git *),Bash(docker compose *),Bash(docker run *)" --output-format json < /dev/null > $SCRATCH/infra-old-A-$n.json 2> $SCRATCH/infra-old-A-$n.err & done; wait
```

Count tool use per run (Skill names, Read paths) to confirm the old skill loaded, and that scenario A runs of the new skill read `infra.md`, `infra-docker.md`, `infra-caddy.md` and no `backend*`/`frontend*` file (Review Focus 2).

- [ ] **Step 6: Judge by hand against the spec's Acceptance list**

For each run record: planted bugs 1–5 found (yes/no, level), false findings (read each against the code), `Packs:` line, commands run and their `ran ✓/✗`/`not run`, Review Focus 1, 3, 4, 5 (scenario C0 vs C1). Write the table into `$SCRATCH/infra-results.md`.

- [ ] **Step 7: Record the Results**

Append `## Results` to `docs/specs/2026-10-06-infra-layer-design.md` with the table from Step 6, the model, tools, run count, and any acceptance item that failed. If an item failed, fix the reference file that caused it, re-run only the affected scenario twice, and record both attempts. Change the spec status line to `accepted` only when every Acceptance bullet passes.

- [ ] **Step 8: Restore and commit**

```bash
claude plugin enable qa@dqcuong93
git add docs/specs/2026-10-06-infra-layer-design.md
git commit -m "docs(qa): record infra layer acceptance results"
```

Print the commit command; do not run it. Tell the owner the plugin is re-enabled and that nothing was tagged.
