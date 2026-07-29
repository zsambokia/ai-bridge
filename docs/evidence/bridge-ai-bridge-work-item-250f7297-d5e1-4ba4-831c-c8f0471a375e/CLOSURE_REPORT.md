# Closure report — Sprint 1 factory E2E technical remediation

## Status

`PASS — READY FOR PRODUCT OWNER REVIEW`

## Delivered

- Recovered the stale governed run using existing execution, event, and JSON
  metadata mechanisms; no persistent Django model, migration, or manual database
  change was introduced.
- Applied the missing canonical migrations and proved the clean run's isolated
  clone, virtual environment, runtime database, migration state, provider event
  stream, worker heartbeat, bounded retry, and provider completion.
- Added raw-event-preserving canonical lifecycle projections and recovery/lease
  coverage, and made `Run ID` the first `ExecutionRunAdmin` data column.
- Restored missing deterministic scope publications from existing authoritative
  records and recorded final gate results.
- Repaired terminal scope publication-hash validation without altering persisted
  business data: new closures retain their published hash, while historical
  closures remain bound to their issued immutable contract hash.

## Final gates

| Gate | Result |
| --- | --- |
| `pytest -q -p no:cacheprovider` | PASS — 165 passed |
| `ruff check .` | PASS |
| `mypy .` | PASS — 134 source files |
| `python manage.py validate_scopes` | PASS |
| `python manage.py migrate --check` | PASS |

The complete machine-readable evidence is in `acceptance-results.json` and
`machine-results.json`; the technical diagnosis is in `ASSESSMENT.md`.

## Closure binding

The governed run is bound to the local commit created in its isolated workspace
after `PROVIDER_COMPLETED`. The host `main` commit is created from the same
validated remediation state before final contract completion.
