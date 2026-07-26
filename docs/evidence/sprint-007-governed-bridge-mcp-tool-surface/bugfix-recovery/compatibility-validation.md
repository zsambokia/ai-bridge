# MCP compatibility validation

The public staging HTTPS endpoint previously passed `initialize`,
`notifications/initialized`, and `tools/list` using JSON-RPC Streamable HTTP
semantics. Discovery returned exactly 23 tools and `factory.get_status`
advertised tool-surface version `2026-07-26.1`.

Valid `tools/call` is not marked compatible yet: each observed valid call
returned HTTP 500 before a JSON-RPC result. The post-migration rerun is the
required proof for compatibility closure.
