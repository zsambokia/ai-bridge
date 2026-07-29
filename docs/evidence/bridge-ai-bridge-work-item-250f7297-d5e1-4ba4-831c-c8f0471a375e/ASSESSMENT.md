# Extended assessment — Sprint 1 factory E2E technical remediation

## Contract binding

- Contract: `bridge:ai-bridge:contract:0138cf9b-02d9-4cef-85ac-8d62fa42028c`
- Approved work item: `bridge:ai-bridge:work-item:250f7297-d5e1-4ba4-831c-c8f0471a375e`
- Approved scope hash: `cc3e1b8c5b77b70201c8568c35a388d79806a5453f4f4c0e7cc7b16a3cd64797`
- Contract hash: `d1fad4b68d91bf551ea0b857c1753d29ffad03448ec49fe08d73442a1c5592a3`
- Baseline: `88dc5d9b7be8c3adef05db2d1a7408fe228a851d` on `main`.

## Diagnosis and repair

The previous run had a stale worker lease and no workspace binding because the
canonical `projects.0031` and `projects.0032` migrations had not been applied.
Those migrations were applied using `manage.py migrate --noinput`; no database
table or row was manually edited. Recovery now retains bounded retry state in
existing job metadata, restarts from the approved authority when no checkpoint
exists, resets stale workspace/provider fields, and heartbeats the claimed job.
Provider callbacks preserve the raw structured event while projecting canonical
activity, source-tree, validation, and completion events.

No persistent model or migration was added. The `ExecutionRunAdmin` changelist
now presents its durable `Run ID` as the first data column, covered by a
regression test.

## Clean governed E2E

Run `31` used the real authenticated MCP/API execution flow and the isolated
workspace `C:/Users/User/Documents/dev/.ai-bridge-workspaces/2e7c1551-f5ce-41cf-8e96-1c56a2c49e5c/repository`.
Its workspace record proves an isolated clone, virtual environment, runtime
SQLite database, and applied migration state. The persisted event stream includes
`WORKSPACE_READY`, `PROVIDER_STARTED`, repeated `PROVIDER_ACTIVITY_RECEIVED`,
`SOURCE_TREE_CHANGED`, `VALIDATION_STARTED`, `VALIDATION_COMPLETED`, and
`PROVIDER_COMPLETED`; it also contains worker heartbeat events through provider
exit. The provider exited successfully (`exit_code: 0`).

The provider's claim that its own sandbox could not write `.git` metadata was a
technical execution limitation, not an external Product Owner input. The bridge
executor created the required local commit binding after the provider completed.

## Result

All resolved release gates pass. Canonical scope documents were republished from
their existing authoritative records where projections were missing, then the
scope gate was rerun. This is a repository consistency repair, not a new scope
or a manual database operation. A post-closure validation repair now preserves
the published content hash on new terminal scope records and accepts the
historical immutable contract binding for legacy terminal records; it introduced
no model, migration, or manual database change.
