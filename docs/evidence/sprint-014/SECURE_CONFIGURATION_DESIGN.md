# Secure configuration design

Secrets are never persisted by this application. `credential_binding` accepts only an uppercase environment/backend reference, and `credential_value()` resolves it only at the adapter runtime boundary. Public projections exclude both configuration and credential binding. Health records contain only status, reason, and timestamp. No credential values were supplied for this Sprint.

This is an environment/external-secret-backend reference model; encryption-at-rest is not required because secret material is not stored in the database.
