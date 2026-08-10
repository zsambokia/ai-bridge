---
status: TRANSITIONAL
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Workflow Engine architecture

## Purpose

The Workflow Engine realizes an approved plan as durable workflow instances, steps and tasks. It is not the conversation orchestrator, planning authority, or raw provider client.

## Workflow State Machine (WSM)

```text
CREATED -> SELECT_WORKFLOW -> CREATE_INSTANCE -> RUNNING_STEP
RUNNING_STEP -> WAITING -> RUNNING_STEP
RUNNING_STEP -> RETRY -> RUNNING_STEP
RUNNING_STEP -> COMPLETED
```

`FAILED` and `CANCELLED` are terminal outcomes. `WAITING` is used for an external dependency, scheduled retry, approval, or human input; it must have a durable wait reason and resumption trigger. The current `READY` state may be retained as an implementation scheduling state beneath this logical model.

## Task and ExecutionRun

A `Task` is the correct unit of business-work intent: it has purpose, input, preconditions, retry policy, result and evidence. `ExecutionRun`/`ExecutionJob` remain the governed execution authority: lease, provider worker, contract, policy and operational recovery. A Workflow task requests an ExecutionRun via an authorization port; it does not replace it.

```text
WorkflowStep owns sequencing
Task owns business outcome and retry intent
ExecutionRun owns authorized execution lifecycle
ExecutionJob owns a concrete leased attempt
```

## Current implementation assessment

The existing durable `WorkflowInstance`, `WorkflowStep`, `Task`, and `WorkflowEvent` records are useful foundation artefacts. However the current chat task adapter includes Factory-chat prompt construction and direct provider invocation. Migrate this adapter behind `ProviderGatewayPort` and a governed ExecutionRun before treating Workflow Engine as an independent engine.
