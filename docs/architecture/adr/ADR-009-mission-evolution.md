---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# ADR-009 - Mission Evolution

**Status:** Accepted architectural boundary; mission capability implementation is evidenced by ORKI-002.

## Decision

Mission, roadmap, and sprint strategy are living Cognitive State entities.
Evidence, accepted decisions, changing constraints, and delivery outcomes may
propose revisions with provenance and an explicit approval boundary.

## Consequences

Orki must distinguish an observed change, a proposed evolution, and an accepted
mission change. It must not overwrite accepted intent from conversation alone.
