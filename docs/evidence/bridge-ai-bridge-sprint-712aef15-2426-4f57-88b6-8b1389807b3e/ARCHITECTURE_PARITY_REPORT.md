# Architecture parity report

Scope: `bridge:ai-bridge:sprint:712aef15-2426-4f57-88b6-8b1389807b3e`
Proposal hash: `1e54604709d93af8c5be513779a7679a8503d6cc19fe6162564fc3b7827fbe6f`

| Approved baseline decision | Foundation evidence |
| --- | --- |
| Goal -> Plan -> Execution -> optional Reflection | `OrkiGoal`, `OrkiPlan`, `OrkiExecution`; Reflection documented only as an extension point |
| OESM internal lifecycle | persisted `state`, `state_version`, transition guard and event trail |
| Cognitive/Execution split | no copied Cognitive State body; optional reference FKs only |
| Provider independent | Runtime imports no provider SDK and stores only opaque context |
| Governance ownership unchanged | approval is observed; no contract, scope, approval or run is created by Runtime |
| Event-driven progress | append-only `OrkiRuntimeEvent` with actor, payload and evidence references |
| Persona/Multi-Agent future fit | extension references documented; no premature domain introduced |

Result: parity is implemented for the authorized Foundation and Shadow Mode. Reflection, Persona and Multi-Agent implementation remain out of scope.

## Approved amendment — Reflection and Knowledge Integration

The additive canonical path is now `Verification -> Reflection -> Knowledge
Integration -> Completed`. `OrkiReflection` stores analysis and evidence only.
`OrkiKnowledgeIntegration` is the only Runtime path which can create a governed
AKB candidate, and it runs only after `reflection.completed`. A candidate is not
active knowledge; existing AKB Governance retains acceptance, activation and
embedding/index authority. Persona and Multi-Agent remain out of scope.
