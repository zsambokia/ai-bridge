# Repository Bootstrap Lifecycle acceptance results

## Executable proof

`projects/tests/test_repository_lifecycle.py` proves the canonical lifecycle
with a provider test double:

| Acceptance | Result | Evidence |
| --- | --- | --- |
| Create and import converge | PASS | parametrized `test_create_and_import_converge_on_governed_repository_akb_pipeline` |
| Content-first document classification | PASS | Constitution, System Design and Roadmap fixture content classifies into corresponding AKB types |
| Governed AKB construction | PASS | three approved active entries, revisions and repository receipts |
| Derived semantic layer | PASS | one embedding per active entry |
| Semantic retrieval | PASS | persisted `KnowledgeContextPackage` contains the matching Constitution entry |
| Idempotent retry | PASS | repeated bootstrap returns original receipts without new entries |
| Incremental sync | PASS | changed document only; prior entry becomes `STALE`; two embeddings total |

## Repository-wide Release Gate

Executed from the final implementation worktree:

```text
python -m pytest -q                 PASS  367 passed in 108.58s
ruff check .                        PASS  all checks passed
mypy .                              PASS  success: no issues in 248 source files
python manage.py validate_scopes    PASS  all canonical scopes valid
python manage.py makemigrations --check --dry-run  PASS  no changes detected
```

## Honest remote-provider boundary

No live GitHub credentials or safe remote proof target were supplied. The
existing GitHub adapter is proved only for branch reads, so clone, remote
creation, history/diff and webhook execution are deliberately not certified.
The provider port is implemented and tested locally; a concrete remote GitHub
adapter must receive its own governed evidence before those capabilities can be
claimed.
