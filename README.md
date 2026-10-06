# agent-skills

Personal engineering skills for [Claude Code](https://code.claude.com), distributed as a plugin marketplace.

The skills are generic: workflow, severity model, stack checklists. Everything specific to a project lives in that project's `.claude/project-profile.md`, so no skill is copied into project repos and nothing drifts between them.

![Three-tier architecture: plugin, project profile, init-profile](docs/architecture.png)

1. **Plugin (this repo):** review workflow, severity model, layer checklists (`backend.md`, `frontend.md`, `infra.md`), stack packs, `stack-signals.md`.
2. **Profile (each project repo):** `.claude/project-profile.md` with layout, commands, invariants, project-specific checks.
3. **`init-profile`:** detects the stack, drafts the profile, asks before writing it.

Editable source: [`docs/architecture.excalidraw`](docs/architecture.excalidraw).

## Plugins

| Plugin | Skills |
|---|---|
| `qa` | `/qa:review`, `/qa:init-profile` |

Layers: `backend`, `frontend`, `infra`. Stack packs: `python`, `django`, `sqlalchemy`, `fastapi`, `vue`, `inertia`, `astro`, `tailwind`, `docker`, `caddy`.

## Install

Just for yourself (all projects on this machine):

```bash
claude plugin marketplace add dqcuong93/agent-skills
claude plugin install qa@dqcuong93
```

For everyone working in a repo, commit this to the repo's `.claude/settings.json` and pin a tag:

```json
{
  "extraKnownMarketplaces": {
    "dqcuong93": {
      "source": { "source": "github", "repo": "dqcuong93/agent-skills", "ref": "v0.3.0" }
    }
  },
  "enabledPlugins": { "qa@dqcuong93": true }
}
```

Machines without a GitHub SSH key: set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`.

## Use in a project

```
/qa:init-profile      # detect stack, draft .claude/project-profile.md, ask before writing
/qa:review           # review uncommitted changes (or: backend|frontend, --no-ask, path / branch / range / staged)
```

### Project profile

One file per project. Facts only; generic best practice stays in the plugin.

```markdown
---
stacks: [python, sqlalchemy]
---
# Project profile
## Layout          # where each layer lives
## Commands        # exact lint / format-check / typecheck / test commands
## Invariants      # numbered rules that must never break, checked first; name what enforces each
## Backend checks  # project-specific items appended to the generic checklist
## Severity overrides   # a matching line fixes the level; no re-grading
## Docs to keep in sync
```

Template: [`plugins/qa/skills/init-profile/profile-template.md`](plugins/qa/skills/init-profile/profile-template.md).

### What a review does

1. Loads the profile. With none, it reads the manifests, shows the stacks it found, and asks how the repo is laid out (`--no-ask` skips the question for headless runs).
2. Routes each changed file to a layer by the profile's `Layout`; the longest path wins.
3. Checks **stack drift** and stale packs (below).
4. Loads the layer checklist plus the pack for each key in `stacks`.
5. Verifies profile invariants first; a break is CRITICAL.
6. Runs the profile's lint / typecheck / test commands, scoped to the change.
7. Looks things up (official docs first) only when a dependency changed, behaviour is version-specific, or an API is in doubt.
8. Returns: **Verdict** → **Findings** (CRITICAL / WARNING / SUGGESTION) → **Profile drift** → **Commands run** → **Not checked**.

## Keeping a project current

| Situation | What happens | What to do |
|---|---|---|
| Project adds a stack that has a pack | Review reports `STACK <key> (pack available)` under **Profile drift** | Add the key to `stacks`, or re-run `/qa:init-profile` (updates in place, keeps your invariants) |
| Project adds a stack with no pack | Review reports `STACK <key> (no pack)` | Add the key to `stacks` and put its rules in the profile's checks; write `references/<layer>-<key>.md` here once two projects need it |
| `stacks` has a key that matches nothing | Review reports `STACK <key> (unknown key)` | Fix the typo or remove it |
| A pack is older than the project's major version | Review reports `PACK <key> (written for <n>, project uses <m>): may be stale` | Refresh the pack here, bump the version |
| You change a pack or skill here | Projects do not see it until the version moves | Bump `version` in `plugins/qa/.claude-plugin/plugin.json`, tag `vX.Y.Z`. Repos pinning `ref` must change it to the new tag. Others: `claude plugin marketplace update dqcuong93`, then `claude plugin update qa@dqcuong93` |

Drift is reported, never auto-fixed: invariants and severity are the owner's call. Auto-update is off by default; each user turns it on under **Marketplaces** in `/plugin`. Dependency-to-stack mapping lives in [`plugins/qa/stack-signals.md`](plugins/qa/stack-signals.md).

## Status

`v0.3.0`, not yet tagged (`v0.2.0` was never tagged; its content is included). `v0.1.0` was published untagged on `main`. Checked so far (Claude `sonnet`, a few runs per case, so treat as indicative):

- Catches planted bugs: 6/6 blatant and 4/4 subtle (invariant, tenant-scope, audit, readiness-gate) on a real project, matching the in-repo skill it is meant to replace.
- With permission to run commands it runs the project's `pytest`/`ruff`/`mypy`/`lint-imports` and cites failing tests.
- No CRITICAL false positives on a real clean commit; it is noisier than the old skill (more WARNING/SUGGESTION) and about 25–50% costlier.
- Drift detection: exact on a synthetic project (6/6 mismatches, 0 false drift on a matching one). Only `pyproject.toml` exercised.

Known gaps:

- Docs review, `/qa:perf`, whole-repo (`all`) scope, `finish-change`, and `nuxt`, `k8s`, `pyqt` packs are not written. The `infra` layer (`docker`, `caddy`) is checked on one real project with planted bugs, two runs per case.
- The checked numbers above are from `v0.1.0` (`review-backend`). `/qa:review` wave-1 results (two real projects, side by side with their old skills, overrides 2/2) are in [`docs/specs/2026-10-05-unified-review-design.md`](docs/specs/2026-10-05-unified-review-design.md#results-2026-10-05).
- Drift records and the `Packs:` line come from `plugins/qa/scripts/drift.py` (unit-tested); the line says which packs a review should load, not that the model read them. Versions in `yarn.lock` and `Pipfile.lock` are not read.
- The banned-word scan in `scripts/check-plugin.py` only runs where a local `.banned-words` exists, so not in CI.
- `/qa:init-profile` asks the user to confirm the layout (first run and updates); tested headless up to the profile write, which headless runs cannot do (`.claude/` is a protected path), so the write step is untested.
- Cursor does not read Claude plugins; `npx skills add dqcuong93/agent-skills -a cursor` is an unverified option.

## Rules for this repo

- A rule true for every project on a layer goes in `references/<layer>.md`; true for one stack goes in `references/<layer>-<stack>.md` (starting with `Written for: <stack> <major>`); true for one project goes in that project's profile, never here.
- No project names, client names, domains, hosts, credentials, or business rules in this repo. It is public.
- Plugin names must not start with `claude-`, `anthropic-`, or `cc-plugin-`.

## Develop

```bash
claude plugin validate . --strict
claude plugin validate ./plugins/qa --strict
python3 scripts/check-plugin.py       # structure + optional local .banned-words scan
claude --plugin-dir ./plugins/qa      # load the working copy in a session
```

See [`CLAUDE.md`](CLAUDE.md) for how skills are tested and the gotchas found so far.

## License

MIT
