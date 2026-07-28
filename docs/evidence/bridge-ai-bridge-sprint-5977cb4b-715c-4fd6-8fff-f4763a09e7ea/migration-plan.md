# Migration plan and compatibility boundary

Migration `projects.0022_akb_foundation` adds two nullable/defaulted session
fields and creates new AKB tables. It neither rewrites nor deletes existing
project, scope, contract, incident, or MCP audit data. Legacy
`akb.get_document` remains available; `akb.search` now queries structured AKB
entries and therefore intentionally returns no legacy document snippets unless
they are imported as approved entries. No automatic legacy import is claimed.
