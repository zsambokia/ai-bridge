# Compatibility validation

Normal orchestrations that own a run keep returning that run's token through
the existing status projection. The new fields appear only when a blocked
orchestration has a verified active conflicting run on the same project and
branch. No token is invented when no such run exists.

The public cancellation contract is unchanged: the returned UUID is passed to
the same `execution.cancel` tool and its existing authorization and lifecycle
checks remain authoritative.
