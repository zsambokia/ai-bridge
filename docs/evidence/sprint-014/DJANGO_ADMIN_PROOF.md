# Django admin proof

`ExecutionProviderAdmin` exposes list/detail configuration, kind/role validation, capability and priority editing, masked credential status, immutable identity fields after first use, read-only health/test metadata, an audit inline, and a non-mutating health action. The action never dispatches governed execution.

The form stores a secret reference only; it has no secret-value field and cannot return a stored secret after save.
