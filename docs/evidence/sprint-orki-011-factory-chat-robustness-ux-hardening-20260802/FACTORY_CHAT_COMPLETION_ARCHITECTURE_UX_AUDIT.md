# ORKI-011 Factory Chat Completion — Architecture and UX Audit

**Date:** 2026-08-02
**Scope:** Factory Chat operational workspace completion
**Outcome:** ACCEPTED FOR TARGETED IMPLEMENTATION

## Audit boundary

This audit examined the existing Factory Chat as an operational interface to
Orki. It does not authorise new cognitive capabilities, changes to governance
authority, provider behaviour, or autonomous execution.

## Architecture findings

| Area | Finding | Required action |
| --- | --- | --- |
| Cognitive State | Canonical, project-isolated state and attributable entries already exist. | Project the existing state; do not create a second chat-owned state. |
| Conversation | The conversation path has correlation-aware, idempotent reply handling. | Retain it and expose its recoverable UX behaviour. |
| Planning | The canonical planning path creates plan, roadmap, and memory candidates from mission state. | Surface those projections and lifecycle status in Factory Chat. |
| Approval | A durable approval object and explicit plan actions already exist. | Make the approval summary, assumptions, alternatives, impact, and recommendation inspectable before action. |
| Documentation lifecycle | Planning artefacts are canonical project projections, but their status is not visible in the workspace. | Show their live projection/status rather than duplicate documents manually. |
| Errors | Chat errors are safe; several plan and memory actions can still return raw exception text. | Replace with safe, structured, correlation-aware responses. |
| Legacy flow | Obsolete discovery-question code remains beside the natural conversation route. | Remove the unused questionnaire path. |

## UX findings

| Area | Finding | Required action |
| --- | --- | --- |
| Cognitive context | The right panel is a narrow mission summary. Facts, assumptions, open decisions, recommendation, plan, roadmap progress, and next step are absent or implicit. | Provide a stable live Cognitive State projection. |
| Planning review | A pending plan is actionable but does not make its reasoning sufficiently legible. | Add an explicit review object before approval. |
| Conversation continuity | The interface only renders the latest 20 messages on initial load. | Increase the bounded operational history without treating it as memory. |
| Resilience | Draft, retry, safe chat errors, autosize, and scroll behaviour are present. | Extend the same safety standard to every action route. |
| Usability | The desktop split view and responsive layout exist. | Preserve the single workspace flow; no multi-page wizard. |

## Internal audit decision

The required capabilities can be completed by extending the existing canonical
Factory Chat, Cognitive State, planning, and approval paths. No new model,
parallel state store, or authority path is justified. Implementation may begin
with the targeted actions above.

## Completion evidence required

The final release gate must demonstrate a long natural conversation, a visible
and explainable Cognitive State projection, plan review and explicit approval,
roadmap and plan projection updates, safe retry/recovery/error behaviour, and
responsive browser usability.
