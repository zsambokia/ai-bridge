# Sprint 006 extended assessment

## Finding

The previous public `/mcp/` handler accepted a proprietary `operation` / `payload`
shape.  It did not implement MCP initialization, `tools/list`, or `tools/call`,
and ordinary Django middleware could return browser-oriented errors.  The internal
Bridge operation registry remains available to canonical application services, but
is no longer the public protocol surface.

## Decision

The public endpoint now implements MCP JSON-RPC 2.0 over Streamable HTTP at
`/mcp/`, using protocol version `2025-03-26`.  It deliberately exposes only the
read-only `factory.get_status` tool.  No separate service implementation or write
tool was introduced.

Authentication is an explicit Bearer token boundary (`MCP_AUTH_MODE=bearer` and
`MCP_API_TOKEN` from the deployment secret store).  A missing secret fails closed
with a JSON-RPC error and HTTP 503; missing or invalid credentials return 401.
OAuth is the production-direction documented in the integration guide.  Cloudflare
Tunnel credentials are transport credentials and are not accepted as MCP client
credentials.

## Contract lifecycle diagnosis

The original issued artifact used `EXACT` with baseline
`8c6e8dc6ed1edab69513220f026f3d2fedd75fc5`.  Committing that artifact made HEAD a
descendant immediately, so an integrity validator correctly rejected it.  The
canonical generator and validator now use and enforce `DESCENDANT_OF`: the
baseline must remain an ancestor of HEAD, preserving history integrity while
allowing an immutable issued artifact to be published.  The original contract is
recorded in `SUPERSEDED_EXECUTION_CONTRACT.json`; the replacement was validated,
issued, and consumed before implementation.
