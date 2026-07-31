# Factory Readiness Audit — 2026-07-31

**Classification:** canonical evidence baseline
**Decision:** **NOT READY**
**Maturity score:** **40/100**
**Estimated non-governance human intervention:** **55%**
**Knowledge maturity:** **4.3/10**

## Scope and method

This is an independent, evidence-based baseline of the AI Bridge development factory. It assesses the complete promised chain:

```text
ChatGPT Business → MCP → Orki assessment → governed execution → repository delivery
→ deployment → operational acceptance
```

Evidence was collected read-only from the repository, local canonical data store, public-tool registry, provider status, staging endpoint, and versioned evidence. No lifecycle record, provider configuration, credential, infrastructure, deployment, or runtime state was changed by this audit.

## Accepted findings

| Finding | Evidence | Consequence |
| --- | --- | --- |
| The full business-to-operational chain is not proven. | Staging MCP is reachable, but existing evidence records no remote provider restart or external-provider acceptance proof. | Reachability is not end-to-end acceptance. |
| Orki is not operationally proven. | `OrchestrationSession=0`, `OwnershipAssessment=0`, `OrchestrationDecision=0`. | No persisted assessment, ownership, or orchestration decision trail governs recovery. |
| Execution lifecycle is inconsistent. | Terminal runs coexist with `STARTED` / `RECOVERY_REVIEW_REQUIRED` jobs with expired leases; workspaces retain dead provider PIDs and `IN_USE` state. | Lifecycle is not yet a recovery-safe source of truth. |
| Automatic remediation is not evidenced. | `FailureIncident=0`, `TechnicalRemediationLoop=0`; observed terminalization/recovery requires operator action. | Routine recovery depends on Attila/operator intervention. |
| Delivery and operational acceptance are not automatic. | Sprint 014 proof is local; deployment guidance is manual/direct and no automatic delivery/operational-acceptance proof exists. | A local pass does not establish factory readiness. |
| AKB is structurally present but immature. | Before this audit `KnowledgeEntry=0`, `KnowledgeRevision=0`; no active knowledge existed. | Autonomous continuity has no reliable accepted knowledge base. |

## Supporting observations

- `manage.py check`, `manage.py validate_scopes`, migration dry-run, and the full test suite passed during the audit; 77 public tools were exposed.
- Codex CLI was locally installed/authenticated and `codex-cli` was `HEALTHY`; this proves local capability, not managed restart-safe lifecycle.
- `GET https://stage.artificial-software-factory.com/mcp/` returned `405`: endpoint reachability only, not authenticated MCP, ChatGPT Business configuration, Orki, delivery, or acceptance.

## Required corrective direction

The next implementation boundary is **EPIC — Canonical Execution Lifecycle Integrity and Autonomous Recovery**. Its implementation-ready proposal is [Sprint 016](../../sprints/SPRINT_016_CANONICAL_EXECUTION_LIFECYCLE_INTEGRITY_AND_AUTONOMOUS_RECOVERY.md); it is a draft only and has no execution authority.

## Cross-links

- [Roadmap maturity baseline](../../roadmap/ROADMAP.md)
- [AKB baseline](../../akb/FACTORY_READINESS_MATURITY_BASELINE_2026-07-31.md)
- [Factory Development Mode execution record](EXECUTION_RECORD.md)
- AKB candidate: `ai-bridge:factory-readiness-maturity-baseline:2026-07-31`, `entry_id=1`, status `CANDIDATE` (not published)
