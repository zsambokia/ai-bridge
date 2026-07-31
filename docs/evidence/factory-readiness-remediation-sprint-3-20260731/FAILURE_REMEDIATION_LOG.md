# Sprint 3 failure and remediation log

This log intentionally retains failed attempts; none were removed from the
acceptance story.

| Detection | Diagnosis | Repair | Verification |
| --- | --- | --- | --- |
| Focused tests raised `NameError` during gate opening. | A contract-type guard was inserted in `open_gate` before `contract` existed. | Removed the misplaced guard and restricted the persistence guard to the runtime binding path. | Focused tests passed. |
| Legacy unit path failed when a `SimpleNamespace` was assigned to a durable FK. | Compatibility test doubles are not Django model instances. | Persist contract/run consumers only for actual model instances; preserve the canonical durable path. | Orchestration regression tests passed. |
| Remote MCP rejected the new retrieval intent and query. | Public tool schema had not yet declared the new fields. | Added and forwarded the two schema fields. | Real HTTP MCP context call succeeded. |
| A real queued run was absent from context usage. | The binding happened in `start_run`, but the governed lifecycle creates the durable run in `enqueue_run`. | Bound `KnowledgeContextUse.execution_run` at queue creation as well. | Remote MCP lifecycle test and live runtime showed run ID `2`. |
| First controlled runtime fixture could not resolve the registry project. | Fixture project ID differed from the static project definition. | Rebuilt the isolated runtime with the canonical `ai-bridge` project ID. | Fresh governed session completed. |
| Product-decision knowledge was not retrieved in the controlled fixture. | The fixture omitted the `is_must_know` classification required by the retrieval rule. | Corrected the fixture and reran on a fresh scope. | Context package `5` included source version `po-runtime-1`. |
| First live roadmap call was rejected. | Client omitted JSON-RPC envelope, then used outdated field names. | Used MCP `tools/call` JSON-RPC and the published `engineering_status` / `operational_status` schema. | Candidate review and canonical `COMPLETED` projection succeeded. |
| A final formatting check reported legacy files under an untracked Sprint 2 runtime workspace. | A repository-root formatter traversal included user-owned, untracked operational artifacts rather than only the governed Git change set. | Kept those artifacts untouched and ran formatting verification against the staged Sprint 3 Python files. | Scoped formatter check passed; repository lint, tests, types, Django checks, and scope validation were rerun. |

All repairs were followed by the affected focused or runtime validation, then
the final full Release Gates.
