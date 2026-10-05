# Unified `/qa:review` — design (wave 1)

Status: draft, awaiting review. Date: 2026-10-05.

## Goal

Build one plugin skill, `/qa:review`, that covers what the per-repo `qa-qc-backend` and `qa-qc-frontend` skills do in the two most complete source projects, driven by each repo's `.claude/project-profile.md`. In wave 1 the old skills stay in place and both run side by side; removing them is a later decision.

Source projects (unnamed here; this repo is public):

- **Project A** — `pyproject.toml` at the root, Django + DRF + Wagtail code in `be/`, `fe/` (Astro + Vue 3 + Tailwind 4) with its own `package.json`.
- **Project B** — Django + Inertia at the repo root, `frontend/` (Vue 3 + Inertia + Tailwind 4).

## Model

Same shape as other workflow plugins: the plugin is installed once (user scope), repos hold no skill copies, and each repo customises through one file.

| Part | Lives in | Holds |
|---|---|---|
| Workflow, severity, output format, generic + stack checklists | this plugin | rules true for every project or every project on a stack |
| Layout, commands, invariants, project checks, severity overrides, docs to sync | each repo's `.claude/project-profile.md` | rules true for one project |
| `/qa:init-profile` | this plugin | drafts the profile; for a stack with no pack, researches and writes its checks into the profile |

A rule moves from a profile into a pack once two projects need it.

## Decisions

### D1. One skill, `/qa:review`, replaces `/qa:review-backend`

`skills/review-backend/` becomes `skills/review/`. One workflow, one report for a diff that spans layers. Later layers (infra, docs) add reference files, not skills.

Rationale: Anthropic's skill authoring guide, "Pattern 2: Domain-specific organization" (one skill, references per domain, read only what applies). A thin per-layer skill that reads a shared workflow file is two levels of indirection, which the same guide warns causes partial reads.

The rename is breaking; the plugin version moves to `0.2.0`. No other installs exist yet.

### D2. Flat references, named `<layer>.md` and `<layer>-<stack>.md`

```text
skills/review/
  SKILL.md
  references/
    backend.md            (was common.md)
    backend-python.md
    backend-django.md
    backend-sqlalchemy.md
    backend-fastapi.md
    frontend.md
    frontend-vue.md
    frontend-inertia.md
    frontend-astro.md
    frontend-tailwind.md
```

`SKILL.md` links every file directly. Reference files link to nothing. A stack key has a pack when any `references/*-<key>.md` exists.

### D3. Routing by profile `Layout`

1. Each changed file is assigned to the layer whose `Layout` path contains it; the longest matching path wins (Project B lists backend as `.` and frontend as `frontend/`).
2. With `NO_PROFILE`, never guess layers from file extensions (`.ts` can be a Node backend). Instead read the manifests (D7 list) at the root and one level down, map them through `stack-signals.md`, and ask the user to confirm, in the conversation's language, with the detected facts filled in. Example:

   > This repo has no `.claude/project-profile.md`, so I need to know how it is laid out.
   > I found:
   > - `be/pyproject.toml` → Django, Django REST Framework
   > - `fe/package.json` → Vue, Astro, Tailwind
   >
   > Is this right?
   > 1. Yes: `be/` is backend, `fe/` is frontend. Review with these stacks.
   > 2. Partly: tell me what to change (e.g. "`fe/` is Nuxt", "`scripts/` is backend too").
   > 3. Create a profile first with `/qa:init-profile` so I don't ask again.

   End the turn with that question; review starts on the reply. The answer applies to this run only; nothing is written. Callers that cannot answer (headless runs, other skills) pass `--no-ask`; then review with `backend.md`/`frontend.md` only, and list every changed file's layer as "assumed" under **Not checked**.
3. Files matching no layer are listed under **Not checked**, never reviewed with another layer's checklist.
4. Arguments: `/qa:review [backend|frontend] [--no-ask] [path | branch | commit | range | staged]`. A layer name restricts the review to that layer.
5. For each layer in scope, load `<layer>.md`, then `<layer>-<key>.md` for each profile `stacks` key that has one.

### D4. Noise controls

Earlier runs were noisier than the replaced skills. `SKILL.md` adds two rules:

1. **Evidence:** a finding names the changed line and the concrete failure or the rule it breaks. No speculative impact; otherwise drop it.
2. **Merge:** the same `file:line` and problem flagged by two checklists is reported once, at the higher level.

### D5. Severity overrides bind first

The grading step opens with: list every profile `Severity overrides` line that matches a finding, apply it, and only then grade the rest by the table. Overrides beat the merge rule.

### D6. Profile read with `Read`, not `!` injection

Both skills drop ``!`cat … || echo "NO_PROFILE"` ``; `||` is rejected by the permission check in headless runs. Step 1 becomes "Read `.claude/project-profile.md`; if missing, `NO_PROFILE`." `!` keeps only commands that cannot fail and have no pipes (`git status --short`, `ls -a`).

### D7. Drift check covers monorepos

Manifests (`pyproject.toml`, `requirements*.txt`, `setup.cfg`, `package.json`) are searched at the root **and** in each `Layout` path. The list lives once, in a `## Manifests` section of `stack-signals.md`. `stack-signals.md` also gains an `inertia` row (`@inertiajs/vue3`, `inertia-django`, `django-inertia`), which today are folded into `vue` and `django`. No manifest found → `STACK ? (no manifest found in <paths>)`, never `none`.

### D8. Frontend checklists

Merged from both projects' frontend skills. Generic items only; project items go to D9.

| File | Covers |
|---|---|
| `frontend.md` | structure and file size, a11y (labels, aria, keyboard, alt, semantic HTML, colour not sole signal), XSS (`v-html` / `set:html`), loading and empty states, `rel="noopener noreferrer"`, animate only `transform`/`opacity`, `prefers-reduced-motion` kept, no leftover `console.*`, dead code |
| `frontend-vue.md` | `<script setup>`, typed `defineProps`/`defineEmits`, stable `:key`, cleanup in `onUnmounted`, `computed` over `watch`, `v-show` vs `v-if`, `defineAsyncComponent` for large/rare components |
| `frontend-inertia.md` | `useForm` for multi-field/upload forms vs `router.post` for simple actions, `onFinish` re-enables buttons, `<Link>`/`router.visit` for internal routes, multipart handled automatically for uploads (`forceFormData` only to force it), `only: [...]` partial reloads, page file name matches backend `render()`, serialisable props |
| `frontend-astro.md` | `client:*` only where hydration is needed, `Astro.cookies` is a no-op on prerendered routes, serialisable island props |
| `frontend-tailwind.md` | design tokens over hex, inline style only when dynamic, responsive prefixes, hover/focus-visible states |

### D9. Project-specific rules leave the plugin

- `backend-django.md` loses the Vietnamese-slug item; it moves to Project A's profile.
- Project A profile: theme tiers, no `:global([data-theme])` in scoped CSS, muted-text contrast floor, critical-CSS constraints, `PUBLIC_*` build-time wiring, motion tiers and easing values, OpenAPI date bump.
- Project B profile: icon library rule, `get_post_data()` helper, palette tokens, pages path, `defineOptions` name on pages, smoke modules from its testing doc.

Profiles stay under ~150 lines (existing `init-profile` rule).

### D10. `init-profile` updates

- Pack detection uses the D2 naming.
- Stack with no pack: research the stack's known pitfalls, ask the user, write the result under the profile's `<Layer> checks`. Keep only items Claude would otherwise miss.

### D11. Look things up only when there is a reason

A review does not research by default (slow, costly, non-deterministic, and generic results are the noise D4 removes). It consults sources only when:

1. the diff adds or upgrades a dependency in a manifest;
2. a finding depends on version-specific behaviour (e.g. Tailwind 4 vs 3);
3. the reviewer is unsure an API behaves as assumed.

Source order: official docs (context7 MCP when available) → changelog / migration guide → community posts, only to corroborate, never as the sole basis. A finding that relies on a lookup cites its URL.

Pack staleness: every pack starts with `Written for: <stack> <major version>`. When the project's manifest declares a newer major version, **Profile drift** reports `PACK <key> (written for <n>, project uses <m>): may be stale`. Packs are refreshed by research in this repo, reviewed by the owner, and released with a version bump, so research happens once for all projects instead of on every review.

## Out of scope (later waves)

Removing the old in-repo skills (and repointing the projects' `finish-change`, `AGENTS.md`, `CLAUDE.md`, `.cursor/README.md` and AI blueprint docs) after confirming how Cursor sees plugin skills — the owner reports Cursor already picks up a Claude Code plugin skill. Infra and docs reference files, `performance-optimization`, `finish-change`, trimming generic items from existing backend packs, Cursor support.

Known pack gaps for the owner's own repos: `frontend-nuxt` and an infra `k8s` pack.

Community release is a separate wave: packs for common non-Python/Vue stacks (React/Next, Node backends), validating D10 research on unfamiliar repos, and example output in the README.

## Acceptance

Run on the real projects, not fixtures.

1. `claude plugin validate . --strict` and `claude plugin validate ./plugins/qa --strict` pass.
2. (Run acceptance 6 first, while no profile exists.) `/qa:init-profile` drafts a profile for Project A and Project B, stops for confirmation, writes only after the user approves; each profile's `Commands` run once.
3. For each project, pick 2–3 recent commits touching backend and frontend. Run `/qa:review` and the project's old skills on the same diff, same model.
4. Pass when, per project: every CRITICAL/WARNING the old skills found is also found (or argued wrong), no extra CRITICAL false positives, and the CRITICAL + WARNING count is not higher than the old skills'; SUGGESTION counts are reported but not compared.
5. Project A drift check reports stacks from the root and `fe/` manifests, not `none`. Temporarily setting a pack's `Written for` major below the project's produces a `PACK … may be stale` line; restored afterwards.
6. Before its profile exists, `/qa:review` on Project A asks the D3 question with the root and `fe/` stacks filled in and stops; it does not start reviewing in the same turn (check 3 runs, since an earlier confirmation gate was skipped once).
7. Both the old in-repo skills and `/qa:review` stay installed and their descriptions overlap; comparisons invoke each explicitly by name. Nothing is deleted from the projects in wave 1.

## Docs in this repo to update

`README.md` (skill name, layout, status), `CLAUDE.md` (layout, stale "nothing committed" line, open work), `docs/architecture.*` (skill name), `plugin.json` version and keywords.

## Results (2026-10-05)

Model `sonnet`, headless, working copy via `--plugin-dir`. Backend test suites were not run in any review (no database running); lint, format, and frontend tests were.

| # | Acceptance item | Result |
|---|---|---|
| 1 | `validate --strict` (both), `check-plugin.py` | pass |
| 2 | `init-profile` on A and B stops for confirmation, writes nothing | pass (both). Profiles written after owner approval; every non-database command ran and passed; backend tests not run (no database) |
| 3–4 | Side by side, 2 commits per project, old skills vs `/qa:review` | First pass: 1 missed WARNING (a test that cannot fail), a11y and convention WARNINGs graded down to SUGGESTION, one false library claim, one wrong drift line. After one wording pass (below), re-runs: every old CRITICAL/WARNING found or argued (one pre-existing ordering issue graded SUGGESTION with reason; convention findings graded SUGGESTION by the table, liftable by an override). No CRITICAL false positives. One extra WARNING on a past commit came from judging it against the current tree; rule added, not re-run |
| 5 | Drift on A reports manifests, not `none`; stale pack | drift `none` on correctly listed stacks (3 runs). Stale detection needed three wording passes; the final run emits `PACK django (written for 5, project uses 6): may be stale` (1 run). The `Packs:` line still shows `?` for some frontend packs whose version is in `fe/package.json` |
| 6 | No profile → asks and stops | 3/3 asked with detected stacks, no Verdict |
| 6b | `--no-ask` without profile | pass (Verdict, no question, layers `assumed`); also commented on an out-of-layer file |
| — | Severity override (Review Focus 5) | 2/2 runs graded the overridden finding exactly at the override level |
| — | Overlapping layout `.` + `frontend/` (Review Focus 1) | `.vue` files reviewed as frontend in all Project B runs |
| 7 | Nothing deleted from the projects | pass |

Wording changes made during acceptance: tests-can-fail item (backend, frontend); accessibility examples and a no-downgrade rule in severity; keys already in `stacks` are never drift; keys without a pack are listed in `stacks`; lookups check the installed package first and never trust project docs about a library; commits are judged at their own tree; drift ends with a `Packs:` line and checks lockfiles for transitive versions.

Cost: about 20 runs, $0.17–0.50 each.
