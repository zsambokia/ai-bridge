# Closure Report — Recover Interrupted Approval Sessions

## Binding

- Handoff: `bridge:ai-bridge:contract:46ee9349-ba76-4ed9-b053-132fd8e7ffb7`
- Sprint: `docs/sprints/e626a32e-b18a-415e-bfe2-5d2baf8bf1b2-recover-interrupted-approval-sessions.md`
- Repository / branch: `zsambokia/ai-bridge` / `main`
- Baseline: `605ef46eb71cbc16147b946dbf8ddad2372712ae`
- Stage capability registry: `2026-07-28.3`, including `scope.resume` and
  `scope.resume_confirm_and_execute`.

## Delivered and assessed

The existing canonical `GovernanceApproval` and
`ConversationOrchestration` lifecycle now supports safe recovery discovery and
authenticated, proposal version/hash-bound resume confirmation. The recovery
path reuses durable records, locks the scope, fails closed on stale bindings,
and writes MCP audit events. It does not introduce a parallel approval or
execution lifecycle.

Cancellation is a recoverable execution state. A durable provider
`turn.completed` activity event is accepted as the terminal signal when a
stale Windows PID observation would otherwise keep completion blocked.
Windows status polling now uses a native process handle and exit code instead
of `os.kill(pid, 0)`, preventing an exited provider process from remaining
reported as `RUNNING` during recovery.

## Validation

| Command | Result |
| --- | --- |
| `pytest projects/tests/test_governed_mcp.py -q` | PASS — 22 tests |
| `pytest -q` | PASS — 92 tests |
| `ruff check .` | PASS |
| `mypy .` | PASS — no issues in 89 source files |
| `python manage.py validate_scopes` | PASS |

The final Release Gate rerun and governed contract completion bind the final
commit to this evidence manifest.

Final regression rerun: `pytest -q` passed with 93 tests.
