# ORKI-002 Assessment and Self-Critique

**Date:** 2026-08-01
**Scope:** Mission Understanding only
**Closure state:** PASS — READY FOR PRODUCT OWNER REVIEW

## Assessment

ORKI-002 adds a bounded Mission Understanding engine that stores an explainable, project-scoped `PROPOSED` Mission State in the Cognitive State. The state is constructed from typed facts, inferences, assumptions, open decisions and evidence. It accepts only structured provider observations, canonicalizes stable values, preserves confidence and supersession history, and exposes a projection without transcript content.

When `mission_understanding` is present, the Factory Chat integration takes the new bounded route only. It does not invoke the legacy Factory Mission/planning workflow. Existing legacy behaviour remains available only when that structured observation is absent.

## Validation summary

| Gate | Result |
| --- | --- |
| Engineering acceptance | PASS — migration, Django checks, focused tests, Ruff and diff integrity pass |
| Operational acceptance | PASS — public Factory Chat boundary and browser-E2E coverage pass |
| Mission Understanding release gate | PASS — independent multi-project behavioural scenario passes |
| COO capability acceptance | FOUNDATION / Mission Understanding capability PASS; later COO engines remain intentionally absent |
| Documentation, architecture index, roadmap and AKB | PASS — updated with the canonical data-flow contract and reusable learning |

Full regression is recorded separately from the focused gate and must remain green from the final repository state before handoff.

## Self-critique and recovery posture

- The capability is intentionally conservative: it records a proposed mission, not an accepted business decision.
- The semantic provider is replaceable. The gate proves Orki's deterministic handling of a structured observation, not universal real-world LLM accuracy.
- Canonicalization currently relies on normalized structured values; future provider qualification should add adversarial multilingual paraphrase sets.
- Legacy Factory Mission behaviour is preserved for compatibility but is fenced off whenever ORKI-002 data is present. Future retirement must be a separately approved migration.
- No recommendation, plan, governance action or execution may use a transcript as memory; the data-flow contract is the mandatory integration boundary.
