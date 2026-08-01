# Factory Readiness Dossier — 2026-08-01

**Epic:** AI Bridge Factory Readiness Remediation (Issue #15)
**Sprint:** 8 — Final Factory Readiness Audit and Attila-Role Acceptance
**Audit baseline:** `40 / 100` maturity, approximately `55%` non-governance human intervention, and `4.3 / 10` knowledge durability
**Audited implementation revision:** `0aa8f503492c3baf08788bdcd83e19868339d5b4`
**Audit result:** **AI Bridge-owned readiness materially improved; full Epic readiness is not certified while ChatGPT Business Platform Certification is pending.**

## Decision boundary

This is an evidence-backed final audit, not a substitution for the missing external-platform proof. The Product Owner deliberately moved that proof to the separate **ChatGPT Business Platform Certification** Epic. Sprint 6 remains historical and unchanged at `BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE`; it is not counted as PASS.

| Boundary | Result | Meaning |
| --- | --- | --- |
| AI Bridge-owned components | **READY SUBJECT TO NORMAL RELEASE GOVERNANCE** | The durable governance, Orki, lifecycle, recovery, workspace, provider, delivery, deployment, AKB, roadmap, and Admin/MCP projections have accepted engineering or isolated-runtime evidence. |
| Complete Product Owner UI to production chain | **NOT CERTIFIED** | A real ChatGPT Business UI request, UI approval, Remote MCP invocation, deployment and later status-retrieval chain cannot be proved from this environment. It belongs to the external certification Epic. |
| Epic #15 final verdict | **OPEN — external certification pending** | The canonical Epic requires all eight Sprints to PASS and a repeatable complete chain. Those conditions are not met while Sprint 6 is not PASS. |

No document in this package labels the unproven external chain as operationally accepted or autonomously ready.

## Maturity reassessment

The original audit scored the complete promised chain at 40/100. The same complete-chain standard is retained here, including the unavailable ChatGPT Business boundary. The score is therefore deliberately lower than a score that would assess only code or only unit tests.

| Dimension | Baseline finding | Final evidence and score | Score / 10 |
| --- | --- | --- | ---: |
| ChatGPT Business / Remote MCP connection | Reachability only; no in-app proof. | Signed-session confirmation repair and local authenticated HTTP/MCP proof exist, but ChatGPT Business UI proof is still external. | 3 |
| Product Owner experience | Routine recovery needed an operator. | Scope/version/hash confirmation is durable and technical recovery is autonomous; in-app approval usability is unverified. | 6 |
| Orki orchestration | No durable sessions, assessment, or decisions. | Sprint 2 persisted session → ownership → decision → contract/run chain and operational proof. | 9 |
| Context, AKB, and roadmap | No active knowledge or durable reuse. | Sprint 3 persisted project-isolated context packages, source versions, consumers, and approval-gated roadmap feedback. | 9 |
| Governance and contract integrity | Incomplete lifecycle binding. | Contract, exact scope/hash binding, confirmation, delivery and completion guardrails are tested and audited. | 9 |
| Execution lifecycle, worker, and recovery | Expired leases, dead PIDs, and inconsistent states. | Sprint 1 and Sprint 7 prove fenced leases, deterministic recovery, bounded remediation, independent gate reruns, and checkpoint restore. | 10 |
| Isolated workspace and provider integration | Dead provider/workspace handling required intervention. | Isolated checkout/database/venv lifecycle and stale-provisioning/provider recovery are evidenced. | 9 |
| Repository delivery | Local-only proof. | Sprint 4 proves clean scoped checkout, normal push, remote SHA readback, and durable shared delivery projection. | 9 |
| Deployment and operational acceptance | Manual/direct deployment and no valid OA chain. | Sprint 5 proves SHA-bound forward deployment, controlled mismatch failure, health/supervision checks and rollback in isolated runtime. | 9 |
| Admin/API/MCP transparency and evidence discipline | State was not reliably shared. | Common canonical projections and honest retained failed-attempt evidence are present across the accepted sprints. | 9 |

**Final complete-chain maturity: 82 / 100 (`+42` from baseline).** The score is not a release verdict. The remaining gap is concentrated at the single critical external platform boundary; a numerical improvement cannot override that missing proof.

### Human intervention and knowledge durability

- **Human technical intervention:** accepted owned-component scenarios demonstrate no routine operator repair: reconciliation, remediation, lease release, validation, and checkpoint resume are durable. A replacement for the baseline `~55%` whole-chain estimate is intentionally **not calculated**, because no valid sampled ChatGPT Business UI run exists. The remaining human action is an external workspace-admin/platform-certification action, not a routine engineering recovery step.
- **Knowledge durability:** **8.8 / 10 (`+4.5`)**. This is supported by versioned, project-isolated AKB records; retrieval packages linked to Orki/session/decision/contract/run consumers; stale/conflict diagnostics; and approval-gated roadmap updates. The missing 1.2 reflects that a new ChatGPT Business session has not yet been proved to retrieve final state through the external UI path.

## Sprint compliance matrix

The Product Owner acceptance statements are durable conversation authority; where a dated repository acceptance record does not exist, the date is marked as *recorded in Product Owner instruction* rather than invented.

| Sprint | Goal and delivered capability | Engineering evidence | Operational evidence | Product Owner status |
| --- | --- | --- | --- | --- |
| 1 | Deterministic lifecycle and recovery; stale lease/dead provider/workspace reconciliation. | `sprint-016-canonical-execution-lifecycle-integrity-and-autonomous-recovery/ACCEPTANCE_RESULTS.md` | `OPERATIONAL_ACCEPTANCE_2026-07-31.md` | PASS — accepted (Product Owner instruction) |
| 2 | Orki is the mandatory orchestration gate. | `sprint-017-orki-mandatory-orchestration-gate/ENGINEERING_ACCEPTANCE.md` | `OPERATIONAL_ACCEPTANCE.md` | PASS — accepted (Product Owner instruction) |
| 3 | Durable AKB retrieval/reuse and approval-gated roadmap feedback. | `factory-readiness-remediation-sprint-3-20260731/ENGINEERING_ACCEPTANCE.md` | `OPERATIONAL_ACCEPTANCE.md` | PASS — accepted (Product Owner instruction) |
| 4 | Canonical verified repository delivery. | `sprint-018-autonomous-repository-delivery/ENGINEERING_ACCEPTANCE.md` | `OPERATIONAL_ACCEPTANCE.md` | PASS — accepted (Product Owner instruction) |
| 5 | SHA-bound deployment and runtime operational acceptance. | `sprint-019-runtime-deployment-operational-acceptance/ENGINEERING_ACCEPTANCE.md` | `OPERATIONAL_ACCEPTANCE.md` | PASS — accepted (Product Owner instruction) |
| 6 | Full ChatGPT Business factory E2E. | Engineering repairs and local preflight retained in `sprint-020-chatgpt-factory-e2e/` | No qualifying in-app UI evidence | **NOT PASS** — external platform certification pending |
| 7 | Autonomous technical remediation, bounded retry and safe resume. | `sprint-021-autonomous-technical-remediation-self-healing/ENGINEERING_ACCEPTANCE.md` | `OPERATIONAL_ACCEPTANCE.md` | PASS — accepted (2026-08-01 Product Owner instruction) |
| 8 | Final re-audit and Attila-role acceptance. | This dossier and [release gates](RELEASE_GATES.md) | [Acceptance-scenario audit](ACCEPTANCE_SCENARIO_AUDIT.md) | **Not eligible for full PASS** while Sprint 6 remains non-PASS |

## Accepted and unaccepted evidence

### Accepted evidence

- Sprint 1 isolated-runtime worker, lease expiry, dead-provider, completion, and Admin/MCP projection evidence.
- Sprint 2 authenticated HTTP–MCP request and persisted Orki chain evidence.
- Sprint 3 project isolation, durable context/retrieval, roadmap lifecycle and Admin/MCP consistency evidence.
- Sprint 4 local Git delivery, remote-SHA verification and delivery fault injection evidence.
- Sprint 5 live isolated deployment, controlled SHA mismatch, forward deployment and rollback evidence.
- Sprint 7 live HTTP/MCP smoke proof and remediation/requeue/checkpoint-resume evidence.

### Explicitly unaccepted as full-chain proof

- A bearer-token local HTTP request is not evidence of a ChatGPT Business UI request.
- A seed or fixture is not evidence of a provider, delivery, deployment, or later retrieval event.
- Prior local delivery and isolated deployment evidence do not prove the complete external Product Owner UI chain.
- The failed initial Sprint 8 scope-validation invocation is audit evidence, not a product failure and not concealed; see [Failed attempts](FAILED_ATTEMPTS.md).

## Final acceptance-scenario result

Sprint 8 requires one external-project change and one AI Bridge self-development change through the canonical managed path, followed by a new ChatGPT session status query. The latter session begins at ChatGPT Business and therefore cannot be simulated honestly by this execution environment. The scenario is **not run** and is recorded as an external certification prerequisite, not converted into a local substitute. See [acceptance-scenario audit](ACCEPTANCE_SCENARIO_AUDIT.md).

## Remaining limitations and next work

1. A ChatGPT Business workspace administrator must make the AI Bridge staging Remote MCP app available to the certification environment.
2. The external certification Epic must record a genuine UI-originated request, UI approval, Remote MCP trace, Orki/run/provider/delivery/deployment chain, and a later UI status retrieval.
3. The certification must bind runtime revision, repository delivery SHA and deployment receipt without exposing credentials.
4. Until that succeeds, Issue #15 must stay open and must not claim `PASS — AI BRIDGE AUTONOMOUS SOFTWARE FACTORY READINESS PROVEN`.

## Attila / Product Owner role conclusion

The accepted owned-component evidence removes Attila from routine technical dispatch, repair, recovery, validation, delivery verification, and state reconstruction. Attila remains correctly required for Product Owner business decisions and for external ChatGPT Business workspace administration. The latter is a platform-access boundary, not an AI Bridge technical task.

## Cross-links

- [Baseline audit](../factory-readiness-audit-20260731/FACTORY_READINESS_AUDIT.md)
- [Sprint 6 preserved external-boundary closure](../factory-readiness-sprint-6-workspace-provisioning-recovery-20260731/CLOSURE_REPORT.md)
- [Sprint 7 closure](../sprint-021-autonomous-technical-remediation-self-healing/CLOSURE_REPORT.md)
- [Independent Sprint 8 audit](INDEPENDENT_SPRINT_AUDIT.md)
- [Closure report](CLOSURE_REPORT.md)
