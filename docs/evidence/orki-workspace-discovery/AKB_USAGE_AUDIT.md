# AKB Usage Audit

## Direct model access inventory

| Location | Direct access | Classification / action |
| --- | --- | --- |
| `projects/knowledge.py` | `KnowledgeEntry`, `KnowledgeContextPackage` lifecycle/query/create | Canonical AKB owner; retain. |
| `projects/knowledge_pipeline.py` | all three models for promotion, indexing and retrieval persistence | Canonical pipeline owner; retain. |
| `projects/semantic/intelligence.py` | `KnowledgeEntry`, `SemanticEmbedding` ranking/indexing | Canonical semantic owner; retain. |
| `projects/repository_lifecycle.py` | `KnowledgeEntry`, `SemanticEmbedding` bootstrap/sync | Canonical repository-to-AKB owner; retain. |
| `projects/factory_memory.py` | `KnowledgeEntry` review queue | Replace with a knowledge projection/service before a dedicated Workspace page. |
| `projects/factory_chat.py` | latest `KnowledgeContextPackage` for display | Replace with a Context Package projection service before expansion. |
| `projects/governed_mcp.py` | entry/package tools | Retain as governed MCP boundary. |
| `projects/admin.py` | registrations | Retain administration-only access. |
| `projects/incidents.py` | KnowledgeEntry from incident closure | Retain domain hand-off, subject to pipeline review. |
| `projects/github_provider_e2e.py` | direct queries/deletes/get for proof fixture | Test/proof-only; never expose through Workspace/runtime. |
| tests/migrations/models | fixtures, assertions, relations | Non-production access; no Workspace consequence. |

## Runtime rule

`projects/orki_runtime.py` does not import or query `KnowledgeEntry`,
`SemanticEmbedding`, or `KnowledgeContextPackage`. Preserve this. The runtime
must receive a package/reference through a canonical execution boundary; the
Workspace must call a projection/retrieval service, never those models.

## Evidence method

The inventory is derived from a repository-wide symbol search for the three
model names, then classified against `KNOWLEDGE_PIPELINE.md` and the owning
modules above. It deliberately distinguishes owner/service access from UI
projection shortcuts.
