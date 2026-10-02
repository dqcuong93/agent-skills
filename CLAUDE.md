# agent-skills — working notes

Public repo (`github.com/dqcuong93/agent-skills`) of generic skills as a Claude Code plugin marketplace. Layout and usage: `README.md`. Never put project/client names, hosts, credentials, or business rules here; those belong in each project's `.claude/project-profile.md`.

Local state: git initialised, remote `origin` set, **nothing committed or pushed yet**.

## Layout

```
.claude-plugin/marketplace.json            marketplace "dqcuong93"
plugins/qa/.claude-plugin/plugin.json      plugin "qa", version 0.1.0
plugins/qa/stack-signals.md                dependency → stack key (shared by both skills)
plugins/qa/skills/review-backend/          SKILL.md + references/{common,python,django,sqlalchemy,fastapi}.md
plugins/qa/skills/init-profile/            SKILL.md + profile-template.md
.github/workflows/validate.yml             claude plugin validate --strict
```

## Before changing a skill

1. `claude plugin validate . --strict` and `claude plugin validate ./plugins/qa --strict`.
2. Behaviour changes need a real run, not just a read-through (see "Testing").
3. Bump `version` in `plugin.json` when a release should reach users; tag `vX.Y.Z`.

## Gotchas found while building

- **`!` command injection goes through the permission check.** Pipes, `||`, `&&`, `( … )` groups are rejected in headless mode ("cannot be checked in advance"). Use single commands and list them in the skill's `allowed-tools`. A non-zero exit fails the whole skill, so `cat missing || echo X` was needed once; prefer commands that cannot fail.
- **`!` cannot `ls` the plugin directory** (outside the session's working dirs). Use `Glob`/`Read` on `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}` instead; both resolve in skill content.
- **`claude -p` argument order:** put the prompt first, then flags, and redirect stdin (`< /dev/null`); `--allowedTools "A,B,C"` as the last positional swallows the prompt.
- **Skill model compliance:** a skill that says "ask the user to confirm" still wrote the file in one test; the fix was an explicit "end the turn with the question; the file is written in a later step". Verify such gates by running them 3 times.
- **zsh:** `--include=*.py` in grep and `echo =====` break (glob / `=cmd` expansion). Use `-F`, `printf`.
- **Descriptions** start with "Use when…" and describe triggers only, never the workflow.

## Testing

No unit tests; skills are tested by running them headless against fake or cloned projects and reading the output (regex scoring over-counts; read results by hand).

- Fake project: `git init`, a profile, a small uncommitted change, then
  `claude -p "/qa:review-backend uncommitted changes" --model sonnet --plugin-dir ./plugins/qa --allowedTools "Read,Glob,Grep,Bash(git *)" --output-format json < /dev/null`.
- Real project: `git clone --no-hardlinks` it to a scratch dir (plain `--local` fails across filesystems), copy in the profile, plant bugs as uncommitted edits, and first record what the project's own tools catch (ground truth).
- Tools that live in the real repo's `.venv` are editable installs pointing at the real source. In a clone, set `PYTHONPATH=$PWD/src` or tests exercise the wrong code.
- Do not touch a shared dev database. Start a throwaway Postgres on another port and rewrite the port in the clone's profile and docs only.
- Compare against the skill being replaced under identical model, tools, and prompt; run each at least twice.

## Open work (priority order)

1. Severity overrides: make profile `Severity overrides` bind reliably (currently 1 of 2). Try placing the override list at the start of the grading step and re-run 3–4 times.
2. Test `/qa:init-profile` on an existing profile (must keep user-written invariants) and drift on `package.json`.
3. Commit, push, tag `v0.1.0`; install from GitHub to test `marketplace add` / `update` for real (only the docs describe this flow so far).
4. Pilot on one real project: commit its drafted profile, keep that project's in-repo QA skill alongside, collect real runs, then remove the old skill.
5. More skills: `review-frontend` (+ `vue`, `tailwind`, `astro` packs), `review-infra`, `review-docs`, `finish-change`, `performance-optimization`; `pyqt` pack for the desktop-UI project.
6. Profiles for the other projects, porting their project-specific rules out of their in-repo skills.
7. Cursor: decide between a `.cursor-plugin/marketplace.json` and `npx skills add`; neither verified.
