# Sprint 011 — Conversational Product Owner Review and Approval

**Status:** PROPOSED  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Execution level:** SPRINT  
**Task type:** SELF_DEVELOPMENT  
**Target branch:** `main`  

## 1. Problem statement

AI Bridge can now create a canonical proposed Work Item from a natural-language Product Owner request, but the conversation flow stops after proposal creation. The Product Owner must currently inspect Django admin or invoke later lifecycle operations manually to discover what was created and to approve it.

This is technically valid but does not yet provide the intended Product Owner experience. When the Product Owner initiates a request through ChatGPT or another conversational client, AI Bridge must return the generated proposal in the same interaction, surface any material clarification questions, and explicitly ask whether the proposal may proceed.

The intended experience is:

```text
Product Owner request
→ AI Bridge proposal
→ proposal summary returned to the requester
→ material clarification questions, if any
→ explicit "Mehet?" approval request
→ Product Owner approval
→ scope.approve
→ scope.publish
→ execution preparation and contract lifecycle
```

Django admin remains sufficient as the temporary operational and diagnostic interface. This Sprint does not require a dedicated Product Owner web UI.

## 2. Product Owner decisions

1. The conversational client is the primary review surface for requests initiated in conversation.
2. Django admin remains the temporary secondary inspection, support, and recovery interface.
3. `work_item.propose` and `sprint.propose` must return a complete, human-reviewable proposal result.
4. AI Bridge or its conversation adapter must ask material clarification questions before approval.
5. When no unresolved material ambiguity remains, the response must explicitly ask for Product Owner confirmation, using a clear equivalent of: `Mehet?`
6. Proposal creation must not itself approve, publish, prepare, issue, consume, or execute the scope.
7. A conversational affirmative response may initiate approval only through the governed approval operation and only when it can be durably bound to the exact proposal version.
8. The system must not infer approval from silence, unrelated positive language, or the original request alone when the current flow requires post-proposal confirmation.

## 3. Scope

### In scope

- Define a versioned proposal-review response contract for Sprint and Work Item proposals.
- Return the canonical proposal summary immediately after proposal creation.
- Surface deterministic policy outcome, unresolved questions, and approval eligibility.
- Ask clarification questions when `clarification_required` is true.
- Ask for explicit Product Owner approval when the proposal is eligible.
- Bind a conversational approval to the exact scope identifier and immutable proposal version or hash.
- Prevent stale, superseded, changed, rejected, or already-approved proposals from being approved accidentally.
- Expose sufficient public MCP operations and schemas for a conversational client to complete the review and approval interaction without reading the database directly.
- Preserve Django admin as a usable diagnostic and manual fallback surface.
- Add positive and negative end-to-end acceptance proofs.
- Update canonical documentation, AKB current state, roadmap, MCP reference, and tests.

### Out of scope

- A new custom Product Owner web interface.
- Orki meeting-room UI implementation.
- Automatic contract consumption or repository mutation immediately after proposal approval.
- Weakening durable Product Owner approval requirements.
- Treating free-form assistant text as execution authority.
- Replacing the canonical Bridge scope record with conversation history.

## 4. Required conversational behavior

### 4.1 Proposal response

After successful proposal creation, the public response must contain enough information for an informed Product Owner decision.

Minimum semantic response:

```yaml
proposal_review:
  project_id: "ai-bridge"
  scope_kind: "WORK_ITEM | SPRINT"
  scope_identifier: "stable identifier"
  proposal_version: "immutable version or hash"
  title: "human-readable title"
  status: "PROPOSED"
  execution_authorization: "NONE"
  work_type: "supported work type"
  execution_level: "TASK | SPRINT"
  execution_profile: "COMPACT | STANDARD | EXTENDED"
  requested_outcome: []
  in_scope: []
  out_of_scope: []
  acceptance_checks: []
  release_gates: []
  risk_modifiers: []
  policy_result: "ACCEPTED | STRENGTHENED | CLARIFICATION_REQUIRED | REJECTED"
  rationale: []
  clarification_required: false
  clarification_questions: []
  approval_eligible: true
  approval_prompt: "Mehet?"
```

Equivalent field names are acceptable if versioned and documented.

The response must not claim that approval, publication, contract issuance, or execution occurred when they did not.

### 4.2 Clarification flow

When material business ambiguity exists:

```text
proposal or classification
→ CLARIFICATION_REQUIRED
→ questions returned to Product Owner
→ Product Owner answers
→ existing proposal is revised or superseded deterministically
→ updated proposal summary is returned
→ explicit approval requested only after ambiguity is resolved
```

Questions must be limited to information that materially affects business intent, scope boundary, risk authorization, acceptance outcome, repository selection, or another governance decision.

Routine technical implementation details must remain autonomous inside the approved scope and must not generate unnecessary Product Owner questions.

### 4.3 Approval flow

A conversational approval must:

- be authenticated and auditable;
- reference the exact `scope_identifier`;
- reference the exact `proposal_version` or content hash shown to the Product Owner;
- create or bind a durable Product Owner approval reference;
- reject stale proposal versions;
- be idempotent;
- not publish automatically unless a separate explicitly governed orchestration operation is designed and documented to perform approval followed by publication;
- return the new lifecycle state and next allowed action.

Recommended canonical sequence:

```text
work_item.propose
→ proposal review response
→ Product Owner: "Mehet"
→ scope.approve
→ approval result
→ scope.publish
→ publication result
```

A higher-level orchestration tool may combine approval and publication only if:

- the internal transitions remain separately audited;
- the exact approved proposal version is bound;
- partial failure is safe and visible;
- retries are idempotent;
- no execution preparation occurs before successful publication.

## 5. Public MCP and service surface

Inspect the current public registry before implementation. Reuse existing lifecycle tools where possible.

Capabilities must include:

- propose a Work Item or Sprint;
- retrieve a human-reviewable proposal summary;
- retrieve clarification questions and approval eligibility;
- submit clarification answers or a revised proposal;
- approve an exact proposal version using a durable Product Owner approval reference;
- retrieve approval result and next action;
- publish an approved scope through the existing governed publication path.

The implementation may add a read-only operation such as:

```text
scope.get_review
```

or enrich existing `work_item.propose`, `sprint.propose`, and `scope.get` responses. Do not create duplicate sources of truth.

The public schema must be usable by ChatGPT without inventing hidden identifiers. Every identifier required by the next operation must be returned by the previous operation.

## 6. Conversation adapter requirements

If the conversational wording is produced outside the core domain service, implement a provider-independent adapter that maps canonical Bridge responses to user-facing review messages.

The adapter must:

- use the canonical structured response, not scrape rendered Markdown;
- preserve status and authorization truthfully;
- summarize without omitting approval-relevant constraints;
- present clarification questions clearly;
- ask for explicit approval only when `approval_eligible=true`;
- avoid asking `Mehet?` after `REJECTED` or while clarification remains unresolved;
- avoid automatically treating the original creation request as post-proposal approval;
- produce deterministic enough output for automated acceptance assertions.

The exact Hungarian wording may be configurable, but the default Product Owner experience must support Hungarian and should use a clear approval question equivalent to:

```text
A javasolt munkatétel elkészült. Mehet a jóváhagyás és a publikálás?
```

The system must not confuse approval with execution. The message must make clear what the next approved transition will do.

## 7. Lifecycle and invariants

Enforce the following:

1. `PROPOSED` means no execution authorization.
2. Proposal review is read-only.
3. Approval binds one exact proposal version.
4. Editing approval-relevant content invalidates or supersedes earlier approval eligibility.
5. A stale conversational approval is rejected with a deterministic error.
6. A rejected proposal cannot be approved.
7. A proposal with unresolved clarification cannot be approved.
8. Duplicate affirmative messages do not create duplicate approvals.
9. Approval does not equal publication unless a documented orchestration operation explicitly performs both transitions.
10. Publication does not equal contract issuance.
11. Contract issuance does not equal contract consumption or execution.
12. Django admin actions must use the same domain services and invariants as MCP operations.

Recommended deterministic errors:

```text
CLARIFICATION_REQUIRED
PROPOSAL_NOT_APPROVAL_ELIGIBLE
STALE_PROPOSAL_VERSION
SCOPE_ALREADY_APPROVED
SCOPE_REJECTED
APPROVAL_REFERENCE_REQUIRED
APPROVAL_IDENTITY_REQUIRED
INVALID_SCOPE_STATE
```

## 8. Django admin

Django admin remains the temporary operational interface.

Ensure the relevant admin views show at minimum:

- scope identifier;
- title;
- project;
- scope kind;
- status;
- execution authorization;
- proposal version or content hash;
- clarification state and questions;
- approval eligibility;
- approval reference;
- published path;
- created, updated, and approved timestamps.

Any admin approval action must call the same approval service used by the public MCP path. Direct field mutation that bypasses lifecycle validation is prohibited.

## 9. Required proving executions

### 9.1 Positive proof — proposal returned and approval requested

Use this exact Product Owner request:

```text
Create a new Django app named storybook.
```

Prove:

1. the request creates or resolves one `PROPOSED` Work Item;
2. the response returns its exact identifier and immutable proposal version;
3. the response includes title, requested outcome, scope, acceptance checks, release gates, risks, status, and authorization;
4. `execution_authorization` remains `NONE`;
5. no repository document is published;
6. no contract is prepared or issued;
7. the response explicitly requests Product Owner approval with `Mehet?` or its documented equivalent.

### 9.2 Positive proof — conversational approval binding

Continue the same scenario with an authenticated Product Owner response equivalent to:

```text
Mehet.
```

Prove:

1. the approval references the exact Storybook Work Item identifier;
2. the approval references the exact proposal version shown previously;
3. one durable approval reference is created;
4. the scope becomes approved according to the canonical lifecycle;
5. repeated identical approval is idempotent;
6. execution still does not begin;
7. the result clearly reports the next allowed step.

Then invoke publication separately and prove the approved scope document appears at its deterministic repository path.

### 9.3 Clarification proof

Use a request with genuine business ambiguity, such as:

```text
Add the new customer feature to the application.
```

Prove:

1. deterministic policy returns `CLARIFICATION_REQUIRED`;
2. the response asks bounded material questions;
3. no approval prompt is emitted;
4. approval attempts are rejected while clarification remains unresolved;
5. after answers are supplied, a revised or superseding proposal is generated and returned for review.

### 9.4 Negative proof — stale approval

1. Create a proposal and return version A.
2. Revise approval-relevant scope content, creating version B.
3. Attempt approval using version A.
4. Expected result:

```text
REJECTED — STALE_PROPOSAL_VERSION
```

No approval reference may be bound to version B through the stale request.

### 9.5 Negative proof — no implicit approval

Prove that these do not approve a proposal unless the dedicated governed approval operation is invoked with the required identifiers:

- the original request;
- proposal generation success;
- silence;
- a generic acknowledgement not bound to the proposal;
- an assistant-authored approval sentence;
- direct database field modification outside the domain service.

## 10. Tests

Add or update tests covering at minimum:

- proposal response schema;
- Work Item and Sprint proposal review summaries;
- clarification-required response;
- approval eligibility calculation;
- exact proposal-version binding;
- stale approval rejection;
- idempotent approval;
- no implicit approval;
- no publication before approval;
- no execution preparation before publication;
- Django admin lifecycle action using the canonical service;
- MCP `tools/list` and runtime-schema consistency;
- remote HTTP/MCP acceptance for the Storybook scenario;
- Hungarian conversational rendering, including the explicit approval question.

## 11. Documentation obligations

Update as applicable:

- `README.md` Product Owner flow;
- MCP tool reference;
- architecture documentation;
- Constitution only if a permanent governance rule is not already covered;
- `AGENTS.md` where executor or conversational-agent behavior changes;
- `docs/akb/CURRENT_STATE.md`;
- roadmap;
- Django admin operational notes;
- evidence index.

Document this separation explicitly:

```text
Bridge DB = live lifecycle and canonical structured state
Conversation = Product Owner review and decisions
GitHub = approved published scope projection and audit history
Django admin = temporary operational and recovery interface
```

## 12. Evidence requirements

Create a Sprint-specific evidence root and include at minimum:

```text
docs/evidence/sprint-011/CONVERSATIONAL_REVIEW_MODEL.md
docs/evidence/sprint-011/STORYBOOK_PROPOSAL_REVIEW_PROOF.md
docs/evidence/sprint-011/CONVERSATIONAL_APPROVAL_PROOF.md
docs/evidence/sprint-011/CLARIFICATION_AND_STALE_APPROVAL_PROOFS.md
docs/evidence/sprint-011/acceptance-results.json
```

Evidence must bind:

- original Product Owner request;
- canonical proposal response;
- scope identifier;
- proposal version/hash;
- clarification state;
- approval message or approval command input;
- authenticated requester;
- durable approval reference;
- audit events;
- publication commit and path;
- proof that execution did not start prematurely;
- Release Gate results;
- final implementation commit.

## 13. Release Gates

Run and record at minimum:

```text
python manage.py makemigrations --check
python manage.py migrate --check
python manage.py validate_scopes
pytest -q
ruff check .
ruff format --check .
mypy .
git diff --check
```

Also run the exact remote MCP Storybook acceptance scenario through the public tool surface, not through direct model or database calls.

## 14. Definition of Done

Sprint 011 is complete only when:

- a conversationally initiated proposal is immediately returned to the Product Owner in human-reviewable form;
- material clarification questions are returned and block approval;
- eligible proposals explicitly ask for approval;
- conversational approval binds the exact immutable proposal version through a durable governed operation;
- stale and ambiguous approvals are rejected deterministically;
- proposal creation does not implicitly approve, publish, contract, or execute work;
- Django admin remains sufficient for inspection and recovery and uses canonical services for lifecycle actions;
- the Storybook scenario passes end to end through proposal review, explicit approval, and separate publication;
- the published Storybook scope appears in GitHub only after approval and publication;
- no repository implementation of the Storybook Django app occurs as part of this Sprint's acceptance proof;
- documentation, AKB, roadmap, tests, and evidence are synchronized;
- all Release Gates pass.

## 15. Final product outcome

The target Product Owner interaction is:

```text
Product Owner: "Create a new Django app named storybook."

AI Bridge:
- creates a PROPOSED Work Item;
- returns what it understood and what it intends to authorize;
- asks only material questions;
- clearly states that execution is not yet authorized;
- asks: "Mehet?"

Product Owner: "Mehet."

AI Bridge:
- binds durable approval to the exact proposal version;
- reports the approval result;
- publishes only through the governed publication step;
- continues toward contract issuance without bypassing any lifecycle boundary.
```
