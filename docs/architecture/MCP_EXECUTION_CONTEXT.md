# MCP Execution Context Foundation

Sprint 004 extends the canonical `projects` domain; it does not create a
second Registry, Context store, or AKB system.

```text
Project Registry + Project Context + .bridge/project.yaml + approved Sprint
                                 ↓
                         Execution Context
                                 ├── MCP response
                                 ├── Codex execution package
                                 ├── Markdown contract (future rendering)
                                 ├── audit record (future persistence)
                                 └── future agent context
```

`POST /mcp/` is the small JSON transport adapter. `list_operations` exposes
the registered operations. Alongside Project resolution and
`generate_execution_context`, it exposes the contract lifecycle operations
`generate_execution_contract`, `validate_execution_contract`,
`issue_execution_contract`, `get_execution_contract`, and
`render_execution_handoff`.

`resolve_project` only searches active, ready Registry records. A single match
returns `PROJECT_RESOLVED`; multiple matches return `USER_INPUT_REQUIRED` with
candidate records and a UUID continuation token. The candidates are persisted
in `ProjectResolutionContinuation`; `continue_project_resolution` consumes the
same record only when the caller selects one of its candidate IDs.

`generate_execution_context` requires explicit `project_id` and
`approved_sprint_path`. It validates the Project, valid Project Context, static
definition, repository identity, and approved Sprint marker. Its structured
response exposes `execution_context` and `codex_execution_package` as two
names for the very same canonical object. It includes the target repository
and branch, Context source commit as the exact baseline, binding governance
paths, release gates, deterministic evidence root, allowed terminal states,
and an execution ID. No value comes from chat memory or an inferred active
project/sprint.

`ExecutionContract` is the durable canonical handoff record. Generation resolves
the current repository baseline, bindings and hashes; validation re-resolves
those inputs; issuance makes the payload immutable and rejects evidence-root
collisions. Human-readable handoff Markdown is rendered only from that stored
payload, so it cannot drift from the issued contract.
