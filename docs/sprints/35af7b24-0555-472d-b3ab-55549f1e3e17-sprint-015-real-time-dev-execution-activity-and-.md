---
approval_reference: conversation-confirmation:v1:7c2e5eb0d7685dc1b95396597df8291f0068a0142b4a487c9e6cc16d5b2157ca
clarification_questions: []
clarification_state: READY_FOR_CONFIRMATION
content_hash: bdf8cb2144d857e15c4514d997d3cb9bbbee22097660bff088dd5ad0c14c03df
created_at: '2026-07-28T07:11:58.848723+00:00'
created_by: AI_BRIDGE
execution_authorization: APPROVED_PROVIDER_EXECUTION
execution_level: SPRINT
identifier: bridge:ai-bridge:sprint:35af7b24-0555-472d-b3ab-55549f1e3e17
intent: 'Implementáld az AI Bridge repositoryban a valós idejű DEV execution activity
  és checklist funkciót a már létrehozott docs/sprints/SPRINT_015_REAL_TIME_DEV_EXECUTION_ACTIVITY_AND_CHECKLIST.md
  specifikáció alapján. Ez kizárólag AI Bridge fejlesztés, nem ASF: ne legyen employee-,
  meeting- vagy csatornaréteg, és ne jelenjenek meg kitalált személyek. A futás közben
  a Product Owner és ChatGPT értelmes, rövid, emoji-dekorált, de nem stack trace jellegű
  állapotfrissítéseket kapjon. Legyen folyamatosan frissülő, számított checklist,
  amely mutatja a pending, in progress, completed, repairing és blocked állapotokat.
  Látszódjon, hol tart a végrehajtás, hol hibázott, elindult-e a diagnózis, milyen
  önjavítás történt, újrafutott-e az ellenőrzés, sikerült-e a javítás, illetve van-e
  legitim blocker. A console és az MCP/ChatGPT ugyanabból a kanonikus execution event
  streamből dolgozzon. Használd újra a meglévő ExecutionRun, event persistence, provider,
  repair loop, audit és MCP eszközöket; ne hozz létre párhuzamos lifecycle-t vagy
  kézzel karbantartott státuszmodellt. DEV módban a strukturált események futás közben,
  nem csak a provider befejezése után legyenek lekérdezhetők. Készüljön minimális
  read-only Django admin Activity nézet, és csak akkor új execution.get_activity_summary
  MCP eszköz, ha az assessment bizonyítja, hogy a meglévő get_run_status és list_events
  nem elegendő. A sprint tartalmazzon valódi proving executiont, amely futás közbeni
  progress eseményeket, checklist-változást, technikai hibát, diagnózist, automatikus
  javítást, gate újrafuttatást és lezárást bizonyít. Minden release gate és evidence
  legyen friss, secret-safe és a final commithoz kötött.'
policy:
  child_contract_required: false
  omission_justifications: []
  profile_version: '1.0'
  required_assessment_depth: extended
  required_documentation_updates:
  - architecture
  - akb
  - roadmap
  required_evidence_artifacts:
  - acceptance-results
  - assessment
  - closure-report
  - compatibility-validation
  - machine-results
  required_release_gates:
  - repository-wide
  - sprint-specific
  resolved_profile: sprint-self_development
  review_requirements:
  - compatibility-validation
project_id: ai-bridge
proposal_hash: a6383cec4d6bbdc954b4dd3f327c2f63b988f205a3505dbcb125f87981784146
proposal_version: 1
risk_modifiers:
- PUBLIC_API_OR_PROTOCOL
schema: ai-bridge-sprint/v1
schema_version: '1'
scope_kind: SPRINT
status: APPROVED
task_type: SELF_DEVELOPMENT
title: Sprint 015 — Real-time DEV execution activity and checklist
updated_at: '2026-07-28T07:13:18.364477+00:00'
work_type: SELF_DEVELOPMENT
---

# Sprint 015 — Real-time DEV execution activity and checklist

## Intent

Implementáld az AI Bridge repositoryban a valós idejű DEV execution activity és checklist funkciót a már létrehozott docs/sprints/SPRINT_015_REAL_TIME_DEV_EXECUTION_ACTIVITY_AND_CHECKLIST.md specifikáció alapján. Ez kizárólag AI Bridge fejlesztés, nem ASF: ne legyen employee-, meeting- vagy csatornaréteg, és ne jelenjenek meg kitalált személyek. A futás közben a Product Owner és ChatGPT értelmes, rövid, emoji-dekorált, de nem stack trace jellegű állapotfrissítéseket kapjon. Legyen folyamatosan frissülő, számított checklist, amely mutatja a pending, in progress, completed, repairing és blocked állapotokat. Látszódjon, hol tart a végrehajtás, hol hibázott, elindult-e a diagnózis, milyen önjavítás történt, újrafutott-e az ellenőrzés, sikerült-e a javítás, illetve van-e legitim blocker. A console és az MCP/ChatGPT ugyanabból a kanonikus execution event streamből dolgozzon. Használd újra a meglévő ExecutionRun, event persistence, provider, repair loop, audit és MCP eszközöket; ne hozz létre párhuzamos lifecycle-t vagy kézzel karbantartott státuszmodellt. DEV módban a strukturált események futás közben, nem csak a provider befejezése után legyenek lekérdezhetők. Készüljön minimális read-only Django admin Activity nézet, és csak akkor új execution.get_activity_summary MCP eszköz, ha az assessment bizonyítja, hogy a meglévő get_run_status és list_events nem elegendő. A sprint tartalmazzon valódi proving executiont, amely futás közbeni progress eseményeket, checklist-változást, technikai hibát, diagnózist, automatikus javítást, gate újrafuttatást és lezárást bizonyít. Minden release gate és evidence legyen friss, secret-safe és a final commithoz kötött.
