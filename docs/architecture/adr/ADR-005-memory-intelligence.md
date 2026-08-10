---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# ADR-005 - Memory Intelligence

**Status:** Implemented â€” ORKI-006.

## Decision

Orki shall maintain evolutionary knowledge rather than relying on transcripts.
Memories shall be reusable, attributable, confidence-scored, correctable,
supersedable, and scoped to the proper project and governance boundary.

## Consequences

Memory retrieval must prefer relevant, current, evidence-backed knowledge and
must disclose uncertainty or conflicts rather than presenting stale facts.

## Implementation evidence

`projects.memory_engine` persists only structured `MEMORY` Cognitive State
entries. Each entry cites active same-project state attributes, retains
allowlisted provenance and confidence, and supersedes a prior memory with the
same key rather than deleting it. Retrieval ranks active structured tags and
values deterministically; it never searches `FactoryChatMessage` transcript
rows. Provider output remains a proposed observation validated by Orki code.

Memory creates no accepted AKB knowledge, plan, governance approval, delivery
work, or execution authority. The independent Release Gate evidence is
[`ORKI-006 Memory Intelligence`](../../evidence/sprint-orki-006-memory-intelligence-20260802/ASSESSMENT.md).
