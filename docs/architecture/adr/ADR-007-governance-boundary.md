---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# ADR-007 - Governance Boundary

**Status:** Accepted architectural boundary; no separate end-to-end behavioural certification claimed.

## Decision

The Cognitive Operating System may understand, assess, recommend, and prepare
governed work. Existing canonical approval, scope, contract, execution, and
evidence lifecycles remain the authority for execution.

## Consequences

No interface, Cognitive State update, recommendation, or LLM response may
silently approve scope, issue an Execution Contract, or execute repository work.
