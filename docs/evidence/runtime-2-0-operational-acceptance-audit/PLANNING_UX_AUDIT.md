# Planning UX Audit

**Status: FAIL.**

Target UX is `Mission → Understanding → evidence resolution → only necessary business questions → updated understanding → plan → review → approval`, all primarily in chat. Current UI displays a chat and plan-review fragment, but the actual path is `prompt → provider JSON → Runtime gap/question transitions → FactoryMission plan creation`. It is not a durable Planning Session experience.

## Required scenario evidence

Twenty representative Product Owner cases were searched for as executable acceptance coverage: new product, vague objective, conflicting constraints, missing owner, missing users, missing inputs, missing outputs, scope boundary, persistence choice, integration choice, cost-impacting dependency, repository import, repository change, roadmap conflict, AKB conflict, semantic evidence conflict, previous-mission reuse, approval, rejection/revision, and follow-up after owner answer. No repository test suite proves the required end-to-end outcome matrix for these scenarios. Existing tests cover selected chat/runtime mechanics, not this acceptance suite.

The workspace contains non-chat dossiers and navigation (`factory_chat.html:12-14,48-75`), so chat is not demonstrably the exclusive primary planning surface. A final PSM must emit explainable updates, questions and approval artefacts without a dashboard or wizard becoming the planning authority.

