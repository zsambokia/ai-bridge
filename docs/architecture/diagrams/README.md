---
architecture_status: CANONICAL
owner: Architecture
classification: VISUAL CONSTITUTION INDEX
language: en
version: 1.0.0
---

# AI Bridge Visual Constitution

This directory is the canonical visual companion to the Architecture
Constitution. Each numbered directory contains a version-controlled Markdown
document with Mermaid as its canonical logical source, a governed `README.md`,
and, where useful, an editable derived `.drawio` visual representation.
Mermaid is authoritative when sources differ; PNG, SVG, and PDF files are
derived artifacts and are not required for every architectural change.

## Status vocabulary

The permitted Architecture Status values are `DRAFT`, `ASSESSMENT`,
`APPROVED`, `CANONICAL`, `TRANSITIONAL`, `HISTORICAL`, and `DEPRECATED`, as
defined by [ADG-107](../ARCHITECTURE_CONSTITUTION.md). Diagrams in this initial
set are `CANONICAL` unless their own visible metadata says otherwise. Dashed
Historical / Transitional elements are explanatory only and never a target
architecture contract.

## Diagram set

| Diagram | Scope | Status |
| --- | --- | --- |
| [01 Conversation Layer](01-conversation-layer/01_CONVERSATION_LAYER.md) | Human interaction through Mission intake | CANONICAL |
| [02 Runtime Boundary](02-runtime-boundary/02_RUNTIME_BOUNDARY.md) | Mission as unified runtime intake | CANONICAL |
| [03 Mission & MSM](03-mission-msm/03_MISSION_MSM.md) | Mission lifecycle ownership | CANONICAL |
| [04 Operational Foundation](04-operational-foundation/04_OPERATIONAL_FOUNDATION.md) | Governed operational delivery boundary | CANONICAL |
| [05 Planning Engine](05-planning-engine/05_PLANNING_ENGINE.md) | Stateless planning capability | CANONICAL |
| [06 Workflow Engine](06-workflow-engine/06_WORKFLOW_ENGINE.md) | Stateless workflow capability | CANONICAL |
| [07 AI Kernel](07-ai-kernel/07_AI_KERNEL.md) | Kernel-owned technical execution core | CANONICAL |
| [08 Execution Layer](08-execution-layer/08_EXECUTION_LAYER.md) | First-class Execution and recovery | CANONICAL |
| [09 Provider Layer](09-provider-layer/09_PROVIDER_LAYER.md) | Provider integration and immutable binding | CANONICAL |
| [10 Knowledge & AKB](10-knowledge-akb/10_KNOWLEDGE_AKB.md) | Knowledge Objects and Context Packages | CANONICAL |
| [11 Repository Lifecycle](11-repository-lifecycle/11_REPOSITORY_LIFECYCLE.md) | Scoped repository resource and knowledge changes | CANONICAL |
| [12 Reflection & Learning](12-reflection-learning/12_REFLECTION_LEARNING.md) | Evidence-led learning and publication | CANONICAL |
| [13 Factory Protocol](13-factory-protocol/13_FACTORY_PROTOCOL.md) | FactoryIP L0-L4 and logical boundary control plane | CANONICAL |
| [99 Full Architecture](99-full-architecture/99_FULL_ARCHITECTURE.md) | Cross-layer target architecture | CANONICAL |

## Change policy

Architecture changes are incomplete until the affected Constitution chapters,
diagrams, Markdown companions, cross-references, and Diagram Impact Assessment
agree. See Article V, Architecture Documentation Governance.
