# Codex idempotency proof

`conversation.confirm` derives its confirmation binding and deterministic retry
key from the approved proposal. The original confirmation created exactly one
orchestration and one consumed contract. The provider registry does not add a
parallel approval or replay path; completion is accepted only once the
provider process has stopped, evidence exists, gates pass, and the final commit
matches the workspace HEAD.
