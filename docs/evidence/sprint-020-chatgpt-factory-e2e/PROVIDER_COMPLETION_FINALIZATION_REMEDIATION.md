# Provider-completion finalization remediation

Date: 2026-07-31  
Scope: Sprint 6 — Complete ChatGPT → Factory End-to-End Proof

## Incident and factual trace

Execution `218cb756-807c-46d5-8e82-dc19ac210f08` recovered isolated workspace
provisioning and reached its second provider attempt. The last successful
recorded operation was the provider terminal activity event:

```text
event: PROVIDER_COMPLETED
sequence: 575
```

The previous event handling then set the live run to
`BLOCKED_EXTERNAL_INPUT` / `PROVIDER_TERMINALIZED`, retained its workspace as
`IN_USE`, and left the provider PID projection populated. No canonical
workspace validation, Git inspection, final commit resolution, release-gate
validation, delivery receipt, deployment verification, or completion transition
was started. This was a Bridge lifecycle defect, not missing Product Owner
approval or a new external-input requirement.

The retained workspace was inspected before this repair. Its repository HEAD
was the baseline `ec7f82b…`; it contained only an untracked `build/` directory
and no provider commit or tracked change. Earlier provider activity reports
also record an ACL failure on `.git/index.lock`. Accordingly, this immutable
historical execution cannot honestly gain a final commit, delivery receipt, or
completion retroactively.

## Repair

The terminal-provider path now queues the worker-owned
`FINALIZE_PROVIDER_COMPLETION` action. The transition is:

```text
PROVIDER_COMPLETED
→ run/workspace VALIDATING and PID cleared
→ Git HEAD/status inspection
→ explicit NO_CHANGE or CANONICAL_COMPLETION_MISSING facts
→ retained workspace and bounded same-contract recovery
```

It deliberately does **not** infer repository delivery, deployment, or scope
completion from a provider exit. A duplicate terminal event sees the already
queued finalization and cannot create a second delivery/recovery path.

## Regression evidence

Focused lifecycle regression suite after the repair:

```text
python -m pytest projects/tests/test_execution.py projects/tests/test_execution_recovery.py -q
40 passed
```

The cases cover terminal-event finalization queueing, duplicate-event
idempotency, PID clearing, workspace validation/retention, repository
inspection, explicit no-change classification, technical recovery, and worker
claim/restart of the same run. Repository-wide gates are recorded separately
after the final scoped revision is prepared.

## Final engineering validation

The final scoped worktree passed the repository Release Gate without excluding
source code or tests:

```text
python scripts/release_gate.py
  Django check: PASS
  pytest: 233 passed
  ruff check: PASS
  ruff format --check: PASS (158 files)
  mypy: PASS (158 source files)

python manage.py makemigrations --check --dry-run --settings=bridge.settings.local
  No changes detected
python manage.py validate_scopes --settings=bridge.settings.local
  All canonical scopes valid
git diff --check
  PASS
```

The first full formatting run revealed that transient, untracked prior Sprint
runtime workspaces were being traversed.  The Release Gate was not suppressed:
the formatter's configured exclusion list now names only those six generated
runtime directories, and the six tracked baseline files it reported were
formatted.  The full gate was then rerun and passed.  No runtime workspace,
evidence, or unrelated user change was deleted or rewritten.

## Honest operational boundary

The repair must be deployed to the staging runtime before a new actual ChatGPT
Business UI request is initiated. The historical execution is not reopened and
no database history is edited manually. A static Bearer-token request is not a
substitute for the required UI-originated Remote MCP proof. Until that fresh
request reaches canonical delivery, deployment, retrieval, and feedback,
Sprint 6 Operational Acceptance remains incomplete.
