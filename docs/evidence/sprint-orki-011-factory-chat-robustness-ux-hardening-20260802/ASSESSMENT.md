# ORKI-011 Assessment — Factory Chat Completion

**Date:** 2026-08-02
**Result:** PASS — READY FOR PRODUCT OWNER REVIEW
**DCMI:** unchanged at 66/100

## Outcome

Factory Chat is now the operational workspace for the existing Orki Cognitive
Operating System. Natural conversation updates the existing, project-scoped
Cognitive State; the workspace then presents an explainable, read-only
projection of mission, facts, assumptions, open decisions, recommendations,
plan, roadmap and next safe step. Conversation history remains an interaction
record, never the memory or system of record.

The existing plan lifecycle is visible as a decision object containing summary,
assumptions, alternatives, impact, recommendation and an explicit Product Owner
decision. Approval records the plan and its document projections as execution
preparation only. It neither starts execution nor creates a new authority.

## Evidence-backed behaviour

- Safe, Hungarian recovery responses conceal raw exceptions, provider
  diagnostics and HTML error bodies while retaining diagnostic detail on the
  server side.
- Correlation-bound idempotency prevents duplicate owner/Orki pairs. Browser
  drafts survive refresh and recoverable failure; retry is explicit.
- The UI provides multiline keyboard input, auto-sizing, near-bottom-aware
  scrolling, visible thinking state, processing lock, live refresh and
  responsive desktop/tablet/mobile panel access.
- The old question-by-question discovery path is removed from the Factory Chat
  route. Planning starts from natural language and is reviewed through a clear
  decision card, not a wizard.
- Existing mission, plan, roadmap and memory-candidate lifecycle artifacts are
  shown through canonical projections. No manual document synchronization is
  required from the Product Owner.

## Independent validation result

The final Factory Chat suite passed **46 tests in 55.752 seconds**. It includes
34 backend cases and 12 Chromium browser cases. Static Django checks, canonical
scope validation, the final diff check and the complete repository regression
(**329 tests**, executed as 125 + 61 + 97 + 46) also pass. Full-repository
`mypy .` continues to report 119 inherited errors in 21 non-ORKI-011 files;
the changed-surface check adds no Factory Chat type errors. See
[Release Gate](RELEASE_GATE.md) and [Validation Walkthrough](VALIDATION_WALKTHROUGH.md).

## Non-claims

This sprint makes already accepted cognition operationally usable; it does not
prove recommendation quality, operational-reasoning quality or Digital COO
behaviour. CVO-002 remains the separate, unexecuted behavioural improvement
loop. No DCMI point or Digital COO certification is claimed here.
