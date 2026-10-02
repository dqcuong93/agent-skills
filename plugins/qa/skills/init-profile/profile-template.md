---
# Stack packs to load. Each key matches a file in a review skill's references/ folder
# (e.g. review-backend/references/django.md). Unknown keys are ignored.
stacks: []
---

# Project profile

<!-- Read by /qa:* review skills. Project-specific facts only; generic rules live in the plugin. -->

## Layout

<!-- Where each layer lives. Reviews use this to decide which checklist applies to a changed file. -->
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
