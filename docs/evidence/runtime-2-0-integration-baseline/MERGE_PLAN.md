# Merge plan

Merge the accepted governed-cancellation branch into `main`, retaining the
existing Runtime 2.0 foundation where branches overlap. Keep one
`ExecutionRun` lifecycle, provider gateway, reconciliation loop, retry/recovery
path, and activity projection.

Branch-local migrations are not accepted because their numbers collide with
canonical history; their schema intent is carried once by migration `0067`.
