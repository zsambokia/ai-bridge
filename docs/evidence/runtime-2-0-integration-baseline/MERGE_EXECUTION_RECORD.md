# Merge execution record

Accepted branch merged by `05d4b92f279183e7d363421897e2ec232375738d`
(`merge: consolidate governed execution lifecycle`).

The resolution retained the operational foundation and incorporated accepted
cancellation/reconciliation behavior. Duplicate `CANCELLING` state and
`ExecutionCancellation` declarations were removed. Side migrations `0017` and
`0018` were replaced by canonical migration `0067`.

The admin cancellation action calls the same prepare, confirmation, and
request services as MCP; it does not directly mutate lifecycle state.
