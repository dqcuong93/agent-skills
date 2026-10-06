# agent-skills — working notes

Public repo (`github.com/dqcuong93/agent-skills`) of generic skills as a Claude Code plugin marketplace. Layout and usage: `README.md`. Never put project/client names, hosts, credentials, or business rules here; those belong in each project's `.claude/project-profile.md`.

State: `main` is published on GitHub; no tags yet.

## Layout

```
.claude-plugin/marketplace.json            marketplace "dqcuong93"
plugins/qa/.claude-plugin/plugin.json      plugin "qa", version 0.3.0
plugins/qa/stack-signals.md                manifests + dependency → stack key (shared by both skills)
plugins/qa/skills/review/                  SKILL.md + references/{backend,frontend}.md + <layer>-<stack>.md packs
plugins/qa/skills/init-profile/            SKILL.md + profile-template.md
scripts/check-plugin.py                    structural checks (also in CI); reads optional local .banned-words
.github/workflows/validate.yml             claude plugin validate --strict + check-plugin.py
docs/specs/, docs/plans/                   design specs and implementation plans
```

## Before changing a skill

1. `claude plugin validate . --strict`, `claude plugin validate ./plugins/qa --strict`, and `python3 scripts/check-plugin.py`.
2. Behaviour changes need a real run, not just a read-through (see "Testing").
3. Bump `version` in `plugin.json` when a release should reach users; tag `vX.Y.Z`.

## Gotchas found while building

- **`!` command injection goes through the permission check.** Pipes, `||`, `&&`, `( … )` groups are rejected in headless mode ("cannot be checked in advance"). Use single commands and list them in the skill's `allowed-tools`. A non-zero exit fails the whole skill, so `cat missing || echo X` was needed once; prefer commands that cannot fail.
- **`!` cannot `ls` the plugin directory** (outside the session's working dirs). Use `Glob`/`Read` on `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}` instead; both resolve in skill content.
- **`claude -p` argument order:** put the prompt first, then flags, and redirect stdin (`< /dev/null`); `--allowedTools "A,B,C"` as the last positional swallows the prompt.
- **Skill model compliance:** a skill that says "ask the user to confirm" still wrote the file in one test; the fix was an explicit "end the turn with the question; the file is written in a later step". Verify such gates by running them 3 times.
- **zsh:** `--include=*.py` in grep and `echo =====` break (glob / `=cmd` expansion). Use `-F`, `printf`.
- **Descriptions** start with "Use when…" and describe triggers only, never the workflow.

- **`drift.py` parses `stack-signals.md` and each pack's line 3.** The `STACK`/`PACK` records and the `Packs:` line of `/qa:review` come from `plugins/qa/scripts/drift.py`, not from the model. Change the signals table format or the `Written for:` line only together with the script and `scripts/test_drift.py`. File-based keys (`docker`, `caddy`) are hard-coded in the script.

## Testing

The deterministic script (`plugins/qa/scripts/drift.py`) has unit tests: `python3 -m unittest discover -s scripts -p 'test_*.py'`. Skills themselves have no unit tests; they are tested by running them headless against fake or cloned projects and reading the output (regex scoring over-counts; read results by hand).

- Fake project: `git init`, a profile, a small uncommitted change, then
  `claude -p "/qa:review" --model sonnet --plugin-dir ./plugins/qa --allowedTools "Read,Glob,Grep,Bash(git *)" --output-format json < /dev/null`.
- If `qa@dqcuong93` is also installed and enabled, two `qa` plugins load; disable the installed one while testing the working copy (`claude plugin disable qa@dqcuong93`, re-enable after).
- Real project: `git clone --no-hardlinks` it to a scratch dir (plain `--local` fails across filesystems), copy in the profile, plant bugs as uncommitted edits, and first record what the project's own tools catch (ground truth).
- Tools that live in the real repo's `.venv` are editable installs pointing at the real source. In a clone, set `PYTHONPATH=$PWD/src` or tests exercise the wrong code.
- Do not touch a shared dev database. Start a throwaway Postgres on another port and rewrite the port in the clone's profile and docs only.
- Compare against the skill being replaced under identical model, tools, and prompt; run each at least twice.

## Open work (priority order)

1. Tag `v0.2.0` and update installs (wave 1 acceptance is recorded in `docs/specs/2026-10-05-unified-review-design.md` § Results).
2. Remove the old in-repo QA skills from those projects once Cursor's handling of plugin skills is confirmed; repoint their `finish-change`, agent instructions, and AI docs to `/qa:review`.
3. Wave 2 cycles, in order (specs and plans in `docs/specs/` and `docs/plans/`, dated 2026-10-06):
   - 0 layout confirmation in `init-profile`: implemented, accepted, not committed until the owner commits it.
   - 1 `infra` layer (`docker`, `caddy` packs; `k8s` later): implemented and accepted (results in `docs/specs/2026-10-06-infra-layer-design.md`); not committed until the owner commits it.
   - 2 `docs` layer; 3 `/qa:perf` as its own skill: no spec yet.
   - 4 `all` scope (whole layer or repo): orchestrator plus per-unit reviewers in fresh contexts, units from a profile `Critical areas` section the owner confirms; recall measured with planted bugs.
   - 5 profile lifecycle: `confirmed:` and `plugin:` lines, `PROFILE` and `GAP` records, re-research when a `STACK … (no pack)` record appears.
   - 6 `finish-change` as a plugin skill that calls `/qa:review --no-ask`; `ui-ux-pro-max` stays an external plugin.
4. Packs the owner's repos need: `nuxt`, `pyqt`, infra `k8s`.
5. Profiles for the other projects, porting their project-specific rules out of their in-repo skills.
6. Community release: React/Next and Node packs, validate `init-profile` research on unfamiliar repos, example output in the README.
