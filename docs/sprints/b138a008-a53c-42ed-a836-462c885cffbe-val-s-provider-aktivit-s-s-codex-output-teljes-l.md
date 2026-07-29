---
approval_reference: conversation-confirmation:v1:2b565e85a77e3725b1a36f1c59e8b358ae002d90c64d2f0a3053353b823f3e7d
clarification_questions: []
clarification_state: READY_FOR_CONFIRMATION
content_hash: d2a50a7d8f7456d4b652fa83688056c358ef874fd4acbf0bd1bd15c485b26992
created_at: '2026-07-29T08:29:25.474694+00:00'
created_by: AI_BRIDGE
execution_authorization: APPROVED_PROVIDER_EXECUTION
execution_level: SPRINT
identifier: bridge:ai-bridge:sprint:b138a008-a53c-42ed-a836-462c885cffbe
intent: 'Vizsgáld meg és javítsd az AI Bridge Codex provider eseményfeldolgozási teljes
  útvonalát a subprocess stdout/stderr olvasástól a JSONL vagy strukturált event parsingen,
  provider adapteren, execution activity persistence-en, worker logoláson, execution
  event API-n és admin/UI megjelenítésen át. Határozd meg bizonyíthatóan, hol veszik
  el a Codex esemény tényleges tartalma, majd javítsd a teljes láncot úgy, hogy a
  rendszer legalább a következő eseménytípusokat különböztesse meg: PROVIDER_STARTED,
  PROVIDER_MESSAGE, PROVIDER_REASONING_SUMMARY, COMMAND_STARTED, COMMAND_OUTPUT, COMMAND_COMPLETED,
  FILE_CHANGED, TEST_STARTED, TEST_RESULT, PROVIDER_WARNING, PROVIDER_ERROR, PROVIDER_COMPLETED.
  Készíts rövid emberi Activity üzeneteket konkrét eseménytartalomból, és csak akkor
  használj fallback szöveget, ha nincs konkrét adat. Őrizd meg és tedd elérhetővé
  a provider valódi szöveges kimenetét és a mezőket: event type, timestamp, execution
  token, provider, item identifier, message text, command, exit code, stdout, stderr,
  file path, sequence number. Nagy stdout/stderr biztonságosan csonkolható vagy artifactba
  menthető, de az első és utolsó releváns rész maradjon elérhető. Biztosíts három
  elkülönített nézetet: Activity, Provider Output, Raw Events. Tartós mentés és megjelenítés
  előtt végezz secret redactiont API-kulcsokra, bearer tokenekre, jelszavakra, secret
  környezeti változókra, authorization headerekre és ismert credential mintákra, az
  auditálhatóság megőrzésével. Minden esemény tartozzon Executionhöz, kapjon monoton
  növekvő sequence numbert, legyen idempotensen menthető, újracsatlakozáskor visszaolvasható
  és worker-újraindításkor se vesszen el. Készíts teszteket a valódi provider message
  megmaradására, command start/completion megjelenítésére, stdout/stderr mentésére,
  sorrendre, duplikált event idempotenciára, secret redactionre, ismeretlen event
  fallbackre, nagy output kezelésére, worker restart utáni visszaolvasásra és provider
  completion megjelenítésére. A végén futtasd a teljes gate-et, készíts evidence-et,
  commitold és pushold a módosítást. Az acceptance outcome szerint a worker konkrét,
  sorszámozott aktivitásokat írjon, például: [42] Codex: Knowledge hierarchy audit
  folyamatban.; [43] Command started: python manage.py validate_scopes; [44] Command
  completed successfully: validate_scopes PASS; [45] Codex: A Platform AKB létezik,
  de az OPS retrieval részben bizonyított.'
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
  - migration-plan
  - migration-validation
  - security-review
  - security-validation
  required_release_gates:
  - repository-wide
  - sprint-specific
  resolved_profile: sprint-bugfix
  review_requirements:
  - compatibility-validation
  - migration-plan
  - migration-validation
  - security-review
  - security-validation
project_id: ai-bridge
proposal_hash: da41810c2c5092154bd9d89b3f995c8ec41efc65bed1eb17e7bc442733d541d9
proposal_version: 1
risk_modifiers:
- DATA_OR_SCHEMA_MIGRATION
- PUBLIC_API_OR_PROTOCOL
- SECURITY_RELEVANT
schema: ai-bridge-sprint/v1
schema_version: '1'
scope_kind: SPRINT
status: APPROVED
task_type: BUGFIX
title: Valós provider-aktivitás és Codex output teljes láncának javítása
updated_at: '2026-07-29T08:31:14.183141+00:00'
work_type: BUGFIX
---

# Valós provider-aktivitás és Codex output teljes láncának javítása

## Intent

Vizsgáld meg és javítsd az AI Bridge Codex provider eseményfeldolgozási teljes útvonalát a subprocess stdout/stderr olvasástól a JSONL vagy strukturált event parsingen, provider adapteren, execution activity persistence-en, worker logoláson, execution event API-n és admin/UI megjelenítésen át. Határozd meg bizonyíthatóan, hol veszik el a Codex esemény tényleges tartalma, majd javítsd a teljes láncot úgy, hogy a rendszer legalább a következő eseménytípusokat különböztesse meg: PROVIDER_STARTED, PROVIDER_MESSAGE, PROVIDER_REASONING_SUMMARY, COMMAND_STARTED, COMMAND_OUTPUT, COMMAND_COMPLETED, FILE_CHANGED, TEST_STARTED, TEST_RESULT, PROVIDER_WARNING, PROVIDER_ERROR, PROVIDER_COMPLETED. Készíts rövid emberi Activity üzeneteket konkrét eseménytartalomból, és csak akkor használj fallback szöveget, ha nincs konkrét adat. Őrizd meg és tedd elérhetővé a provider valódi szöveges kimenetét és a mezőket: event type, timestamp, execution token, provider, item identifier, message text, command, exit code, stdout, stderr, file path, sequence number. Nagy stdout/stderr biztonságosan csonkolható vagy artifactba menthető, de az első és utolsó releváns rész maradjon elérhető. Biztosíts három elkülönített nézetet: Activity, Provider Output, Raw Events. Tartós mentés és megjelenítés előtt végezz secret redactiont API-kulcsokra, bearer tokenekre, jelszavakra, secret környezeti változókra, authorization headerekre és ismert credential mintákra, az auditálhatóság megőrzésével. Minden esemény tartozzon Executionhöz, kapjon monoton növekvő sequence numbert, legyen idempotensen menthető, újracsatlakozáskor visszaolvasható és worker-újraindításkor se vesszen el. Készíts teszteket a valódi provider message megmaradására, command start/completion megjelenítésére, stdout/stderr mentésére, sorrendre, duplikált event idempotenciára, secret redactionre, ismeretlen event fallbackre, nagy output kezelésére, worker restart utáni visszaolvasásra és provider completion megjelenítésére. A végén futtasd a teljes gate-et, készíts evidence-et, commitold és pushold a módosítást. Az acceptance outcome szerint a worker konkrét, sorszámozott aktivitásokat írjon, például: [42] Codex: Knowledge hierarchy audit folyamatban.; [43] Command started: python manage.py validate_scopes; [44] Command completed successfully: validate_scopes PASS; [45] Codex: A Platform AKB létezik, de az OPS retrieval részben bizonyított.
