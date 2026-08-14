# FFS conformance

`resolve_route` is a thin control-plane lookup: it validates scope project, logical Nodes, service ownership and Zone rules, then returns the published transport binding. It never receives or forwards packet payload. Node key, service key and endpoint/transport binding are persisted separately. Dynamic discovery, leases, heartbeats, load balancing, active-active topology and HA/failover are explicitly deferred because physical topology remains open.
