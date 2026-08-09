# Conversation Layer Compliance Audit (Sprint 2)

**Status: FAIL.**

The browser layer has useful projection characteristics: `factory_chat.py` builds server-side context and `factory_chat.html` renders messages, status, approval and evidence projections. It does not itself import a provider gateway. That is only partial compliance.

It remains an operational ingress that can initiate chat execution, plan/repository actions and dispatch. `factory_chat_message` recognizes `X-Orki-Runtime-Async` (`factory_chat.py:390-413`); its browser code immediately fetches the returned dispatch URL (`factory_chat.html:37`). The UI also submits repository lifecycle operations (`factory_chat.html:24`) and exposes an extensive workspace navigation. Downstream, `FactoryMissions` imports Runtime functions directly.

Thus the Conversation Layer does more than display events/questions and forward answers to an MSM-owned command boundary. It has no demonstrated hard boundary preventing direct Conversation → Runtime/Workflow authority paths. Right-side and workspace panels are projections in many cases, but the overall UI is not proven read-only with respect to planning, mission, workflow and engine state.

