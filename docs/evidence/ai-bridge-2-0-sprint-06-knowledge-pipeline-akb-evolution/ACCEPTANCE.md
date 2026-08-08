# Factory Acceptance Evidence

All scenarios were executed against the Django test database using real model,
governance, embedding-cache and vector-store contracts.

| Scenario | Executed proof | Result |
| --- | --- | --- |
| Candidate to governed active knowledge | `test_pipeline_requires_governed_promotion_then_indexes_and_retrieves` creates a real Runtime candidate, requests review, supplies a real `GovernanceApproval`, indexes it, and retrieves it semantically. | PASS |
| Duplicate protection | `test_pipeline_deduplicates_content_without_second_akb_or_vector_mutation` processes equivalent candidates and proves one AKB entry and no premature embedding. | PASS |
| Negative governance path | `test_pipeline_rejects_unapproved_promotion_without_activating_knowledge` proves promotion without an approval reference fails and creates no embedding. | PASS |
| Canonical Factory Acceptance | `projects/tests/test_factory_acceptance_suite.py` | PASS (2 tests) |
| Canonical Runtime mission E2E | `projects/tests/test_orki_runtime_mission_e2e.py` | PASS (2 tests) |

The focused pipeline command was:

```text
python -m pytest projects/tests/test_knowledge_pipeline.py --durations=3 -q
```

It passed 3 tests in 3.60 seconds. The Factory Acceptance and Runtime mission
E2E commands each passed their two tests.
