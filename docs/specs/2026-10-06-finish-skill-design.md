# `/qa:finish` — design (wave 2, cycle 6)

Status: implemented; see Results for what was and was not verified. Date: 2026-10-06. The plan is folded into this spec.

## Goal

Port Project A's in-repo `finish-change` skill into the plugin: the last pass after coding and before the owner commits. It orchestrates the rest of the plugin and holds no project rules.

## Decisions

- **Skill `/qa:finish [--no-ask] [path | branch | range]`**, `disable-model-invocation` so it only runs when called.
- **Steps**: scope, reviewers, full verification commands, triage into auto-fix and needs-decision, fix, test gaps, stale docs, report with a commit message. It never runs `git commit`, `git push`, or `git tag`; it prints the message and stops.
- **Reviewers**: `/qa:review --no-ask` once for the whole scope (it routes by layer and now covers backend, frontend, infra, and docs), then every `reviewers:` line of the profile's new `## Finish` section whose path matches a changed file (for example an external UI review for the frontend), and an offer of `/qa:perf` for the profile's hot paths.
- **Ownership of verification**: `/qa:review` runs the profile's commands scoped to the change; `/qa:finish` runs them in full. The report states which ran.
- **Profile**: a `## Finish` section with `reviewers`, `commit-format`, `ticket-from-branch`. The commit message defaults to Conventional Commits; the ticket id comes from the branch name by the profile's pattern.
- **`--no-ask`**: needs-decision items are left unfixed and listed instead of asked.
- **External plugins stay external.** The plugin names them only through the profile.

## Results

Clone of Project A on a ticket branch (`MW-999`), profile with a `Finish` section, `--no-ask`, Sonnet, working copy via `--plugin-dir`.

- Needs-decision case (a permission class changed to `AllowAny`, one doc line edited): two runs. Both invoked `/qa:review` through the `Skill` tool, found the broken contract (anonymous callers reach a view that writes `request.user`), the test that now fails, the stale schema and docs, and the throttle and CSRF consequences, left everything unfixed as the `--no-ask` rule says, and printed a Conventional Commits message with the ticket taken from the branch name (`MW-999`) and the attribution line. Neither ran `git commit` or `git push`. The verification commands that were not allowed were reported as `not run`; one run's message offered two drafts for the two possible decisions.
- Auto-fix case (a debug `print` of the request body and an unused import added): one run. It reviewed, removed both lines with two edits, ran the project's lint, format check, and the tests of the touched app (18 passed), skipped the test-writing step because the final diff was empty, and said there was nothing left to commit. It did not run `git commit` or `git push`.

Not tested: the interactive question for needs-decision items, writing a missing test, the `reviewers:` profile lines (an external UI review), and the `/qa:perf` offer. The auto-fix test ran the project's tests against the services already running on the machine (the test database is separate, the cache is shared); a run on a machine without them reports `not run` instead.
