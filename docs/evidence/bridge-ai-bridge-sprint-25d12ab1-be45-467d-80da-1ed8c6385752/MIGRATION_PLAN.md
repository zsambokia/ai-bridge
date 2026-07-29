# Migration plan

Migration `projects.0027_technicalremediationloop` adds the additive
`TechnicalRemediationLoop` table. It references the pre-existing parent run,
parent scope, and one remediation scope using `PROTECT`; it does not rewrite
execution history, scope content, contracts, or provider records.

Deployment order: apply the normal Django migration before an execution worker
uses the new loop. Rollback is code rollback only after ensuring no durable
remediation records need to be retained; production lifecycle evidence is not
deleted as part of this Sprint.
