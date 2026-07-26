# Sprint 012 — Existing Conversational Confirmation Path Assessment and Repair

**Status:** PROPOSED  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Execution level:** SPRINT  
**Task type:** SELF_DEVELOPMENT  
**Target branch:** `main`

## 1. Problem statement

Sprint 011 introduced a conversational confirmation path intended to let a Product Owner review one exact proposal, reply with an affirmative phrase such as `Igen, jó lesz így.`, and allow AI Bridge to create durable approval authority and continue the governed lifecycle.

The current repository already appears to contain the relevant pieces:

- `conversation.confirm` public MCP tool;
- `scope.confirm_and_execute` public MCP tool;
- durable `ConversationOrchestration` state;
- accepted Product Owner confirmation vocabulary;
- exact proposal version and hash validation;
- durable `GovernanceApproval` creation from the confirmation reference;
- composition of approval, publication, preparation, contract generation, validation, issuance, consumption, provider dispatch, and status reporting.

However, a real ChatGPT → AI Bridge interaction produced this outcome:

```text
Product Owner: Igen, jó lesz.
AI Bridge: APPROVAL_REQUIRED
```

This indicates that the conversational request did not reach, or did not correctly use, the already implemented conversational confirmation capability. The failure must be assessed before introducing any new adapter, approval subsystem, or parallel lifecycle path.

## 2. Product Owner decision

Do not create a new conversational approval adapter unless Codex proves that no adequate canonical implementation already exists.

The mandatory first step is repository and runtime-path assessment.

The preferred outcome is to repair tool exposure, routing, tool selection, identity/reference construction, schema usage, deployment synchronization, or conversation instructions so the existing canonical path works as designed.

A new component is allowed only if the assessment demonstrates a real architectural gap that cannot be solved by correctly wiring the existing canonical services.

## 3. Known repository evidence to verify

Codex must inspect the current implementation rather than relying on this summary, but at minimum verify these apparent existing elements in `projects/governed_mcp.py`:

1. `conversation.confirm` is declared as a public governed MCP tool.
2. Its inputs include:
   - `project_id`;
   - `scope_identifier`;
   - `confirmation_text`;
   - `product_owner_identity`;
   - `confirmation_reference`;
   - `idempotency_key`.
3. `_confirm_conversation(...)` validates accepted affirmative language, resolves the exact scope, obtains the current proposal version/hash through `review_scope(...)`, and delegates to `_confirm_and_execute(...)`.
4. `_confirm_and_execute(...)` creates or reuses one durable `GovernanceApproval` with `AUTHORIZE_EXECUTION`, creates `ConversationOrchestration`, validates the exact proposal version/hash, and advances the canonical lifecycle.
5. `_advance_orchestration(...)` composes existing canonical approval, publication, preparation, contract, consumption, and provider-dispatch services.
6. Generic lifecycle operations such as `scope.approve` still correctly require an already existing durable `approval_reference` and therefore must not be used as the conversational confirmation entry point.

## 4. Primary hypothesis

The most likely defect is not the absence of a conversational confirmation implementation, but incorrect runtime routing or invocation.

Potential causes to assess include:

- ChatGPT or the connector selected `scope.approve` instead of `conversation.confirm`;
- the deployed MCP server does not expose the current Sprint 011 tool surface;
- tool metadata or descriptions do not make the intended next action sufficiently deterministic;
- the proposal response does not return the exact identifiers and next-tool hint required for confirmation;
- the conversation layer does not preserve or resolve the pending scope identifier;
- `product_owner_identity`, `confirmation_reference`, or `idempotency_key` are not derived by the caller;
- the currently connected AI Bridge instance runs an older commit or stale deployment;
- MCP tool discovery/schema caching is stale;
- the tool invocation failed and a fallback path incorrectly attempted `scope.approve`;
- documentation or AGENTS instructions still direct agents toward the old multi-step lifecycle.

These are hypotheses only. Codex must produce evidence for the actual cause.

## 5. Phase A — Mandatory assessment before implementation

Before changing code, Codex must:

1. update local `main` from `origin/main`;
2. verify the current deployed/reference commit and compare it with repository `main`;
3. locate and read all applicable `AGENTS.md` files;
4. read the Constitution and current architecture documentation;
5. inspect Sprint 011 implementation and evidence;
6. inspect the public MCP registry, `tools/list`, runtime schema validation, dispatch logic, HTTP transport, authentication context, conversation-facing descriptions, and deployment configuration;
7. identify the exact tool call that produced `APPROVAL_REQUIRED` in the failed scenario;
8. determine whether `conversation.confirm` was:
   - exposed;
   - discoverable;
   - selected;
   - invoked with valid arguments;
   - executed against the expected deployment;
9. reproduce the failure through the real remote HTTP/MCP path where possible;
10. document the full call sequence and exact failure point.

No new adapter or approval subsystem may be created during Phase A.

## 6. Required assessment outcomes

Codex must classify the root cause into one of these categories:

```text
A. EXISTING_CAPABILITY_NOT_DEPLOYED
B. EXISTING_CAPABILITY_NOT_EXPOSED
C. WRONG_TOOL_SELECTED
D. REQUIRED_CONTEXT_NOT_RETURNED
E. REQUIRED_IDENTITY_OR_REFERENCE_NOT_DERIVED
F. STALE_TOOL_SCHEMA_OR_CLIENT_CACHE
G. EXISTING_IMPLEMENTATION_DEFECT
H. GENUINE_ARCHITECTURAL_GAP
I. OTHER — documented precisely
```

The assessment report must state:

- whether a canonical conversational confirmation implementation already exists;
- whether it is sufficient in design;
- whether the failure is wiring, deployment, schema, routing, instruction, client, or domain-service related;
- the smallest safe correction;
- why a new adapter is or is not required.

## 7. Implementation rule

### 7.1 If an adequate existing solution exists

Repair and complete the existing canonical path only.

Possible allowed corrections include:

- deploy the current tool surface;
- fix MCP registration or exposure;
- improve canonical tool descriptions and next-action hints;
- ensure proposal/review responses return all confirmation inputs;
- make `conversation.confirm` the explicit next tool for eligible proposals;
- derive a durable confirmation reference from the authenticated request/conversation identity;
- derive an auditable Product Owner identity from authenticated caller context;
- generate a deterministic idempotency key;
- prevent generic `scope.approve` fallback after conversational confirmation;
- synchronize MCP docs, AGENTS instructions, and runtime behavior;
- add missing error translation or structured continuation data;
- fix an implementation defect in the existing orchestration path;
- refresh/redeploy the connected AI Bridge service.

Do not duplicate `conversation.confirm`, `scope.confirm_and_execute`, `GovernanceApproval`, or `ConversationOrchestration` under a new abstraction unless technically unavoidable.

### 7.2 If a genuine architectural gap exists

Codex may propose and implement the smallest missing component only after documenting evidence that the existing services cannot meet the requirement.

Any new component must:

- compose the existing canonical services;
- not create parallel approval authority;
- not weaken exact proposal-hash binding;
- not treat free-form chat text as authority by itself;
- preserve durable identity, reference, idempotency, audit, and lifecycle boundaries.

## 8. Target behavior

The user experience must be:

```text
Product Owner:
I want a new Django app named storybook.

AI Bridge:
Ezt értettem meg...
...
Jó lesz így?

Product Owner:
Igen, jó lesz.

AI Bridge:
- resolves the exact pending proposal;
- invokes the existing canonical conversational confirmation path;
- creates or reuses durable approval authority;
- advances the governed lifecycle;
- returns orchestration status truthfully.
```

The Product Owner must not manually supply:

- an approval reference;
- a proposal hash;
- a proposal version;
- an idempotency key;
- an internal orchestration token.

Those values must be returned, resolved, or derived by the governed system and authenticated conversation context.

## 9. Required MCP contract behavior

For a confirmation-eligible proposal, the proposal/review response must return at minimum:

```yaml
project_id: ai-bridge
scope_identifier: bridge:...
proposal_version: 1
proposal_hash: 64-character hash
confirmation_eligible: true
confirmation_prompt: "Jó lesz így?"
next_tool: conversation.confirm
required_user_input:
  - confirmation_text
```

The conversation-facing client must be able to derive or receive securely:

```yaml
product_owner_identity: authenticated durable identity
confirmation_reference: durable unique message/conversation approval reference
idempotency_key: deterministic retry-safe key
```

The caller must invoke `conversation.confirm`, not `scope.approve`, for an affirmative response to a pending reviewed proposal.

`scope.approve` must remain strict and continue to require an existing durable approval reference for direct lower-level use.

## 10. Required proving scenario

Use a fresh Work Item that does not collide with the already created `storybook` app. Use exactly:

```text
Create a new Django app named confirmationproof.
```

### Phase 1 — proposal

Prove through the real ChatGPT-compatible remote MCP path:

1. one `PROPOSED` Work Item is created;
2. the response returns the exact scope identifier;
3. the response returns proposal version and hash;
4. confirmation eligibility is true;
5. the response asks `Jó lesz így?`;
6. the next canonical action is `conversation.confirm`;
7. no durable approval exists yet;
8. no publication, contract, or execution exists yet.

### Phase 2 — natural-language confirmation

Reply exactly:

```text
Igen, jó lesz.
```

Prove:

1. the client invokes `conversation.confirm`;
2. it does not invoke `scope.approve` as the entry point;
3. the exact pending scope is resolved;
4. the exact current proposal version/hash is bound;
5. a durable `GovernanceApproval` is created or idempotently reused;
6. a durable `ConversationOrchestration` is created or resumed;
7. publication, preparation, contract generation, validation, issuance, consumption, and provider dispatch proceed through canonical services;
8. no `APPROVAL_REQUIRED` response is returned for the conversational confirmation;
9. retries do not duplicate approval, contract, or execution;
10. orchestration status is returned truthfully.

The proof may stop at a truthful provider-running or provider-completed state if full application completion requires a separate provider callback, but it must prove that the original `APPROVAL_REQUIRED` defect is resolved and execution authority was created through the existing conversational path.

## 11. Negative proofs

Prove:

- unrelated affirmative language is rejected;
- stale proposal version/hash is rejected;
- a confirmation cannot bind an ambiguous or missing pending proposal;
- assistant-authored confirmation does not create authority;
- confirmation-reference reuse with mismatched identity or proposal fails;
- direct `scope.approve` without an existing durable approval reference still returns `APPROVAL_REQUIRED`;
- no duplicate approval or execution occurs on retry;
- an unauthenticated caller cannot fabricate Product Owner identity.

## 12. Deployment and client synchronization

If the root cause includes deployment or tool-schema staleness, Codex must:

- identify the commit currently running in the connected environment;
- deploy or document the exact deployment step required;
- verify `factory.list_capabilities` exposes `conversation.confirm` and `scope.confirm_and_execute`;
- verify the tool surface version matches the intended release;
- verify the ChatGPT connector refreshes the current tool schema;
- record any manual reconnection or cache-refresh step required for Product Owner acceptance.

Do not claim the defect fixed solely because local tests pass if the connected remote MCP path still exposes old behavior.

## 13. Tests

Add or update tests covering at minimum:

- `conversation.confirm` is present in `tools/list`;
- proposal response identifies `conversation.confirm` as the next tool;
- accepted Hungarian confirmation phrase;
- automatic binding to current proposal version/hash;
- durable approval creation;
- orchestration creation/resume;
- no generic `scope.approve` fallback;
- authenticated identity/reference derivation or validation;
- idempotent retries;
- stale and ambiguous confirmation rejection;
- remote MCP schema and runtime consistency;
- regression for the exact `APPROVAL_REQUIRED` scenario.

## 14. Release Gates

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

Also run the real remote HTTP/MCP confirmation proof against the active AI Bridge environment.

## 15. Evidence

Create evidence under:

```text
docs/evidence/sprint-012/
```

At minimum:

```text
EXISTING_CAPABILITY_ASSESSMENT.md
FAILED_CALL_PATH_RECONSTRUCTION.md
ROOT_CAUSE_AND_MINIMAL_REPAIR.md
REMOTE_CONVERSATIONAL_CONFIRMATION_PROOF.md
NO_DUPLICATE_ADAPTER_PROOF.md
DEPLOYMENT_AND_TOOL_SCHEMA_VERIFICATION.md
acceptance-results.json
```

Evidence must bind:

- repository baseline commit;
- deployed commit/tool-surface version;
- failed scope identifier if available;
- actual failed tool call and error;
- existing implementation discovered;
- root-cause classification;
- changed files;
- real remote tool sequence after correction;
- durable approval and orchestration identifiers;
- Release Gate results;
- final commit or PR;
- Product Owner acceptance instructions.

## 16. Documentation obligations

Update as applicable:

- README Product Owner flow;
- MCP tool reference;
- architecture documentation;
- AGENTS.md instructions for conversational confirmation;
- AKB current state;
- roadmap;
- deployment/runbook documentation;
- evidence index.

Documentation must explicitly distinguish:

```text
conversation.confirm = high-level conversational approval entry point
scope.confirm_and_execute = explicit structured orchestration entry point
scope.approve = lower-level approval binding requiring pre-existing durable authority
```

## 17. Definition of Done

Sprint 012 is complete only when:

- Codex first proves whether the capability already existed;
- no unnecessary parallel adapter is introduced;
- the exact cause of `APPROVAL_REQUIRED` is documented;
- `Igen, jó lesz.` routes to the canonical conversational confirmation path;
- durable approval is created without Product Owner-supplied internal identifiers;
- exact proposal version/hash binding remains enforced;
- generic lower-level approval rules remain strict;
- the active remote MCP environment exposes and executes the corrected path;
- retry, stale-version, ambiguity, identity, and no-implicit-authority tests pass;
- Release Gates pass;
- evidence and documentation are complete.

## 18. Required final report

Return:

- final assessment;
- root-cause category;
- whether an adequate solution already existed;
- whether any new adapter/component was created and why;
- implementation commit SHA;
- deployed commit and tool-surface version;
- changed-file summary;
- migration summary;
- exact failed tool path before repair;
- exact successful tool path after repair;
- proof scope identifier;
- approval reference;
- orchestration identifier;
- contract and execution identifiers if reached;
- Release Gate results;
- evidence paths;
- Product Owner retest instructions;
- remaining risks or limitations.

Allowed terminal assessments:

```text
PASS — READY FOR PRODUCT OWNER ACCEPTANCE
FAIL — BLOCKED
```

Do not report PASS based only on local unit tests. The corrected behavior must be proven through the connected remote MCP path.