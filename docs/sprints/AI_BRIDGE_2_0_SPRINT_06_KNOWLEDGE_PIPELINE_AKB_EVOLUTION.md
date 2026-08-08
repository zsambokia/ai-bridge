# AI Bridge 2.0 — Sprint 06: Knowledge Pipeline & AKB Evolution

**Status:** APPROVED
**Execution mode:** Factory Development Mode
**Handoff identifier:** `AI-BRIDGE-2.0-SPRINT-06-FDM-20260808`

## Authority

Product Owner authority is used for AI Bridge self-development. Codex may
proceed without an AI Bridge-managed provider execution, active provider
heartbeat, or Bridge-issued running execution while the managed runtime is not
yet proven stable. This authority applies only to this Factory Development Mode
phase.

## Objective

Implement the first independent Knowledge Pipeline. It begins where the
Runtime ends and consumes `RuntimeKnowledgeCandidate.v1`; the Runtime remains
unchanged and is a stable platform for this Sprint.

## Approved scope

```text
RuntimeKnowledgeCandidate.v1
        ↓
Knowledge Validation
        ↓
Knowledge Normalization
        ↓
Knowledge Classification
        ↓
Knowledge Deduplication
        ↓
Knowledge Promotion
        ↓
KnowledgeEntry
        ↓
Embedding
        ↓
Vector Store
        ↓
Semantic Index
        ↓
AKB
        ↓
Semantic Retrieval
        ↓
KnowledgeContextPackage
```

The pipeline must preserve provenance and an auditable evidence trail. A
promotion is an explicit governed action: the pipeline may validate and apply
an approved promotion, but must not make a business decision autonomously.

## Explicit exclusions and frozen components

The following components must not be modified by this Sprint:

- Orki Runtime and its state machine;
- Semantic Layer;
- Reasoning Framework;
- Structured Decision Framework;
- Provider Gateway; and
- `projects/runtime_knowledge_compat.py`.

`runtime_knowledge_compat.py` remains an unchanged, deprecated compatibility
layer. It is not part of the canonical pipeline; removal is deferred to the
future Runtime Cleanup migration Sprint.

## Acceptance scenarios

1. A valid runtime knowledge candidate is validated, normalized, classified,
   recorded as an AKB candidate, and carries provenance and evidence.
2. A governed approval promotes that candidate to an active `KnowledgeEntry`,
   generates an embedding after AKB activation, and makes it retrievable from
   the semantic index.
3. A repeated equivalent candidate is deterministically deduplicated without a
   duplicate AKB entry or vector record.
4. Invalid, unsupported, and unapproved inputs cannot mutate active knowledge.
5. Semantic retrieval is represented as a durable `KnowledgeContextPackage`.

## Required closure

All repository and Sprint Release Gates, unit, integration, Factory Acceptance,
canonical E2E, complete regression, documentation, AKB update, and final
evidence must pass before the only successful closure state:

```text
PASS — READY FOR PRODUCT OWNER REVIEW
```

Evidence root: `docs/evidence/ai-bridge-2-0-sprint-06-knowledge-pipeline-akb-evolution/`.
