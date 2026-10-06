---
# Every stack key the project uses (see stack-signals.md). A key with a pack loads
# references/<layer>-<key>.md (e.g. backend-django.md → django); a key without one is
# listed anyway and its rules go under the layer's checks below.
stacks: []
# Date (YYYY-MM-DD) the owner last confirmed this profile, and the plugin version it was written
# with. /qa:init-profile sets both; reviews report a profile that is older than review-after-days.
confirmed:
plugin:
review-after-days: 180
---

# Project profile

<!-- Read by /qa:* review skills. Project-specific facts only; generic rules live in the plugin. -->

## Layout

<!-- Where each layer lives, as paths or globs from the repo root, comma-separated, each
     optionally followed by a note in parentheses. Reviews assign a changed file to the layer
     whose entry matches it; with several matches the entry with the longest literal prefix
     (the text before the first `*`) wins (`frontend/` beats `.`, `be/Dockerfile*` beats `be/`).
     `ignore` lists paths the owner said belong to no layer; they are never reviewed. -->
- backend:
- frontend:
- infra:
- docs:
- tests:
- ignore:

## Commands

<!-- Exact commands. Reviews run these instead of guessing. Leave blank if absent. -->
- lint:
- format-check:
- typecheck:
- test:
- perf:
- extra:

## Invariants

<!-- Rules that must never break. Checked FIRST by every review. Number them so findings can cite them. -->
<!-- - INV-001: <rule, one line> — enforced by <file/test/constraint> · <doc path § section that explains it> -->

## Critical areas

<!-- Places where a bug costs money, data, or trust. /qa:review all reviews these first and asks which to review.
     One per line: path or glob — why it matters — INV-xxx it enforces (if any). -->

## Backend checks

<!-- Project-specific items appended to the generic backend checklist. -->

## Frontend checks

## Infra checks

## Docs checks

<!-- Project-specific items appended to the generic docs checklist: doc paths that must be updated for a given change, grep audits, update order. -->

## Performance

<!-- Used by /qa:perf: latency or size budgets, hot paths (pages, endpoints, jobs), known traps. Measurement commands go on the `perf:` line under Commands. -->

## Finish

<!-- Used by /qa:finish. `reviewers`: path or glob — skill or command to run in addition to /qa:review (e.g. an external UI review for the frontend). `commit-format`: how the commit message looks (default Conventional Commits). `ticket-from-branch`: a regular expression that takes the ticket id from the branch name, and where it goes in the message. -->

- reviewers:
- commit-format:
- ticket-from-branch:

## Severity overrides

<!-- Promote or demote specific findings for this project. -->
<!-- - CRITICAL: <condition> -->
<!-- - WARNING: <condition> -->

## Docs to keep in sync

<!-- Docs that describe shipped behavior, one per line: <topic or path that triggers it> — <doc path> (§ section). Reviews read the matching doc, and only that section, before judging a change in that topic; the docs stay the source of truth, so do not copy their text here. Drift between a doc and the code is a contract bug. -->
