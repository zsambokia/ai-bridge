# Runtime sequence and transition evidence

The canonical diagrams are maintained in [ORKI_ORCHESTRATOR_RUNTIME.md](../../architecture/ORKI_ORCHESTRATOR_RUNTIME.md).

Observed Factory Chat sequence under test:

1. Existing Factory Plan creates its existing scope and proposal artifacts.
2. Runtime creates `Goal`, `Plan`, `Execution` and events in `SHADOW` mode.
3. OESM reaches `WAITING_APPROVAL`.
4. Existing Factory Plan approval completes through its existing path.
5. Runtime records `APPROVAL_OBSERVED` and `SHADOW_GOVERNANCE_HANDOFF_RECORDED`, then reaches `WAITING_GOVERNANCE`.
6. No contract, `ExecutionRun`, `ExecutionJob`, queue entry or provider invocation occurs.

The automated assertions are `projects.tests.test_orki_runtime` and `projects.tests.test_factory_chat`.
