# Migration plan and rollback

Migration `projects.0055_orki_runtime_foundation` adds four additive tables and indexes only. It alters no existing table, column, lifecycle or data.

Forward rollout: deploy code and run the normal Django migration process. Shadow Mode is inert until Factory Chat creates a new plan. Existing records need no backfill.

Rollback: disable/revert the adapter code first; newly created Runtime rows become harmless audit data. Schema rollback is deterministic through Django migration `0055` because no existing canonical record is transformed. A production rollback must follow the repository's normal backup/change controls before reversing any applied schema.
