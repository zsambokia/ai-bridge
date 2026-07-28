# Execution continuity defect: terminated Codex PID retained `RUNNING`

Reported during this approved Sprint: after the previous Codex process/PID
ended, the associated AI Bridge execution remained `RUNNING`.

This is recorded as a **separate execution-governance defect**, not as proof
that a live worker exists. The repository currently has activity/heartbeat
projections, but this Sprint does not contain a durable process-liveness
reconciler that transitions a run when its originating Codex PID terminates.
No destructive lifecycle mutation was inferred from the report. Required
follow-up: a separately authorized recovery/continuity scope must reconcile
the affected execution token from durable provider/process evidence and define
safe terminal/recovery behavior.
