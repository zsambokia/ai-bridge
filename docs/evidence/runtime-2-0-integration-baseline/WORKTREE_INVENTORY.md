# Worktree inventory

Inventory recorded before consolidation on 2026-08-09.

| Worktree | Branch | HEAD | Result |
| --- | --- | --- | --- |
| `ai-bridge` | `main` | `43ebb3e638d855abc53a5dc22fb4013e6da1b237` | canonical target |
| `ai-bridge-factory-lifecycle` | `agent/factory-development-lifecycle` | `af4800b9ebe5cf2496ca6aa48404f78e51f0c6df` | accepted; contained by cancellation branch |
| `ai-bridge-governed-cancellation` | `agent/governed-execution-cancellation` | `43e5b75dfb961840052d9779e1679b3d8d9ac418` | accepted merge source |

The target baseline had one protected, unrelated local change in
`bridge/settings/local.py`; it is excluded from integration commits.
