# SQLAlchemy stack pack

Written for: SQLAlchemy 2

- [ ] **Typed models**: `Mapped[...]` / `mapped_column(...)`; no legacy `Column` declarations in new models.
- [ ] **Mutation through services**: Fields changed only inside the owning module's service functions, so immutability/append-only rules hold.
- [ ] **Flush vs commit**: Service functions `session.flush()` so ids/defaults are available; the caller (request scope, job, test fixture) owns `commit()`/rollback.
- [ ] **Versioning over overwrite**: When the domain says history matters, write a new row/version instead of mutating content in place.
- [ ] **Hybrid schema**: Fields used in filters/FKs/constraints are typed columns; free-form content in JSON/JSONB columns. Don't hide queryable data in a JSON blob.
- [ ] **Constraints**: Uniqueness rules as `UniqueConstraint`, and every caller-chosen key's constraint includes the tenant/project column.
- [ ] **Loading strategy**: Explicit `selectinload`/`joinedload` when iterating relationships; no lazy loads inside loops.
- [ ] **Bulk**: `session.execute(insert(Model), rows)` / `update()` for batch writes.
- [ ] **Scoped lookups**: Ids from outside fetched with a tenant/project-scoped query, never bare `session.get(Model, id)`.
- [ ] **Tests on a real DB** when the project chooses that (savepoint-per-test fixture); don't introduce mocked sessions into such a suite.
