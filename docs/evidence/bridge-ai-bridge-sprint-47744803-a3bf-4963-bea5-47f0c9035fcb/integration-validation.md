# Integration validation

The stage MCP connector was exercised against the formerly failing execution
token `baa36d2a-e7c7-44a8-a65a-accee9e56f67` after the local stage service
reloaded the repaired Django source.

| Tool | Result |
| --- | --- |
| `execution.get_run_status` | controlled `EXECUTION_NOT_FOUND` tool error |
| `execution.get_activity_summary` | controlled `EXECUTION_NOT_FOUND` tool error |
| `execution.list_events` | controlled `EXECUTION_NOT_FOUND` tool error |
| `execution.cancel` | controlled `EXECUTION_NOT_FOUND` tool error |

The token is not present in the stage canonical store, so there was no active
run left to cancel. This is a successful, non-500 cancellation attempt; no
database record was created, deleted, or directly modified.
