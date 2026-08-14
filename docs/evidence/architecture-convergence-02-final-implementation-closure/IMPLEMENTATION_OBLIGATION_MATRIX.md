# Implementation obligation matrix

| Obligation | Classification | Closure evidence |
| --- | --- | --- |
| R19 assurance result families | IMPLEMENTED | `EvidenceAssuranceEvaluation`, protocol tests |
| R22 accountable Claim | IMPLEMENTED | `ResolutionClaim`, protocol tests |
| R20–R21 Artifact/Knowledge boundary | IMPLEMENTED | version/candidate/resolution and approval guard |
| R23–R24 Factory Packet/IP | IMPLEMENTED | persisted routed request/response trace |
| R25 FFS MVP | IMPLEMENTED | service-to-transport control-plane resolution |
| R26 Zoning | IMPLEMENTED | deny-first, deny-precedence and bidirectional checks |
| Physical FFS HA/failover | EXPLICITLY DEFERRED BY PO | source leaves physical topology/HA open |
| Universal Resolution application | EXPLICITLY DEFERRED BY PO | source permits Claim, not an invented universal resolver |

No OPEN PRODUCT DECISION blocks this closure.
