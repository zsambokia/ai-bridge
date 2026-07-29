# Migration plan

## Change

Migration `projects.0024_executionjob` adds the `projects_executionjob` table
and its one-to-one relation to the already-existing `ExecutionRun` table. It
does not alter, rewrite, or delete existing execution runs, contracts, events,
or approvals.

## Forward procedure

1. Deploy the application code containing the worker command and migration.
2. Run `python manage.py migrate` using the normal deployment database owner.
3. Start at least one independent `run_execution_worker` process.
4. Verify an authorized dispatch creates `ExecutionRun(REQUESTED)` and one
   `ExecutionJob(QUEUED)` before the worker starts the provider.

## Rollback and safety

The migration is additive. Before reversing it, stop workers and ensure no
queued or leased jobs remain; otherwise durable dispatch records would be
discarded. Roll back the application code only after all jobs are terminal or
otherwise deliberately handled under governance, then reverse `0024` through
the normal Django migration procedure. No automatic destructive rollback is
performed.
