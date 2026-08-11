---
architecture_status: CANONICAL
owner: Architecture
classification: VISUAL CONSTITUTION INDEX
language: en
version: 1.0.0
---

# AI Bridge Visual Constitution

This directory is the canonical visual companion to the Architecture
Constitution. Each numbered directory contains one editable `.drawio` source
and its governed Markdown companion. The `.drawio` file is authoritative;
PNG, SVG, and PDF files are derived artifacts and are not required to be
committed for every architectural change.

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
| [01 Conversation Layer](01-conversation-layer/README.md) | Human interaction through Mission intake | CANONICAL |
| [02 Runtime Boundary](02-runtime-boundary/README.md) | Mission as unified runtime intake | CANONICAL |
| [03 Mission & MSM](03-mission-msm/README.md) | Mission lifecycle ownership | CANONICAL |
| [04 Operational Foundation](04-operational-foundation/README.md) | Governed operational delivery boundary | CANONICAL |
| [05 Planning Engine](05-planning-engine/README.md) | Stateless planning capability | CANONICAL |
| [06 Workflow Engine](06-workflow-engine/README.md) | Stateless workflow capability | CANONICAL |
| [07 AI Kernel](07-ai-kernel/README.md) | Kernel-owned technical execution core | CANONICAL |
| [08 Execution Layer](08-execution-layer/README.md) | First-class Execution and recovery | CANONICAL |
| [09 Provider Layer](09-provider-layer/README.md) | Provider integration and immutable binding | CANONICAL |
| [10 Knowledge & AKB](10-knowledge-akb/README.md) | Knowledge Objects and Context Packages | CANONICAL |
| [11 Repository Lifecycle](11-repository-lifecycle/README.md) | Scoped repository resource and knowledge changes | CANONICAL |
| [12 Reflection & Learning](12-reflection-learning/README.md) | Evidence-led learning and publication | CANONICAL |
| [99 Full Architecture](99-full-architecture/README.md) | Cross-layer target architecture | CANONICAL |

## Change policy

Architecture changes are incomplete until the affected Constitution chapters,
diagrams, Markdown companions, cross-references, and Diagram Impact Assessment
agree. See Article V, Architecture Documentation Governance.
