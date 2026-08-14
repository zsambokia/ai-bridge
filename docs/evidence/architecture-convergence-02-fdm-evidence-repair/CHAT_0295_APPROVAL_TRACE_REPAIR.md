# CHAT-0295 approval trace repair

## Finding and root cause

The prior approval-register row ended at `CHAT-0290`. It therefore omitted the
stable source locator for the Product Owner's explicit acceptance of the final
seven L3 closure proposals. The target semantics were already reconstructed;
this repair changes traceability, not architecture.

## Primary-source chain

| Step | Reproducible source | Finding |
| --- | --- | --- |
| Request for closure | `CHAT-0293`, manifest id `661c5e3c-20cd-4151-a0ed-d6b2b69d3ae5` | The Product Owner asks for proposals for every remaining point so the area can be closed. |
| Proposals | `CHAT-0294`, manifest id `414e1965-b86f-4a4b-85b9-ba9661cb0698` | FP-L3/11–17 specify Artifact Contract, materialization/payload, integrity, composition/dependencies, applicability, retention/availability/scope, and L3 protocol hand-off. |
| Approval | `CHAT-0295`, manifest id `0fde5f19-6df7-48ac-8a0c-f4eb08158068` | The Product Owner individually accepts FP-L3/11 through FP-L3/17. |
| Later boundary refinement | `CHAT-0297` | L4 must not be treated as resolution-only; this does not revoke the L3 acceptance. |

The acquisition manifest records all four messages as exact-id-verified. There
is no source timestamp; the deterministic locator is acquisition sequence plus
manifest UUID and role.

## Decision and impact mapping

| Approved item | Reconstruction target | Constitutional impact |
| --- | --- | --- |
| FP-L3/11–16 | R-20 Artifact Contract/version/payload/integrity/lifecycle semantics; `TARGET_ARCHITECTURE.md`, Factory Protocol L3 | `02_CONSTITUTION_AMENDMENT_REQUIREMENTS.md` §3 L3 and §6 Knowledge architecture. |
| FP-L3/17 | R-20 L3 boundary detail; its unresolved-authority hand-off is constrained by R-23 L4 | Amendment requirements §3 L3/L4 and §7 Resolution / Claim. |

`R-21` and `R-22` retain their independently located approval history. The
approval-register range continues to map the whole L3 discussion to R-20–R-23;
it does not assert that `CHAT-0295` alone approves every earlier Claim or L4
semantic.

## Result

`CHAT-0295 → PO approval → R-20 target semantics → Constitution-impact
requirements` is reproducible. **PASS.**
