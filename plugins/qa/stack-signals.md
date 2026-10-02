# Stack signals

Single source for mapping a project's dependencies to stack keys. Used by `init-profile` (to draft `stacks`) and `review-backend` (to detect drift).

A stack key has a **pack** when a file `<key>.md` exists under any `skills/*/references/`. Keys without a pack are still reported by name so the user knows they are unreviewed.

Match a signal case-insensitively against dependency names in `pyproject.toml`, `requirements*.txt`, and `package.json`. Ignore dependencies that match no row.

| Stack key | Signals (dependency names) |
|---|---|
| `python` | any `pyproject.toml`, `requirements*.txt`, or `setup.cfg` |
| `django` | `django`, `djangorestframework`, `drf-spectacular`, `django-inertia`, `inertia-django` |
| `fastapi` | `fastapi`, `starlette` |
| `sqlalchemy` | `sqlalchemy`, `sqlmodel` |
| `pydantic` | `pydantic`, `pydantic-settings` |
| `celery` | `celery` |
| `temporal` | `temporalio` |
| `pgvector` | `pgvector` |
| `pyqt` | `pyqt5`, `pyqt6`, `pyside2`, `pyside6` |
| `vue` | `vue`, `@inertiajs/vue3` |
| `astro` | `astro` |
| `tailwind` | `tailwindcss` |
| `docker` | a `Dockerfile` or `docker-compose*.yml` at the project root |
