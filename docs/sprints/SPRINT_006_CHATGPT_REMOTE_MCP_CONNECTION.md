# Sprint 006 — ChatGPT Remote MCP Connection

**Status:** APPROVED FOR CODEX EXECUTION  
**Execution level:** SPRINT  
**Task type:** CONFIGURATION  
**Risk modifiers:** EXTERNAL_INTEGRATION, AUTHENTICATION_OR_AUTHORIZATION, PUBLIC_API_OR_PROTOCOL  
**Target branch:** `main`

## 1. Vision

Make AI Bridge usable from ChatGPT Business as a standards-compliant remote MCP app through a public HTTPS endpoint.

The required end-to-end path is:

```text
ChatGPT Business
→ Custom MCP App
→ HTTPS Streamable HTTP MCP endpoint
→ Cloudflare Tunnel
→ AI Bridge
→ governed Bridge tools
```

Success means ChatGPT can discover the Bridge tools, authenticate according to the approved staging policy, and call at least one safe read-only tool without receiving Django HTML, CSRF, host, redirect, or proprietary-protocol errors.

## 2. Confirmed starting state

The current `/mcp/` endpoint is a custom Django JSON adapter using an `operation` and `payload` request shape. It is not yet a standards-compliant remote MCP server and does not provide the required MCP initialization, tool discovery, tool schemas, or `tools/call` behavior.

The implementation must assess and reuse the canonical Bridge services and existing tool logic. It must not preserve the proprietary HTTP adapter as the ChatGPT-facing protocol merely by renaming it MCP.

## 3. In scope

- assess the current MCP adapter, routing, schemas, services, tests, Cloudflare-facing settings, and deployment assumptions;
- implement a standards-compliant remote MCP endpoint using Streamable HTTP when supported by the selected current MCP SDK;
- provide MCP initialization, capability negotiation, tool discovery, structured tool schemas, and tool invocation;
- expose at least one safe read-only status tool, preferably `factory.get_status`, backed by real Bridge state;
- introduce explicit authentication configuration suitable for ChatGPT custom MCP apps;
- implement a safe staging authentication mode and document the production OAuth direction;
- ensure the endpoint is compatible with Cloudflare proxying and Django/ASGI behavior;
- eliminate CSRF HTML failures and HTML login redirects from the MCP protocol surface;
- configure the approved Cloudflare hostnames without wildcard host acceptance;
- add environment configuration examples without committing secrets;
- add automated protocol, authentication, host, proxy, tool-discovery, and regression tests;
- create precise ChatGPT Business setup documentation;
- create deterministic evidence bound to the final commit.

## 4. Explicitly out of scope

- a general-purpose user account system;
- a login UI or new administrative dashboard;
- unrestricted write tools;
- autonomous Codex execution initiated by ChatGPT without existing governance checks;
- a second parallel Bridge business-service implementation;
- committing real tokens, OAuth secrets, Cloudflare credentials, or tunnel credentials;
- treating a Cloudflare Tunnel token as MCP client authentication;
- activating the production hostname when external DNS or Cloudflare configuration is unavailable to the execution environment.

Production readiness must be documented and tested where deterministic, but external activation remains a Product Owner deployment action unless credentials and access are explicitly available.

## 5. Required transport and protocol behavior

The public MCP URL should normally be:

```text
https://stage.artificial-software-factory.com/mcp/
```

The prepared production URL is:

```text
https://app.artificial-software-factory.com/mcp/
```

Use the current standards-compliant remote MCP transport supported by ChatGPT, preferring Streamable HTTP. The endpoint must support the MCP initialization and tool lifecycle required by a remote client.

The ChatGPT-facing endpoint must:

- return MCP/JSON protocol responses rather than HTML;
- expose valid tool names, descriptions, input schemas, and appropriate annotations;
- support tool listing and tool calls;
- return structured protocol errors;
- use appropriate HTTP status codes;
- avoid application login redirects;
- avoid Cloudflare caching of protocol traffic;
- preserve the canonical Bridge service layer rather than duplicate it.

If the repository also needs a local `stdio` transport, both transports must share the same canonical tool registry and service implementation.

## 6. Authentication decision

Implement authentication as an explicit, configurable subsystem.

The Sprint must support a secure staging connection that ChatGPT can actually use. Select the simplest standards-compatible option supported by the current ChatGPT custom MCP app configuration and document the decision.

Permitted staging approaches, in preference order based on verified compatibility:

1. standards-compliant OAuth;
2. supported Bearer-token authentication from environment configuration;
3. anonymous access only for a tightly controlled temporary staging proof when the ChatGPT interface cannot transmit the required token and the exposure is explicitly documented, read-only, revocable, and not enabled by default.

Requirements:

- secrets are loaded only from environment or a deployment secret manager;
- secrets never appear in source, logs, tests, evidence, or documentation examples;
- missing required secrets fail closed;
- invalid credentials return machine-readable `401` or `403` responses;
- token generation, rotation, and revocation are documented;
- OAuth is the documented production direction if the first proof uses a simpler staging mechanism;
- authentication and authorization are modeled separately;
- Cloudflare Tunnel credentials, Cloudflare Access service credentials, MCP API credentials, and OAuth secrets are clearly distinguished.

## 7. Cloudflare and Django requirements

Approved hosts:

```text
stage.artificial-software-factory.com
app.artificial-software-factory.com
```

Do not use unrestricted wildcard hosts.

Assess and configure, where relevant:

- `ALLOWED_HOSTS`;
- trusted origins only where browser-origin protection is actually applicable;
- proxy SSL headers;
- forwarded host and scheme behavior;
- ASGI deployment and streaming support;
- timeout and buffering assumptions;
- cache-control for MCP traffic;
- deterministic handling of Cloudflare forwarding headers.

Do not apply ordinary browser CSRF enforcement to authenticated machine-to-machine MCP protocol requests in a way that produces HTML failures. Use an appropriate API authentication boundary instead.

The staging hostname must be proven. The production hostname may be marked deployment-pending when DNS or Cloudflare activation is external, but its application configuration and tests must be ready.

## 8. Minimum tool proof

Expose at least:

```text
factory.get_status
```

or an equivalently named canonical read-only status tool if repository conventions require another name.

The tool must:

- have a precise description;
- have a valid input JSON schema;
- read real Bridge state;
- return a deterministic structured result;
- not depend on hidden chat history;
- not mutate repository or runtime state;
- return protocol-compliant errors.

Do not expose broad write capabilities merely to satisfy tool discovery.

## 9. Environment and operational documentation

Create or update a secret-free `.env.example` using existing repository naming conventions. It must represent at least:

```text
DJANGO_ALLOWED_HOSTS=stage.artificial-software-factory.com,app.artificial-software-factory.com
MCP_PUBLIC_BASE_URL=https://stage.artificial-software-factory.com
MCP_AUTH_MODE=<resolved mode>
MCP_API_TOKEN=
```

Exact names may differ if the repository already has canonical configuration names.

Create:

```text
docs/integrations/CHATGPT_MCP_CONNECTION.md
```

Document:

- prerequisites for ChatGPT Business workspace administration;
- Developer mode and custom app enablement;
- the exact MCP endpoint;
- selected authentication mode;
- where the credential is generated and stored;
- the ChatGPT app creation and tool-scan steps;
- a test prompt using `factory.get_status`;
- token rotation/revocation or OAuth lifecycle;
- Cloudflare Tunnel versus client-auth distinctions;
- troubleshooting for 401, 403, 404, 405, 502, 504, host rejection, CSRF HTML, invalid MCP response, no tools discovered, and OAuth redirect mismatch;
- the manual Product Owner steps that cannot be performed from Codex.

## 10. Acceptance scenarios

### A. Standards-compliant initialization

A standards-compliant remote MCP client can initialize against `/mcp/` and receives valid negotiated capabilities without proprietary `operation/payload` requests.

### B. Tool discovery

A client can list tools and receives at least the canonical read-only status tool with a valid name, description, input schema, and annotations where applicable.

### C. Tool invocation

The status tool can be called and returns real, structured Bridge status through MCP.

### D. Authentication

When authentication is enabled:

- missing credentials are rejected;
- invalid credentials are rejected;
- valid credentials permit initialization, discovery, and the read-only tool call;
- no secret appears in logs or evidence.

### E. Cloudflare/Django behavior

- the staging hostname is accepted;
- the application hostname is accepted at application configuration level;
- an unapproved hostname remains rejected;
- proxy scheme and host handling are correct;
- protocol requests do not receive Django CSRF or login HTML;
- MCP responses are not cacheable by shared intermediaries.

### F. ChatGPT readiness

The documentation provides all values and steps needed to create a ChatGPT custom MCP app and run `Scan Tools` successfully.

When Codex cannot operate the Product Owner's ChatGPT UI, server-side compatibility must be fully proven with a standards-compliant client and the remaining UI validation must be explicitly recorded as a manual Product Owner acceptance step rather than falsely reported as completed.

### G. Regression safety

All repository-wide Release Gates and existing Bridge MCP/context tests pass. Existing canonical services remain reusable and no parallel implementation is introduced.

## 11. Required tests

Add automated tests covering at least:

1. MCP initialization;
2. tool listing and schema validity;
3. `factory.get_status` invocation;
4. protocol-compliant error behavior;
5. missing, invalid, and valid authentication credentials;
6. approved and unapproved hosts;
7. forwarded HTTPS/proxy handling;
8. absence of CSRF/login HTML on MCP requests;
9. cache-control behavior;
10. compatibility with the existing Bridge context/tool service layer;
11. complete repository regression gates.

## 12. Evidence

Evidence root:

```text
docs/evidence/sprint-006-chatgpt-remote-mcp-connection/
```

Required artifacts:

```text
CLOSURE_REPORT.md
acceptance-results.json
mcp-protocol-validation.json
tool-discovery-results.json
authentication-validation.json
cloudflare-endpoint-validation.json
chatgpt-setup-checklist.md
```

Evidence must record:

- repository, branch, baseline, and final commit;
- assessment of the old adapter;
- selected SDK, protocol, transport, and authentication decision;
- exact commands and sanitized results;
- all acceptance scenarios;
- staging endpoint validation;
- production configuration readiness or precise external blocker;
- final ChatGPT UI steps for the Product Owner;
- exact allowed terminal state.

## 13. Release Gates

Run every repository-wide Release Gate resolved from `.bridge/project.yaml`, plus the Sprint-specific protocol, authentication, host, proxy, tool-discovery, and regression tests.

Ordinary dependency, implementation, configuration, test, lint, type, documentation, or evidence failures must be diagnosed, repaired, and rerun. They are not valid reasons to request Product Owner intervention.

## 14. Closure

Update all affected canonical documentation and `docs/akb/CURRENT_STATE.md` truthfully.

Close with exactly one allowed terminal state:

```text
PASS — READY FOR PRODUCT OWNER REVIEW
BLOCKED — BUSINESS DECISION REQUIRED
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

A PASS may include a clearly identified Product Owner UI acceptance step only when all repository-side and remotely reproducible MCP requirements have passed and the Codex environment cannot access the ChatGPT workspace UI.
