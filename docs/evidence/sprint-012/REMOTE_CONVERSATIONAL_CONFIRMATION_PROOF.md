# Remote conversational confirmation proof

The active local AI Bridge server was reached through
`https://stage.artificial-software-factory.com/mcp/` on 2026-07-27.  This is
the Cloudflare Tunnel transport for the repaired local server, not a simulated
client or a local-only test.

| Step | Actual result |
| --- | --- |
| `work_item.propose` | one fresh scope: `bridge:ai-bridge:work-item:a21f70c5-e7ed-4b00-b116-0b37fbbdb5df` |
| `scope.review` | version `1`, hash `89233b2c2de4d12fff4231809b7a95beae22a29ed7482c0405cb13fb8b641449`, eligible, next tool `conversation.confirm` |
| `conversation.confirm` with `Igen, jó lesz.` | `EXECUTION_STARTED`, not `APPROVAL_REQUIRED` |
| durable approval | reference `conversation-confirmation:v1:6fb47d6e92a41976a243aa7ceb6937e70e12a93d7fb3af11e8cd5d0f8540dc1a` |
| durable orchestration | `3b8234b7-48f4-42cf-97a5-76aaaafbf25a` |
| issued/consumed contract | `bridge:ai-bridge:contract:9805dbfd-c446-49db-a2f0-bd645084f51b` |
| provider run | `46612027-99bb-462f-a97f-8526e7f8a4f7`, provider process `2752`, which finished |

The provider created the previously absent `confirmationproof/` Django app,
registered `confirmationproof.apps.ConfirmationProofConfig`, and wrote its
own scope evidence under
`docs/evidence/bridge-ai-bridge-work-item-a21f70c5-e7ed-4b00-b116-0b37fbbdb5df/`.
No bootstrap reference was supplied to this Work Item and `scope.approve` was
not its conversational entry point.

An identical remote `conversation.confirm` retry returned HTTP 200 with
`idempotent_replay: true`, the same orchestration token, contract identifier,
and execution token.  It created no second approval, orchestration, contract,
or run.

The final `scope.complete_execution` response is bound to the final Sprint
commit and recorded in the terminal evidence update.
