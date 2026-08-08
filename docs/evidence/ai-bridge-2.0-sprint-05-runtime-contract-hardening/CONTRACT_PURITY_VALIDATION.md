# Contract Purity Validation

## Schema controls

Both candidate types require RuntimeCandidate.v1, explicit allow-lists, required
fields, confidence validation, evidence references, and recursive key inspection.
They reject embedding, embedding_vector, vector, vector_id, vector_row,
vector_store, knowledge_entry, knowledge_entry_id, activation, activation_status,
activated, index, index_id, lifecycle, akb, akb_id, and knowledge_document.

## Regression evidence

projects/tests/test_runtime_contract.py proves:

- explicit persisted fields and no generic payload;
- rejection of embedding, knowledge_entry_id, vector_id, and activation;
- no KnowledgeEntry created by canonical execution; and
- reflection and knowledge candidates reject mutation after creation.

Targeted contract tests: PASS — 5 passed.
