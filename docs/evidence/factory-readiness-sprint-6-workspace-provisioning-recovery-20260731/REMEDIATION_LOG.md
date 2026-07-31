# Remediation log

| Iteration | Result | Action |
| --- | --- | --- |
| Diagnosis | Stale `STARTING` lease was not a reconciliation candidate | Added separate provider-free provisioning recovery classifier and queue path. |
| Initial regression-test harness | A fixture was incorrectly unpacked directly | Corrected the test wrapper/teardown; no production behavior changed. |
| One-shot worker observation | Provider PID later disappeared after one-shot process exit | Recorded as the existing, separate provider-loss recovery path; verified provision-to-provider-start with a continuous worker. |
| Browser E2E attempt | No controllable ChatGPT Business browser (`iab`) | Preserved as an external-input requirement; did not falsify it with a static token request. |
