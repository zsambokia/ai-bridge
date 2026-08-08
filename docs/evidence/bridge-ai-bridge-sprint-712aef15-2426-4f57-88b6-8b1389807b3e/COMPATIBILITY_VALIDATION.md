# Compatibility validation

The Runtime Foundation was validated against its explicit non-ownership
boundaries. The detailed reports are:

- `GOVERNANCE_COMPATIBILITY_REPORT.md`
- `EXECUTION_COMPATIBILITY_REPORT.md`
- `EVIDENCE_CHAIN_VALIDATION.md`
- `RECOVERY_VALIDATION.md`
- `SHADOW_MODE_COMPARISON.md`

Focused tests confirm Factory Chat retains its existing plan and approval flow,
while the Runtime creates only Shadow Mode records and event evidence. No
Governance, Approval, ExecutionRun, ExecutionJob, queue, provider, or Cognitive
State mutation path was added.
