---
name: init-profile
description: Use when a project has no .claude/project-profile.md, when /qa review skills report NO_PROFILE, or when the project's stack, layout, commands, or invariants changed and the profile needs updating.
disable-model-invocation: true
allowed-tools: Bash(ls *) Glob Read
---

# Create or update the project profile

The profile at `.claude/project-profile.md` is the only project-specific input to the `/qa:*` review skills. It holds facts about this project; generic rules stay in the plugin.

## Current profile

Read `.claude/project-profile.md`. If it does not exist, there is no profile yet; draft a new one.

## Project signals

Project root listing (look for `pyproject.toml`, `requirements*.txt`, `manage.py`, `package.json`, `astro.config.*`, `vite.config.*`, `docker-compose*.yml`, `Dockerfile`, `Caddyfile`, `Makefile`, `AGENTS.md`, `CLAUDE.md`, `.cursor/`, `docs/`):

!`ls -a "${CLAUDE_PROJECT_DIR}"`

Available stack packs: Glob `${CLAUDE_PLUGIN_ROOT}/skills/review/references/*-*.md`. The stack key is the part of the file name after the first `-` (`frontend-vue.md` → `vue`). Files without a `-` (`backend.md`, `frontend.md`) are layer checklists, always loaded, never listed in `stacks`.

## Steps

1. **Detect.** Read the manifests listed in `${CLAUDE_PLUGIN_ROOT}/stack-signals.md` § Manifests at the root and one directory down, plus compose files, `Makefile` targets, and `AGENTS.md`/`CLAUDE.md`. Derive: stacks, layout per layer (backend, frontend, infra, tests), and the exact lint/format/typecheck/test commands.
2. **Map stacks.** Match dependencies against `stack-signals.md` § Signals. Set `stacks` to every matched key. A key with a pack loads it; a key without one is listed anyway, so reviews stop reporting it as drift, and its rules live in the profile. For each matched key with no pack, research it: official docs first (context7 when available), then the changelog or migration guide; community posts only to corroborate. Keep only pitfalls Claude would otherwise miss, and put them under the profile's `<Layer> checks` with the source URL. Mark these as researched in the step-5 summary.
3. **Harvest invariants and rules.** Pull candidate invariants and project-specific checks from `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, `docs/`, existing `.claude/skills/*/SKILL.md`, DB constraints, and import-linter contracts. Keep only rules specific to this project; drop anything already covered by the generic checklists.
4. **Draft.** Fill `${CLAUDE_SKILL_DIR}/profile-template.md`. If a profile exists, update it in place and keep every user-written invariant unless the user says to remove it.
5. **Present and end the turn.** Show the full draft in chat, list the invariants you inferred and where each came from, and ask the user to confirm or edit them and any severity overrides. This turn ends with that question; the file is written in step 6.
6. **Write after confirmation.** On the user's reply, apply their edits and write `.claude/project-profile.md`.
7. **Verify commands.** Run each command in `Commands` once; mark any that fail and say why.

## Rules for profile content

- Facts only: paths, commands, invariants, project-specific checks. No generic best practices.
- Each invariant names what enforces it (file, constraint, test) so reviews can verify it.
- Keep it short. A profile over ~150 lines usually means generic rules leaked in.
- Write valid Markdown: a blank line after every heading and before every list, as in the template. Projects often lint `.claude/` with markdownlint, and a failing hook blocks the commit.
