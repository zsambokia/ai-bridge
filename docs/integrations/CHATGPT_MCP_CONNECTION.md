# ChatGPT Business remote MCP connection

## Connection values

| Setting | Value |
| --- | --- |
| App name | `AI Bridge staging` |
| MCP endpoint | `https://stage.artificial-software-factory.com/mcp/` |
| Transport | Streamable HTTP (MCP protocol `2025-03-26`) |
| Staging authentication | `Authorization: Bearer <MCP_API_TOKEN>` |
| Discovered tool | `factory.get_status` |

The endpoint is a remote MCP server, not a browser login endpoint. It accepts
JSON-RPC 2.0 requests and returns JSON for all protocol and authentication
failures. The production hostname is prepared as
`https://app.artificial-software-factory.com/mcp/`, but must not be selected
until its Cloudflare/DNS deployment has been explicitly activated.

## Prerequisites

A ChatGPT Business workspace administrator must enable the workspace's custom
app/developer-mode capability and have permission to add a remote MCP app. The
staging tunnel must be running and the deployment must have the following
secret-free configuration plus a real deployment-secret value:

```dotenv
DJANGO_ALLOWED_HOSTS=stage.artificial-software-factory.com,app.artificial-software-factory.com
MCP_PUBLIC_BASE_URL=https://stage.artificial-software-factory.com
MCP_AUTH_MODE=bearer
MCP_API_TOKEN=<generated-secret>
```

Generate `MCP_API_TOKEN` with a cryptographically secure password generator
and store it only in the deployment secret manager and the authorized ChatGPT
app credential configuration. Never place it in source control, evidence,
Cloudflare Tunnel configuration, request URLs, screenshots, or prompts.

## Create and verify the app

1. In the ChatGPT Business workspace, open the administrator/developer custom
   app area and create a remote MCP app.
2. Enter the endpoint exactly as
   `https://stage.artificial-software-factory.com/mcp/`; do not append an
   `operation` or `payload` path/query.
3. Select Streamable HTTP if the UI requests a transport.
4. Configure the app's supported Bearer authorization credential with the
   current `MCP_API_TOKEN`. Do not configure a Cloudflare Tunnel token here.
5. Run the UI's tool scan. It must discover `factory.get_status` with no input.
6. In a new chat, invoke: `Use factory.get_status and summarize the current AI
   Bridge project status.` Approve the read-only tool request if the workspace
   policy asks for approval.

The OpenAI remote MCP guide documents public remote MCP servers, server URLs,
tool discovery, tool-call approval, and the security model:
<https://developers.openai.com/api/docs/guides/tools-connectors-mcp>.

## Authorization and operations

`MCP_API_TOKEN` authenticates the MCP client; it is not an end-user identity or
authorization grant. The current public registry is intentionally restricted
to the read-only `factory.get_status` capability. Authentication therefore
permits access only to that least-privilege surface. Future write tools require
a separate approved authorization design and Sprint.

Rotate the token by generating a replacement, updating the deployment secret,
restarting/redeploying the service, updating the ChatGPT credential, and
performing a new tool scan. Revoke a suspected token by replacing or removing
the deployment secret; a missing secret fails closed with JSON `503`, and an
invalid token returns JSON `401` with `WWW-Authenticate: Bearer`.

The production direction is standards-compliant OAuth with explicit client
registration, scopes, consent, access-token expiration, revocation, and
redirect-URI validation. Bearer authentication is the revocable, supported
staging proof; do not silently fall back to anonymous access.

Cloudflare Tunnel credentials authorize the tunnel agent to connect to
Cloudflare. Cloudflare Access service credentials authorize Cloudflare Access.
Neither authenticates an MCP client to Django; `MCP_API_TOKEN` is the separate
MCP client credential.

## Governed tool refresh (Sprint 007)

After deploying the registry, refresh or re-scan the custom MCP app. ChatGPT
should discover `factory.list_capabilities`, project resolution/context, bounded
AKB search, execution preparation, governed contract lifecycle tools, and the
execution-start request boundary. If it only shows `factory.get_status`, remove
and re-add the app or force its tool refresh, then verify `tools/list` with the
same endpoint and Bearer token. State-changing tools may return an approval
requirement: the workspace credential does not replace a durable Product Owner
approval record. The complete inventory is in `BRIDGE_MCP_TOOL_REFERENCE.md`.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `401` | Missing or wrong Bearer token; rotate/update the app credential. |
| `403` | Check Cloudflare Access policy separately from the MCP token. |
| `404` | Use the exact `/mcp/` path and verify the Django route is deployed. |
| `405` | Send a JSON-RPC POST, not a browser GET. |
| `502` / `504` | Verify the tunnel process, upstream ASGI/Django service, timeout, and buffering configuration. |
| Host rejection | Configure only the approved hostname in `DJANGO_ALLOWED_HOSTS`; do not use wildcards. |
| CSRF HTML or login page | A deployed old version/proxy is handling the request; the MCP route itself is CSRF-exempt and JSON-only. |
| Invalid MCP response | Confirm JSON-RPC 2.0 with `initialize` before `tools/list`/`tools/call`, and preserve the protocol version. |
| No tools discovered | Rescan after valid authentication; expect exactly `factory.get_status`. |
| OAuth redirect mismatch | OAuth is not enabled in this staging proof; when production OAuth is introduced, register the exact HTTPS redirect URI. |

## Product Owner acceptance

Codex cannot operate the Business workspace UI. After the deployed endpoint is
reachable, the Product Owner must perform the app creation, credential entry,
tool scan, and one read-only prompt above. This UI verification does not
authorize additional tools or anonymous staging access.
