# Sprint D acceptance results

Targeted acceptance suite: `python -m pytest projects/tests/test_local_codex.py -q`.

| Check | Result | Evidence |
| --- | --- | --- |
| Contract and scope binding | PASS | Drifted proposal hash is rejected. |
| Django reload continuity | PASS | Fresh ORM read sees the same leased job and heartbeat. |
| Local interruption recovery | PASS | A complete checkpoint moves the same run/job to recovery. |
| Completion binding | PASS | Verified Git HEAD and evidence close only the original contract/run. |
| Untrusted existing session | PASS | Session is audited `UNVERIFIED` then rejected. |

The detailed final repository-wide gate results are recorded in the engineering
audit after the final rerun.
