# ADR-012: Product Owner Model Confidence and Drift

**Status:** Implemented in ORKI-009; Product Owner model evolution accepted.
**Date:** 2026-08-02

## Context

ORKI-008 established a project-aware, evidence-bound Product Owner Cognitive
Model. The Product Owner required that it explicitly show how certain it is,
how the supporting evidence affects confidence, and when a working pattern has
genuinely changed over time.

## Decision

Keep the Product Owner Cognitive Model as revisioned Cognitive State entries.
For every profile revision, calculate and expose confidence from a declared
value (60%) and the mean confidence of its referenced state evidence (40%).
Retain every revision and derive a cognitive-drift record when consecutive
preferences for the same dimension differ.

If referenced evidence lacks numeric confidence, report its unscored count and
use the declared confidence without fabricating a numeric evidence contribution.

The result is project-scoped, explainable and correctable. Evidence views
contain state identifiers, allowed attributes, confidence and source message
identifiers only; raw transcript content remains excluded. Drift is descriptive
and grants neither decision nor execution authority.

## Consequences

- Profile evolution is reviewable rather than a silent overwrite.
- A Product Owner can distinguish an evidence-supported operational change
  from the previous working pattern and issue a correction where needed.
- Recommendation Intelligence remains out of ORKI-009. Its later Operational
  Reasoning Engine must consume this projection only as bounded, disclosed
  context and must prove the effect independently.
