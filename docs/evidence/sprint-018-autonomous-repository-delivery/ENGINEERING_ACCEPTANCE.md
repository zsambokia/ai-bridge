# Sprint 4 Engineering Acceptance

Sprint 4 adds a contract-bound repository delivery gate.  It persists policy and verification state, rejects dirty/out-of-scope/force/evidence/self-approval failures, detects remote movement for reconciliation, publishes only through ordinary `git push`, and binds completed runs to the remote-verified final SHA.

Final validation results are recorded in `RELEASE_GATES.md`; final commit and remote SHA are appended at closure.
