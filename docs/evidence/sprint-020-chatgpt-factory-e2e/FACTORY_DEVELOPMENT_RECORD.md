# Sprint 6 Factory Development Mode record

## Authority and boundary

- Epic: AI Bridge Factory Readiness Remediation
- Sprint: 6 — Complete ChatGPT → Factory End-to-End Proof
- Authority: explicit Product Owner Factory Development Mode authorization.
- Repository and branch: `zsambokia/ai-bridge`, `main`.
- Baseline: `ffd4e1f98cee5c1b99a3481ebe7121ae9c08a22f`.
- Scope: only sections 43–46 of
  `docs/epics/factory-readiness-remediation.md`. Sprint 7–8 are excluded.

## Durable execution log

1. Read the Constitution, evidence-driven workflow, exact Sprint 6 scope, and
   the referenced orchestration, MCP, delivery, deployment, AKB and ChatGPT
   connection context before any mutation.
2. Confirmed `main` and `origin/main` were both bound to the baseline before
   this Sprint started. Pre-existing modified recovery/scope files and
   untracked local runtime/configuration/work-item files remain deliberately
   excluded.
3. Performed a secret-free staging preflight against
   `https://stage.artificial-software-factory.com/mcp/`: an unauthenticated
   JSON-RPC request failed closed with `401` and the Bearer challenge; an
   authenticated `initialize` and `tools/list` request using the locally
   configured credential succeeded without recording the credential. The
   endpoint advertised protocol `2025-03-26`, tool-surface version
   `2026-07-31.3`, and 83 governed tools.
4. `factory.get_status` returned two ready projects, including
   `ai-bridge` / `zsambokia/ai-bridge`; this is endpoint evidence, not evidence
   of a ChatGPT Business UI invocation.
5. The staging `/health/` response was `200` but reported an empty
   `build_sha`. Therefore the running remote deployment cannot currently be
   bound to the accepted baseline or to a Sprint 6 delivery artifact.
6. Inspected the actual public transport. It authenticates a single static
   Bearer credential and hashes that credential for its caller binding. This
   provides credential binding without secret disclosure, but cannot by itself
   distinguish a ChatGPT Business UI tool call from another holder of the same
   credential.
7. Used the designated in-app-browser integration to locate a ChatGPT Business
   session. No browser instance was available in this execution environment.
   The workspace-admin UI required by the canonical connection procedure is
   consequently unavailable to this Factory Development Mode process.
8. Repaired the remote deployment identity by running a clean detached
   checkout at `89938b662e2bb757110aee0d1cffecfe524c5c23`, applying the three
   pending `projects` migrations to the local staging database, and starting
   the runtime with that immutable build SHA. The previous runtime launch
   initially failed local readiness because the explicit host list omitted
   `127.0.0.1`; the corrected launch added only that local verification host.
9. The first canonical public deployment verification received a `403` from
   the edge because Python's default user agent was rejected. The verifier was
   repaired with explicit JSON accept and named user-agent headers, covered by
   a focused test, then all 224 tests and repository gates passed. The repaired
   verifier subsequently passed health, migration, dependency, worker, and
   scheduler checks against staging. An authenticated post-deploy MCP
   `factory.get_status` request also returned the two-project READY registry.

## Current evidence boundary

The remote endpoint is reachable, fail-closed, SHA-bound to
`89938b662e2bb757110aee0d1cffecfe524c5c23`, authenticated, and exposes the
governed registry. It does **not** yet prove the mandatory Sprint 6 fact:

- that the request originated from the actual configured ChatGPT Business
  connection and completed the required governed Factory chain.

That fact must remain unclaimed until the configured ChatGPT Business app is
available and its UI request can be observed end-to-end against this runtime.
