# Sprint D migration plan

Migration `projects.0028_executionjob_completed` adds the terminal
`COMPLETED` choice to the existing `ExecutionJob.status` field. It is an
additive schema metadata change: no table, data, scope, contract, or provider
record is rewritten. Existing queued and recovery values remain valid.

Rollback is the normal forward repair: restore a compatible status choice only
after all completed jobs have been retained or migrated deliberately. This
Sprint performs no destructive data migration.
