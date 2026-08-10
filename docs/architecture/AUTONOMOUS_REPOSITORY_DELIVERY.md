---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Autonomous repository delivery

Sprint 4 makes repository publication a durable, contract-bound execution phase. A project branch policy is embedded in the execution contract as a delivery policy. Completion invokes the verifier before terminalising the run.

The verifier requires an exact final local HEAD, a clean workspace, changed paths within the approved policy, passing declared gates, existing evidence carrying the same SHA, an unchanged remote baseline, a normal push, and a post-push remote SHA readback. It never constructs a force push. Remote movement enters durable reconciliation rather than overwriting another change.

`ExecutionDelivery` is the single persisted projection for API/MCP/Admin. It records policy, baseline, final and remote SHA, changed files, verifier, outcome and failure. The execution provider may not be the independent verifier. Main-only is the configured policy path for this repository; a PR route is not claimed where project policy does not support it.
