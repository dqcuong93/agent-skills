# Caddy stack pack

Written for: Caddy 2

## Routing

- [ ] **Route order**: Within a site block, `handle` blocks are tried in the order written. A narrow path must come before a broad one (`/api/special` before `/api/*`), or the broad block shadows it.
- [ ] **No duplicate handlers**: The same path is not matched by two blocks with conflicting behaviour.
- [ ] **Snippets**: Repeated `reverse_proxy` options are factored into a `(snippet)` and imported, not pasted per route.
- [ ] **Single upstream health checks**: A route with one upstream has no active health check; a flaky check would take the only instance out of rotation.

## Headers

- [ ] **One owner per header**: A top-level `header` directive runs before `reverse_proxy` and sets a value; the proxy then adds the upstream's own value for the same name, so the client sees two. Pick one place to own each header.
- [ ] **Override upstream values**: To force a value regardless of what the upstream sends, use `header_down <Name> "<value>"` inside `reverse_proxy`; it runs after the response arrives and replaces the value.
- [ ] **Verified, not assumed**: When a header changes, check it with `curl -sS -D - -o /dev/null <url>`: each header name appears once. Two lines of the same name is this bug.

## Caching

- [ ] **Hashed assets**: Content-hashed file names get a long `max-age` plus `immutable`.
- [ ] **Unhashed static files**: A moderate `max-age`, optionally with `stale-while-revalidate`; never `immutable`.
- [ ] **HTML and CDNs**: Many CDNs do not cache HTML unless a rule says so, whatever `Cache-Control` the origin sends. A change that expects HTML to be edge-cached needs that rule, not only a header.
- [ ] **Purge after deploy**: If anything caches the output (browser, CDN, proxy), the deploy procedure names the purge step.

## TLS and clients

- [ ] **Site addresses**: Production site blocks name explicit hostnames. `auto_https off` and `tls internal` need a comment saying why.
- [ ] **Ports**: 80 and 443 (TCP, and UDP for HTTP/3) are reachable for certificate issuance and renewal.
- [ ] **Client IP behind a proxy or CDN**: When another proxy sits in front, `trusted_proxies` is set deliberately; otherwise the upstream sees the edge address and per-client throttling or attribution is wrong.

## Validation

- [ ] **Validated**: `caddy validate --config <Caddyfile>` passes (or the containerised equivalent); run it when the profile or the environment allows, otherwise say `not run`.
- [ ] **Formatted**: `caddy fmt --diff` shows no change for the touched file.
