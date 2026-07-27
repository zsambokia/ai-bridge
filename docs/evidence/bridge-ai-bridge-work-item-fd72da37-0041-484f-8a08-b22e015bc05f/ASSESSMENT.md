# Sprint 013 provider-boundary assessment

## Contract binding

- Contract: `bridge:ai-bridge:contract:b88fcd0f-9120-43a2-968b-4dbdf6373511`
- Approved scope: `bridge:ai-bridge:work-item:fd72da37-0041-484f-8a08-b22e015bc05f`, version `1`
- Verified scope content hash: `b21723cbec900b01f71f464aa7f2611160f61960d869b0397b6b359e8fd4ae32`
- Repository and branch: `zsambokia/ai-bridge` on `main`
- Declared baseline: `0707aca6d8b1484e099128aa2d8d8c741b307d5e` (HEAD at preflight)

## Inventory and findings

| Required capability | Finding |
| --- | --- |
| `conversation.confirm` | Canonical high-level Product Owner confirmation entry point; derives caller binding, confirmation reference, and retry key. |
| `GovernanceApproval` | Durable approval record used by the canonical lifecycle. |
| `ConversationOrchestration` | Resumable conversation orchestration that advances the approved lifecycle. |
| `ExecutionContract` | AI Bridge issues schema `2.0` contracts and embeds the selected and eligible provider identity. |
| `ExecutionRun` | Cannot start without a consumed contract and receipt; it records the resolved provider identity. |
| Codex CLI adapter | The only operational adapter is the fixed-argument `codex-cli` adapter. |

`scope.confirm_and_execute` remains the structured entry point for an exact
review version and hash. `scope.approve` only binds an already-existing durable
approval reference and is not a free-form conversational confirmation path.

## Required classification

`EXECUTION_PROVIDER_IS_HARD_CODED` — confirmed. `codex-cli` is the sole
operational identity. This is an explicit boundary, not a fallback: the resolver
rejects a configured or requested identity other than `codex-cli`.

## Provider identity binding

Before dispatch, contract consumption requires the provider identity to be both
selected and eligible. `start_run` requires the durable consumption receipt and
resolves the adapter using the receipt identity before invoking the provider.
The governed orchestration passes the contract's selected identity into
consumption. An unsupported identity cannot silently select another provider.

## Scope decision

The audit found the approved hard boundary and no unsupported-provider fallback.
The smallest authorized repair is the explicit selected/eligible identity
enforcement and its focused regression coverage; no dynamic-provider abstraction
was introduced.
