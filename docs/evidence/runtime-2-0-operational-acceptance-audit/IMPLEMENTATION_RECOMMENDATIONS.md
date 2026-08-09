# Implementation Recommendations (not implemented by this audit)

1. Establish the end-to-end ownership contract first: Conversation emits commands/events only; MSM resolves mission information and creates work items; Operational Foundation runs them; PSM and WSM own only their domains; Gateway is the sole provider boundary.
2. Extract the current mission/planning states from `OrkiExecution` into an explicit MSM and PSM. Retire duplicate transitions only after migration evidence proves continuity; do not introduce parallel runtimes.
3. Route Factory Chat provider work through canonical `ExecutionRequest → ExecutionRun → ExecutionJob`; preserve the existing durable queue, workers, polling, retry, telemetry and recovery rather than rebuilding them.
4. Make the Workflow Engine consume independently scheduled work and remove Runtime calls to `execute_task_adapter`.
5. Make Mission Resolution exhaust AKB, repository receipts/bootstrap, configuration, semantic retrieval and relevant prior missions before emitting an owner question. Persist evidence for every resolution decision.
6. Reduce Conversation to chat, projection, approval and event forwarding. Move authoritative repository/planning/workflow initiation to MSM commands and make right-side panels projections.
7. Implement the 20-scenario Product Owner acceptance suite plus architectural negative tests for every prohibited direct edge.

Significant deviations from prior code must be documented during the approved implementation sprint. This audit proposes a convergence refactor, not compatibility layers or a second queue/engine family.

