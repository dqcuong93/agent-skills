# agent-skills

Personal engineering skills for [Claude Code](https://code.claude.com), distributed as a plugin marketplace.

The skills are generic: workflow, severity model, stack checklists. Everything specific to a project lives in that project's `.claude/project-profile.md`, so no skill is copied into project repos and nothing drifts between them.

![Three-tier architecture: plugin, project profile, init-profile](docs/architecture.png)

1. **Plugin (this repo):** review workflow, severity model, `common.md`, stack packs, `stack-signals.md`.
2. **Profile (each project repo):** `.claude/project-profile.md` with layout, commands, invariants, project-specific checks.
3. **`init-profile`:** detects the stack, drafts the profile, asks before writing it.

Editable source: [`docs/architecture.excalidraw`](docs/architecture.excalidraw).

## Plugins

| Plugin | Skills |
|---|---|
| `qa` | `/qa:review-backend`, `/qa:init-profile` |

Stack packs for `review-backend`: `python`, `django`, `sqlalchemy`, `fastapi`.

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
      "source": { "source": "github", "repo": "dqcuong93/agent-skills", "ref": "v0.1.0" }
    }
  },
  "enabledPlugins": { "qa@dqcuong93": true }
}
```

Machines without a GitHub SSH key: set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`.

## Use in a project

```
/qa:init-profile      # detect stack, draft .claude/project-profile.md, ask before writing
/qa:review-backend    # review uncommitted changes (or pass a path / branch / staged)
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

1. Loads the profile (`NO_PROFILE` → generic checklist only, suggests `/qa:init-profile`).
2. Checks **stack drift** (below).
3. Loads `common.md` plus the pack for each key in `stacks`.
4. Verifies profile invariants first; a break is CRITICAL.
5. Runs the profile's lint / typecheck / test commands, scoped to the change.
6. Returns: **Verdict** → **Findings** (CRITICAL / WARNING / SUGGESTION) → **Profile drift** → **Commands run** → **Not checked**.

## Keeping a project current

| Situation | What happens | What to do |
|---|---|---|
| Project adds a stack that has a pack | Review reports `STACK <key> (pack available)` under **Profile drift** | Add the key to `stacks`, or re-run `/qa:init-profile` (updates in place, keeps your invariants) |
| Project adds a stack with no pack | Review reports `STACK <key> (no pack)` | Put the rules in the profile's `Backend checks`; write `references/<key>.md` here once two projects need it |
| `stacks` has a key that matches nothing | Review reports `STACK <key> (unknown key)` | Fix the typo or remove it |
| You change a pack or skill here | Projects do not see it until the version moves | Bump `version` in `plugins/qa/.claude-plugin/plugin.json`, tag `vX.Y.Z`. Repos pinning `ref` must change it to the new tag. Others: `claude plugin marketplace update dqcuong93`, then `claude plugin update qa@dqcuong93` |

Drift is reported, never auto-fixed: invariants and severity are the owner's call. Auto-update is off by default; each user turns it on under **Marketplaces** in `/plugin`. Dependency-to-stack mapping lives in [`plugins/qa/stack-signals.md`](plugins/qa/stack-signals.md).

## Status

`v0.1.0`, not yet tagged or released. Checked so far (Claude `sonnet`, a few runs per case, so treat as indicative):

- Catches planted bugs: 6/6 blatant and 4/4 subtle (invariant, tenant-scope, audit, readiness-gate) on a real project, matching the in-repo skill it is meant to replace.
- With permission to run commands it runs the project's `pytest`/`ruff`/`mypy`/`lint-imports` and cites failing tests.
- No CRITICAL false positives on a real clean commit; it is noisier than the old skill (more WARNING/SUGGESTION) and about 25–50% costlier.
- Drift detection: exact on a synthetic project (6/6 mismatches, 0 false drift on a matching one). Only `pyproject.toml` exercised.

Known gaps:

- Severity overrides in the profile are not reliably honored (1 of 2 runs graded two overridden items higher).
- Only backend review exists. Frontend, infra, docs, `finish-change`, and a `pyqt` pack are not written.
- Updating an existing profile via `/qa:init-profile` is untested.
- Cursor does not read Claude plugins; `npx skills add dqcuong93/agent-skills -a cursor` is an unverified option.

## Rules for this repo

- A rule true for every project goes in `references/common.md`; true for one stack goes in `references/<stack>.md`; true for one project goes in that project's profile, never here.
- No project names, client names, domains, hosts, credentials, or business rules in this repo. It is public.
- Plugin names must not start with `claude-`, `anthropic-`, or `cc-plugin-`.

## Develop

```bash
claude plugin validate . --strict
claude plugin validate ./plugins/qa --strict
claude --plugin-dir ./plugins/qa      # load the working copy in a session
```

See [`CLAUDE.md`](CLAUDE.md) for how skills are tested and the gotchas found so far.

## License

MIT
