# Sprint 011 — Conversational Product Owner Review, Approval, and Governed Execution Orchestration

**Status:** PROPOSED  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Execution level:** SPRINT  
**Task type:** SELF_DEVELOPMENT  
**Target branch:** `main`  

## 1. Problem statement

AI Bridge can now create a canonical proposed Work Item from a natural-language Product Owner request, but the conversational experience still exposes too many internal lifecycle steps and can stop after proposal creation or approval.

The intended Product Owner experience is simpler:

```text
Product Owner: explains the requested outcome.
AI Bridge: returns what it understood and the plan it created.
AI Bridge: asks material clarification questions if needed.
AI Bridge: asks: "Jó lesz így?"
Product Owner: confirms once.
AI Bridge: completes the governed lifecycle and implementation autonomously.
AI Bridge: returns the finished result, evidence, test instructions, and any remaining limitations.
```

The Product Owner should not need to manually invoke approval, publication, preparation, contract generation, contract issuance, consumption, execution start, evidence collection, or closure as separate conversational actions.

Those transitions must remain technically separate, deterministic, auditable, and recoverable inside AI Bridge, but one valid Product Owner confirmation should authorize AI Bridge to orchestrate the complete bounded flow.

Django admin remains sufficient as the temporary operational, diagnostic, support, and recovery interface. This Sprint does not require a dedicated Product Owner web UI.

## 2. Product Owner decisions

1. The conversation is the primary Product Owner interaction surface for requests initiated in conversation.
2. Django admin remains the temporary secondary inspection, support, and recovery interface.
3. AI Bridge must return a complete, human-reviewable proposal immediately after creating or revising a Sprint or Work Item.
4. AI Bridge must ask only material business or governance questions. Routine technical decisions remain autonomous within the approved scope.
5. When no unresolved material ambiguity remains, AI Bridge must ask a clear equivalent of: `Jó lesz így?`
6. The original request creates a proposal only. It does not itself authorize execution.
7. One authenticated affirmative Product Owner response to the displayed immutable proposal authorizes AI Bridge to orchestrate the full bounded governed lifecycle.
8. The confirmation must bind the exact scope identifier and immutable proposal version or content hash shown to the Product Owner.
9. Internal lifecycle transitions remain separate and audited even though they are not separate Product Owner interactions.
10. AI Bridge must pause and return to the Product Owner only when a genuine blocker, new business decision, new external authority, material scope change, or newly discovered risk requires it.
11. On successful completion, AI Bridge must return a concise completion report equivalent to: `Főnök, kész!`
12. Successful approval must not be interpreted as unbounded authority. It applies only to the reviewed and version-bound scope.

## 3. Target Product Owner experience

### 3.1 Request and proposal

Example:

```text
Product Owner:
Create a new Django app named storybook.

AI Bridge:
Ezt értettem meg:
- új Django app készüljön `storybook` néven;
- az app legyen regisztrálva a projektben;
- készüljenek el az alapfájlok;
- fussanak le a kötelező Release Gate-ek;
- készüljön evidence a módosításról és az eredményekről.

Ezt a tervet készítettem:
- ...

Jó lesz így?
```

### 3.2 Product Owner confirmation

```text
Product Owner:
Igen.
```

This one confirmation means:

> I approve this exact displayed proposal version and authorize AI Bridge to complete the governed publication, contract, execution, testing, evidence, and closure lifecycle within this bounded scope.

### 3.3 Autonomous governed execution

After valid confirmation, AI Bridge must orchestrate:

```text
scope.approve
→ scope.publish
→ execution.prepare
→ contract.generate
→ contract.validate
→ contract.issue
→ contract.consume
→ execution.request_start
→ execution provider implementation
→ Release Gates
→ evidence collection
→ execution completion
→ final result reporting
```

Equivalent canonical operation names are acceptable.

The system must not ask the Product Owner to approve each internal transition separately.

### 3.4 Completion response

Example:

```text
AI Bridge:
Főnök, kész!

Elkészült:
- létrejött a `storybook` Django app;
- regisztrálva lett a projektben;
- az alapfájlok elkészültek.

Ellenőrzések:
- pytest: PASS
- ruff: PASS
- mypy: PASS

Repository eredmény:
- commit vagy PR: ...

Evidence:
- ...

Így tudod kipróbálni:
- ...

Ismert korlátozás vagy további teendő:
- nincs / ...
```

The wording may vary, but the completion response must be truthful, structured, and backed by canonical execution state and evidence.

## 4. Scope

### In scope

- Define a versioned conversational proposal-review response for Sprint and Work Item proposals.
- Return the canonical proposal summary immediately after proposal creation or revision.
- Surface deterministic policy outcome, unresolved questions, and confirmation eligibility.
- Ask clarification questions when material ambiguity exists.
- Ask `Jó lesz így?` only when the proposal is confirmation-eligible.
- Bind one conversational confirmation to the exact scope identifier and immutable proposal version or hash.
- Implement or complete a canonical orchestration service that executes the full governed lifecycle after confirmation.
- Keep approval, publication, preparation, contract, consumption, execution, evidence, and closure as separate auditable transitions internally.
- Provide safe idempotency and resumability for partial failures.
- Prevent stale, superseded, changed, rejected, clarification-blocked, or already-terminal proposals from being confirmed accidentally.
- Return running, blocked, failed, or completed state truthfully.
- Return a final completion report with evidence and test instructions.
- Preserve Django admin as a usable diagnostic, support, and manual recovery surface.
- Add positive and negative end-to-end acceptance proofs.
- Update canonical documentation, AKB current state, roadmap, MCP reference, and tests.

### Out of scope

- A new custom Product Owner web interface.
- Orki meeting-room UI implementation.
- Treating conversation history as canonical scope authority.
- Treating free-form assistant text as execution authority.
- Removing internal approval, publication, contract, execution, or evidence boundaries.
- Allowing one confirmation to authorize work outside the displayed proposal.
- Requiring the Product Owner to manually drive normal internal lifecycle transitions.
- Hiding failures or claiming completion before evidence-backed closure.

## 5. Proposal review contract

After successful proposal creation or revision, the public response must contain enough information for an informed Product Owner decision.

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
  confirmation_eligible: true
  confirmation_prompt: "Jó lesz így?"
```

Equivalent versioned field names are acceptable.

The response must not claim that approval, publication, contract issuance, execution, or completion has occurred when it has not.

## 6. Clarification behavior

When material business ambiguity exists:

```text
request
→ semantic proposal
→ deterministic policy result: CLARIFICATION_REQUIRED
→ bounded questions returned to Product Owner
→ Product Owner answers
→ proposal revised or superseded deterministically
→ updated proposal summary returned
→ "Jó lesz így?" asked only after ambiguity is resolved
```

Questions must be limited to information that materially affects:

- business intent;
- scope boundary;
- acceptance outcome;
- repository or project selection;
- risk authorization;
- external credentials or authority;
- irreversible or production-impacting decisions.

Routine technical implementation details must remain autonomous inside the approved scope.

## 7. Confirmation binding

A conversational confirmation must:

- be authenticated and auditable;
- reference the exact `scope_identifier`;
- reference the exact `proposal_version` or content hash shown to the Product Owner;
- create or bind one durable Product Owner approval reference;
- explicitly authorize full governed execution within that exact scope;
- reject stale proposal versions;
- be idempotent;
- never authorize an amended or broader proposal implicitly.

Accepted user wording may include equivalents of:

```text
Igen.
Jó lesz.
Mehet.
Rendben, csináld meg.
```

Natural-language interpretation is advisory. The confirmation handler must resolve the currently pending exact proposal context and invoke the canonical governed confirmation operation with explicit identifiers and version binding.

Silence, the original request, unrelated positive language, assistant-authored wording, or an unbound generic acknowledgement must not create execution authority.

## 8. Governed execution orchestration

Implement one canonical application-level orchestration capability equivalent to:

```text
scope.confirm_and_execute
```

The exact operation name may differ.

The operation must receive or resolve at minimum:

```yaml
project_id: "..."
scope_identifier: "..."
proposal_version: "..."
product_owner_identity: "auditable identity"
confirmation_reference: "durable conversation or request reference"
idempotency_key: "..."
```

It must orchestrate existing canonical domain services rather than duplicating their authority.

Required internal sequence:

1. validate Product Owner identity and authority;
2. validate scope state and exact proposal version;
3. bind durable approval;
4. publish the approved scope;
5. prepare execution from the published canonical scope;
6. generate the Execution Contract;
7. validate the contract;
8. issue the contract;
9. allow the execution provider to consume the issued contract;
10. request execution start;
11. track execution state;
12. collect Release Gate results and evidence;
13. complete or fail the execution truthfully;
14. return the final structured result.

Each transition must remain separately audited.

The orchestration layer must not recreate approval, publication, contract, or execution rules in parallel. It must call the existing canonical services.

### 8.1 Idempotency and resumability

The orchestration operation must:

- safely retry after network or provider interruption;
- avoid duplicate approvals, publications, contracts, executions, or evidence records;
- resume from the last valid durable state;
- expose the current step and blocker;
- preserve one correlation or orchestration identifier across the full lifecycle.

### 8.2 Product Owner re-entry conditions

AI Bridge may return to the Product Owner before completion only when:

- a material clarification is required;
- the scope must change materially;
- a newly discovered risk requires approval;
- external credentials, secret, payment, environment access, or legal authority are missing;
- the target repository or branch has changed incompatibly;
- the execution provider is unavailable and no safe retry path remains;
- tests reveal a product decision rather than a technical defect;
- an irreversible or production action requires separate explicit authority.

A routine implementation detail, code choice, file layout decision, or fix inside the approved scope is not a reason to ask the Product Owner again.

## 9. Public MCP and conversation adapter

Inspect the current public registry before implementation. Reuse existing lifecycle tools where possible.

Capabilities must include:

- propose a Work Item or Sprint;
- retrieve a human-reviewable proposal summary;
- retrieve clarification questions and confirmation eligibility;
- submit clarification answers or create a revised proposal;
- confirm and orchestrate one exact proposal version;
- retrieve orchestration status;
- retrieve final execution result, evidence locations, and test instructions.

Every identifier required by the next operation must be returned by the previous operation. The conversational client must not invent hidden identifiers.

The public `tools/list` schema and runtime argument validation must continue to derive from one canonical registry.

The conversation adapter must:

- use canonical structured responses;
- not scrape Markdown for authority;
- preserve lifecycle truthfully;
- present the proposal clearly;
- ask questions only when necessary;
- ask `Jó lesz így?` only when eligible;
- map valid Product Owner confirmation to the exact pending proposal context;
- invoke the canonical orchestration path;
- report `IN_PROGRESS`, `BLOCKED`, `FAILED`, or `COMPLETED` truthfully;
- produce the final evidence-backed completion message.

Default Hungarian proposal wording should be equivalent to:

```text
Ezt értettem meg, és ezt a tervet készítettem.
...
Jó lesz így?
```

Default Hungarian completion wording should be equivalent to:

```text
Főnök, kész!
```

## 10. Lifecycle invariants

Enforce the following:

1. `PROPOSED` means no execution authorization.
2. Proposal review is read-only.
3. One confirmation binds one exact proposal version.
4. Editing approval-relevant content invalidates or supersedes earlier confirmation eligibility.
5. A stale confirmation is rejected deterministically.
6. A rejected or clarification-blocked proposal cannot be confirmed.
7. Duplicate confirmation does not create duplicate approvals or executions.
8. Approval remains a distinct internal lifecycle transition.
9. Publication remains a distinct internal lifecycle transition.
10. Contract issuance remains distinct from consumption and execution.
11. The orchestration service may sequence these transitions but must not collapse their audit semantics.
12. No repository mutation occurs before valid contract consumption and execution start.
13. No completion claim occurs before Release Gates and required evidence are recorded.
14. Material scope change requires a new proposal version and new Product Owner confirmation.
15. Django admin actions must use the same canonical domain services and invariants as MCP operations.
16. Direct field mutation must not bypass lifecycle validation.

Recommended deterministic errors:

```text
CLARIFICATION_REQUIRED
PROPOSAL_NOT_CONFIRMATION_ELIGIBLE
STALE_PROPOSAL_VERSION
SCOPE_ALREADY_APPROVED
SCOPE_ALREADY_EXECUTING
SCOPE_REJECTED
APPROVAL_REFERENCE_REQUIRED
APPROVAL_IDENTITY_REQUIRED
INVALID_SCOPE_STATE
PUBLICATION_FAILED
CONTRACT_ISSUANCE_FAILED
CONTRACT_CONSUMPTION_FAILED
EXECUTION_PROVIDER_UNAVAILABLE
EXECUTION_BLOCKED
RECONFIRMATION_REQUIRED
```

Equivalent documented codes are acceptable.

## 11. Django admin

Django admin remains the temporary operational and recovery interface.

Ensure the relevant admin views show at minimum:

- scope identifier;
- title;
- project;
- scope kind;
- status;
- execution authorization;
- proposal version or content hash;
- clarification state and questions;
- confirmation eligibility;
- approval reference;
- published path and publication commit;
- orchestration identifier and current step;
- contract identifier and state;
- execution run and provider state;
- evidence root;
- created, updated, approved, started, completed, and failed timestamps;
- last blocker or failure reason.

Any admin action must call the same canonical services used by the public MCP path.

Manual recovery actions may resume a failed orchestration, but must not bypass approval, contract, or execution invariants.

## 12. Required proving executions

### 12.1 Positive proof — proposal review

Use exactly:

```text
Create a new Django app named storybook.
```

Prove:

1. one `PROPOSED` Work Item exists;
2. the exact scope identifier and immutable proposal version are returned;
3. the response includes requested outcome, in scope, out of scope, acceptance checks, Release Gates, risks, policy result, status, and authorization;
4. `execution_authorization` remains `NONE`;
5. no repository scope document is published yet;
6. no contract is prepared or issued yet;
7. the response asks `Jó lesz így?` or its documented equivalent.

### 12.2 Positive proof — one confirmation drives the complete lifecycle

Continue the same scenario with an authenticated Product Owner response equivalent to:

```text
Igen.
```

Prove the one confirmation:

1. binds the exact Storybook Work Item identifier;
2. binds the exact proposal version shown previously;
3. creates one durable approval reference;
4. publishes the approved scope document;
5. records publication path, commit, and content hash;
6. prepares execution from the published canonical scope;
7. generates, validates, and issues one Execution Contract;
8. is consumed by the execution provider;
9. starts one execution run;
10. creates the actual `storybook` Django app in the governed target repository;
11. registers the app in the Django project;
12. creates the required base files;
13. runs the required Release Gates;
14. writes evidence under the deterministic Work Item evidence root;
15. completes the execution and binds the final commit or PR;
16. returns a final evidence-backed `Főnök, kész!` response;
17. includes clear instructions for how the Product Owner can test the result.

Repeated delivery of the same confirmation or orchestration request must be idempotent and must not create duplicate work.

### 12.3 Clarification proof

Use:

```text
Add the new customer feature to the application.
```

Prove:

1. deterministic policy returns `CLARIFICATION_REQUIRED`;
2. bounded material questions are returned;
3. `Jó lesz így?` is not emitted;
4. confirmation is rejected while clarification remains unresolved;
5. after answers, a revised or superseding proposal is returned;
6. the Product Owner confirms only the revised exact version;
7. no execution occurs from the obsolete version.

### 12.4 Negative proof — stale confirmation

1. Create proposal version A.
2. Change approval-relevant content, producing version B.
3. Attempt confirmation using version A.
4. Expected result:

```text
REJECTED — STALE_PROPOSAL_VERSION
```

No approval or execution may be attached to version B through the stale confirmation.

### 12.5 Negative proof — no implicit execution authority

Prove that these do not approve or execute a proposal:

- the original request;
- proposal creation success;
- silence;
- unrelated positive language;
- assistant-authored confirmation wording;
- a confirmation that cannot resolve one exact pending proposal;
- direct database modification outside canonical services.

### 12.6 Negative proof — material scope change during execution

After valid confirmation, simulate discovery of a required change outside the approved scope.

Expected behavior:

```text
execution pauses safely
→ RECONFIRMATION_REQUIRED
→ revised proposal version returned
→ Product Owner review requested
→ no out-of-scope mutation occurs before new confirmation
```

### 12.7 Recovery proof

Simulate a safe interruption after publication, contract issuance, or provider start.

Prove:

- retry uses the same orchestration identity;
- no duplicate publication, contract, or execution is created;
- orchestration resumes from the last durable valid state;
- the final completion result remains consistent.

## 13. Tests

Add or update tests covering at minimum:

- proposal-review response schema;
- Work Item and Sprint summaries;
- clarification-required response;
- confirmation eligibility;
- exact proposal-version binding;
- stale confirmation rejection;
- idempotent confirmation;
- no implicit approval or execution;
- approval, publication, contract, consumption, and execution remain separately audited;
- full orchestration from one Product Owner confirmation;
- partial-failure recovery and resume;
- no duplicate execution on retry;
- reconfirmation on material scope change;
- no execution before publication and contract consumption;
- no completion before gates and evidence;
- Django admin canonical actions;
- MCP `tools/list` and runtime-schema consistency;
- remote HTTP/MCP Storybook end-to-end acceptance;
- Hungarian proposal rendering with `Jó lesz így?`;
- Hungarian completion rendering with `Főnök, kész!`;
- final result includes evidence and test instructions.

## 14. Release Gates

At minimum run and record:

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

Also run the complete remote HTTP/MCP acceptance flow using the exact Storybook scenario and a real governed target repository or isolated repository that proves actual mutation, contract consumption, execution, tests, evidence, and final completion.

Do not replace the acceptance proof with a fake payload, mocked successful provider, or pre-created Storybook app.

## 15. Evidence requirements

Create evidence under:

```text
docs/evidence/sprint-011/
```

At minimum:

```text
CONVERSATIONAL_PRODUCT_OWNER_MODEL.md
SINGLE_CONFIRMATION_ORCHESTRATION_PROOF.md
STORYBOOK_END_TO_END_EXECUTION_PROOF.md
CLARIFICATION_AND_STALE_CONFIRMATION_PROOFS.md
RECOVERY_AND_IDEMPOTENCY_PROOF.md
FINAL_RESULT_REPORTING_PROOF.md
acceptance-results.json
```

Evidence must bind:

- original Product Owner request;
- structured proposal;
- deterministic policy result;
- proposal version shown to the Product Owner;
- Product Owner confirmation reference;
- durable approval reference;
- publication path, hash, and commit;
- preparation and contract identifiers;
- contract issue and consumption events;
- execution run and provider identity;
- changed files;
- Release Gate results;
- evidence root;
- final commit or PR;
- final user-facing completion response;
- Product Owner test instructions;
- interruption and recovery results where applicable.

## 16. Documentation obligations

Update as applicable:

- `README.md` Product Owner flow;
- MCP tool reference;
- architecture documentation;
- Constitution if this permanent operating principle is not already represented;
- `AGENTS.md` for executor and conversational-agent behavior;
- `docs/akb/CURRENT_STATE.md`;
- roadmap;
- Django admin operational and recovery notes;
- evidence index.

Document this separation explicitly:

```text
Bridge DB = live lifecycle and canonical structured state
Conversation = Product Owner intent, review, clarification, confirmation, and result
GitHub = approved published scope, implementation, and audit history
Django admin = temporary operational, diagnostic, and recovery interface
Execution Provider = bounded implementation under issued contract
```

Document the central Product Owner contract:

> The Product Owner explains the outcome, reviews the exact generated plan, and confirms it once. AI Bridge then completes the governed lifecycle autonomously within that scope and returns evidence-backed results. The Product Owner is asked again only when a genuine new decision or authority is required.

## 17. Definition of Done

Sprint 011 is complete only when:

- a conversational request returns a complete reviewable proposal;
- material clarification is requested only when necessary;
- eligible proposals ask `Jó lesz így?`;
- one authenticated Product Owner confirmation binds the exact proposal version;
- the same confirmation authorizes full bounded governed orchestration;
- approval, publication, contract, consumption, execution, evidence, and closure remain separately audited internally;
- normal execution does not require additional Product Owner lifecycle commands;
- genuine blockers and material scope changes safely return to the Product Owner;
- the Storybook request completes through actual governed repository mutation;
- required Release Gates pass and evidence is written;
- the final response says, in substance, `Főnök, kész!` and includes evidence, repository result, and test instructions;
- retries are idempotent and interrupted execution is resumable;
- no stale, implicit, assistant-authored, or unbound confirmation can authorize execution;
- Django admin supports inspection and canonical recovery without becoming a bypass;
- documentation and AKB state are synchronized;
- all Release Gates and required proofs pass.

## 18. Required final implementation report

The implementation report must include:

- final assessment;
- implementation commit SHA;
- changed-file summary;
- migration summary;
- public MCP and service changes;
- Storybook Work Item identifier;
- proposal version and approval reference;
- publication commit and path;
- contract and execution identifiers;
- target repository final commit or PR;
- Release Gate results;
- evidence paths;
- exact final Product Owner completion message;
- Product Owner test instructions;
- remaining risks or limitations.

Allowed terminal assessments:

```text
PASS — READY FOR PRODUCT OWNER ACCEPTANCE
FAIL — BLOCKED
```

Do not report PASS when any required acceptance proof, actual repository mutation, provider consumption, Release Gate, evidence record, documentation obligation, recovery proof, or final result report is missing.