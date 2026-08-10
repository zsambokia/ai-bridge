# Open Issues and Architecture Challenges

| ID | Type | Question | Required disposition |
| --- | --- | --- | --- |
| AC-01 | ADR required | Does durable `ExecutionJob` remain an implementation queue object, or evolve into an Execution Attempt? | ADR-034 disposition before Wave 2 |
| AC-02 | Architecture Challenge | Can `ExecutionRun` and `OrkiExecution` be mapped to one Execution without splitting Mission authority and delivery authority? | Produce lifecycle mapping and recovery proof; do not rename first |
| AC-03 | ADR required | What is the canonical Organization → Workspace → Repository ownership and migration/backfill policy for existing `Project` data? | scope/tenant ADR before Wave 4 |
| AC-04 | ADR required | Which Knowledge Object types, URI grammar, graph relations, and publication boundary are minimally required for first migration? | AKB implementation ADR before Wave 3 |
| AC-05 | ADR required | What localization fallback, source-language, review, and evidence policy applies to prompt/persona/knowledge/documentation assets? | localization ADR before Wave 4/5 |
| AC-06 | Architecture Challenge | Current Operational Foundation Constitution uses transitional `ExecutionRun`; target Kernel calls Execution first-class. | Preserve the constitutional target; define a migration alias/mapping, not a competing owner |
