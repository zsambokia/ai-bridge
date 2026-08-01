# Issue #17 — Sprint 1: Factory Chat UX contract and domain boundaries

## Authority and boundary

- Product Owner authority: explicit Factory Development Mode instruction supplied
  with Issue #17 on 2026-08-01.
- Repository: `zsambokia/ai-bridge`.
- Branch and baseline before mutation: `main` at
  `be6c2c6bc136cf47886df4ba8d95239865e72a19`.
- Authoritative scope: [GitHub Issue #17](https://github.com/zsambokia/ai-bridge/issues/17),
  Sprint 1 only.

This document is the Sprint 1 interaction contract and Product Owner review
package. It authorizes neither browser UI implementation nor Sprint 2 work.
The existing canonical server-side orchestration, scope, conversation,
approval, execution, project, and AKB components remain the source of truth.

## Sprint 1 outcome

Define the minimum, mobile-first Factory Chat control surface so a Product
Owner can see what project is active, what work is in progress, what requires
approval, and what governed artifact is being inspected. The primary screen is
an operational workspace, not a chat application or social feed.

### Primary desktop wireframe

```text
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│ Factory Chat                                      Project: [ai-bridge ▾]  [New project]     │
│ Workspace: Product Owner        Mode: [Planning] [Coding] [Memory]       status / account   │
├──────────────────────┬─────────────────────────────┬─────────────────────────────────────────┤
│ Projects             │ Conversation (30–35%)        │ Active Work Context (dominant)          │
│ ┌──────────────────┐ │ ┌─────────────────────────┐ │ ┌─────────────────────────────────────┐ │
│ │ ai-bridge      ● │ │ │ Plain-language progress │ │ │ Context header: project, mode,       │ │
│ │ …                │ │ │ + governed interaction  │ │ │ current plan / sprint / execution    │ │
│ └──────────────────┘ │ │ history                  │ │ └─────────────────────────────────────┘ │
│ [Project filter]     │ ├─────────────────────────┤ │ [Plan] [Sprint] [Execution] [Memory]  │
│                      │ │ Request / reply composer│ │                                     │
│                      │ └─────────────────────────┘ │ Primary selected artifact, evidence,  │
│                      │     resizable / collapsible  │ approval, validation, or memory view  │
│                      │                               │                                     │
│                      │                               │ [Approve] [Request changes] [Reject] │
└──────────────────────┴─────────────────────────────┴─────────────────────────────────────────┘
```

- The right context panel is the default focus and remains visually dominant.
- The project list and conversation panel can be collapsed; their collapsed
  state is a local UI preference, never a source of business state.
- The conversation panel defaults to approximately 30–35% of the workspace
  width, can be resized within accessible limits, and must not obscure a
  pending approval or active artifact.
- “New project” starts the existing governed project/bootstrap flow. It does
  not create a browser-only project record or bypass repository policy.

### Mobile navigation and layout

```text
┌──────────────────────────────────┐
│ Factory Chat   [Project ▾] [Mode] │
│ ai-bridge · Sprint 1 · attention  │
├──────────────────────────────────┤
│ Active artifact / approval        │
│ (the current panel; full width)   │
│                                  │
├──────────────────────────────────┤
│ [Context] [Chat] [Projects]       │
└──────────────────────────────────┘
```

- Mobile is chat-first for entry, but the current Active Work Context remains
  one tap away and is selected automatically for a required approval.
- `Context`, `Chat`, and `Projects` are mutually exclusive full-width panels;
  no desktop three-column layout is squeezed into a handset.
- The selected project, selected context artifact, active mode, and most
  recent panel are restored on return when the server still permits access.
- The navigation order is predictable: workspace/project, mode, current
  context, conversation, projects. Browser back returns to the prior view
  without fabricating or resubmitting a governed action.

## Information architecture and Active Work Context

```text
Workspace (Product Owner control surface)
  └─ Project (existing canonical Project registry record)
       └─ Active Work Context (server-resolved UI projection; not a Sprint 1 model)
            ├─ Plan / approved scope
            ├─ Epic or Sprint
            ├─ Execution / run / job status
            ├─ Memory Inquiry / AKB evidence
            └─ Conversation and pending approval
```

`Active Work Context` is a server-resolved presentation contract for the
single project currently selected by a user. It is not a replacement for a
Scope, ExecutionContract, OrchestrationSession, Run, Job, knowledge entry, or
conversation record. Future implementation may persist user interface
preferences, but it must resolve artifact identifiers and permissions against
the relevant canonical service at request time.

| Context member | Owner / source of truth | UI responsibility |
| --- | --- | --- |
| Workspace and selected project | Existing `Project` registry and authenticated server session | List, select, and start the governed project flow |
| Plan / scope | Canonical scope and approved proposal lifecycle | Render status, version, approver, and evidence link |
| Epic / Sprint | Canonical work hierarchy and contract metadata | Render the active unit and permitted next action |
| Execution | Canonical orchestration, execution, run, and job records | Render plain-language progress, status, logs, and recovery state |
| Memory Inquiry | AKB / knowledge and evidence services | Search and display attributable context and evidence |
| Conversation | Canonical conversation-orchestration binding | Render the interaction trail; submit requests to the server |
| Approval | Canonical server-side `conversation.confirm` path | Show only server-authorized actions and submit the selected outcome |

The context header always shows at least the project identity, current mode,
active artifact type and title, current status, and any action requiring a
Product Owner decision. Every artifact view links to its canonical detail and
evidence rather than duplicating mutable truth into a chat transcript.

## Interaction contract

### Modes

- **Planning** selects plans, scopes, proposals, sprint context, review
  material, and governed approvals. It does not create implicit approval.
- **Coding** selects the active execution/run/job and its plain-language
  progress, validation, logs, and recovery state. The browser cannot invoke a
  provider directly or inspect protected runtime context.
- **Memory** selects a Memory Inquiry, its retrieved AKB/evidence context, and
  attributable sources. It is not a generic document dump.

Mode selection changes the default artifact within the same Active Work
Context. It never changes the approved scope, execution authority, or project
membership by itself.

### Conversation and progress

Conversation is contextual, readable, and secondary to the selected artifact.
The application presents status in Hungarian by default, using plain language
alongside stable identifiers where useful. Examples: “Ellenőrzés fut”,
“Jóváhagyásra vár”, “Végrehajtás helyreállítása szükséges”.

Normal activity must update an in-page region, not force a full-page form
reload. The intended minimal implementation direction for Sprint 2 is Django
server-rendered pages and fragments with `fetch`-based progressive enhancement;
short bounded polling may be used for run status, and a future SSE stream must
have an equivalent non-streaming fallback. React or Vue is out of scope unless
a later decision documents a concrete need that Django templates and small
progressive enhancement cannot meet.

Every pending, failed, delayed, or recovered activity has a visible state:

- loading: what is being loaded and the last known status;
- waiting: why it waits, what system owns the next step, and when it will
  refresh or can be retried;
- error: a concise user-safe message, a stable support/reference identifier,
  and a retry only when the server says retry is safe;
- stale/reconnected: last update time and an explicit refresh action;
- empty: what is absent and the permitted next action.

### Approval contract

An approval card appears only when the server has resolved a specific,
authorized action requiring Product Owner confirmation. It includes the exact
artifact and version, impact/summary, current status, evidence links, and the
available outcomes.

| Outcome | Browser action | Server outcome |
| --- | --- | --- |
| Approve | Submit the displayed server action and interaction reference | Calls the canonical high-level `conversation.confirm` flow; server binds confirmation and performs all policy, identity, version, and idempotency checks |
| Request changes | Submit required written feedback against the displayed artifact | Records the governed response without converting it into approval |
| Reject | Submit a required reason | Records rejection against the displayed artifact/version and preserves the audit trail |

The browser never constructs an approval reference, contract hash, provider
request, execution payload, or authority decision. The server owns
authentication, authorization, scope/version binding, retry keys, and durable
audit logging. A repeated click must receive the same idempotent result or a
clear “already processed” state; it must never silently create a second
approval. Natural-language confirmations may be offered through conversation,
but are interpreted and bound by the same canonical server path.

The UI must show no more than one unresolved approval card as the primary
context. If several governed decisions exist, the server supplies a clearly
ordered queue and the selected card explains why it is first.

### Accessibility and usability baseline

- All panels, tabs, resize controls, approval actions, and project selection
  work by keyboard and have accessible names and visible focus.
- Status changes use a restrained live region; routine polling must not steal
  focus or repeatedly announce unchanged content.
- Colour is never the sole status signal; labels, icons, and text describe
  state. Layout supports zoom and narrow viewports without hidden approval
  actions.
- Touch targets are adequate for mobile, destructive/reject paths have clear
  labels, and validation feedback appears next to the affected action.

## Explicit non-goals

- No generic messaging or social-chat product.
- No browser-direct provider call, credential exposure, prompt inspection, or
  execution dispatch.
- No replacement workflow, approval system, scope model, project registry,
  execution model, or AKB store.
- No browser-only project, sprint, or approval record.
- No visual introduction of hidden parallel backend state.
- No Sprint 2 shell, authentication change, endpoint, model, migration, or
  runtime implementation in Sprint 1.

## Required Product Owner review

Before Sprint 2 begins, the Product Owner must accept this contract exactly on
these five decision areas:

1. primary desktop and mobile screen structure;
2. navigation and state-restoration behaviour;
3. Active Work Context as a server-resolved projection under an existing
   Project, including its five artifact members;
4. approval interaction through the canonical `conversation.confirm` server
   path and its three outcomes; and
5. desktop panel and mobile tab behaviour.

Acceptance can be recorded with: **“Elfogadom az Issue #17 Sprint 1
interakciós szerződését.”** Specific requested changes reopen only the affected
contract section. Sprint 2 remains prohibited until this review is accepted.

## Follow-on implementation boundary

After the required review, Sprint 2 may build only the minimal shell described
by Issue #17: server-rendered authenticated entry, workspace/project shell,
desktop/mobile layout, and a reusable server-backed Active Work Context
adapter. It must reuse the canonical components listed above, preserve normal
form fallback, and add no provider-facing browser capability.
