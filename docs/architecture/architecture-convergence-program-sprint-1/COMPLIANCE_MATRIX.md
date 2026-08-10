---
status: SUPPORTING
version: 0.1.0
---

# Compliance Matrix

`Aligned` means a documented foundation exists, not that an end-to-end Runtime
claim is certified. `Partial` and `Gap` require future governed work.

| Approved requirement | Evidence in current documents / repository | Status | Classification | Closure action |
| --- | --- | --- | --- | --- |
| Mission is unified Runtime intake | Runtime 2.0 makes MSM Mission authority; Factory Chat still has direct legacy route per R20-00. | Partial | Módosítani | ADR-022 and Phase 2. |
| Conversation only for humans | Conversation is projection/ingress; MCP binding and Factory Chat exist. Other ingress is not one explicit contract. | Partial | Módosítani | Separate human Conversation Adapter from common intake. |
| Operational Foundation is independent layer | Foundation Constitution and Runtime 2.0 define provider-bound handoff. | Aligned | Megtartani | Elevate as Book chapter. |
| AI Kernel is a distinct execution core | Existing Runtime documents mix operational-core and broader runtime terminology; no accepted AI Kernel boundary exists. | Gap | Új elem / ADR szükséges | Adopt Article III and ADR-033; retain legacy terms as transitional aliases until migration proof. |
| Execution is first-class; Engine does not run | `ExecutionRun` exists as attempt; no canonical Execution aggregate. | Partial | ADR szükséges | ADR-023 and Phase 3. |
| Engine operationally stateless | Engine documents permit own persisted state but do not separate business from execution state. | Partial | Módosítani | Explicit invariant and ownership tests. |
| Capability-first addressing | Domain Engines are first-class, but no capability catalogue/resolver contract exists. | Gap | Új elem / ADR szükséges | ADR-024 and Phase 2. |
| Stateless Provider; stateful Provider Executor | Existing provider gateway, `ExecutionRun` and recovery mechanics exist; the active governed path is intentionally fixed to `codex-cli`. | Gap | Új elem / ADR szükséges | ADR-029 and Phase 3; do not relabel existing mechanics as Provider Executor compliance. |
| Provider binding is immutable for an Execution | Existing provider selection and recovery records do not yet establish an immutable, auditable binding on a canonical Execution. | Gap | Módosítani / ADR szükséges | ADR-029 with ADR-023; allow replacement Executor only within the already-bound Provider. |
| Recovery remains within the bound Provider | Existing recovery behavior is not yet constrained by a Provider Binding and Runtime Profile contract. | Gap | Módosítani / ADR szükséges | ADR-029 and Phase 3; provider outage must be explicit, never an automatic cross-provider failover. |
| Provider Resolver and Provider-owned capacity | No capability-aware multi-provider selection, executor pool, capacity-exhausted result or policy-governed fallback contract is implemented. | Gap | Új elem / ADR szükséges | ADR-029 and Phase 3. |
| Immutable auditable Context Package | `KnowledgeContextPackage` and evidence foundations exist; no generalized reproducible execution context. | Partial | Új elem / ADR szükséges | ADR-025 and Phase 3. |
| Scope-aware / tenant-ready | Project isolation exists; no organization/workspace/repository scope model or scoped authorization. | Gap | ADR szükséges | ADR-021 and Phases 1, 5. |
| Localization-ready | Some Hungarian UI content; project settings do not establish a platform i18n model. | Gap | Új elem / ADR szükséges | ADR-026 and Phase 5. |
| Canonical English normative language | Existing normative docs are predominantly English. | Partial | Megtartani / Módosítani | Make derivation/version rule explicit. |
| Evidence, correlation, recovery | Strong existing evidence, `ExecutionRun`, job/recovery and multiple event records. | Partial | Migrálni | ADR-027 and Phase 6. |
| Historical record preservation | Baseline/evolution documents distinguish current and target state. | Aligned | Megtartani | Apply Book status labels without rewriting evidence. |
