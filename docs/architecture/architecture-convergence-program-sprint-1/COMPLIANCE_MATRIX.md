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
| Execution is first-class; Engine does not run | `ExecutionRun` exists as attempt; no canonical Execution aggregate. | Partial | ADR szükséges | ADR-023 and Phase 3. |
| Engine operationally stateless | Engine documents permit own persisted state but do not separate business from execution state. | Partial | Módosítani | Explicit invariant and ownership tests. |
| Capability-first addressing | Domain Engines are first-class, but no capability catalogue/resolver contract exists. | Gap | Új elem / ADR szükséges | ADR-024 and Phase 2. |
| Immutable auditable Context Package | `KnowledgeContextPackage` and evidence foundations exist; no generalized reproducible execution context. | Partial | Új elem / ADR szükséges | ADR-025 and Phase 3. |
| Scope-aware / tenant-ready | Project isolation exists; no organization/workspace/repository scope model or scoped authorization. | Gap | ADR szükséges | ADR-021 and Phases 1, 5. |
| Localization-ready | Some Hungarian UI content; project settings do not establish a platform i18n model. | Gap | Új elem / ADR szükséges | ADR-026 and Phase 5. |
| Canonical English normative language | Existing normative docs are predominantly English. | Partial | Megtartani / Módosítani | Make derivation/version rule explicit. |
| Evidence, correlation, recovery | Strong existing evidence, `ExecutionRun`, job/recovery and multiple event records. | Partial | Migrálni | ADR-027 and Phase 6. |
| Historical record preservation | Baseline/evolution documents distinguish current and target state. | Aligned | Megtartani | Apply Book status labels without rewriting evidence. |
