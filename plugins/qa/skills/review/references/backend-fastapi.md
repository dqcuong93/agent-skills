# FastAPI / Pydantic v2 stack pack

Written for: FastAPI 0

- [ ] **Schemas**: Request/response bodies are Pydantic v2 models (`model_validate`, `model_dump`); no raw dicts across the boundary.
- [ ] **`response_model`** set so internal fields don't leak; separate input and output models when they differ.
- [ ] **Dependencies for cross-cutting concerns**: Auth, DB session, tenant resolution via `Depends`, not repeated in each route.
- [ ] **Session lifecycle**: Session dependency yields and closes/rolls back in `finally`.
- [ ] **Async correctness**: No blocking I/O (sync DB driver, `requests`, file reads) inside `async def` routes; use sync `def` or a thread pool.
- [ ] **Errors**: `HTTPException` with correct status; custom exception handlers return a consistent error shape.
- [ ] **Settings**: `pydantic-settings` (or project equivalent) reads env; no secrets in defaults.
- [ ] **OpenAPI**: `responses=` documents non-2xx responses for non-trivial endpoints.
- [ ] **Tests**: `TestClient`/`httpx.AsyncClient` with dependency overrides; auth-required routes tested without credentials.
