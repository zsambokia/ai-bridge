# Open Issues and Architecture Challenges

> **Status: HISTORICAL ASSESSMENT, PARTIALLY SUPERSEDED.** This Phase 2 record
> preserves the questions as they were assessed. AC-03 and AC-05 are accepted
> target decisions in [Article VI -- Scope Architecture](../SCOPE_ARCHITECTURE_CONSTITUTION.md)
> and [Article VII -- Localization Architecture](../LOCALIZATION_ARCHITECTURE_CONSTITUTION.md).
> Its old `Organization -> Workspace -> Repository` wording is not canonical.

| ID | Type | Question | Required disposition |
| --- | --- | --- | --- |
| AC-01 | ADR required | Does durable `ExecutionJob` remain an implementation queue object, or evolve into an Execution Attempt? | ADR-034 disposition before Wave 2 |
| AC-02 | Architecture Challenge | Can `ExecutionRun` and `OrkiExecution` be mapped to one Execution without splitting Mission authority and delivery authority? | Produce lifecycle mapping and recovery proof; do not rename first |
| AC-03 | Accepted target; implementation design remains open | Canonical hierarchy is Organization -> Workspace -> Project; Repository is a Scope-owned Resource, normally Project-owned. | ADR-035 and a future approved implementation Sprint for authorization, inheritance and data disposition |
| AC-04 | ADR required | Which Knowledge Object types, URI grammar, graph relations, and publication boundary are minimally required for first migration? | AKB implementation ADR before Wave 3 |
| AC-05 | Accepted target; implementation design remains open | English canonical identifiers; multilingual localizable content; original Evidence is preserved and translations are derived representations. | ADR-037 and a future approved implementation Sprint for representation, fallback and publication mechanics |
| AC-06 | Architecture Challenge | Current Operational Foundation Constitution uses transitional `ExecutionRun`; target Kernel calls Execution first-class. | Preserve the constitutional target; define a migration alias/mapping, not a competing owner |
