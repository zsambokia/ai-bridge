# Sprint 05 – Orki Runtime Orchestrator

Status: APPROVED — Factory Development Mode enabled by Product Owner.

This is an evolutionary migration of the existing Runtime, not a destructive
rewrite. The canonical path is:

```text
StructuredDecision -> Planning -> Execution -> Verification
-> ReflectionCandidate -> KnowledgeCandidate
```

Runtime owns execution coordination, verification, reflection-candidate and
knowledge-candidate production. It does not select business candidates, mutate
AKB, activate knowledge, generate embeddings, or update a vector index.

The existing Factory Runtime Knowledge Integration remains operational only
behind `projects.runtime_knowledge_compat`, a deprecated compatibility adapter.
Sprint 06 owns promotion, governance, AKB mutation, embedding, and indexing.

Release gates: repository Ruff, mypy, Django and migration checks; unit,
integration, Factory Acceptance and full regression; current architecture and
evidence. Technical failures follow DETECT → DIAGNOSE → REPAIR → RERUN.
