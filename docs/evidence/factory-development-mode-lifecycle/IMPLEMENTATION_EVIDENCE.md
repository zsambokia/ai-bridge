# Factory Development Mode and Execution Lifecycle Recovery Evidence

## Authority and scope

This self-development change was authorized by the Product Owner bootstrap
override in the repository-root `AGENTS.md`. The override explicitly permits
this exact `ai-bridge` governance/execution repair to proceed without an AI
Bridge-issued, hash-bound Sprint or Execution Contract. The implementation was
developed in the isolated branch `agent/factory-development-lifecycle` from
baseline `cf2dedd39f6bb1da43dea8730f27777b9837cd33`; the user's dirty `main`
worktree was left untouched.

## Root cause and repair

The existing provider adapter could observe a finished process, but the
canonical `ExecutionRun` remained `RUNNING` unless a later caller explicitly
submitted completion. A disconnected or completed local Codex execution could
therefore remain presented as running.

The audit reproduced this against durable local evidence: `ExecutionRun #20`
had provider execution `2776`, last event `turn.completed`, and provider status
`FINISHED`, while its persisted lifecycle was still `RUNNING / EXECUTING`.

The repair retains the existing execution model. It adds the narrowly scoped
`FACTORY_DEVELOPMENT` execution profile, durable Product Owner authority facts,
idempotent factory start, provider-terminal reconciliation, ordered terminal
and validation-continuation events, a watchdog management command, and
evidence-derived Product Owner progress. Factory start is restricted to the
canonical `ai-bridge` repository; ordinary customer governance remains
contract-first.

The Product Owner read model was completed as a derived extension of the same
canonical event stream: source-event mapping, icon, confidence, provider
status, blocker, next expected action, and deterministic terminal category are
now available without a parallel activity service or mutable heartbeat state.

## Verification

All commands were run in the isolated implementation worktree after the final
source and documentation changes:

```text
python -m ruff check .                            PASS
python -m ruff format --check .                   PASS (91 files)
python manage.py check                            PASS
python manage.py makemigrations --check --dry-run PASS (No changes detected)
python -m pytest -q                               PASS (82 passed)
python -m mypy projects                            PASS (49 source files)
```

Focused lifecycle and MCP regression coverage also passed before the complete
suite: `python -m pytest projects/tests/test_execution.py
projects/tests/test_governed_mcp.py -q` — `24 passed`.

## Closure handoff

The implementation branch is committed, pushed, and presented as a draft Pull
Request after this evidence record is finalized. It is not merged or deployed.
