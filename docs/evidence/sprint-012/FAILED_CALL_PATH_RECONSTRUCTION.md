# Failed `APPROVAL_REQUIRED` path reconstruction

The local canonical audit record identifies the failed scope as
`bridge:ai-bridge:work-item:4b2b13a3-6ab9-4c3d-8108-99cc8e646765`.

| UTC time | Tool | Result |
| --- | --- | --- |
| 2026-07-26 19:50:49 | `work_item.propose` | `SCOPE_PROPOSED` |
| 2026-07-26 19:51:29 | `scope.approve` | `APPROVAL_REQUIRED` |

The failed affirmative interaction invoked `scope.approve`, not
`conversation.confirm`. `scope.approve` is correctly strict: it only binds an
already-existing durable approval reference. The scope therefore remained
`PROPOSED`; no approval, publication, contract, or execution was created.

This proves the observed response was not a failure inside the canonical
conversation orchestration. It was a wrong-tool selection caused by an
insufficiently explicit review continuation and by a high-level confirmation
schema that exposed internal binding values to the client.
