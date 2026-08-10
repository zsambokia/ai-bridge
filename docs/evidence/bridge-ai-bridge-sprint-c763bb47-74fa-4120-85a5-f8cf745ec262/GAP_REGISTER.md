# R20-00 Gap Register and Migration Map

| ID | Finding | Severity | Governed follow-up |
| --- | --- | --- | --- |
| G-01 | `ExecutionRequest` is immutable only in memory; no durable canonical request identity, provenance, or idempotency boundary exists. | high | R20-02 |
| G-02 | No dedicated MSM or durable mission transition set owns mission/work authorization. | critical | R20-01 |
| G-03 | No canonical authorized Operational Work Item exists; current tests explicitly prohibit an `OperationalWorkItem` model name. | critical | R20-01 design + R20-02 mapping |
| G-04 | Factory Chat reaches `execute_task_adapter` and the provider lambda directly, bypassing Foundation queue/lease/recovery. | critical | R20-02 |
| G-05 | No `MISSION_READY_FOR_PLANNING` gate was found. | high | R20-01 |
| G-06 | Conversation/mission code contains a repository lifecycle action, exceeding adapter-only target authority. | high | R20-01 |
| G-07 | PSM/WSM separation and provider routing are not proven on the constitutional path. | high | R20-03 / R20-04 |

The non-duplicating direction is to preserve `ExecutionRun` and `ExecutionJob`
as the one Operational Foundation mechanics lifecycle. A future approved
design must make the authorized work item a canonical authorization layer that
maps to that existing lifecycle, rather than creating a parallel queue/table or
worker. No constitutional amendment is requested by this audit; the mapping is
not yet implemented or proved.
