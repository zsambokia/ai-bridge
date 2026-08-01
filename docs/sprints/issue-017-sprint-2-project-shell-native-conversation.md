# Issue #17 — Sprint 2: Project Shell and Native Conversation

## Authority and boundary

- Product Owner authority: the explicit Factory Development Mode instruction supplied with Issue #17 on 2026-08-01.
- Prerequisite: Sprint 1 passed and its interaction contract was accepted by the Product Owner.
- Branch and baseline before mutation: `main` at `f4a1f95c63fe4ee0b6ab404c5874d4361687b9f6`.
- Scope: authenticated project shell, native server-rendered conversation, Active Work Context projection, restoration, and responsive shell only.

## Delivered behaviour

- `/` is an authenticated Factory Chat workspace and `/accounts/login/` is a normal Django login fallback.
- The Project Registry is the sole project list and selection source. “New project” links to the existing governed registry flow; it creates no browser record.
- Conversation input posts to the server and renders a bounded session-backed interaction trail. It never invokes a provider, creates authority, or replaces a canonical confirmation flow.
- Active Work Context is a request-time projection of existing Project, Scope, Roadmap, ExecutionRun, KnowledgeContextPackage, and ConversationOrchestration records. No new domain model or migration was introduced.
- A five-second authenticated fragment refresh updates the context without a full navigation. Normal form submission remains usable as a fallback.
- The desktop has project, conversation, and dominant context panels. On a narrow viewport those become mutually exclusive mobile panels; selected project, mode, and panel are restored in the authenticated server session.

## Explicit exclusions

This Sprint does not create a plan, submit approval, start an execution, call a provider, or modify knowledge. Those remain the distinct Sprint 3–5 boundaries.

## Acceptance and validation

The targeted integration suite verifies authentication, shell rendering, project/mode/panel restoration, native input retention, provider-boundary text, and the authenticated context fragment. The full release gates and a local HTTP login-route check passed from the final implementation state. Detailed evidence is in `docs/evidence/issue-017-sprint-2-project-shell-native-conversation/`.
