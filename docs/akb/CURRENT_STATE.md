# AI Bridge – Current State

## Repository

- Repository: `zsambokia/ai-bridge`
- Development branch: `main`
- Canonical Bridge Constitution: `docs/constitution/BRIDGE_CONSTITUTION.md`

## Implemented foundation

The Django 5.2 foundation contains split settings, SQLite configuration, the
`core` health endpoint, and the canonical `projects` domain. The latter
provides one Project Registry model, onboarding readiness (`PENDING`, `READY`,
`INVALID`), a static `.bridge/project.yaml` loader, the constrained
`bootstrap_project` command, and Project Context validation (`VALID`,
`INVALID`, `STALE`).

The Project Definition is static configuration. Lifecycle, onboarding, Context,
and capability state are runtime data and are not written back to YAML.

## Verified current execution

Sprint 003 bootstrap was run against this repository's own Project Definition.
It created the canonical `ai-bridge` Registry record with onboarding `READY`
and a first `VALID` Project Context. The result is runtime data in the local
Django database, not a fixture or seed.

The same canonical bootstrap was also proven against the persistent, independent
`zsambokia/bridge-demo` repository. Its `bridge-demo` Registry record remains
`READY`; its current Context is `VALID`, and its earlier source revision is
preserved as `STALE`. The local development database therefore contains exactly
the `ai-bridge` and `bridge-demo` Registry records. Django Admin exposes both
runtime models as read-only operational views; it cannot create, change, or
delete them outside the canonical bootstrap lifecycle.

## Implemented execution foundation

Sprint 004 adds a lightweight, registered MCP transport at `POST /mcp/` to the
canonical `projects` domain. It resolves only active ready Registry records,
persists ambiguous-resolution candidate state behind a continuation token, and
requires the caller to choose a listed `project_id` before continuation.

The same domain now constructs a canonical, structured Execution Context from a
Project, its valid Project Context, `.bridge/project.yaml`, and an explicit
approved Sprint path. The Context includes repository, branch, exact baseline,
binding documents, release gates, evidence root, allowed terminal states, and a
unique execution identifier. It is the source for the MCP response and Codex
execution package; Markdown contracts are representations rather than the
canonical object.

Sprint 005 adds the canonical `ExecutionContract` persistence model and the
generate, validate, issue, retrieve and render lifecycle through the same MCP
surface. Issued payloads are immutable, have reproducible SHA-256 hashes, bind
their governance documents and baseline commit, and render human handoffs only
from stored data. The generator successfully issued the required Sprint 004
contract from baseline `14ce5ff7f1c6e5739d7aa83044529e9d6d55b1e7`.

The scope intentionally does not add AKB indexing, vector search, Discovery,
autonomous planning, or a large user interface.

## Next approved action

Use the canonical Execution Contract Generator to issue the approved contract
for the next sprint before its execution begins.
