# Orki Factory Chat Operational Workspace

## Purpose

Factory Chat is Orki's operational workspace. It is an interface to the
canonical Cognitive State; it is neither a chatbot memory store nor a planning
questionnaire.

## Data flow

```text
Natural conversation
        |
        v
Conversation observation and Cognitive State update
        |
        +--> Mission / facts / assumptions / decisions / recommendations
        |
        v
Canonical planning and approval artefacts
        |
        +--> plan, roadmap, and memory-document projections
        |
        v
Factory Chat live workspace projection
        |
        v
Explicit Product Owner review and approval
```

Conversation history supports continuity only. Cognitive State entries,
planning artefacts, and approved decisions remain the canonical project
knowledge. The workspace must never infer durable knowledge from rendered chat
history.

## Workspace contract

The fixed workspace projection exposes, where evidence exists:

- Mission
- Facts
- Assumptions
- Open Decisions
- Recommendation
- Plan
- Roadmap Progress
- Current Next Step

Every displayed item includes only canonical value, provenance, and confidence
information that is available from the underlying state. Missing evidence is
shown as unknown, never invented.

## Plan review and documentation projections

Before a Product Owner approves a plan, the workspace displays the canonical
approval object: summary, assumptions, alternatives, trade-offs or relevant
limitations, expected impact, and Orki's recommendation. Approval acts on the
existing governed plan object. It does not make Factory Chat an authority
source.

Plan creation updates the existing plan, roadmap, and memory-document
projections. The workspace displays their lifecycle status immediately; it does
not create a duplicate manually synchronised document path.

## Failure boundary

Backend failures may be logged with correlation information, but Factory Chat
returns a safe actionable message to the Product Owner. Raw exceptions,
tracebacks, and internal operation names are never rendered in the workspace.

## Non-goals

This workspace does not introduce a new reasoning engine, alter LLM-provider
independence, expand governance authority, or autonomously execute work.
