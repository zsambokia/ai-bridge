# Sprint 6 remote MCP preflight

**Time:** 2026-07-31  
**Target:** `https://stage.artificial-software-factory.com/mcp/`  
**Credential handling:** the configured credential was used only in process;
it is not present in this record, terminal output, request body, or source.

| Check | Observed result | Interpretation |
| --- | --- | --- |
| Unauthenticated JSON-RPC `initialize` | `401`, `WWW-Authenticate: Bearer realm="ai-bridge-mcp"` | Fail-closed authentication is live. |
| Authenticated `initialize` | `200`; protocol `2025-03-26`; server `ai-bridge@2026-07-31.3` | Streamable HTTP MCP endpoint is live. |
| Authenticated `tools/list` | `200`; 83 governed tools, including `conversation.confirm` | The governed surface is discoverable to a valid client. |
| Authenticated `factory.get_status` | `200`; `ai-bridge` and `bridge-demo` are `ACTIVE` / `READY` | Project registry is readable through the public MCP surface. |
| Initial unauthenticated `/health/` | `200`; `status: ok`; `build_sha: ""` | The remote deployment identity was not proven. This failed preflight is retained. |
| Repaired SHA-bound `/health/` | `200`; `status: ok`; `build_sha: ffd4e1f98cee5c1b99a3481ebe7121ae9c08a22f` | The clean, SHA-bound runtime repair is live. |
| Initial `verify_runtime_deployment` request | `403` from the public edge | The verifier used Python's default user agent, which the edge rejected. This failed attempt is retained. |
| Verifier repair | Explicit `Accept: application/json` and `User-Agent: ai-bridge-runtime-verifier/1.0`, with unit coverage | The public-runtime verifier now identifies itself deterministically instead of depending on a blocked default client. |

## Provenance limitation

The public endpoint uses a static Bearer credential. Its durable caller value
is a hash of the Authorization header, so it safely binds records to that
credential without exposing it. The protocol does not receive trustworthy
evidence that distinguishes the ChatGPT Business UI from another client using
the same credential. A hand-issued HTTP request therefore cannot substitute
for the actual configured ChatGPT Business request mandated by Sprint 6.

## Required next operational observation

Once a workspace administrator makes the existing `AI Bridge staging` remote
MCP app available to the authorized Product Owner, the Product Owner must use
that UI to submit a business-oriented request and approve the reviewed
proposal. The ensuing persisted IDs, delivery/deployment receipts and later
retrieval can then be captured without recreating the request through a
synthetic HTTP client. Before that observation, this record remains a
preflight only; the repaired runtime proof does not claim a ChatGPT Business
request occurred.
