# Sprint 7 assessment — Autonomous Technical Remediation and Self-Healing Proof

Date: 2026-07-31

## Authority and boundary

This is Factory Development Mode work for `zsambokia/ai-bridge`, on `main`
from baseline `f7c69661f404c74bb67ec4a1ee2cc5ab910416e3`. It implements only
Sprint 7 of the canonical Factory Readiness Remediation Epic. Sprint 6 is
still `BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE`; no Sprint 6 evidence
or status was changed.

## Finding

The existing lifecycle could create durable, governed remediation for selected
failures, but an otherwise unclassified worker exception could leave a leased
job without a canonical remediation record. It also did not preserve the
original lifecycle checkpoint as an explicit resume target, did not record
independent validation separately, and did not present the complete repair
chain through the read-only MCP projection.

## Implemented decision

Unknown worker exceptions now create one bounded `TechnicalRemediationLoop`
with a `FailureIncident`, ownership assessment, evidence references, a
child `WORK_ITEM`, and an immutable checkpoint of the parent execution. The
worker releases its lease and records `TECHNICAL_REMEDIATION_OPENED`; it
never becomes silently quiet in an in-between state. Passing independent
validation closes the incident, records a reviewable AKB candidate, restores
that exact checkpoint, and queues the original job/run rather than creating a
replacement execution.

Technical remediation is limited to three attempts for one run/gate pair. The
limit is an explicit audited `REPAIRING` state that releases the job; it is
not a loop and is not misclassified as a Product Owner decision. Actual
business ambiguity uses the separate, durable Product Owner escalation path.

## Scope exclusions

No external ChatGPT Business UI certification was claimed. That dependency
remains in the separate ChatGPT Business Platform Certification Epic.

