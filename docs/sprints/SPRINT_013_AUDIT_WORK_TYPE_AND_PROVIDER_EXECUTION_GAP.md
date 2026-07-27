# Sprint 013 — Audit Work Type and Execution Provider Gap Assessment

**Status:** APPROVED FOR CODEX EXECUTION  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Execution level:** SPRINT  
**Task type:** SELF_DEVELOPMENT  
**Target branch:** `main`  
**Baseline:** `800e185d5bb7b2e23bf5c71de3f71ba5118a0feb`

## 1. Product Owner decision

AI Bridge must support **AUDIT** as a first-class governed `work_type` for bounded executable Sprint or Work Item scopes.

`AUDIT` is not a new executable hierarchy level. The canonical executable scope kinds remain:

```text
SPRINT
WORK_ITEM
```

Planning containers remain non-executable:

```text
INITIATIVE
MILESTONE
EPIC
```

An audit may therefore be authorized as either:

```yaml
scope_kind: SPRINT | WORK_ITEM
work_type: AUDIT
```

The term `PLATFORM_AUDIT` may be used as a human-readable title or specialization, but the canonical work type is `AUDIT` unless the repository assessment proves a real need for typed audit subcategories.

## 2. Governing principle

Apply this rule throughout the Sprint:

> Before designing or implementing a new component, first prove that the required capability does not already exist in an adequate canonical form.

A missing route, provider binding, tool description, schema field, or runtime dispatch does not automatically justify a new subsystem.

## 3. Problem statement

Sprint 010 established that every repository mutation requires one approved executable Sprint or Work Item and that AI Bridge is the Contract Authority, while Codex, Claude Code, OpenAI Codex, another coding agent, or a governed human may act as an Execution Provider.

The current system can create, review, confirm, approve, issue, consume, and track a governed execution. However, the Product Owner expects that a broad platform audit may still stop after approval or contract issuance because execution-provider selection, dispatch, invocation, and result collection are not yet fully generalized across providers such as Codex, OpenAI, Claude, or other executors.

This Sprint must determine the actual state before adding anything.

## 4. Primary outcomes

1. Add `AUDIT` to the canonical work-type model everywhere required.
2. Prove whether the existing provider execution machinery can execute an Audit scope end to end.
3. Inventory the current Execution Provider boundary and all supported provider identities.
4. Determine whether provider selection and dispatch are already generic, partially generic, hard-coded, missing, or only documented.
5. Repair the smallest existing path needed for one real governed Audit execution.
6. Do not build a broad multi-provider marketplace, UI, employee model, or agent platform in this Sprint.

## 5. Mandatory assessment before implementation

Before code changes, Codex must inspect:

- all applicable `AGENTS.md` files;
- Constitution and architecture documents;
- Sprint 009, Sprint 010, Sprint 011, and Sprint 012 contracts and evidence;
- Work Item and Sprint schemas;
- work-type enums and policy validation;
- MCP public tool registry and schemas;
- Execution Contract schema;
- provider policy fields;
- provider dispatch services;
- execution-run lifecycle;
- Codex-specific adapters, commands, or runtime assumptions;
- any references to Claude, OpenAI, coding agents, human executors, or generic providers;
- local runtime and Cloudflare tunnel path;
- tests and evidence for provider execution.

No new provider subsystem may be created during this assessment phase.

## 6. Required classification

Classify the provider-execution state as one primary category:

```text
A. GENERIC_PROVIDER_BOUNDARY_ALREADY_COMPLETE
B. GENERIC_BOUNDARY_EXISTS_BUT_AUDIT_IS_NOT_WIRED
C. PROVIDER_SELECTION_EXISTS_BUT_DISPATCH_IS_CODEX_SPECIFIC
D. CONTRACT_SUPPORTS_PROVIDERS_BUT_RUNTIME_DISPATCH_IS_MISSING
E. EXECUTION_PROVIDER_IS_HARD_CODED
F. PROVIDER_CAPABILITY_OR_TOOL_METADATA_IS_MISSING
G. EXISTING_IMPLEMENTATION_DEFECT
H. GENUINE_ARCHITECTURAL_GAP
I. OTHER — documented precisely
```

The report must distinguish:

- provider identity;
- provider eligibility/capability matching;
- provider selection;
- contract binding;
- dispatch;
- progress observation;
- test-fix loop ownership;
- result/evidence return;
- completion binding.

## 7. AUDIT work-type contract

Add `AUDIT` as a canonical work type alongside existing values such as:

```text
FEATURE
BUGFIX
MIGRATION
RECOVERY
DOCUMENTATION
RELEASE
SELF_DEVELOPMENT
ONBOARDING
SECURITY
CONFIGURATION
AUDIT
```

An Audit scope must be able to define:

```yaml
work_type: AUDIT
audit_target:
audit_questions: []
required_inventory: []
required_classifications: []
mutation_policy: READ_ONLY | REPAIR_ALLOWED
repair_rule: "Prove existing capability before new design"
acceptance_checks: []
evidence_root:
```

`READ_ONLY` audit contracts may not mutate the target repository except for their own approved evidence/documentation output when explicitly included in scope.

`REPAIR_ALLOWED` audit contracts may perform only the bounded repairs authorized by the exact approved scope and proposal hash.

## 8. Execution-provider boundary requirements

The canonical model must preserve:

```text
AI Bridge = Contract Authority
Execution Provider = bounded executor
```

An Execution Provider must never:

- approve its own scope;
- issue its own contract;
- broaden the approved outcome;
- mutate before successful contract consumption;
- claim completion without evidence and final-state binding.

Provider-independent contract fields must be identified and used where already present. Provider-specific configuration must remain behind a replaceable adapter or explicit provider profile.

At minimum assess support for these conceptual providers:

```text
CODEX
OPENAI_CODEX
CLAUDE_CODE
HUMAN
OTHER_REGISTERED_PROVIDER
```

Do not claim operational support merely because a name appears in documentation.

## 9. Smallest required implementation

After assessment:

### If the existing boundary is sufficient

- wire `AUDIT` into existing schemas, policy, proposal, review, confirmation, contract, dispatch, evidence, and completion handling;
- reuse the current provider path;
- add tests and runtime proof;
- do not create a new provider manager.

### If dispatch is Codex-specific but reusable

- extract only the smallest provider-neutral boundary required to preserve current Codex behavior and execute the proving Audit;
- retain Codex as the only operational provider if that is the truthful current state;
- represent unsupported providers as unavailable, not simulated.

### If a genuine gap exists

Document first:

1. the exact missing responsibility;
2. all existing components examined;
3. why composition or extension is insufficient;
4. the smallest new interface or adapter required;
5. why it does not duplicate Contract Authority, approval, orchestration, or execution-run state.

Only then implement it.

## 10. Proving Audit

Create and execute one fresh governed Audit scope with this exact outcome:

```text
Audit the AI Bridge Product Owner confirmation and execution-provider paths. Inventory existing capabilities, classify gaps, and perform only the smallest repairs explicitly authorized by the approved Audit scope.
```

The proving flow must be:

```text
AUDIT proposal
→ scope.review
→ Product Owner confirmation through conversation.confirm
→ GovernanceApproval
→ ConversationOrchestration
→ Execution Contract
→ provider selection/binding
→ provider dispatch
→ audit execution
→ evidence generation
→ Release Gates
→ completion binding
```

The provider must be truthful. If only Codex is operational, bind and report Codex. Do not fabricate OpenAI or Claude execution.

## 11. Autonomous test-fix loop

The local environment is authoritative:

```text
ChatGPT
→ Cloudflare Tunnel
→ 127.0.0.1:8001
→ local AI Bridge MCP server
→ local repository/runtime/provider
```

For any local HTTP 5xx, failing test, dispatch failure, or provider exception:

```text
test
→ inspect local logs/traceback
→ reproduce
→ regression test
→ minimal fix
→ Release Gates
→ restart affected local process
→ retest
```

Continue until PASS or until a blocker is proven outside the repository, local runtime, tunnel, provider process, and available credentials.

## 12. Negative proofs

Prove:

- `AUDIT` is not an executable hierarchy level;
- Initiative, Milestone, and Epic still cannot authorize direct mutation;
- an Audit cannot self-approve or self-issue a contract;
- unsupported providers are rejected or marked unavailable;
- provider selection cannot silently fall back to a different provider;
- a READ_ONLY audit cannot perform unauthorized repairs;
- a REPAIR_ALLOWED audit cannot broaden beyond the proposal hash;
- retry does not duplicate approval, orchestration, contract, execution, or evidence root;
- direct mutation before contract consumption remains forbidden.

## 13. Documentation updates

Update as applicable:

- Work Type documentation;
- Sprint and Work Item contract documentation;
- MCP tool reference;
- architecture/provider boundary documentation;
- README Product Owner flow;
- roadmap;
- AKB current state;
- `AGENTS.md`;
- evidence index.

Documentation must state clearly:

```text
AUDIT = governed work type
SPRINT / WORK_ITEM = executable scope kinds
INITIATIVE / MILESTONE / EPIC = planning containers
```

It must also state the truthful current operational provider support.

## 14. Evidence

Create evidence under:

```text
docs/evidence/sprint-013/
```

At minimum:

```text
EXISTING_AUDIT_CAPABILITY_ASSESSMENT.md
WORK_TYPE_SCHEMA_PROOF.md
EXECUTION_PROVIDER_INVENTORY.md
PROVIDER_BOUNDARY_CLASSIFICATION.md
GENUINE_GAPS.md
MINIMAL_REPAIR.md
AUDIT_END_TO_END_PROOF.md
PROVIDER_DISPATCH_PROOF.md
IDEMPOTENCY_PROOF.md
NEGATIVE_PROOFS.md
RELEASE_GATE_RESULTS.md
acceptance-results.json
```

## 15. Release Gates

Run and record:

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

Also run the real MCP proving flow through the Cloudflare tunnel into the local server.

## 16. Commit rule

Do not commit partial or unproven changes.

Only after the proving Audit completes, all gates pass, evidence is complete, and no credentials are persisted:

1. stage intended Sprint 013 changes;
2. create one coherent commit;
3. push to `origin/main`;
4. verify runtime commit and tool-surface version;
5. perform one final smoke test.

## 17. Definition of Done

Sprint 013 is complete only when:

- `AUDIT` is a canonical governed work type;
- existing capability was assessed before new design;
- the provider boundary is truthfully classified;
- no unnecessary provider manager or parallel lifecycle was created;
- one real Audit reaches an Execution Provider and completes;
- current operational provider support is documented accurately;
- unsupported providers are not simulated;
- all negative proofs pass;
- all Release Gates pass;
- evidence and documentation are complete;
- final commit is pushed.

## 18. Required final report

Return:

- baseline and final commit;
- push result;
- runtime commit and MCP tool-surface version;
- provider-boundary classification;
- operational providers actually proven;
- providers recognized but unavailable;
- whether any new interface/adapter was created and proof of necessity;
- Audit scope identifier;
- approval, orchestration, contract, and execution identifiers;
- provider identity;
- evidence paths;
- Release Gate results;
- remaining limitations;
- Product Owner retest instructions.

Allowed terminal results:

```text
PASS — READY FOR PRODUCT OWNER ACCEPTANCE
FAIL — BLOCKED
```

A repository defect, local HTTP 500, local provider exception, failing test, or missing local restart is not a terminal blocker. It must enter the autonomous test-fix loop.