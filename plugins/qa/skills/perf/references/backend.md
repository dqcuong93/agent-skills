# Backend performance checklist

Framework-agnostic. Report only items the path can reach.

## 1. Measurement

- [ ] **A number first**: Latency (p50 and p95), query count per request, and memory are recorded before any change; a fix without a baseline cannot be shown to help.
- [ ] **Profile, not guess**: A profiler or the query log is used to find the hot function or statement before code is rewritten.

## 2. Database

- [ ] **N+1**: Related rows are fetched by one query or one join, not by a query per parent row.
- [ ] **Bounded results**: Every list query has a limit or pagination; no endpoint returns an unbounded table.
- [ ] **Columns and rows**: Wide rows are not loaded when two fields are used; counts and existence checks run in the database, not by loading rows.
- [ ] **Bulk writes**: Multiple inserts or updates use one bulk statement, not a statement per row.
- [ ] **Indexes**: Columns used in filters, joins, and ordering on large tables are indexed; check the query plan for the slow statement.
- [ ] **Query count**: The number of queries per request is small and does not grow with the number of rows returned.

## 3. Work per request

- [ ] **Blocking calls**: A network or disk call in the request path has a timeout, and slow work moves to a background job.
- [ ] **Repeated work**: The same computation or lookup is not repeated inside a loop or on every request when it can be computed once.
- [ ] **Payload size**: Responses carry only the fields the caller uses; large serialisation is not done in a loop with per-item queries.

## 4. Caching and background work

- [ ] **Cache with an owner**: A cache entry has a key, a lifetime, and an invalidation rule; stale data after a write is a bug, not a trade-off.
- [ ] **Jobs**: Long work runs in a worker, is safe to retry, and reports failure.
