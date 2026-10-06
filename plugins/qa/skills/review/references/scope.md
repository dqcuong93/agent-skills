# Whole-scope review (`all`)

Used when the argument is `all`: `all`, `all backend`, `all infra`, `all <path>`. It replaces steps 4–7 of `SKILL.md`; steps 1–3 and 8–10 run as usual. A review of the whole layer is a different job from a review of a diff: one long pass reads the end of the code worse than the start, so the work is split into units and each unit is reviewed in a fresh context.

## 1. Units

- A unit is a directory or glob. The profile's `## Critical areas` entries (`path — why it matters — INV-xxx`) come first, in the order written. Every other directory of the layers in scope is added after them as one unit per top-level directory, marked `rest`.
- A unit over 40 files is split by subdirectory. Files directly in a layer root form their own unit.
- With no `Critical areas` section, every unit is `rest`; say so and suggest `/qa:init-profile` to name the critical ones.
- Also glob the top-level directories of the repository and report each that no `Layout` or `ignore` entry covers as `LAYOUT <directory> (unmapped)`.

## 2. Choose

Say how many units and files there are, and that a unit is one reviewer's worth of cost. Without `--no-ask`, list the units numbered (critical first, then `rest`) and ask which to review; offer `critical` (the default), `layer` (every unit of the layer), and `everything`. End the turn with the question. `--units critical|layer|everything` answers the question in advance. With `--no-ask` and no `--units`, review the critical units only. A unit that is not chosen goes under **Not checked** as `not selected`.

## 3. Run

- Run the profile's full `lint`, `typecheck`, and `test` commands once, not once per unit; report each as in step 7.
- For each chosen unit start one reviewer with the Agent tool, up to four at a time. Give it only: the unit's paths, the paths of the layer checklist and packs to read (steps 3–4 of `SKILL.md`), the profile invariants whose enforcing path lies in the unit (and any that name the unit), the profile's `<Layer> checks` and severity overrides, the finding rules and the severity table, and this output contract: one line per finding, `SEVERITY path:line — problem. Why it matters. Fix.`, naming the violating line, nothing else. It reads its unit and, when a finding needs it, the callers of the code in question; it does not review other units.
- With no Agent tool, review the units yourself one after another, say `reviewed in one context` for each, and stop after six units; the rest go under **Not checked** as `not reached`.

## 4. Merge

- Collect all finding lines. Re-open the cited line of each; drop any whose line does not show the problem.
- Merge findings with the same file, line, and cause; apply the profile's severity overrides first, then the table.
- In this scope a finding names the violating line, not a changed line.

## 5. Output

The usual five parts, plus a **Coverage** line before **Not checked**: `Coverage: <x> of <y> units, <n> of <m> files, <z> critical units of <w>`. Verdict `PASS` here means no finding in the units reviewed; the Coverage line says what that covers. Units not reviewed are listed under **Not checked** with the reason (`not selected`, `not reached`, `reviewer failed`).
