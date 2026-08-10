---
status: TRANSITIONAL
owner: Operational Foundation
supersedes: []
superseded_by: Constitution Book (planned adoption)
version: 1.0.0
---

# Operational Foundation Constitution

> **Terminology status (2026-08-10):** Transitional. Operational Foundation
> remains a separate architectural layer. The target technical execution core
> is the **AI Kernel**; a Provider Gateway is only a Provider Integration
> adapter, never a first-class architectural object.

The Operational Foundation is common delivery infrastructure, not a business
or Mission authority.

1. It SHALL be the sole canonical mechanical handoff boundary for authorized
   provider-bound work.
2. It SHALL accept work only as an immutable, MSM-authorized Operational Work
   Item and SHALL preserve its authorization, correlation, idempotency, and
   evidence binding.
3. It owns delivery mechanics: queueing, scheduling, leasing, retry, recovery,
   heartbeat, `ExecutionRun` lifecycle, and provider-adapter invocation.
4. It MUST NOT create or authorize a Work Item, interpret business intent,
   change Mission state, mutate a Domain Engine state machine, make a Product
   Owner decision, or treat provider output as authority.
5. It MUST NOT provide a bypass for Engine-to-Engine, Engine-to-Gateway, or
   Runtime-to-provider calls.
6. Its observable results SHALL be durable, attributable receipts, events, and
   evidence that the MSM and relevant Engine may consume.

The Runtime and MSM use the Foundation through its declared handoff contract
only. A Provider Gateway is a Foundation-owned Provider Integration transport adapter, not a domain
service.
