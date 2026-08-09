# Orki Workspace Gap Analysis

| Category | Gap | Consequence / governed next step |
| --- | --- | --- |
| Backend | No single Workspace read-model API joining project, context, runtime and repository readiness | Define projection contracts; preserve owners. |
| Frontend | Only Factory Chat is a full screen | Build navigation and projections incrementally after contracts. |
| Runtime | Context Package reference is not uniformly visible on an execution projection | Specify request/projection contract; no direct AKB reads. |
| Provider | Factory Chat dispatch is provider-dependent; structured Runtime expects validated request | Define one governed hand-off, retaining provider gateway. |
| Knowledge | UI accesses package/queue models directly in places | Replace with projection services. |
| Repository | Lifecycle has backend/evidence but no user-facing readiness view | Add Repository projection after lifecycle contract review. |
| Workflow | Plans/scopes/contracts are dispersed as actions/records | Add Workflows projection, not a new workflow engine. |
| Governance | Workspace navigation could be mistaken for execution authority | Every action must retain scope/approval/contract checks and evidence. |

## Risk controls

1. Projection-first: read models before write actions.
2. One canonical owner for Runtime, AKB, repository lifecycle and approval.
3. Feature flags/shadow views for every new area until acceptance evidence exists.
4. Separate visual completeness from executable/operational acceptance.
