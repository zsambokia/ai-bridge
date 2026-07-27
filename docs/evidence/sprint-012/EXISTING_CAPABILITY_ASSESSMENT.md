# Sprint 012 existing capability assessment

## Binding and method

- Repository baseline: `43fce9d02f20c8ff85b593f018bb050aec9f61fd` on `main`.
- Sprint document: `docs/sprints/SPRINT_012_EXISTING_CONVERSATIONAL_CONFIRMATION_PATH_ASSESSMENT_AND_REPAIR.md`, blob `92dd94ea6b377763cd992fcf7fae0e8c393d6b8c`, SHA-256 `93631F8D8198685D082968E0FC9EFF4F20E6A78C7AB1B26D169B38B6916BB2C4`.
- Bootstrap addendum: `docs/sprints/SPRINT_012_BOOTSTRAP_EXECUTION_ADDENDUM.md`, blob `851e107c72724d25631d1874b864fafd2f64a966`, SHA-256 `0D8A3AEC7ADE467F7E9FFCD776464795DD34B5E5029BB013FB3C3FCB88019848`.
- Executor: Codex, local checkout on `main`.

## Assessment-first finding

An adequate canonical conversational confirmation implementation already
exists. `projects/governed_mcp.py` registers `conversation.confirm` and
`scope.confirm_and_execute`; `ConversationOrchestration` is the durable
coordinator. `_confirm_conversation` validates affirmative vocabulary, resolves
the current review, and delegates to `_confirm_and_execute`. That service
creates or reuses one `GovernanceApproval` with `AUTHORIZE_EXECUTION`, creates
or resumes one orchestration, and `_advance_orchestration` invokes the existing
approval, publication, preparation, contract, consumption, and provider paths.

The public registry is returned by `public_tools()` through `tools/list` and
the Streamable HTTP transport in `projects/views.py` authenticates Bearer
callers before dispatch. The pre-repair high-level tool unnecessarily required
the caller to provide Product Owner identity, confirmation reference, and an
idempotency key, while the review response did not explicitly route the client
to it.

## Conclusion

Root-cause classification is **C. WRONG_TOOL_SELECTED**, with contributing
**D. REQUIRED_CONTEXT_NOT_RETURNED** and **E. REQUIRED_IDENTITY_OR_REFERENCE_NOT_DERIVED**. No architectural gap was found and no new adapter, approval
authority, or lifecycle component was created.
