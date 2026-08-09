# Machine Results — Workflow Engine Foundation & Task Model

Final-state commands run on 2026-08-09:

| Command | Result |
| --- | --- |
| `python manage.py check` | PASS — no issues (0 silenced) |
| `python manage.py makemigrations projects --check --dry-run` | PASS — no changes detected |
| `python manage.py test projects.tests.test_orki_runtime_mission_e2e projects.tests.test_factory_chat_runtime_integration projects.tests.test_structured_decision_runtime --verbosity 1` | PASS — 10 tests |
| `python manage.py test projects.tests.test_factory_chat.FactoryChatTests.test_chat_reports_exact_unconfigured_provider_message_and_persists_it --verbosity 1` | PASS — 1 test |
| `pytest -q` | PASS — 382 passed in 159.50s |
| `git diff --check` | PASS — no whitespace errors |

The complete suite includes browser E2E, Runtime integration and provider
regression coverage. The former exact missing-provider response is preserved
at the Runtime adapter boundary while task failure/retry evidence is retained.
