# Django stack pack (performance)

Written for: Django 6

- [ ] **Related objects**: `select_related` for foreign keys and one-to-one, `prefetch_related` for many-to-many and reverse relations; serializer fields and template loops are checked for hidden per-row queries.
- [ ] **Columns**: `.only()` or `.defer()` when a wide model is read for a few fields; `.values()` or `.values_list()` when model instances are not needed.
- [ ] **Counting and existence**: `.exists()` instead of `len(qs)` or `bool(qs)`; `.count()` instead of `len(qs)` when rows are not used.
- [ ] **Bulk operations**: `bulk_create`, `bulk_update`, and `QuerySet.update` instead of save in a loop; `.iterator()` for large read-only scans.
- [ ] **Pagination**: List views and DRF viewsets set a pagination class or a slice; admin `list_display` that follows relations sets `list_select_related`.
- [ ] **Connections**: Persistent connections (`CONN_MAX_AGE`) or a pooler are configured for production; no connection opened per call in a loop.
- [ ] **Query plan**: `queryset.explain()` is read for the slow statement before an index is added.
