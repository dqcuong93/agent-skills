# Python stack pack

- [ ] **Version idioms**: Matches the project's Python version. `X | None`, `list[str]`, `dict[str, Any]`; no `Optional`/`Union`/`List`/`Dict` from `typing` on 3.10+. `match/case` where it clarifies branching.
- [ ] **Return types explicit**: Including `-> None`.
- [ ] **Lint/format**: `ruff check` and `ruff format --check` (or the project's toolchain) pass on changed files.
- [ ] **Type check**: mypy/pyright clean on changed files when the project runs one.
- [ ] **Import boundaries**: Layer rules (e.g. import-linter contracts) still pass; lower layers don't import upper ones.
- [ ] **Exceptions**: Catch specific exceptions; no bare `except:` or `except Exception: pass`. Re-raise with `from err`.
- [ ] **Mutable defaults**: No `def f(x=[])` / `{}` defaults.
- [ ] **Dataclasses/Pydantic for domain values**: Service layer returns typed objects, not loose dicts.
- [ ] **Context managers**: Files, locks, sessions, connections opened with `with`.
- [ ] **Datetime**: Timezone-aware datetimes; no naive `datetime.now()` for stored timestamps.
- [ ] **Tests**: pytest fixtures shared from one `conftest.py` per scope as the project defines; `tmp_path` for files; markers for integration/hardware tests.
