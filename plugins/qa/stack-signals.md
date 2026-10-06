# Stack signals

Single source for mapping a project's dependencies to stack keys. Used by `init-profile` (to draft `stacks`) and `review` (layout question and drift).

A stack key has a **pack** when a file `references/<layer>-<key>.md` exists under `skills/review/`. Keys without a pack are still reported by name so the user knows they are unreviewed.

## Manifests

Read these files to find dependencies. Search the project root and each `Layout` path from the profile; without a profile, the root and one directory down.

- `pyproject.toml` (`[project] dependencies`, `[tool.poetry.dependencies]`, `[dependency-groups]`)
- `requirements*.txt`
- `setup.cfg` (`install_requires`)
- `package.json` (`dependencies`, `devDependencies`)
- `Dockerfile*`, `docker-compose*.yml`, `compose*.yaml`, `Caddyfile*`: found by file name anywhere in the repo (Glob `**/<name>`), not only at the root. Nothing is parsed. They only suggest stack keys; where a file belongs is decided by the profile's `Layout`.

## Signals

Match a signal case-insensitively against dependency names. Ignore dependencies that match no row.

| Stack key | Layer | Signals (dependency names) |
|---|---|---|
| `python` | backend | any Python manifest above |
| `django` | backend | `django`, `djangorestframework`, `drf-spectacular` |
| `fastapi` | backend | `fastapi`, `starlette` |
| `sqlalchemy` | backend | `sqlalchemy`, `sqlmodel` |
| `pydantic` | backend | `pydantic`, `pydantic-settings` |
| `celery` | backend | `celery` |
| `temporal` | backend | `temporalio` |
| `pgvector` | backend | `pgvector` |
| `pyqt` | backend | `pyqt5`, `pyqt6`, `pyside2`, `pyside6` |
| `inertia` | frontend | `@inertiajs/vue3`, `@inertiajs/react`, `inertia-django`, `django-inertia` |
| `vue` | frontend | `vue` |
| `nuxt` | frontend | `nuxt` |
| `astro` | frontend | `astro` |
| `tailwind` | frontend | `tailwindcss` |
| `docker` | infra | a `Dockerfile*` or `docker-compose*.yml` / `compose*.yaml` anywhere in the repo |
| `caddy` | infra | a `Caddyfile*` anywhere in the repo |
