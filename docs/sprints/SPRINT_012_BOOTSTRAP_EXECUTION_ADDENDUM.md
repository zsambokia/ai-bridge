# Sprint 012 — One-Time Bootstrap Execution Addendum

**Status:** APPROVED BOOTSTRAP AUTHORITY  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Target Sprint:** `SPRINT_012_EXISTING_CONVERSATIONAL_CONFIRMATION_PATH_ASSESSMENT_AND_REPAIR.md`  
**Bootstrap approval reference:** `PO-BOOTSTRAP-SPRINT-012-2026-07-26`

## 1. Purpose

Sprint 012 exists to assess and repair the conversational confirmation path that should convert one authenticated Product Owner reply into durable governed approval and execution orchestration.

That capability is itself required for Sprint 012 to obtain the normal durable conversational approval needed to execute. This creates a temporary bootstrap deadlock.

For Sprint 012 only, the exact Sprint 012 scope document together with this addendum authorizes Codex to perform the assessment, minimal repair, remote verification, evidence, documentation, release gates, commit, and push required by Sprint 012 without first obtaining a normally issued AI Bridge Execution Contract.

This is a one-time bootstrap exception. It is not a permanent alternative approval path.

## 2. Exact authorized scope

The bootstrap authority applies only to the exact contents of:

1. `docs/sprints/SPRINT_012_EXISTING_CONVERSATIONAL_CONFIRMATION_PATH_ASSESSMENT_AND_REPAIR.md`
2. `docs/sprints/SPRINT_012_BOOTSTRAP_EXECUTION_ADDENDUM.md`

Codex must bind execution to the repository commits and content hashes of both documents before implementation.

Any material scope change requires a new Product Owner decision and invalidates this bootstrap authority until reconfirmed.

## 3. Mandatory assessment-first rule

This exception does not authorize Codex to skip Sprint 012 Phase A.

Before changing implementation code, Codex must determine whether the repository already contains an adequate canonical conversational confirmation solution.

Codex must not create a new adapter, approval subsystem, or parallel lifecycle unless it first proves and documents a genuine architectural gap.

The preferred result remains the smallest repair to the existing canonical path.

## 4. Authorized actions

Within the exact Sprint 012 scope, Codex may:

- inspect repository and runtime state;
- reconstruct the failed `APPROVAL_REQUIRED` path;
- compare repository and deployed tool surfaces;
- repair existing MCP exposure, routing, tool metadata, continuation data, identity/reference derivation, deployment synchronization, or implementation defects;
- add or update tests;
- run the required remote confirmation proof;
- update required documentation and evidence;
- run all required Release Gates;
- commit and push the completed Sprint 012 result to `origin/main`.

## 5. Prohibited use

This bootstrap authority must not be used to:

- authorize work outside Sprint 012;
- authorize Sprint 013 or any other Sprint or Work Item;
- bypass the mandatory assessment-first phase;
- justify an unnecessary new adapter;
- weaken exact proposal-version or hash binding;
- weaken Product Owner identity or durable-reference requirements;
- bypass Release Gates or evidence requirements;
- fabricate remote deployment, provider, approval, execution, test, or evidence results;
- authorize production deployment, destructive operations, secret changes, payments, or legal decisions;
- become a reusable fallback when normal conversational confirmation fails.

## 6. Normal-path proof remains mandatory

The fresh `confirmationproof` Work Item required by Sprint 012 must run through the corrected normal conversational confirmation path.

The bootstrap exception may authorize implementation of Sprint 012, but it must not be used as the approval authority for the `confirmationproof` acceptance scenario.

The acceptance scenario must prove:

```text
proposal
→ review
→ Product Owner: "Igen, jó lesz."
→ conversation.confirm
→ durable GovernanceApproval
→ durable ConversationOrchestration
→ canonical governed lifecycle
```

It must also prove that `scope.approve` remains a strict lower-level operation requiring pre-existing durable authority.

## 7. Retrospective canonical recording

Before Sprint 012 is reported complete, Codex must record or reconcile truthful canonical metadata for this bootstrap execution, including:

- Sprint 012 document paths;
- document commits and content hashes;
- bootstrap approval reference `PO-BOOTSTRAP-SPRINT-012-2026-07-26`;
- executor identity;
- assessment result;
- implementation commit;
- Release Gate results;
- evidence root;
- final status;
- explicit bootstrap retirement.

Only actually completed events may be recorded as completed.

## 8. Retirement condition

The bootstrap authority is automatically retired when Sprint 012 reaches either terminal state:

```text
PASS — READY FOR PRODUCT OWNER ACCEPTANCE
FAIL — BLOCKED
```

After retirement, the same reference must not authorize retries, new work, amendments, or any later Sprint.

## 9. Required evidence

Add to `docs/evidence/sprint-012/`:

```text
BOOTSTRAP_AUTHORITY_AND_RETIREMENT_PROOF.md
```

The evidence must bind:

- both Sprint 012 documents;
- their commits and hashes;
- the bootstrap approval reference;
- the exact authorized scope;
- the executor;
- the assessment-first result;
- the final implementation commit;
- Release Gate results;
- the normal-path `confirmationproof` acceptance;
- explicit retirement of the exception.

## 10. Product Owner authorization

The Product Owner authorizes this exact one-time exception so Sprint 012 can assess and repair the normal conversational approval path that will remove the need for future bootstrap handling.

This authorization does not relax the permanent governance model. It exists only to eliminate the current bootstrap deadlock and must be retired at Sprint completion.
