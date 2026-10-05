---
# Every stack key the project uses (see stack-signals.md). A key with a pack loads
# references/<layer>-<key>.md (e.g. backend-django.md → django); a key without one is
# listed anyway and its rules go under the layer's checks below.
stacks: []
---

# Project profile

<!-- Read by /qa:* review skills. Project-specific facts only; generic rules live in the plugin. -->

## Layout

<!-- Where each layer lives, as paths from the repo root. Reviews assign a changed file to the
     layer whose path contains it; the longest path wins (`frontend/` beats `.`). -->
- backend:
- frontend:
- infra:
- tests:

## Commands

<!-- Exact commands. Reviews run these instead of guessing. Leave blank if absent. -->
- lint:
- format-check:
- typecheck:
- test:
- extra:

## Invariants

<!-- Rules that must never break. Checked FIRST by every review. Number them so findings can cite them. -->
<!-- - INV-001: <rule> — enforced by <file/test/constraint> -->

## Backend checks

<!-- Project-specific items appended to the generic backend checklist. -->

## Frontend checks

## Infra checks

## Severity overrides

<!-- Promote or demote specific findings for this project. -->
<!-- - CRITICAL: <condition> -->
<!-- - WARNING: <condition> -->

## Docs to keep in sync

<!-- Docs that describe shipped behavior. Drift between these and code is a contract bug. -->
