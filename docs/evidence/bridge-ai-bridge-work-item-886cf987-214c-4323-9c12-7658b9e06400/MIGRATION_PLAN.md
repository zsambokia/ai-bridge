# Migration plan

1. Add `RECONCILING` and `ACCEPTED` to canonical executable-scope statuses and their Sprint and Work Item schemas.
2. Create `ExternalExecutionReconciliation`, protected by a one-to-one scope relation, holding verified inputs, digest, transition log, and audit facts.
3. Apply migration `0025_external_execution_reconciliation` before using the reconciliation command in the canonical Bridge database.
4. Reconcile only after all code and repository release gates pass.

The migration is additive: it neither rewrites scope history nor creates a provider run, contract, or historical execution event.
