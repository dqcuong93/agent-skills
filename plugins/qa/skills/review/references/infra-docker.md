# Docker and Compose stack pack

Written for: Docker Compose 2

## Compose

- [ ] **Health checks**: A service that others wait on has a `healthcheck`, and dependents use `depends_on` with `condition: service_healthy`. A service that is the only instance behind a proxy has none, because a flaky check would mark the only upstream down.
- [ ] **Restart policy**: Long-running production services set `restart: unless-stopped` or `always`; one-shot jobs set `"no"` or `on-failure`.
- [ ] **Resource limits**: Production services that can grow (workers, renderers, databases) set memory and CPU limits so one container cannot starve the others.
- [ ] **Volumes**: Persistent data lives on a named volume or bind mount, not the container layer. Services that share files mount the same source at the paths their configs expect. A mount the service never writes to is `:ro`.
- [ ] **Networks**: Services reach each other by service name on the compose network, not through published host ports.
- [ ] **Image tags**: Images are pinned to at least a major version; `latest` is not used for anything that gets deployed.
- [ ] **Validation**: `docker compose config -q` passes for every compose file the change touches (run it when the profile allows).

## Dockerfile

- [ ] **Layer cache**: Dependency manifests are copied and installed before the source is copied, so a source edit does not reinstall dependencies.
- [ ] **Multi-stage**: Build tools and dev dependencies stay out of the final image.
- [ ] **Non-root**: The final stage sets a non-root `USER`.
- [ ] **No secrets in layers**: No secret in `ENV`, `ARG`, or a copied file; `.dockerignore` excludes env files, VCS data, and local dependency directories.
- [ ] **Reproducible base**: The base image tag is pinned to at least a major version.
