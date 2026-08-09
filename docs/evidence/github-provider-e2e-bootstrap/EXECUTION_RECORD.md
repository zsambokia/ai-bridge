# GitHub Provider E2E Bootstrap — Execution Record

## Authority and scope

- Mode: Product Owner Factory Development Mode for AI Bridge self-development.
- Scope: create a new `zsambokia/ai-bridge-bootstrap-e2e-<timestamp>` repository
  through the AI Bridge GitHub provider, then prove provider-only bootstrap,
  AKB intake, semantic retrieval, runtime readiness, and incremental update.
- Baseline recorded before this Factory Development Mode work:
  `bf6f886bb5a08187eafb9cccd02b662ff9856f66` on `main`.
- Local Git, `gh`, VS Code authentication, and credential-manager
  authentication were not used for GitHub access.

## Implemented provider boundary

The canonical `projects.providers.GitHubAdapter` now provides these
provider-bound operations:

- branch state read;
- organization repository creation;
- repository contents create/update; and
- commit/ref comparison.

Every successful remote request records a `ProviderAuditEvent` containing the
HTTP method, endpoint path, provider credential-binding reference, and the
authentication mode `PROVIDER_ENVIRONMENT_BINDING`. Credential values and
request authorization headers are never persisted. Repository selection is
exact-identity and capability-gated through `select_repository_provider`; no
fallback credential source exists.

## Preflight evidence

The canonical `github` provider was inspected locally without a remote request.
At inspection it was:

| Field | Observed value |
| --- | --- |
| kind / role | `GITHUB` / `REPOSITORY_SERVICE` |
| adapter key | `github` |
| status | `ACTIVE` |
| enabled | `False` |
| capabilities | `REPOSITORY_READ`, `REPOSITORY_WRITE`, `BRANCH_MANAGEMENT`, `PULL_REQUEST_MANAGEMENT`, `HEALTH_CHECK` |
| credential binding | absent (empty) |

Presence-only checks also found no `GITHUB_TOKEN`, `GH_TOKEN`, or
`GITHUB_API_TOKEN` environment variable. No values were read or emitted.

## Result

`BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE`

No repository creation request was sent. Sending it would require bypassing
the mandated provider-credential boundary, which this implementation does not
permit. Accordingly, there is no invented repository URL, repository ID,
remote commit, webhook, or E2E PASS evidence.

## Exact next action

An authorized secure operator must configure and enable the existing canonical
`github` `ExecutionProvider` with a provider-owned credential binding (for
example `AI_BRIDGE_GITHUB_PROVIDER_TOKEN`) and make that binding available only
to the AI Bridge process. The credential must authorize organization repository
creation and contents writes for `zsambokia`.

After that external configuration is present, rerun the E2E bootstrap using
the canonical GitHub adapter. It must create a fresh timestamped repository,
record the provider audit events, and then execute the remaining bootstrap,
incremental-update, runtime, and reproducibility proofs against that real
repository.

## Local validation from the final workspace state

- `python -m pytest -q` — PASS (`369 passed`)
- `ruff check .` — PASS
- `mypy .` — PASS (`248 source files`)
- `python manage.py validate_scopes` — PASS
- `python manage.py makemigrations --check --dry-run` — PASS
- `git diff --check` — PASS (local whitespace check only; no remote Git
  operation or GitHub authentication was used)
