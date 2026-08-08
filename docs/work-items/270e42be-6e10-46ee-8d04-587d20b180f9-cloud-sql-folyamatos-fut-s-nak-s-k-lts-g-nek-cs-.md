---
approval_reference: conversation-confirmation:v1:71ecbaf39619285633f0f5cb5a30050e8fb55c26b3b5ba1b2383b0f4e771bc6a
clarification_questions: []
clarification_state: READY_FOR_CONFIRMATION
content_hash: f5a1598c02cce7e83f60f6da1849715dea94e8c9c7344668ef1704c288be1469
created_at: '2026-07-30T17:05:27.517955+00:00'
created_by: AI_BRIDGE
execution_authorization: APPROVED_PROVIDER_EXECUTION
execution_level: TASK
identifier: bridge:ai-bridge:work-item:270e42be-6e10-46ee-8d04-587d20b180f9
intent: Vizsgáld meg az asfactory Google Cloud projektben, hogy a Cloud SQL erőforrás miért fut folyamatosan, pontosan mely komponensek, kapcsolatok, worker-ek, health checkek, scheduler-ek vagy alkalmazások tartják aktívan, és mi okozza a jelenlegi, aránytalanul magas költséget. Készíts tételes költség- és használati bontást, azonosítsd a szükségtelen 24/7 kapacitást, túlméretezést, redundáns példányokat, storage/backup/logging/network költségeket és minden olyan konfigurációt, amely biztonságosan optimalizálható. Ezután hajtsd végre a költségcsökkentő módosításokat kizárólag az asfactory projektben. TILOS bármely más Google Cloud projektet, billing accountot, megosztott erőforrást vagy külső környezetet módosítani. Ne törölj adatot, ne állíts le üzletileg szükséges szolgáltatást, és ne végezz visszafordíthatatlan műveletet bizonyított biztonsági mentés és egyértelmű indoklás nélkül. Elsődlegesen a legkisebb biztonságos Cloud SQL gépméretet, leállíthatóságot vagy időzített működést, fejlesztői környezethez illő availability beállítást, backup/PITR/retention optimalizálást, storage auto-resize és log retention felülvizsgálatot, valamint a folyamatos adatbázis-ébresztést okozó alkalmazásoldali polling/health-check/worker viselkedést vizsgáld. A végén bizonyítsd, hogy az alkalmazás továbbra is működik, a szükséges migrációk és worker-ek rendben vannak, és adj előtte–utána havi költségbecslést, módosításlistát, rollback tervet és evidence-et.
policy:
  child_contract_required: false
  omission_justifications: []
  profile_version: '1.0'
  required_assessment_depth: standard
  required_documentation_updates:
  - behavior
  required_evidence_artifacts:
  - acceptance-results
  - assessment
  - closure-note
  - integration-validation
  - production-smoke
  - rollback-assessment
  required_release_gates:
  - repository-wide
  - sprint-specific
  resolved_profile: task-configuration
  review_requirements:
  - integration-validation
  - production-smoke
  - rollback-assessment
project_id: ai-bridge
proposal_hash: 8280a36ce70798981d54806afe866fffe2ecfa2dcf10ecbf95a4617282c537ad
proposal_version: 1
risk_modifiers:
- EXTERNAL_INTEGRATION
- PRODUCTION_IMPACT
schema: ai-bridge-work-item/v1
schema_version: '1'
scope_kind: WORK_ITEM
status: APPROVED
task_type: CONFIGURATION
title: Cloud SQL folyamatos futásának és költségének csökkentése
updated_at: '2026-07-30T17:07:50.181479+00:00'
work_type: CONFIGURATION
---

# Cloud SQL folyamatos futásának és költségének csökkentése

## Intent

Vizsgáld meg az asfactory Google Cloud projektben, hogy a Cloud SQL erőforrás miért fut folyamatosan, pontosan mely komponensek, kapcsolatok, worker-ek, health checkek, scheduler-ek vagy alkalmazások tartják aktívan, és mi okozza a jelenlegi, aránytalanul magas költséget. Készíts tételes költség- és használati bontást, azonosítsd a szükségtelen 24/7 kapacitást, túlméretezést, redundáns példányokat, storage/backup/logging/network költségeket és minden olyan konfigurációt, amely biztonságosan optimalizálható. Ezután hajtsd végre a költségcsökkentő módosításokat kizárólag az asfactory projektben. TILOS bármely más Google Cloud projektet, billing accountot, megosztott erőforrást vagy külső környezetet módosítani. Ne törölj adatot, ne állíts le üzletileg szükséges szolgáltatást, és ne végezz visszafordíthatatlan műveletet bizonyított biztonsági mentés és egyértelmű indoklás nélkül. Elsődlegesen a legkisebb biztonságos Cloud SQL gépméretet, leállíthatóságot vagy időzített működést, fejlesztői környezethez illő availability beállítást, backup/PITR/retention optimalizálást, storage auto-resize és log retention felülvizsgálatot, valamint a folyamatos adatbázis-ébresztést okozó alkalmazásoldali polling/health-check/worker viselkedést vizsgáld. A végén bizonyítsd, hogy az alkalmazás továbbra is működik, a szükséges migrációk és worker-ek rendben vannak, és adj előtte–utána havi költségbecslést, módosításlistát, rollback tervet és evidence-et.
