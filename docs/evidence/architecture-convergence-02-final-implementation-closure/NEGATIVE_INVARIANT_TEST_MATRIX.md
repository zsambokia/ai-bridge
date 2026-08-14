# Negative invariant test matrix

| Invariant | Test evidence |
| --- | --- |
| Cross-project resource injection cannot reach retrieval | `test_l0_rejects_cross_project_knowledge_before_context_retrieval` |
| Unresolved profile emits no cognitive result | `test_unresolved_profile_has_explicit_return_without_cognitive_result` |
| Deny overrides Allow | `test_zoning_denies_even_when_an_allow_exists` |
| Missing return Allow fails closed | `test_ffs_resolves_only_the_published_service_and_requires_each_direction` |
| Wrong Node/service ownership fails | `test_ffs_resolves_only_the_published_service_and_requires_each_direction` |
| Scope, Evidence, Results, Claims and packets cannot mutate | Protocol immutability tests |
| Artifact does not publish without explicit approval | `test_scope_provenance_and_artifact_candidates_are_append_only` |
| Claim cannot omit accountable ownership | `test_r22_claim_has_owner_and_references_without_resolving_domain_state` |
| Cognitive Processing does not mutate Mission or publish Knowledge | End-to-end boundary assertions |
