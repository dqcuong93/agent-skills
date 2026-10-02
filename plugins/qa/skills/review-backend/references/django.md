# Django / DRF stack pack

## Models & DB
- [ ] **Migrations**: Model changes ship with a migration; migration is reversible or explicitly irreversible; no data migration mixed with a large schema change without reason.
- [ ] **Transactions**: Multi-step writes in `transaction.atomic()`.
- [ ] **Concurrent state changes**: Status transitions (claim/unclaim, job state) use `select_for_update()` inside a transaction, or a conditional `update()`.
- [ ] **N+1**: `select_related` (FK/one-to-one) / `prefetch_related` (reverse/M2M) when iterating related objects, including in serializers and templates.
- [ ] **Bulk**: `bulk_create` / `bulk_update` / `QuerySet.update()` instead of save-in-loop.
- [ ] **Constraints in the DB**: Uniqueness and invariants as `UniqueConstraint`/`CheckConstraint`, not only in Python.

## Views & API
- [ ] **Thin views**: Views validate → call service (`services.py`) → respond. No business rules in views/serializers.
- [ ] **Serializers at the boundary only**: Service layer takes/returns domain types (dataclasses/models), not serializers.
- [ ] **Permissions explicit**: `permission_classes` declared on every ViewSet/APIView; don't rely on global defaults alone.
- [ ] **Querysets scoped**: `get_queryset()` filters by the requesting user/tenant; detail lookups go through it.
- [ ] **401 vs 403**: Know which the auth stack returns for unauthenticated requests (e.g. JWT before Session → 401) and assert it in tests.
- [ ] **OpenAPI (drf-spectacular)**: `@extend_schema(responses={200: S, 404: OpenApiResponse(...)})` dict form; error responses declared; ViewSet actions annotated via `@extend_schema_view`.
- [ ] **Pagination** on list endpoints.

## Inertia (when used)
- [ ] **Props minimal and serializable**; no ORM objects or secrets in props.
- [ ] **Shared data** via middleware only for data every page needs.
- [ ] **Request body parsing** through the project's single helper (JSON vs multipart), not ad hoc `request.POST`/`request.body`.

## Security & config
- [ ] `python manage.py check --deploy` passes for production settings.
- [ ] `SECRET_KEY`, DB credentials, API keys from env.
- [ ] No `DEBUG=True` or `ALLOWED_HOSTS=['*']` reachable in production settings.
- [ ] No `raw()`/`extra()`/cursor SQL built from user input.

## Background work
- [ ] Heavy/slow work offloaded (Celery/RQ/etc.) when available; tasks idempotent and pass ids, not model instances.

## i18n / Vietnamese data
- [ ] **Slugs for closed sets**: Don't derive keys by stripping diacritics when it causes collisions (e.g. `Tý`/`Tỵ` → `ty`); use explicit `TextChoices` mapping, kept in sync with the frontend.
