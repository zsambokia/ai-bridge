# Manual Acceptance Validation

**Status: OPERATIONAL VALIDATION REQUIRED**

Date of attempted validation: 2026-08-08
Scope: `bridge:ai-bridge:sprint:712aef15-2426-4f57-88b6-8b1389807b3e`
Proposal hash: `1e54604709d93af8c5be513779a7679a8503d6cc19fe6162564fc3b7827fbe6f`

## Purpose

This is the Product Owner-required real-user acceptance validation. It is not
a substitute for an automated browser test. A PASS requires an authenticated
interactive Factory Chat session, visible Live Runtime Monitor transitions,
and screenshots captured from that session.

## Environment check

| Check | Result | Evidence |
| --- | --- | --- |
| Local Django endpoint | PASS | `http://127.0.0.1:8000/` responded with `302` to `/accounts/login/?next=/`, confirming the running application and its authenticated Factory Chat boundary. |
| Interactive in-app browser | UNAVAILABLE | The browser runtime reported: `Browser is not available: iab`. |
| Screenshot capture | NOT POSSIBLE | No interactive browser session exists in this execution environment. |
| Provider-backed user conversation | NOT EXECUTED | It would require an authenticated interactive session; no synthetic response was treated as manual acceptance evidence. |

The inability to run the scenarios here is an environmental limitation. It is
not evidence of a Factory Chat bypass, an OESM defect, or a generic provider
failure.

## Required release-environment scenarios

Run these scenarios as an authenticated user in a browser-capable release
environment. For each row, capture the submitted message, the Live Runtime
Monitor state history, the terminal state, and screenshots.

| Scenario | User message | Required visible path | Result |
| --- | --- | --- | --- |
| 1. New application | `Új alkalmazást szeretnék.` | Planning -> Goal -> Completed | NOT EXECUTED IN THIS ENVIRONMENT |
| 2. Bug fix | `Javítsd ezt a bugot.` | Planning -> Execution -> Reflection -> Completed | NOT EXECUTED IN THIS ENVIRONMENT |
| 3. Plan disagreement | `Nem értek egyet a tervvel.` | Critic / change request -> Planning -> Completed | NOT EXECUTED IN THIS ENVIRONMENT |
| 4. Resume prior work | `Folytassuk a tegnapi munkát.` | Existing Goal -> Resume -> Completed | NOT EXECUTED IN THIS ENVIRONMENT |
| 5. Approval wait | `Várjuk meg a jóváhagyást.` | WAITING_FOR_APPROVAL -> Resume -> Completed | NOT EXECUTED IN THIS ENVIRONMENT |

## PASS criteria

Manual Acceptance Validation passes only when all five scenarios visibly use
the Runtime route and the Live Runtime Monitor displays the current OESM state,
Goal, planning status, progress, waiting reason, recovery events, reflection,
and knowledge integration where applicable. Any runtime/provider fault must be
shown as a concrete Runtime state and reason, never as a generic unavailable
message.

## Next action

Execute this evidence sheet in a browser-capable release environment, attach
the five screenshot sets and observed Runtime event identifiers, then update
the Result column and Release Gate validation. Only then may merge, push,
baseline tagging, or repository cleanup be requested.
