# Sprint 7 remediation log

| Iteration | Observation | Repair / result |
| --- | --- | --- |
| 1 | Generic worker exception could finish without a durable canonical repair chain. | Added incident, ownership, evidence, child scope, checkpoint, independent validation, exact resume, Admin/MCP projection, and worker integration. |
| 2 | A bounded retry limit could itself leave a worker-held lease if `open_technical_remediation` raised. | Released the lease and wrote an audited `TECHNICAL_REMEDIATION_LIMIT_REACHED` recovery state. |
| 3 | First isolated HTTP probe was 401 because an empty parent environment value did not survive child-process startup. | Explicitly supplied the test-only process token; authenticated MCP initialize and tools/list passed. No production credential was inspected or logged. |

All repairs were followed by focused regression tests and the full Release
Gate suite recorded in `ENGINEERING_ACCEPTANCE.md`.

