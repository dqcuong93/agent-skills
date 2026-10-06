# Infra checklist

Tool-agnostic. Report only items the change affects. Tool-specific rules are in the `infra-<stack>.md` packs; rules for one project are in the profile's `Infra checks`.

## 1. Secrets and env

- [ ] **No secret literals**: No credential, token, key, or password value in any tracked file (compose `environment:`, scripts, Dockerfile `ENV`/`ARG`, CI files). Values come from untracked env files or a secret store.
- [ ] **Env files untracked**: Real `.env*` files are gitignored; only `*.example` files are tracked, with placeholder values.
- [ ] **Env example in sync**: Every variable the config reads exists in the example env file; a variable the change removes is removed there too.

## 2. Change safety

- [ ] **Validated before reload**: The config is checked with the tool's own validator before a reload or deploy. If the profile names the command, run it.
- [ ] **Reload, not restart**: Where the tool supports a graceful reload, the procedure uses it instead of a restart that drops connections.
- [ ] **Revertible**: The change is undone by reverting one commit. No step depends on an edit made by hand on the host.
- [ ] **Scripts fail loudly**: Shell scripts stop on error (`set -e` or `set -euo pipefail`), quote variable expansions, and never run `rm -rf` on a path built from an unchecked variable. Running the script twice is safe.

## 3. Exposure

- [ ] **Published ports**: Only the public entrypoint publishes a port. Databases and caches stay on the internal network or bind to `127.0.0.1`.
- [ ] **Privilege**: No `privileged: true`, no container-runtime socket mounted into an app container without a restricting proxy, no root user without a reason in a comment.
- [ ] **Logs**: Config does not log request bodies, tokens, or other secrets; log rotation or a size limit exists for long-running services.
