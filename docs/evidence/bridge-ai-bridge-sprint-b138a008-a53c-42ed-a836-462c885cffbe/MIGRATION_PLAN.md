# Migration plan

Migration `projects.0030_executionprogressevent_provider_event_identity` adds a
nullable `provider_event_id` field and a conditional unique constraint on
`(run, provider_event_id)` when the identifier is present. It is additive and
does not rewrite existing execution events.

Deployment order: deploy code and migration, run `manage.py migrate`, verify
`showmigrations projects`, then start or restart the supervised execution worker.
