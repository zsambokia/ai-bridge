---
status: CANONICAL
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Engine Constitution

An Engine is the exclusive owner of one bounded domain concern, such as
Planning, Workflow, Repository, Knowledge, Reflection, Learning, Deployment,
or Documentation. This document is the one common Engine constitution; domain
documents refine their own concerns and MUST NOT create parallel Engine
constitutions.

An Engine:

- SHALL own its domain model, permitted internal transitions, and produced
  evidence;
- MAY consume an MSM-authorized Work Item and emit a durable result or
  immutable Execution Request;
- MUST NOT create an Operational Work Item or a Mission transition;
- MUST NOT directly invoke another Engine, the Operational Foundation's
  internals, Provider Gateway, Provider, or `ExecutionRun`;
- MUST NOT write another Engine's state;
- MUST NOT ask the Product Owner directly; unresolved intent is reported to the
  MSM through an Execution Request or result.

The MSM coordinates across domains without inheriting their business logic.
Provider output remains untrusted input until handled by the owning boundary.

