# Sprint 005 closure report

**Closure state:** PASS — READY FOR PRODUCT OWNER REVIEW
**Branch:** `main`
**Implementation commit:** `e2305919b1ab80e998856a5d21ca68b166e3d52f`

## Delivered

- The canonical Execution Contract now resolves deterministic HOTFIX, BUGFIX,
  TASK, SPRINT, and EPIC policy profiles from execution level, task type, and
  declared risks. Risk only strengthens obligations.
- The durable lifecycle supports consume, complete, supersede, and revoke.
  Completion binds the final commit and governed closure state; Epic contracts
  cannot be consumed as code-change authority.
- `stage.artificial-software-factory.com` and
  `app.artificial-software-factory.com` are explicit safe Django hosts.
  `DJANGO_ALLOWED_HOSTS` can add explicit deployment hosts; `*` raises a
  configuration error.
- The old pre-tiered Sprint contract was superseded. The replacement Sprint
  contract and a separate BUGFIX + CONFIGURATION Cloudflare repair contract
  were consumed and completed against the implementation commit.

## Evidence

- `acceptance-results.json` records contract identifiers, hashes, lifecycle,
  and all required checks.
- `cloudflare-host-validation.json` records Django client host validation:
  both approved hosts return 200 for `/health/`; an unapproved host returns
  400, so Django no longer raises `DisallowedHost` for either approved tunnel
  host.

## Release gates

`pytest` passed with 28 tests. `ruff check .`, `ruff format --check .`,
`mypy .`, `scripts.release_gate`, and `makemigrations --check --dry-run` all
passed.

The requested login UI remains out of scope for this approved Sprint.
