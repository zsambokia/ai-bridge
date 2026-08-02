# ORKI-001 Cognitive State Release Gate

**Date:** 2026-08-01
**Decision:** `PASS — READY FOR PRODUCT OWNER REVIEW`
**Execution profile:** Product Owner Factory Development Mode
**Repository / branch / baseline:** `zsambokia/ai-bridge` / `agent/issue-17-conversational-po` / `0f8153ad1e790f40662d5701247e6c5681ddaaa5`

## Audit method

The gate is an independent HTTP-level behavioural scenario, separate from the
foundation unit tests. It drives `factory-chat-message`, the Product Owner's
actual Factory Chat endpoint, through a configured provider boundary. The
provider response is deterministic solely to make the state transition
repeatable; the transcript, session selection, mission update, and canonical
Cognitive State write path are the production code paths.

The scenario sends 25 consecutive Product Owner messages to one project and
one message to a second project. It creates 50 durable chat messages in the
first project and asserts the persisted state after every relevant evolution.

**Executable evidence:**

```text
PYTHON_DOTENV_DISABLED=true .venv\Scripts\python.exe manage.py test \
  projects.tests.test_orki_cognitive_state_release_gate --verbosity 2

Ran 1 test in 1.817s
OK
```

## Behavioural acceptance evidence

| Required proof | Result | Observed evidence |
| --- | --- | --- |
| Conversation and memory are separate | PASS | A unique raw Product Owner phrase remains in `FactoryChatMessage` and is absent from every Cognitive State `content` and `provenance` value. State retains only a message ID and SHA-256 source reference. |
| Evidence tracking | PASS | Each of 25 successful primary-project turns creates one typed `EVIDENCE` entry with the owner message ID, hash, correlation ID, provider ID, and model identity. |
| Assumption handling | PASS | The first assumption is retained as `SUPERSEDED`; the changed assumption is `ACTIVE` and points back through `supersedes`. |
| Confidence evolution | PASS | The active recommendation evolves from confidence `0.42` to `0.83`; no duplicate active snapshot remains. |
| Recommendation evolution | PASS | The initial integration-first recommendation is superseded by the data-quality-first recommendation, with an auditable lifecycle link. |
| Project isolation | PASS | A second project receives only its own mission projection. The primary project's objective is absent from that projection. |
| Long-conversation stability | PASS | 25 sequential Product Owner turns complete through Factory Chat; all 50 owner/Orki transcript messages persist and all 25 observations are attributed. |
| Conflict handling | PASS | A changed assumption and recommendation close their earlier active snapshots through `SUPERSEDED`, rather than silently overwriting history. |
| State evolution | PASS | An explicitly resolved open decision becomes an active empty decision snapshot; the prior unresolved-decision snapshot is superseded. |
| Explainability | PASS | The active recommendation projection exposes typed content, confidence, provenance, correlation, source message hash, provider, and model without exposing transcript text. |

## Release Gate decision

| Gate | Result |
| --- | --- |
| Engineering acceptance | PASS |
| Operational behavioural acceptance | PASS |
| Independent behavioural audit | PASS |
| Migration drift and system checks | PASS — `makemigrations --check --dry-run` reported no changes; `manage.py check` reported no issues |
| Focused and regression tests | PASS — `projects.tests` and the repository suite: 57 tests passed in each run |
| Documentation, AKB, and roadmap | PASS |
| COO Capability Acceptance for ORKI-001 foundation | PASS — only the Cognitive State foundation criteria assessed; later COO capabilities remain out of scope |

## Scope boundary and self-critique

This gate proves persistence and evolution of structured cognitive state under
real Factory Chat request handling. It does not claim that ORKI-002 Mission
Understanding, recommendation quality, planning intelligence, or long-term AKB
memory are complete. The model remains a replaceable structured-input provider;
the lifecycle, provenance, isolation, and explainability rules execute in AI
Bridge code.

The release gate is therefore sufficient to unblock planning and execution of
the separately approved ORKI-002 Sprint, but it is not evidence of Epic
completion.
