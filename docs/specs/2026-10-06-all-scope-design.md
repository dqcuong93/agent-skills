# Whole-scope review (`all`) — design (wave 2, cycle 4)

Status: implemented; accepted with the caveats under Results. Date: 2026-10-06. The plan is folded into this spec.

## Goal

Before shipping, a diff review is not enough: bugs that never appeared in any diff, or that only matter together, are missed. `/qa:review all` reviews whole layers. The design follows what the research and the tests showed: one long pass reads the end of the code worse than the start, so the work is split into units and each unit is reviewed in a fresh context.

## Decisions

- **Argument**: `all [layer] [--units critical|layer|everything] [path]`. The procedure is in `references/scope.md` and replaces steps 4–7 of `SKILL.md`.
- **Units** come from the profile's `## Critical areas` (`path — why — INV-xxx`), critical first, then one `rest` unit per remaining top-level directory; units over 40 files are split.
- **The owner chooses** which units to review (a numbered question that ends the turn); `--units` answers it in advance; `--no-ask` alone reviews the critical units. Units not chosen are listed under **Not checked** as `not selected`.
- **Orchestrator plus reviewers**: the main session runs the profile's full commands once and starts one reviewer per unit through the Agent tool (up to four at a time), each given only its unit, the checklists, the relevant invariants, the finding rules, and an output contract. It then merges, re-opens each cited line, drops findings the line does not show, and applies overrides. Without an Agent tool it reviews units one after another in one context and stops after six, listing the rest as `not reached`.
- **Output**: the usual parts plus a `Coverage` line (units, files, critical units). A `PASS` means no finding in what was reviewed.
- **Profile**: `Critical areas` section; `init-profile` proposes entries from the paths that enforce each invariant and from categories (money, authentication, locks and transactions, irreversible data changes, secrets, outside input, deployment) and asks the owner to confirm them.

## Results

Clone of Project A's backend with seven planted bugs: three in critical units (a removed row lock in the billing service, an `AllowAny` on a user view, an `AllowAny` on a paid-job view) and four in `rest` units (an `AllowAny` on a notifications view, a hard-coded vendor token, `eval` on user input, `shell=True` with concatenated input). The first attempt left the bugs uncommitted, so every arm read them from `git diff`; that attempt measured nothing about whole-scope review and was discarded. The valid attempt used a scratch repository with the bugs committed (no diff). Several of its runs ended on the account's monthly spend limit and were discarded; the numbers below come from the runs that completed.

| Arm | Runs | Planted bugs found | Cost |
|---|---|---|---|
| Orchestrator and reviewers (`all backend --units everything`) | 1 | 7 of 7, all CRITICAL; coverage line: 17 units, 12 reviewers, the 3 critical units included | $5.0 |
| Same skill without an Agent tool (sequential, one context) | 1 | 3 of 7 (the critical units; the stop-after-six rule left the rest unread, and it said so) | $1.15 |
| Old `qa-qc-backend` asked to review the whole backend | 2 | 4 of 7 and 2 of 7 (no coverage statement) | $0.36–0.45 |

The orchestrator run is the only one that reached the four bugs outside the critical units. Findings were read against the files; none contradicted them.

Caveats:

- One orchestrator run, one sequential run, two old-skill runs; the spread between the two old runs is as large as the gap to the sequential arm. The result supports the design; it does not give a recall rate.
- Cost is about 4× to 14× that of the alternatives for a repository of this size (about 230 Python files in the backend). `--units critical` (the default with `--no-ask`) is the cheaper mode and was not run in this test.
- Reviewers' prompts were written by the main session; a poor split (a unit too large) was not tested.
- Frontend, infra, and docs layers in `all` mode were not tested.
