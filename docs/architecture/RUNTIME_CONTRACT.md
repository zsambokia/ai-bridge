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

The legacy OrkiKnowledgeIntegration path is a separate compatibility adapter:

> Deprecated compatibility adapter.
>
> Maintained only during Runtime → Knowledge Pipeline migration.
> New Runtime implementations MUST NOT depend on this component.
> Scheduled for removal after Sprint 06.

This adapter is isolated from the canonical Runtime flow and is not extended by new
Runtime functionality.

## Validation and evidence

projects.runtime_contract is the single schema authority. Its validators enforce
schema version, allowed fields, required fields, recursive ownership purity, and
confidence/tag constraints before a candidate is stored. Regression tests prove
explicit field persistence without generic payload; rejection of embedding,
knowledge_entry_id, vector_id, and activation; no KnowledgeEntry creation on the
canonical Runtime path; and immutable candidates after creation.
