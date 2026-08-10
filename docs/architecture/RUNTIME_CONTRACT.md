---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Runtime Candidate Contract

## Purpose

The canonical Runtime produces only immutable ReflectionCandidate and
KnowledgeCandidate records. These are evidence-bearing proposals for the future
Knowledge Pipeline; they are neither AKB records nor vector-index documents.

## Canonical flow

StructuredDecision -> Planning -> Execution -> Verification ->
RuntimeReflectionCandidate -> RuntimeKnowledgeCandidate ->
Knowledge Pipeline (Sprint 06 ownership).

## Canonical contracts

Both records use RuntimeCandidate.v1, explicit allow-lists, required fields,
recursive forbidden-field validation, and model-level immutability after creation.

RuntimeReflectionCandidate contains goal_id, execution, summary, reflection_text,
verification_result, confidence, evidence_references, and created_at.

RuntimeKnowledgeCandidate contains title, summary, body, reason, confidence, tags,
execution, reflection_candidate, evidence_references, and created_at.

The validators reject unknown fields and recursively reject embedding,
embedding_vector, vector, vector_id, vector_row, vector_store, knowledge_entry,
knowledge_entry_id, activation, activation_status, activated, index, index_id,
lifecycle, akb, akb_id, and knowledge_document.

## Ownership boundary

The Runtime owns planning, execution, verification, reflection-candidate
production, and knowledge-candidate production. It does not generate embeddings,
write vectors, mutate AKB, activate knowledge, or construct KnowledgeEntry objects
on the canonical structured-decision path.

The active legacy OrkiKnowledgeIntegration adapter was removed by the Post-MVP
Runtime Cleanup. Historical integration rows remain readable audit data only;
no active Runtime path creates or updates them.

The removed adapter is retained only in historical evidence and migration records;
it is not part of the current Runtime contract.

## Validation and evidence

projects.runtime_contract is the single schema authority. Its validators enforce
schema version, allowed fields, required fields, recursive ownership purity, and
confidence/tag constraints before a candidate is stored. Regression tests prove
explicit field persistence without generic payload; rejection of embedding,
knowledge_entry_id, vector_id, and activation; no KnowledgeEntry creation on the
canonical Runtime path; and immutable candidates after creation.

## Sprint 06 consumption boundary

Sprint 06 consumes `RuntimeKnowledgeCandidate.v1` through the independent
[Knowledge Pipeline](KNOWLEDGE_PIPELINE.md). The Pipeline validates,
normalizes, mechanically classifies and deduplicates candidates, then creates a
governed `KnowledgeEntry` candidate. It can activate and index an entry only
after an explicit AKB governance approval. This is a downstream consumer
boundary: the canonical Runtime does not change as part of that Pipeline.
