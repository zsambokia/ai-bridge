# `execution.prepare` schema bugfix closure report

The repair makes the MCP schema the authoritative runtime validation source for
the governed public registry. The HTTP acceptance test uses an isolated Git
repository and real durable Project, Scope, Approval, Preparation, and
ExecutionContract lifecycle. It proves the `storybook` request reaches issued
contract status without creating a Django application or bypassing approval.

## Final verification

- `pytest -q`: 43 passed
- `ruff check .`: passed
- `ruff format --check .`: 55 files already formatted
- `mypy .`: no issues in 55 source files
- `python manage.py migrate --check`: passed after applying the repository's
  already-present local migration `projects.0009_closure_authority_fields`
- `python manage.py validate_scopes`: all canonical scopes are valid

The acceptance flow stops at contract issuance. It does not consume a contract,
request execution start, or create `storybook`; those actions remain behind the
normal provider-consumption and execution-start boundary.
