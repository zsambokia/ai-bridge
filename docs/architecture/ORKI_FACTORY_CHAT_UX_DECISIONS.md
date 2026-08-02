# ORKI-011 Factory Chat UX Decisions

## Decision 1 — one operational workspace

Factory Chat remains a fixed-project, split workspace: project selection on the
left, natural conversation in the centre, and a live Cognitive State projection
on the right. Navigation must not turn mission understanding or planning into a
multi-page form.

## Decision 2 — conversation is continuous, not a form sequence

Natural language is the primary input. The obsolete discovery-question flow is
removed. Questions remain exceptional and are owned by Orki's existing
mission-understanding path, not browser-side routing rules.

## Decision 3 — state is visible and explainable

The right projection is stable across conversation updates and labels each
category rather than exposing model internals. It only displays canonical
entries and their available confidence/provenance, so Product Owners can see
what is known, assumed, recommended, or awaiting decision.

## Decision 4 — approval is a deliberate review moment

The approval card makes summary, assumptions, alternatives, expected impact,
recommendation, and the required Product Owner decision visible before any
approval action. The interface cannot silently convert a conversational turn
into authority.

## Decision 5 — recovery is part of the working experience

Pending drafts survive retryable chat failures. The browser shows safe recovery
guidance and never displays backend exception detail. Status updates use a
fragment refresh rather than a full workspace reload.

## Decision 6 — documents are projections, never a second sync task

The workspace surfaces the existing mission, plan, initiative, architectural,
and roadmap projections. Product Owners do not manually copy state into a
separate document flow.
