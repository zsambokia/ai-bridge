# Clarification and stale-confirmation proofs

`projects/tests/test_scopes.py::test_clarifications_create_a_new_confirmable_proposal_version`
proves that a material clarification creates a revised proposal version and
prevents confirmation until that revision is displayed.

`projects/tests/test_governed_mcp.py::test_conversational_confirmation_binds_the_current_exact_review`
proves that `conversation.confirm` requires the current proposal version and
exact SHA-256 proposal hash, accepts a bounded affirmative confirmation, and
rejects an unsuitable confirmation. A stale version or hash therefore cannot
authorize a changed proposal.

The final repository gate run executed these tests as part of `pytest -q` and
passed with 46 tests.
