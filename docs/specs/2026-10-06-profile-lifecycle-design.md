# Profile lifecycle — design (wave 2, cycle 5)

Status: implemented; verified by unit tests and one run on a real profile. Date: 2026-10-06. The plan is folded into this spec (the cycle is one script change, three text edits, one check).

## Goal

A profile goes stale as a project changes and as the plugin gains packs and layers. Reviews should say so, deterministically, and should say when a layer the project uses has no rules anywhere.

## Decisions

### D1. Two lines in the profile front matter

`confirmed:` (a `YYYY-MM-DD` date) and `plugin:` (the plugin version the profile was written with), plus `review-after-days:` (default 180 when absent). `/qa:init-profile` sets the first two in its write step (`date +%F`; the version from the plugin's `plugin.json`) and keeps the third as the owner has it. The date is written only after the owner confirms the draft; nobody else sets it.

### D2. Records, computed by `drift.py`

All of these come from `plugins/qa/scripts/drift.py`, not from the model, and appear in **Profile drift**:

- `PROFILE (no confirmed date)`: no valid `confirmed:`.
- `PROFILE (confirmed <date>, <n> days ago; limit <m>)`: older than `review-after-days`.
- `PROFILE (written with plugin <a>, installed <b>)`: `plugin:` is older than the installed version in major.minor. A profile with no `plugin:` gets only the first record.
- `GAP layer <role> (no checklist in the plugin and no profile checks)`: a `Layout` role other than `tests` and `ignore` with entries, no `references/<role>.md` in the plugin, and nothing under its `## <Role> checks` section (HTML comments do not count).

`STACK <key> (no pack)` already covers a stack with no pack. Reviews only report; the action for `PROFILE` is to re-run `/qa:init-profile`, for `GAP` to add checks to the profile (and to tell the plugin owner if other projects need the layer).

### D3. What this does not do

It does not send anything outside the project and does not auto-update a profile. Promoting a rule from profiles into a pack stays a manual decision by the plugin owner.

## Tests

`scripts/test_drift.py`: no `confirmed`, `confirmed` too old with a custom limit, within the limit; profile written with an older plugin version, current version; a layer with neither checklist nor profile checks, the same layer with checks, `tests` and `ignore` exempt. The script takes `--today` so the tests do not depend on the clock. `scripts/check-plugin.py` checks that the template carries the three front-matter keys.

## Results

12 unit tests pass (3 new for this cycle, 9 earlier ones adjusted for a fixture that now carries `confirmed:` and the layer checklists). On Project A's real profile the script reports `PROFILE (no confirmed date)` and nothing else lifecycle-related, as expected: the owner has not run `/qa:init-profile` since the field was added. Not tested: the init-profile write step setting both fields (headless runs cannot write under `.claude/`).
