# Evidence-chain validation

Each Runtime state and coordination decision is persisted as `OrkiRuntimeEvent` with sequence, actor, timestamp, payload and optional evidence references. The Shadow creation event references the existing scope identifier; approval handoff references both scope identifier and existing approval reference.

This adds a Runtime audit projection without replacing the existing Governance or `ExecutionRun` evidence chain. The test suite asserts the expected creation, approval and recovery event types.
