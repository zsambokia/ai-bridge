# Issue #17 — Sprint 3: Planning Mode and Plan Approval

## Authority and boundary

- Authority: Product Owner Factory Development Mode for Issue #17, with the accepted Sprint 1 interaction contract.
- Branch and baseline before mutation: `main` at `72aaf1aabbf79aea237bb3edcee69c1bfac4aa0a`.
- Scope: the exact planning questionnaire, durable plan artifact, one-time plan approval, candidate Roadmap and Memory outputs, and escalation separation boundary.

## Delivered behaviour

- Planning Mode submits a structured server-side questionnaire for the selected canonical Project.
- The server creates a `FactoryPlan`, a `PROPOSED` canonical scope with `execution_authorization=NONE`, a candidate Roadmap update, and a candidate Memory entry.
- Plan approval is a distinct, durable `GovernanceApproval` with action `PLAN_ARTIFACT_APPROVAL`. It can occur once only and never binds execution approval, starts a provider, promotes Roadmap, or activates Memory.
- An identified business decision places the plan in `BUSINESS_DECISION_REQUIRED`; technical constraints and acceptance checks remain plan content rather than a business escalation.
- Enhanced browser posts refresh the server-owned AWC fragment without navigation; ordinary POST redirects remain the no-JavaScript fallback. The browser header is only a presentation hint.

## Explicit exclusions

This Sprint does not execute code, call a provider, confirm an execution scope, accept a Roadmap change, or publish Memory. Those remain later ordered boundaries.

## Acceptance and validation

The targeted suite proves artifact state, candidate-only projections, business blocking, durable one-time approval, no execution authority, and no-redirect enhanced submission. Full repository gates and the independent audit are recorded in `docs/evidence/issue-017-sprint-3-planning-mode-plan-approval/`.
