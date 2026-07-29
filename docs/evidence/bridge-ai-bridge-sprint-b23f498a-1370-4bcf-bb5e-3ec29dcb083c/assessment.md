# Sprint 2 engineering-memory assessment

- Scope: `bridge:ai-bridge:sprint:b23f498a-1370-4bcf-bb5e-3ec29dcb083c`
- Contract: `bridge:ai-bridge:contract:3934ff62-7c60-426e-8a2b-d6292aea4ed3`
- Contract SHA-256: `2517ad4089c79f2e73580b373c18fa9609ec49d60177a8f997f2edf02d906196`
- Baseline: `9973ef315f0ddae78076aea9df3c0d2f897fdebf`
- Assessment date: 2026-07-29

## Implemented scope evidence

`EngineeringEntity`, `EngineeringEntityRevision`, and
`EngineeringRelationship` provide project-isolated, versioned engineering
objects and typed, evidence-bearing edges. Candidate authoring is separate
from approval-gated activation. Revision snapshots are append-only and expose
read-only history and revision diffs.

The governed MCP surface provides generic engineering search, entity lookup,
candidate upsert/review, relationship, impact, history, and planning tools,
plus first-class Roadmap, Constitution, UI Plan, and System Design adapters.
All adapter operations are included in the durable MCP audit metadata.

Lifecycle writers create idempotent, reviewable candidates for Sprint
completion, gate results, remediation completion, incident resolution, and
release completion. None auto-publishes knowledge. Deployment and rollback
ingestion are not claimed: the current lifecycle does not emit those events.

## Acceptance checks

| Required capability | Evidence | Result |
| --- | --- | --- |
| Project-isolated entities and typed relations | `test_relationships_are_typed_project_isolated_and_queryable_by_role` | PASS |
| Candidate/version/approval history | `test_candidate_activation_has_approval_and_append_only_history` | PASS |
| Five lifecycle event classes, retry safety | `test_all_required_lifecycle_events_are_retry_safe_candidates` | PASS |
| Roadmap, Constitution, UI Plan, System Design adapters | `test_first_class_adapters_validate_structured_objects_and_versions` | PASS |
| Constitution history and immutable diff | `test_constitution_diff_and_history_are_project_isolated` | PASS |
| Planning gaps, prerequisites, GitHub conflicts | `test_planning_assessment_finds_gaps_prerequisites_and_conflicts` | PASS |
| Repository regression suite | `pytest` | PASS: 138 passed |
| Static quality and schema drift | `ruff check .`, `mypy .`, `makemigrations --check --dry-run`, `manage.py check` | PASS |
| Sprint 2 published scope binding | direct canonical hash comparison | PASS |

## Canonical-publication remediation

The required `python manage.py validate_scopes` gate initially identified one
pre-existing inconsistency: the Sprint 1 publication at
`docs/sprints/5977cb4b-715c-4fd6-8fff-f4763a09e7ea-sprint-1-akb-foundation-and-chatgpt-management.md`
still represented the earlier `APPROVED` record while its durable scope record
had transitioned to `COMPLETED`. The document was restored to the exact output
of `render_scope` for the existing, completed Sprint 1 record; no scope was
created, no Sprint 2 field changed, and hash validation remained enabled.

The rerun now reports `All canonical scopes are valid.` The restored document
equals the deterministic renderer byte-for-byte and carries the durable
content hash `35eac454c4ce4e67f6d088f43d8ca4d9e251b25c3b3714f3aefe1ecdf3f4218d`.

## Final release-gate rerun

| Command | Result |
| --- | --- |
| `python manage.py makemigrations --check` | PASS |
| `python manage.py check` | PASS |
| `pytest` | PASS: 138 passed |
| `ruff check .` | PASS |
| `mypy .` | PASS: 109 source files |
| `python manage.py validate_scopes` | PASS |
| `git diff --check` | PASS |
