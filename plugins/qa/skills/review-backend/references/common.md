# Common backend checklist

Language- and framework-agnostic. Report only items the change affects.

## 1. Coding standards

- [ ] **Types**: Public functions have parameter and return types.
- [ ] **Naming**: Domain names, not `data`/`temp`/`x`. Constants named, not magic numbers.
- [ ] **Size**: No function/module that grew past the point of one responsibility; split by responsibility, not by line count alone.
- [ ] **Dead code**: No unused imports, unreachable branches, commented-out code.
- [ ] **Logging**: Logger with structured context (event + ids), not `print()`. No secrets, tokens, PINs, or raw personal data in logs or exception messages.
- [ ] **Docstrings/comments**: Public APIs say what they do and what they raise. Comments explain *why*, not what. A docstring or comment that describes the old behavior after the change is a contract bug (WARNING).

## 2. DRY & single source of truth

- [ ] **One implementation per rule**: Validation, status transitions, permission checks live in one place; the change doesn't re-implement them elsewhere.
- [ ] **Enums, not string literals**: Statuses/types use the shared enum/constant.
- [ ] **Config**: Read through the project's config accessor; defaults defined once.
- [ ] **Errors**: Domain exception classes defined once; no bare `raise Exception("...")`.

## 3. Business logic

- [ ] **Correctness**: Matches the requirement/spec/doc the change cites.
- [ ] **Edge cases**: Null/empty input, missing records, duplicates, boundary values (off-by-one on dates, `<` vs `<=`), unexpected enum values (fail closed).
- [ ] **Atomicity**: Multi-step writes in one transaction; no partial write on failure.
- [ ] **Concurrency**: State-machine transitions and counters guarded (row lock, conditional update, unique constraint) against concurrent writers.
- [ ] **Idempotency**: Retried operations (jobs, webhooks, batch inserts, resumable work) are safe to run twice.
- [ ] **Resume safety**: Interrupted long-running work can be picked up again without skipping or duplicating items.

## 4. API / interface boundary

- [ ] **Status codes**: Correct HTTP codes (200/201/204, 400, 401 vs 403, 404, 409, 422, 5xx); never "always 200 + error in body".
- [ ] **Error shape**: Consistent, minimal, no stack traces or internals to the client.
- [ ] **Validation at the boundary**: Input validated where it enters (serializer/schema); domain layer receives typed values.
- [ ] **Lists**: Paginated or bounded.
- [ ] **Auth by default**: New endpoints/tools require auth and an explicit permission check.
- [ ] **No business logic in handlers**: Handler validates → calls service → shapes response.
- [ ] **Schema docs**: OpenAPI/schema updated when the contract changes, including error responses.

## 5. Security

- [ ] **Secrets**: From env/secret store only; nothing committed (`.env`, keys, license files are gitignored).
- [ ] **Injection**: No string-built SQL, shell commands, or file paths from user input.
- [ ] **Path handling**: User-supplied paths validated/resolved; no traversal outside the allowed root.
- [ ] **Authorization on every id**: Any id that comes from outside is looked up scoped to the caller (owner/tenant/project), not fetched globally.
- [ ] **No probing oracle**: "not found" and "not yours" return the same response.
- [ ] **Crypto**: Library primitives with recommended parameters; verification failures raise, not return a bool that callers can ignore.
- [ ] **Sensitive data at rest**: Credentials hashed or encrypted; plaintext shown once at most.

## 6. Performance

- [ ] **N+1**: No per-row queries inside loops over related objects.
- [ ] **Bulk**: Bulk insert/update instead of per-row loops on batch paths.
- [ ] **Unbounded loads**: No loading a whole table/file into memory on a path that can grow; stream or paginate.
- [ ] **Indexes**: Columns used in new filters/joins/order-bys are indexed.
- [ ] **Resources**: Connections, sessions, file handles, device sessions closed in `finally`/context managers.
- [ ] **Heavy work**: Offloaded to a background job when one exists.

## 7. Testing

- [ ] **Runs**: Tests pass with the project's runner (see profile `Commands`).
- [ ] **Changed critical paths tested**: Auth/permission, state transitions, money/data-integrity paths have explicit tests.
- [ ] **Failure paths**: Not only the happy path — invalid input, blocked/forbidden, external failure, retry/resume.
- [ ] **Isolation**: Each test owns its data (fixtures/temp dirs); no shared mutable state or writes into the repo.
- [ ] **Mocks at the edge**: External services/devices mocked; follow the project's rule on whether the DB is real or mocked.
- [ ] **Slow/hardware tests marked**: Tests needing real devices/services are tagged and skippable in CI.
