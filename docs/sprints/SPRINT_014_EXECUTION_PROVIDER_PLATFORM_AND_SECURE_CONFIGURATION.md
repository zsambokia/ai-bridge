# Sprint 014 — Execution Provider Platform and Secure Configuration

**Status:** APPROVED FOR CODEX EXECUTION  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Execution level:** SPRINT  
**Task type:** SELF_DEVELOPMENT  
**Target branch:** `main`  
**Baseline:** `4f2ff74df681ba62b3783efcbc1ba90870f698cd`  
**Primary outcome:** Replace the proven hard-coded `codex-cli` provider boundary with a governed, provider-neutral execution platform that can register, configure, select, validate, dispatch, observe, cancel, and audit multiple provider kinds without creating a parallel approval, contract, or orchestration lifecycle.

## 1. Proven baseline

Sprint 013 proved the following:

- `AUDIT` is a canonical work type;
- `conversation.confirm` is the canonical conversational Product Owner confirmation entry point;
- `GovernanceApproval`, `ConversationOrchestration`, `ExecutionContract`, consumption, and `ExecutionRun` already form the canonical governed lifecycle;
- provider identity is now carried through contract, consumption, dispatch, status, and cancellation;
- the only operational provider is `codex-cli`;
- the provider implementation is classified as `EXECUTION_PROVIDER_IS_HARD_CODED`;
- no generic provider registry, provider configuration domain, capability negotiation, or dynamic provider selection currently exists.

Sprint 014 must build on that proven baseline. It must not replace or duplicate the canonical governance lifecycle.

## 2. Governing principle

Before creating any new abstraction, prove whether an adequate provider registry, provider configuration model, secret abstraction, capability model, adapter interface, dispatch resolver, or admin surface already exists.

Prefer extending and composing existing canonical services. A new component is allowed only when the repository assessment proves a real gap.

## 3. Scope decisions

### 3.1 Provider categories

The platform must distinguish provider roles rather than pretending all integrations execute the same kind of work.

Initial provider kinds:

```text
CODEX
OPENAI
CLAUDE
GITHUB
BIGQUERY
```

Required role classification:

```text
EXECUTION_AGENT
MODEL_API
REPOSITORY_SERVICE
DATA_SERVICE
```

Expected initial mapping:

```text
CODEX    → EXECUTION_AGENT
OPENAI   → MODEL_API and optionally EXECUTION_AGENT only if a real executable adapter is implemented and proven
CLAUDE   → MODEL_API and optionally EXECUTION_AGENT only if a real executable adapter is implemented and proven
GITHUB   → REPOSITORY_SERVICE
BIGQUERY → DATA_SERVICE
```

Do not claim that GitHub or BigQuery are coding agents. They are governed providers/services used by execution workflows.

### 3.2 Canonical lifecycle preservation

The existing flow remains authoritative:

```text
Product Owner intent
→ proposal
→ review
→ conversation.confirm
→ GovernanceApproval
→ ConversationOrchestration
→ Execution Contract
→ provider selection
→ contract consumption
→ provider dispatch
→ status/cancellation
→ evidence
→ completion
```

Sprint 014 may generalize provider resolution and dispatch, but it must not create:

- another approval model;
- another contract model;
- another orchestration model;
- provider-specific authorization shortcuts;
- direct admin-triggered repository mutation outside the governed lifecycle.

## 4. Mandatory assessment before implementation

Inspect and document:

- current `codex-cli` adapter and resolver;
- provider identity fields in contracts and consumption receipts;
- execution start, status, cancellation, retry, and completion paths;
- current secret/environment-variable handling;
- existing Django models and admin patterns;
- any existing connector, credential, integration, or configuration domains;
- current encryption, signing, hashing, redaction, and audit facilities;
- current GitHub and BigQuery usage;
- any OpenAI or Claude SDK/client usage;
- provider names that exist only in documentation.

Classify each relevant component as:

```text
ALREADY_REUSABLE
PARTIALLY_REUSABLE
HARD_CODED
DUPLICATE
MISSING
DOCUMENTATION_ONLY
```

Create the assessment before writing the provider platform.

## 5. Provider domain

Implement the smallest provider-neutral domain proven necessary by the assessment.

At minimum, the domain must represent:

```yaml
provider:
  id: stable identifier
  name: human-readable name
  kind: CODEX | OPENAI | CLAUDE | GITHUB | BIGQUERY
  role: EXECUTION_AGENT | MODEL_API | REPOSITORY_SERVICE | DATA_SERVICE
  status: DRAFT | ACTIVE | DISABLED | UNAVAILABLE | MISCONFIGURED | DEPRECATED
  adapter_key: stable adapter identity
  enabled: boolean
  priority: integer
  configuration: non-secret structured settings
  credential_binding: secure secret reference
  capabilities: []
  health_status: UNKNOWN | HEALTHY | DEGRADED | UNAVAILABLE | MISCONFIGURED
  last_health_check_at: timestamp or null
  created_at: timestamp
  updated_at: timestamp
```

Provider identity must remain stable and auditable.

## 6. Secure configuration and credentials

Execution Provider configuration must be manageable in Django admin.

The Product Owner or authorized administrator must be able to configure, as applicable:

- API keys;
- access tokens;
- passwords;
- client IDs;
- client secrets;
- service-account credentials;
- project/account identifiers;
- organization identifiers;
- endpoints and regions;
- model names;
- timeouts;
- concurrency limits;
- provider-specific command paths and workspace settings;
- enabled/disabled state;
- priority and allowed capabilities.

### 6.1 Secret safety invariants

Secrets must never:

- be stored in Git;
- appear in evidence;
- appear in logs or tracebacks;
- appear in API responses;
- appear in MCP responses;
- appear in admin list views;
- be returned after save;
- be included in contract payloads;
- be included in provider status metadata.

The implementation must use an existing secure secret facility if one already exists.

If no adequate facility exists, implement the smallest secure abstraction possible. The preferred design is secret references backed by environment variables or an external secret backend. Database persistence of encrypted secret material is allowed only when:

- encryption at rest is implemented with a key not stored in the database or repository;
- values are write-only in Django admin;
- rotation and replacement are supported;
- decryption is restricted to the provider runtime boundary;
- redaction and audit tests prove secrets cannot leak.

Never store plaintext secrets in the database.

### 6.2 Django admin requirements

Django admin must provide:

- provider list and detail views;
- safe provider creation and editing;
- write-only secret inputs;
- masked credential status such as `configured`, `missing`, or `invalid`, never secret content;
- capability configuration;
- enable/disable controls;
- provider role and kind validation;
- priority configuration;
- health-check action;
- test-configuration action that performs a non-mutating connectivity/authentication check where supported;
- last test result and timestamp;
- immutable or clearly audited provider identity fields after first use;
- audit history for security-sensitive changes.

Admin actions must not directly start governed code execution.

## 7. Provider adapter contract

Introduce or generalize one canonical adapter boundary only if the assessment proves it is missing.

The adapter contract must support only the operations appropriate for the provider role.

Common operations may include:

```text
validate_configuration
health_check
get_capabilities
```

Execution-agent operations:

```text
start
status
cancel
collect_result
```

Repository-service operations:

```text
read_repository_state
create_branch
commit_or_push through governed execution context
open_pull_request
status
```

Data-service operations:

```text
validate_query
execute_read
execute_governed_write when explicitly authorized
job_status
cancel_job
```

Model API operations:

```text
invoke_model
stream_result where supported
estimate_or_record usage
```

Do not force every provider to implement irrelevant methods. Use capabilities or role-specific protocols rather than empty or misleading stubs.

## 8. Initial provider implementations

### 8.1 Codex

Migrate the existing `codex-cli` implementation behind the canonical provider boundary without changing its proven behavior.

Codex must remain operational and must pass the full governed execution proof.

### 8.2 OpenAI

Add a real configurable OpenAI provider using the current official API/client supported by the repository environment.

At minimum prove:

- credential/configuration validation;
- non-mutating health check;
- one real bounded model invocation;
- capability reporting;
- usage and error recording without secret leakage.

Do not claim full autonomous coding execution unless a real execution-agent adapter is implemented and proven end to end.

### 8.3 Claude

Add a real configurable Claude provider using the official supported API/client available to the environment.

At minimum prove:

- credential/configuration validation;
- non-mutating health check;
- one real bounded model invocation;
- capability reporting;
- usage and error recording without secret leakage.

Do not claim Claude Code execution unless an actual executable Claude Code adapter is available locally and proven.

### 8.4 GitHub

Represent GitHub as a governed repository-service provider.

At minimum prove:

- secure credential binding or reuse of an existing authenticated integration;
- repository read/status capability;
- one harmless governed write in a test or proof repository/scope;
- explicit repository and branch binding;
- no unrestricted repository mutation from Django admin;
- status and error reporting.

Reuse existing GitHub integration code where adequate. Do not create a second GitHub lifecycle.

### 8.5 BigQuery

Represent BigQuery as a governed data-service provider.

At minimum prove:

- secure service-account or application-default credential binding;
- project/dataset configuration;
- non-mutating health check;
- one bounded read-only query;
- capability reporting;
- job status and cancellation where supported;
- no data-changing query without an exact governed contract and explicit mutation permission.

## 9. Provider capabilities

Capabilities must be structured and queryable.

At minimum support:

```text
CODE_EXECUTION
MODEL_INFERENCE
REPOSITORY_READ
REPOSITORY_WRITE
BRANCH_MANAGEMENT
PULL_REQUEST_MANAGEMENT
DATA_QUERY_READ
DATA_QUERY_WRITE
STREAMING
CANCELLATION
STATUS_POLLING
USAGE_REPORTING
HEALTH_CHECK
```

The provider must report only capabilities actually implemented and proven.

Contracts must request capabilities, not provider marketing names alone.

## 10. Provider selection

Implement deterministic provider selection using existing contract policy where possible.

Selection must consider:

- requested provider identity, when explicitly approved;
- required capabilities;
- provider role;
- enabled status;
- configuration validity;
- health status;
- project/provider allow-list;
- contract-eligible provider identities;
- deterministic priority;
- no silent fallback when the contract pins an exact provider.

When the Product Owner has not selected an exact provider, policy may choose among eligible configured providers only if the proposal and contract permit policy-based selection.

Selection must be recorded in the issued contract before consumption.

## 11. Failure and fallback rules

- A disabled, missing, misconfigured, or unhealthy provider must not be dispatched.
- Exact provider selection must fail truthfully rather than silently fall back.
- Policy-based fallback is allowed only when explicitly authorized by the contract.
- A fallback must create an auditable event and preserve idempotency.
- No duplicate execution may occur during retry or fallback.
- Provider-specific technical failure enters the autonomous diagnose/repair/retry loop where safe.
- Credential or permission decisions reserved for the Product Owner must stop with an exact actionable status.

## 12. Public and admin visibility

Add or extend read-only MCP capabilities only where necessary to expose safe provider state, such as:

```text
provider.list
provider.get
provider.capabilities
provider.health
```

Public responses may include:

- provider identity;
- kind and role;
- enabled/status state;
- safe capability list;
- safe health summary;
- last check timestamp.

They must not expose secrets, credential references that reveal infrastructure details, raw exception payloads, or internal command lines.

Provider creation, secret mutation, activation, or destructive configuration changes must remain admin-governed and permission-protected.

## 13. Required acceptance proofs

Use fresh proof objects and avoid active production repositories or datasets.

### 13.1 Codex governed execution

Prove one real Work Item from proposal through `conversation.confirm`, contract issuance, dynamic provider selection, consumption, Codex dispatch, completion, and evidence.

### 13.2 OpenAI provider

From Django admin or a governed configuration path:

- configure the provider safely;
- prove credentials are write-only and redacted;
- run health check;
- perform one bounded model invocation;
- record safe result metadata and usage.

### 13.3 Claude provider

Perform the equivalent proof for Claude when credentials are available.

If credentials are not supplied, prove the complete configuration, validation, unavailable-state, redaction, and no-dispatch behavior. Do not fabricate a successful external call.

### 13.4 GitHub provider

Prove one harmless governed repository-service operation with exact repository/branch binding and evidence.

### 13.5 BigQuery provider

Prove one bounded read-only query against an explicitly configured safe dataset/project. If credentials or a safe dataset are unavailable, prove configuration validation and truthful unavailability without fabricating execution.

### 13.6 Selection and rejection

Prove:

- capability-based selection chooses an eligible provider deterministically;
- exact selected provider is preserved through contract and receipt;
- unsupported capability is rejected;
- disabled provider is rejected;
- misconfigured provider is rejected;
- unhealthy provider is rejected or handled according to explicit contract policy;
- exact-provider execution never silently falls back;
- policy-authorized fallback is idempotent and auditable, if implemented.

### 13.7 Secret negative proofs

Prove secrets do not appear in:

- database plaintext inspection;
- admin pages after save;
- MCP responses;
- contract payloads;
- execution records;
- logs;
- tracebacks;
- evidence;
- Git diff;
- commits.

## 14. Evidence

Create evidence under:

```text
docs/evidence/sprint-014/
```

At minimum include:

```text
EXISTING_PROVIDER_ASSESSMENT.md
PROVIDER_DOMAIN_AND_ROLE_MODEL.md
SECURE_CONFIGURATION_DESIGN.md
DJANGO_ADMIN_PROOF.md
PROVIDER_ADAPTER_CONTRACT.md
PROVIDER_REGISTRY_PROOF.md
PROVIDER_SELECTION_PROOF.md
CODEX_MIGRATION_AND_EXECUTION_PROOF.md
OPENAI_PROVIDER_PROOF.md
CLAUDE_PROVIDER_PROOF.md
GITHUB_PROVIDER_PROOF.md
BIGQUERY_PROVIDER_PROOF.md
SECRET_REDACTION_AND_STORAGE_PROOF.md
NEGATIVE_AND_FAILURE_PROOFS.md
IDEMPOTENCY_AND_RETRY_PROOF.md
REMOTE_END_TO_END_PROOF.md
RELEASE_GATE_RESULTS.md
REMAINING_LIMITATIONS.md
acceptance-results.json
```

Evidence must distinguish:

- operational and remotely proven;
- locally proven;
- configured but unavailable due to missing credentials;
- documentation-only;
- explicitly deferred.

## 15. Documentation

Update as applicable:

- README;
- architecture;
- MCP tool reference;
- Django admin/operator documentation;
- local runtime and deployment documentation;
- secret-management documentation;
- AKB/current state;
- roadmap;
- evidence index;
- applicable `AGENTS.md` files.

Document provider roles clearly so users do not confuse model APIs, execution agents, repository services, and data services.

## 16. Prohibited solutions

Do not:

- store plaintext credentials;
- commit credentials;
- expose secrets in evidence or responses;
- build a second approval or contract lifecycle;
- allow Django admin to bypass governed execution;
- represent documentation-only providers as operational;
- claim OpenAI or Claude autonomous coding execution based only on a model API call;
- treat GitHub or BigQuery as coding agents;
- silently fall back from an exact provider;
- duplicate existing GitHub, contract, orchestration, or audit services;
- add a broad marketplace, billing engine, or multi-agent scheduler not required by this Sprint;
- stop at the first local defect.

## 17. Release Gates

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

Also run:

- Django admin tests for permissions, masking, write-only secrets, validation, and audit history;
- provider registry and selection tests;
- adapter contract tests;
- secret-leak scans across logs, evidence, Git diff, and generated payloads;
- real provider proofs where credentials are available;
- local MCP restart and remote acceptance through the Cloudflare Tunnel.

## 18. Autonomous test–diagnose–fix loop

The development environment is local:

```text
ChatGPT
→ Cloudflare Tunnel
→ 127.0.0.1:8001
→ local AI Bridge MCP server
→ local Django/provider runtime
```

For any local HTTP 500, traceback, failing gate, adapter error, migration issue, routing defect, or restartable runtime failure:

```text
test
→ inspect local logs
→ reproduce
→ add regression test
→ implement minimal fix
→ rerun gates
→ restart MCP/runtime
→ retest
```

Continue until PASS or until a genuine external blocker is proven.

Missing external credentials may block only the corresponding live external-provider proof. They do not block implementation, safe configuration, negative tests, truthful unavailable status, or the operational Codex proof.

## 19. Commit rule

Do not commit partial or unproven work.

Before the final commit:

- complete the assessment;
- implement the smallest justified provider platform;
- migrate Codex without regression;
- complete Django admin secure configuration;
- complete all available provider proofs;
- truthfully document credential-dependent limitations;
- pass all Release Gates;
- verify no secret material is present.

Then create one coherent commit, push to `origin/main`, restart the local runtime from that commit, and rerun the final smoke proof.

## 20. Completion criteria

Sprint 014 is complete only when:

- the hard-coded Codex boundary is replaced by one canonical provider registry/resolver;
- Codex still completes a real governed execution;
- provider roles and capabilities are structured;
- Django admin safely manages provider configuration;
- secrets are write-only, protected, redacted, and never committed;
- provider selection is deterministic and contract-bound;
- unsupported, disabled, unhealthy, and misconfigured providers fail truthfully;
- OpenAI, Claude, GitHub, and BigQuery are represented accurately according to their proven operational level;
- available external-provider proofs are real;
- unavailable credentials produce explicit limitations rather than fabricated success;
- retries remain idempotent;
- documentation and evidence are complete;
- all Release Gates pass;
- final commit is pushed and the runtime is verified from that commit.

## 21. Final report

Return:

- baseline commit;
- final commit and push result;
- deployed/runtime commit;
- migration summary;
- provider-domain components created or reused;
- provider inventory with kind, role, status, and proven capabilities;
- Django admin configuration summary;
- secret backend and encryption/reference model;
- Codex proof identifiers;
- OpenAI proof or exact credential blocker;
- Claude proof or exact credential blocker;
- GitHub proof identifiers;
- BigQuery proof or exact credential/dataset blocker;
- selection and rejection proofs;
- idempotency proof;
- secret negative-proof results;
- Release Gate results;
- evidence paths;
- remaining limitations;
- Product Owner retest instructions.

Allowed terminal responses:

```text
PASS — READY FOR PRODUCT OWNER ACCEPTANCE
```

or

```text
FAIL — BLOCKED
```

`FAIL — BLOCKED` is allowed only when the remaining blocker is outside the repository, local Django application, local MCP server, local provider runtime, local logs, local restart/deployment control, and available configuration. A local defect is not a terminal blocker.
