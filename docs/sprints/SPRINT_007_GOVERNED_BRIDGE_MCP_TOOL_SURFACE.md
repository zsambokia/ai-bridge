# Sprint 007 — Governed Bridge MCP Tool Surface

**Status:** APPROVED FOR CODEX EXECUTION  
**Execution level:** SPRINT  
**Task type:** FEATURE  
**Risk modifiers:** EXTERNAL_INTEGRATION, AUTHENTICATION_OR_AUTHORIZATION, PUBLIC_API_OR_PROTOCOL, STATE_MUTATION, EXECUTION_ORCHESTRATION  
**Target branch:** `main`

## 1. Vision

Turn the proven ChatGPT ↔ AI Bridge MCP connection into a complete, governed operational surface that lets ChatGPT identify a project, inspect its accepted knowledge and current state, prepare execution safely, continue ambiguous flows, inspect execution status, and invoke only explicitly authorized lifecycle transitions.

The user experience should support natural requests such as:

```text
@bridge Folytassuk a Mesél az Erdőt.
Nézd meg, hol tart a projekt, készítsd elő a következő végrehajtást,
és mondd meg, ha tőlem döntés szükséges.
```

ChatGPT should choose the appropriate Bridge tools automatically. The Product Owner should not need to know internal tool names.

## 2. Current baseline

Sprint 006 proves the remote Streamable HTTP MCP transport, Bearer authentication, ChatGPT tool discovery, and one read-only tool: `factory.get_status`.

The current public tool definition and dispatch are hardcoded in `projects/views.py`. The internal Bridge service surface already contains Project resolution, continuation handling, Execution Context generation, tiered Execution Contract generation, validation, issuance, lifecycle operations, and related governance logic.

Sprint 007 must expose a deliberate public MCP façade over those canonical services. It must not duplicate or bypass them.

## 3. Architecture requirement

Replace the single-tool conditional dispatch with a canonical MCP tool registry.

Each public tool definition must include:

- stable external name;
- precise natural-language description suitable for model tool selection;
- strict JSON input schema;
- output schema where useful;
- read-only, destructive, idempotent, and open-world annotations;
- authorization classification;
- implementation handler;
- deterministic structured result;
- protocol-compliant error mapping;
- audit metadata where the operation changes state.

The HTTP transport must remain a thin MCP protocol adapter. Business logic belongs in canonical domain services.

## 4. Tool surface

Implement the following minimum public tool surface. Existing canonical names may be retained internally, but these external MCP names and responsibilities must be supported unless assessment proves a materially better stable naming scheme. Any renamed external tool must be documented with rationale and full mapping.

### 4.1 Discovery and status — read-only

#### `factory.get_status`

Return Bridge service status, tool-surface version, project registry summary, deployment/protocol information safe for the authenticated caller, and capability availability. Preserve backward compatibility with the Sprint 006 result while extending it safely.

#### `factory.list_capabilities`

Return the public Bridge capabilities and tools available to the caller, grouped by read-only, preparatory, approval-required, and lifecycle-changing actions. This is semantic capability information, not merely the raw MCP `tools/list` response.

### 4.2 Project discovery and resolution — read-only except continuation state

#### `project.list`

List active, ready projects visible to the caller. Support optional filters such as name, slug, repository, lifecycle, and onboarding status. Return compact project cards with stable identifiers.

#### `project.resolve`

Resolve a user-provided project reference from natural text, name, slug, repository, or project identifier using the canonical resolver.

Outcomes must include:

- `PROJECT_RESOLVED` with one stable project;
- `USER_INPUT_REQUIRED` with ranked candidates and a continuation token;
- `PROJECT_NOT_FOUND` with safe recovery suggestions.

Do not silently choose among ambiguous candidates.

#### `project.continue_resolution`

Continue a prior ambiguous resolution using the issued continuation token and an explicitly selected project identifier. Reject expired, forged, mismatched, or already-consumed continuation state.

#### `project.get`

Return one project's canonical registry details and readiness state using a stable project identifier.

### 4.3 Project context and accepted knowledge — read-only

#### `project.get_context`

Return the bounded current Project Context required for informed planning, including project identity, repository binding, technology profile, current milestone, readiness, important constraints, and links/paths to canonical documents. Do not return secrets or unbounded file content.

#### `akb.search`

Search the accepted project knowledge base for a query within a selected project. Use the canonical AKB/index/search capability if implemented. If the current repository supports only bounded accepted-document retrieval rather than full indexing, implement the strongest canonical deterministic search available and clearly expose capability limitations in results.

Inputs must support:

- project identifier;
- query;
- optional result limit within a safe maximum;
- optional accepted document categories.

Results must provide source paths/identifiers, relevance or deterministic ranking information, concise snippets, and accepted/current-state metadata.

#### `akb.get_document`

Return one accepted AKB document or a bounded section by canonical document identifier/path. Enforce project scope and safe size limits. Do not expose arbitrary repository file reading through this tool.

### 4.4 Execution preparation — governed, non-executing

#### `execution.prepare`

Create a governed execution preparation from:

- selected project;
- user intent;
- requested execution level;
- task type;
- declared risk modifiers;
- optional approved Sprint path when applicable;
- optional continuation context.

The operation must:

1. validate project readiness;
2. generate or retrieve the bounded Execution Context;
3. resolve tiered policy deterministically;
4. identify missing Product Owner inputs;
5. identify whether an approved Sprint is required;
6. return a preview of scope, policy, gates, evidence obligations, and next allowed action;
7. never start Codex or mutate an Execution Contract lifecycle merely because preparation succeeded.

Possible outcomes must include at least:

- `EXECUTION_PREPARED`;
- `USER_INPUT_REQUIRED`;
- `SPRINT_APPROVAL_REQUIRED`;
- `POLICY_REJECTED`;
- `PROJECT_NOT_READY`.

#### `execution.continue`

Continue a prepared execution after explicit Product Owner input or project selection. Use canonical continuation state. Do not accept arbitrary client-supplied hidden state.

#### `execution.get_status`

Return the status of an execution preparation, Execution Context, or Execution Contract by stable identifier. Include lifecycle, allowed next actions, blockers, required inputs, release gates, and evidence location where authorized.

#### `execution.render_handoff`

Render the human-readable Codex handoff or execution package only from a validated canonical stored context/contract. The result must not drift from the stored machine payload.

### 4.5 Contract lifecycle — state-changing and approval-sensitive

The following tools may be exposed only with explicit authorization controls, strong annotations, durable audit events, idempotency protection, and tests proving that ChatGPT cannot accidentally advance governance state.

#### `contract.generate`

Generate a draft tiered Execution Contract from an approved preparation and exact repository/project/sprint bindings. Generation is not issuance.

#### `contract.validate`

Validate a generated or issued contract against current repository bindings, hashes, baseline rule, project definition, Sprint approval, and resolved policy.

#### `contract.issue`

Issue a validated contract only when all required Product Owner approvals and policy requirements are represented in canonical state. Do not treat conversational wording alone as approval.

The tool must require an explicit approval token/identifier or equivalent durable approval record produced by the Bridge governance model. A plain Boolean such as `confirm: true` is insufficient.

#### `contract.consume`

Consume one `ISSUED` contract for an authorized execution. Enforce lifecycle, baseline, hash, repository, branch, and single-use rules.

#### `contract.complete`

Complete one consumed contract with final commit binding, evidence verification, release-gate results, and one allowed terminal state.

#### `contract.supersede`

Supersede a contract with a durable reason and replacement identifier where applicable.

#### `contract.revoke`

Revoke a contract with a durable reason and authorization record.

### 4.6 Execution launch boundary

#### `execution.request_start`

Create an authorized request to start Codex execution from a consumed contract or from the exact canonical transition required by current architecture.

This tool does not need to launch Codex unless a canonical dispatcher already exists and is explicitly in scope. If no dispatcher exists, it must return a durable `EXECUTION_START_REQUESTED` record and the exact next system action.

Do not implement a fake successful execution launch.

## 5. Public tool classifications

Every tool must belong to one of these classes:

```text
READ_ONLY
PREPARATORY_STATE
APPROVAL_REQUIRED
LIFECYCLE_MUTATION
EXECUTION_BOUNDARY
```

Authorization policy must be centralized and tested.

Minimum expectations:

- read-only tools: authenticated caller;
- preparatory state tools: authenticated caller plus project visibility;
- approval-required tools: durable canonical Product Owner approval reference;
- lifecycle mutations: exact contract lifecycle and idempotency rules;
- execution boundary: consumed/authorized contract and dispatcher boundary checks.

Bearer authentication alone proves caller access to the MCP server; it must not automatically grant every state-changing operation.

## 6. ChatGPT-safe tool design

Descriptions and schemas must help ChatGPT select tools correctly.

Requirements:

- use namespaced stable names;
- avoid overlapping tools with indistinguishable descriptions;
- state when a tool must be called before another;
- make read-only versus state-changing behavior explicit;
- use enums for execution levels, task types, risk modifiers, terminal states, and lifecycle actions;
- prohibit unknown input properties unless a specific reason is documented;
- include safe result statuses instead of relying only on prose;
- return structured errors with remediation guidance;
- never require the model to manufacture repository SHAs, approval identifiers, contract hashes, continuation tokens, or project IDs when those can be returned by prior tools;
- avoid exposing internal secrets, stack traces, absolute local paths, or unrestricted filesystem access.

## 7. Tool chaining and user journeys

Prove at least these end-to-end journeys through MCP.

### Journey A — known project status

```text
project.resolve
→ project.get_context
→ akb.search
```

Natural request example:

```text
Folytassuk a Mesél az Erdőt. Hol tartunk, és mi a következő jóváhagyott lépés?
```

### Journey B — ambiguous project

```text
project.resolve
→ USER_INPUT_REQUIRED
→ project.continue_resolution
→ project.get_context
```

No silent selection is permitted.

### Journey C — execution preparation

```text
project.resolve
→ execution.prepare
→ execution.get_status
→ execution.render_handoff
```

Preparation must not issue or consume a contract automatically.

### Journey D — approved Sprint contract

```text
execution.prepare
→ contract.generate
→ contract.validate
→ contract.issue
```

Issuance must require a durable approval reference and approved Sprint where policy requires it.

### Journey E — lifecycle safety

```text
contract.consume
→ execution.request_start
→ contract.complete
```

Prove invalid ordering, duplicate calls, stale baselines, wrong repositories, missing approvals, and forged identifiers are rejected.

## 8. Tool discovery and refresh

ChatGPT must discover the full public tool registry via `tools/list`.

Update the ChatGPT integration documentation with:

- final tool inventory;
- classification of each tool;
- example user prompts rather than only raw tool calls;
- required app refresh/re-scan steps after deployment;
- safe explanation of why some state-changing calls may require an additional confirmation or approval workflow;
- troubleshooting when ChatGPT shows only the old `factory.get_status` tool.

The tool list must be deterministic and versioned. Add a public `tool_surface_version` to status/capability output.

## 9. Assessment-first requirement

Before implementation, inspect and document:

1. existing internal MCP operation registry;
2. canonical project resolver and continuation state;
3. Execution Context generator;
4. Execution Contract generator and lifecycle services;
5. AKB/current-state storage and available search capability;
6. project visibility and authorization model;
7. audit/event/idempotency support;
8. whether a canonical Codex dispatcher/start-request model already exists;
9. current public MCP protocol implementation and tests;
10. any operation that must remain internal because authorization is not yet sufficient.

Reuse canonical services. Do not create parallel project resolution, context, AKB, contract, or lifecycle implementations.

If a required tool cannot safely be exposed because the underlying authorization or durable approval model is absent, implement the missing minimal canonical governance foundation within this Sprint rather than returning a fake tool. If that foundation would fundamentally change the approved architecture, record the precise business decision required.

## 10. Security and governance

- Maintain fail-closed authentication.
- Add authorization independent of authentication.
- Use constant-time credential comparison where relevant.
- Never expose secrets through tools or evidence.
- Enforce project scope on every project-specific tool.
- Enforce bounded output size and result limits.
- Validate all enums and identifiers.
- Store durable audit events for state-changing tools.
- Add idempotency keys or canonical duplicate protection for mutations.
- Protect against replay, forged continuation tokens, forged approval references, and lifecycle skipping.
- Treat tool descriptions and remote content as prompt-injection boundaries; Bridge canonical policy overrides tool caller instructions.
- No arbitrary shell, GitHub write, filesystem write, SQL, or code execution tool may be added in this Sprint.
- Do not expose raw Django model mutation APIs.

## 11. Compatibility

- Preserve the Sprint 006 remote MCP endpoint and Bearer authentication behavior.
- Preserve `factory.get_status` as a compatible public tool.
- Continue to support `initialize`, `notifications/initialized`, `tools/list`, and `tools/call` correctly.
- Unknown tools and invalid arguments return protocol-compliant errors/results.
- Keep the internal operation registry available to canonical services unless assessment proves it obsolete and migration is fully covered.
- Do not reintroduce the former proprietary public `operation/payload` protocol.

## 12. Required automated tests

Add tests for at least:

1. deterministic full tool discovery;
2. unique names and valid JSON schemas;
3. tool annotations and authorization classifications;
4. every tool's happy path;
5. invalid arguments and unknown properties;
6. project visibility enforcement;
7. ambiguous resolution and continuation;
8. expired/forged/consumed continuation tokens;
9. bounded AKB search and document retrieval;
10. execution preparation without implicit issuance;
11. policy resolution for multiple levels/task types/risks;
12. durable approval requirement for issue/consume/mutations;
13. invalid lifecycle ordering;
14. idempotent duplicate mutation behavior;
15. stale baseline/hash/repository rejection;
16. audit event creation;
17. tool chaining for Journeys A–E;
18. backward compatibility of `factory.get_status`;
19. Bearer auth failures and JSON-only error behavior;
20. complete repository Release Gates.

## 13. Live MCP acceptance

After deployment credentials are available, validate the staging endpoint through a standards-compliant remote MCP client:

```text
initialize
notifications/initialized
tools/list
tools/call for representative read-only tool
tools/call for project resolution
tools/call for execution preparation
```

Do not perform irreversible lifecycle mutations against staging merely for acceptance. Use seeded test records or a controlled reversible test fixture where mutation proof is required.

The final tool list must also be verified in ChatGPT Business using app refresh/re-scan. If Codex cannot access the Product Owner workspace UI, record this as the sole manual UI acceptance step only after all server-side behavior passes.

## 14. Documentation updates

Update at least:

```text
README.md
docs/architecture/MCP_EXECUTION_CONTEXT.md
docs/integrations/CHATGPT_MCP_CONNECTION.md
docs/akb/CURRENT_STATE.md
docs/roadmap/ROADMAP.md
```

Add a dedicated tool reference, preferably:

```text
docs/integrations/BRIDGE_MCP_TOOL_REFERENCE.md
```

For every public tool document:

- purpose;
- classification;
- prerequisites;
- input schema summary;
- result statuses;
- allowed next tools;
- mutation/audit behavior;
- example natural-language request.

## 15. Evidence

Evidence root:

```text
docs/evidence/sprint-007-governed-bridge-mcp-tool-surface/
```

Required artifacts:

```text
CLOSURE_REPORT.md
assessment.md
acceptance-results.json
tool-registry-validation.json
tool-schema-validation.json
authorization-validation.json
project-resolution-validation.json
akb-validation.json
execution-preparation-validation.json
contract-lifecycle-validation.json
audit-idempotency-validation.json
mcp-integration-validation.json
chatgpt-tool-scan-checklist.md
```

Evidence must bind repository, branch, baseline, final commit, consumed contract, completed lifecycle, exact commands, test results, and every acceptance journey.

## 16. Release Gates

Run all repository-wide gates resolved from `.bridge/project.yaml`, all policy-resolved gates, and every Sprint-specific acceptance test.

Ordinary implementation, schema, migration, dependency, test, lint, type, configuration, documentation, and evidence failures follow:

```text
DETECT → DIAGNOSE → REPAIR → RERUN
```

They are not Product Owner blockers.

## 17. Tiered Execution Contract requirement

Do not implement this Sprint from this file alone.

Use the canonical tiered Execution Contract Generator to generate, validate, and issue a new contract bound to this exact Sprint.

Required classification:

```yaml
execution_level: SPRINT
task_type: FEATURE
risk_modifiers:
  - EXTERNAL_INTEGRATION
  - AUTHENTICATION_OR_AUTHORIZATION
  - PUBLIC_API_OR_PROTOCOL
  - STATE_MUTATION
  - EXECUTION_ORCHESTRATION
```

If the canonical risk-modifier enum uses different existing names, map these intentions to the strongest available canonical modifiers and document the mapping. Do not weaken policy to make issuance easier.

The generated contract must:

- use the safe repository-stored baseline rule established after Sprint 006;
- bind this Sprint and all canonical documents by hash;
- resolve extended/deep assessment as required by policy;
- include authorization, integration, compatibility, lifecycle, audit, and evidence obligations;
- be committed to the repository in `ISSUED` state before implementation;
- be consumed before mutation;
- be completed with final commit and evidence binding at closure.

No bootstrap or manual-contract exception is permitted.

## 18. Closure

Allowed terminal states:

```text
PASS — READY FOR PRODUCT OWNER REVIEW
BLOCKED — BUSINESS DECISION REQUIRED
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

A PASS requires:

- all safe and necessary tools implemented;
- no fake or bypass tool;
- full automated acceptance;
- completed contract lifecycle;
- final commit pushed to `origin/main`;
- documentation and AKB synchronized;
- evidence committed;
- ChatGPT app re-scan either completed or isolated as the only remaining Product Owner UI acceptance step.
