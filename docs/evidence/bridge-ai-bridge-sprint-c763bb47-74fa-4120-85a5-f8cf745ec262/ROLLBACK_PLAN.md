# R20-00 Rollback and Migration Constraints

R20-00 changes no runtime state, schema, queue, worker, provider route, or
production system. Runtime rollback is therefore not applicable; removing this
audit's documentation restores the pre-audit documentation state.

For R20-01/R20-02, the mandatory rollback constraints are:

1. Additive, reversible schema changes with explicit migration evidence.
2. Preserve `ExecutionRun`/`ExecutionJob` identity, lease, retry, recovery,
   and evidence provenance; do not duplicate the worker lifecycle.
3. Keep the legacy Factory Chat route isolated behind an explicit compatibility
   boundary until the MSM-to-Foundation route passes end-to-end acceptance.
4. Prove idempotent replay and safe recovery before enabling a new ingress.
5. Supply an approved rollback procedure before any provider-route cutover.
