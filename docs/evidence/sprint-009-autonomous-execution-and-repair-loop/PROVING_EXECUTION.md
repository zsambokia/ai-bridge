# Controlled proving execution

- Execution token: `4485753e-0bb3-4810-acde-f7cc7bf915eb`
- Provider: `codex-cli`
- Provider execution ID: `10508`
- Start result: `EXECUTION_STARTED`
- Durable preflight event: sequence 1, bound to `main` and baseline
  `10130902415aeba64d6d59c80a58a6cceacd79f5`
- Durable provider-start event: sequence 2
- Authorized bounded cancellation: sequence 3, `EXECUTION_CANCELLED`

The start was performed by `execution.request_start` only after a consumed
contract and a scoped durable approval were present. The dispatch audit record,
start request and execution run were committed to the operational database
before the Codex CLI process was launched. The provider has the repository
workspace and contract instruction only; raw stdout/stderr and credentials are
neither captured nor used as evidence.

Repository mutations for the bounded proving path are the Sprint 009 dispatcher,
migration, tests, documentation and this evidence bundle. Acceptance is based
on the final repository gates and contract closure, not on the provider process
start alone. The proving run was deliberately cancelled after its start/status/
event path had been demonstrated, so it cannot be misrepresented as the final
Sprint closure.
