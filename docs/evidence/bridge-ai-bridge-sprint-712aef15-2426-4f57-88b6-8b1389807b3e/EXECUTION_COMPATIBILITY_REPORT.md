# Execution compatibility and Shadow Mode report

`OrkiExecution.execution_run` is nullable and Foundation Shadow Mode leaves it null. The Runtime adapter does not import or invoke execution dispatch, jobs, queues, provider transport or existing execution recovery.

The passing test `test_approval_is_observed_without_starting_execution_run` proves approval reaches `WAITING_GOVERNANCE` with no `ExecutionRun`. Existing Factory Chat approval tests remain green, demonstrating the prior lifecycle remains intact.
