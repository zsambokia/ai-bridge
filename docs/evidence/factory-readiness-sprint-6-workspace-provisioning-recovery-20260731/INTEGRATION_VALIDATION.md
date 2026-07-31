# Integration validation

The repair was exercised against the persisted production-shaped local runtime
record, not only model fixtures:

1. Reconcile the stale lease for execution
   `218cb756-807c-46d5-8e82-dc19ac210f08`.
2. Verify durable `WORKSPACE_PROVISIONING_RECOVERY_QUEUED` evidence.
3. Run the worker against the same queued job.
4. Verify the ordered workspace transitions through `PROVIDER_STARTED` and
   `WORKER_DISPATCH_COMPLETED`.
5. Run a continuous worker and verify provider PID/worker heartbeats before its
   separately recorded provider-terminal path.

This validates the checkout, venv, dependency, database, migration, seed,
bootstrap, and provider-start boundary. It does not validate the externally
controlled Business UI ingress or approval boundary.
