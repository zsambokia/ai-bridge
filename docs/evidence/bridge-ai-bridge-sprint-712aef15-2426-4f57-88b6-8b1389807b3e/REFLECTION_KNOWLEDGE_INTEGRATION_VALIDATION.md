# Reflection and Knowledge Integration validation

The post-execution OESM path is `RUNNING -> VERIFYING -> REFLECTING -> KNOWLEDGE_INTEGRATING -> COMPLETED`.

- Goal Integrity Validation consumes observed repository changes, build result, regression result, original outcome, original acceptance checks and evidence references.
- Failed objective verification returns to `WAITING_EXTERNAL`, from which the existing Runtime recovery reassessment returns to `PLANNING`.
- `OrkiReflection` is append-only run analysis with evidence references; it does not write Cognitive State.
- `OrkiKnowledgeIntegration` is created only after `reflection.completed`; its only successful Foundation action is creation of a governed `KnowledgeEntry` candidate.
- The candidate remains `CANDIDATE`; the existing AKB owner retains review, acceptance, activation and indexing authority.
- No `embedding.generated` event is emitted while the entry is a candidate.

`projects.tests.test_factory_acceptance_suite` asserts event ordering, candidate status, absence of the embedding event, absence of Cognitive State writes and evidence references on every Runtime event.
