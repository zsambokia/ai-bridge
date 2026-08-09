# Orki Workspace Information Architecture — Discovery Audit

**Status:** proposed navigation only; no UI implementation is authorized.

## Target navigation

| Area | Why it exists | Current source / status |
| --- | --- | --- |
| Home | cross-project current mission, next action and alerts | Merge Factory Chat context/status. |
| Orki | conversational goal intake and Cognitive State | Keep and rename Factory Chat as the Orki area. |
| Projects | project selection, registry and bootstrap status | Partial: selector and new-project entry exist. |
| Execution | plan, approval, OESM state, events and recovery | Partial API/runtime monitor; no dedicated page. |
| Knowledge | Context Packages, provenance, review queue and retrieval evidence | Partial memory mode and endpoints; no dedicated page. |
| Repository | bootstrap, import, sync, source freshness and readiness | Backend/evidence only; no page. |
| Roadmap | project plan and governed milestones | Projected in context; no dedicated page. |
| Architecture | canonical architecture and constraints | Repository documentation only. |
| Decisions | structured decisions and approval history | Decision API exists; no human page. |
| Meetings | meeting-derived facts/decisions with provenance | No dedicated owner or page found. |
| Workflows | executable scope, contracts and run lifecycle | Existing governance records; no dedicated page. |
| Runtime | provider-neutral execution diagnostics/event stream | API and embedded monitor; no dedicated page. |
| Evidence | receipts, test proof and closure reports | Repository evidence only. |
| Administration | registry, models and governed configuration | Django admin only. |

## Interaction and visibility model

The Workspace should make the following chain visible without implying that
every transition is automatic:

```text
Goal -> Intent -> Planning -> Context Package -> Reasoning -> Approval
-> Execution -> Reflection -> Knowledge Update -> Response
```

Visible state labels should distinguish: draft/understanding incomplete,
waiting for approval, governance wait, provider/external wait, running,
verifying, reflecting, knowledge candidate, completed, failed, and recovery.
The current Runtime monitor already exposes a subset of these through the
`execution_projection` and SSE endpoint.

## Screen migration decision

| Current screen or endpoint | Decision | Rationale |
| --- | --- | --- |
| `/` Factory Chat | Keep, then rename/position as **Orki** | It is the only complete authenticated product surface. |
| Factory context/status fragment | Merge into Home, Orki and Execution projections | It is a partial projection, not an independent page. |
| `/factory/new-project/` | Keep as registry/bootstrap entry; replace its standalone shell later | Project ownership stays server-side. |
| `/reasoning/*` | Keep as API; add Decisions projection only after contract review | No human-facing screen today. |
| `/runtime/executions/*` | Keep as API and event source; add Execution/Runtime projections | Canonical lifecycle must remain service-owned. |
| `/factory/memory/*` | Merge into Knowledge | Review/search are already governed actions. |
| `/factory/plan/*` | Merge into Execution/Workflows | Plan actions are governed, not navigation roots. |
| `/admin/` | Keep as Administration | Django admin is operational, not the Orki Workspace. |

## Navigation rule

Each area is a read projection plus explicitly governed actions. Navigation
does not grant execution authority, and no area can create a parallel domain
owner.
