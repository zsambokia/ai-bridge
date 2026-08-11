---
architecture_status: CANONICAL
owner: Architecture
classification: VISUAL CONSTITUTION
language: en
---
# Diagram 09 — Provider Layer

## Purpose

Canonical logical source: [`09_PROVIDER_LAYER.md`](09_PROVIDER_LAYER.md) (Mermaid). The `.drawio` file is its derived, editable visual representation.

Defines the canonical technical provider route from Execution to external
capability infrastructure.

## Responsibility and ownership

Provider Integration is a Kernel boundary; Provider Resolver selects a
stateless Provider definition; Provider creates a stateful Provider Executor.
The Provider owns neither Mission, Execution, Context, AKB, nor Evidence.

## Contracts, lifecycle, and rules

The route is `Execution -> Provider Integration -> Provider Resolver ->
Provider -> Provider Executor`. Runtime Profile declares checkpoint, resume,
recovery, streaming, migration, and lease support. Binding remains immutable.

## Failure, evidence, and open questions

Executor replacement and recovery remain on the same Provider. Provider Gateway
is Historical / Transitional implementation terminology only. Provider-specific
credentials and protocols are implementation concerns.

## Related authority and maintenance

Provider Architecture v2 and Article III — AI Kernel Architecture.
