# `infra` layer for `/qa:review` — design (wave 2, cycle 1)

Status: implemented; acceptance passed with the caveats under Results. Date: 2026-10-06.

## Goal

Add an `infra` layer to `/qa:review` so it covers what Project A's in-repo `qa-qc-infra` skill covers (Caddy, docker-compose, deploy scripts, env files), driven by the project profile. When this passes the acceptance tests below, that in-repo skill can be removed. Project A and the model are described in `2026-10-05-unified-review-design.md`.

Out of scope: a `k8s` pack (no repo to test it on yet; adding it later is one file plus one row in `stack-signals.md`), cloud-provider consoles (DNS records, CDN dashboards), and `docs`/`performance` (separate cycles).

## Decisions

### D1. Files

No new skill (D1 of the unified design). Three new reference files under `skills/review/references/`:

| File | Holds |
|---|---|
| `infra.md` | Rules true for any infrastructure config |
| `infra-docker.md` | Dockerfile and compose rules. `Written for: Docker Compose 2` |
| `infra-caddy.md` | Caddyfile rules. `Written for: Caddy 2` |

`SKILL.md` changes: the routing table links the three files (load `infra-<key>.md` when `infra` is in scope and the key is in `stacks`); the argument becomes `[backend|frontend|infra]`; the profile section `Infra checks` is walked in step 6 like the other layers' checks; `infra` is removed from the "layers with no checklist yet" example.

### D2. Where each old rule goes

Every item of the old skill falls in exactly one group. A rule moves into a pack only if it holds for every project on that tool; a rule that names a host, vendor account, script, or path stays in the profile.

| Old rule | Goes to |
|---|---|
| No real secrets tracked; `.env.example` holds placeholders only | `infra.md` |
| New env var documented in `.env.example` | `infra.md` |
| Validate config before reload; reload, not restart | `infra.md` (the command itself comes from the profile, or the pack names the tool's own validator) |
| Rollback = one revertible commit; no hand edits on the host | `infra.md` |
| Deploy pulls built images; no build on the server | profile (project policy, not universal) |
| Health check present where needed, absent where a flaky check would mark the only instance down | `infra-docker.md` |
| Restart policy, resource limits, volumes consistent between compose and the proxy's roots | `infra-docker.md` |
| `handle`/route order: specific before catch-all; no duplicate handlers; snippets for repeated proxy config | `infra-caddy.md` |
| One header, one owner: top-level `header` plus upstream header gives two values; override upstream with `header_down` | `infra-caddy.md` |
| Verify with `curl -sS -D - -o /dev/null`, each header appears once | `infra-caddy.md` |
| CDN does not cache HTML by default; hashed assets `immutable`; know the purge step after deploy | `infra-caddy.md` for the generic part; zone ids and purge script stay in the profile |
| Hostnames in the site block have DNS; `ALLOWED_HOSTS`/CSRF origins match them | profile (needs project env names) |
| Specific headers (CSP, COOP), shared log pipeline, socket proxy | profile (already there as INV-019 and Infra checks in Project A) |

Anything the profile already holds is not copied into the plugin.

### D3. Stack signals

`stack-signals.md` already has `docker | infra | a `Dockerfile*` or `docker-compose*.yml` / compose*.yaml at the project root`. Add:

| Stack key | Layer | Signals |
|---|---|---|
| `caddy` | infra | a `Caddyfile*` anywhere in the repo |

The manifest list gains the file names `Dockerfile*`, `docker-compose*.yml`, `compose*.yaml`, `Caddyfile*`, found anywhere in the repo by name. The plugin assumes no directory layout: signals only suggest `stacks` keys, and the profile's `Layout` (paths and globs) alone decides which layer a file belongs to. Drift records work unchanged. The stale-pack line applies only when a version is readable (an image tag such as `caddy:2`); otherwise the `Packs:` line shows `?`.

### D4. Routing and `--no-ask`

Routing is by the profile's `Layout` only, as for backend and frontend; there is no routing by file name. A layout path may be a glob, so a project that keeps `Dockerfile` inside its backend directory lists that file under `infra` and the longest match wins. A project that does not list it gets the file reviewed under the layer whose path contains it. With `NO_PROFILE` and `--no-ask`, infra files stay under **Not checked** as `assumed`, as today. With `NO_PROFILE` and no `--no-ask`, the layout question lists the infra manifests it found and asks which layer each belongs to.

### D5. Commands

Infra checks that need a tool (`caddy validate`, `docker compose config -q`) come from the profile's `extra` commands, not from the plugin. If the tool is missing or not allowed, the report says `not run (<why>)`; a config rule is then judged from the text only and the finding says so.

### D6. `check-plugin.py`

No code change. The existing checks already cover the new files: linked from `SKILL.md`, no links inside references, `Written for:` on line 3 of each pack, a signals row for each pack key.

## Tests

Clone Project A to a scratch directory (per `CLAUDE.md` § Testing), copy in the profile, plant uncommitted edits, and first record what the project's own tools say (ground truth). Plant:

1. A specific route placed after a broad `/api/*` handler.
2. A top-level `header` directive for a header the upstream also sends.
3. A secret literal in a compose `environment:` block.
4. A new env var read by compose but missing from `.env.example`.
5. A prod service with no restart policy.
6. A change that touches infra and backend together (checks routing across layers).
7. A `Dockerfile` inside a backend directory, run once with the profile unchanged and once with its glob listed under `infra` (checks that routing follows the profile and nothing else).

Run `/qa:review` and the old `qa-qc-infra` twice each, same model, tools, and prompt.

## Acceptance

- Each planted bug 1–5 is reported by `/qa:review` in at least one of two runs and in both runs for 1–3; none is graded below WARNING except 5; secret literal is CRITICAL.
- No finding contradicts the code (read each by hand).
- Run 6 reports backend and infra findings in one report, each under its layer's rules.
- `Packs:` lists `docker` and `caddy`; the output is valid in both runs.
- `check-plugin.py` passes and `claude plugin validate ./plugins/qa --strict` passes.
- On the same diff, `/qa:review` finds everything the old skill found. Extra findings are judged by hand.

## Risks

- A pack written from one project's habits can be wrong for another. Mitigation: each pack item names the failure it prevents; items Project A needs only go in the profile.
- Infra rules are easy to over-apply to a diff that does not touch them. Mitigation: step 6 already reports only items the change affects.

## Results

Model Sonnet, headless, working copy via `--plugin-dir` (old skill: its own in-repo copy), two runs per scenario, on a scratch clone of Project A with the profile extended by `docker, caddy` in `stacks` and the two validators under `extra`. Ground truth on the planted tree: `caddy validate` and `docker compose config -q` both pass, so none of the planted bugs is visible to the project's own tools; only reading finds them.

Scenario A (bugs 1–5, uncommitted, infra only):

| Planted bug | New skill, run 1 / run 2 | Old `qa-qc-infra`, run 1 / run 2 |
|---|---|---|
| 1 route shadowed by `/api/*` | CRITICAL / CRITICAL | found / found |
| 2 top-level `header` on `/api/*` (duplicate `Cache-Control`) | CRITICAL (+ WARNING for the duplicate) / CRITICAL | found / found |
| 3 password literal in compose `environment:` | CRITICAL / CRITICAL | found (merged with 4) / found |
| 4 variable not in `.env.example` | WARNING / WARNING | found (merged with 3) / found |
| 5 `restart:` removed from a service | WARNING / WARNING | found / found |

Both new runs read `infra.md`, `infra-docker.md`, `infra-caddy.md` and no backend or frontend reference, ran both validators (`ran ✓`), and ended with `Packs: docker 2/?, caddy 2/?` copied from `drift.py`. The new skill took 10–12 turns ($0.25–0.28); the old one 4 turns ($0.17) and ran no validator.

Scenario B (A plus a removed permission class in a backend view): both runs reported the backend CRITICAL (cited INV-012) and the infra findings in one report, `Packs: python 3/3, django 6/6, docker 2/?, caddy 2/?`.

Scenario C (a Dockerfile with a secret in `ENV` and `USER root`, inside a backend directory):

- Profile without a glob for it (C0): both runs reported `LAYOUT be (unmapped)` and did not review the file; both still described its problems under **Not checked**, labelled as informal notes.
- Profile with `be/Dockerfile*` under `infra` (C1): both runs reviewed it with the infra and Docker rules: secret CRITICAL, `USER root` WARNING, missing `.dockerignore` WARNING. Routing followed the profile only.

Findings were read against the code; none contradicted it (one run's claim that the real Dockerfile is `be/app/Dockerfile` was checked and is right).

Caveats:

- Scenario B run 2 made no `Read` of any reference file, yet its `Packs:` line lists `docker` and `caddy`: the script prints the packs a review should load, not proof that they were loaded. The findings it reported were still correct (they came from the diff and the profile).
- Bug 4 and bug 5 were found in both runs, not only one as the acceptance list required at minimum.
- Severity of bug 1 was CRITICAL in all four new runs here, but WARNING in one earlier run of the same bug on another tree; it varies unless the profile has an override.
- `caddy validate` also passed on the bug-1 and bug-2 tree. `k8s` is out of scope and untested.
