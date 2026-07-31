# Sprint 4 failure and remediation log

This log is retained deliberately; rejected attempts are evidence, not noise.

| Detection | Diagnosis | Repair | Result |
| --- | --- | --- | --- |
| Default local runtime database lacked migration `0038`. | The developer database was not an Operational Acceptance runtime. | Created an isolated SQLite runtime and applied all migrations. | PASS: migration and runtime proof use the isolated database. |
| HTTP MCP returned `DisallowedHost`. | The narrow runtime allow-list omitted the loopback host. | Added only `127.0.0.1,localhost` for the isolated process. | PASS. |
| Initial inline PowerShell request returned JSON parse error. | Shell argument conversion altered the request body. | Sent exact UTF-8 JSON files with `curl.exe --data-binary`. | PASS. |
| Admin probe using Django's `testserver` returned 400. | It was intentionally absent from the narrow allow-list. | Re-ran the request with allowed `localhost`. | PASS. |
| A broad formatter run touched unrelated test files. | The command scope was too broad. | Restored those unrelated formatting changes before staging; no such file is committed. | PASS. |
