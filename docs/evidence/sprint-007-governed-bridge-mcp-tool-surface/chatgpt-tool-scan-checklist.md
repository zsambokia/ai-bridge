# ChatGPT Business tool refresh checklist

Status: not ready for Product Owner UI acceptance because the authenticated staging exchange is still blocked by unavailable execution-process credentials.

After deployment and the successful external MCP-client proof, the Product Owner should:

1. Open the Custom MCP App configuration in ChatGPT Business.
2. Use `https://stage.artificial-software-factory.com/mcp/` and Bearer authentication with the configured MCP API token.
3. Refresh or re-scan tools and confirm tool-surface version `2026-07-26.1`.
4. Confirm all 23 tools are visible, including `factory.get_status`, `project.resolve`, `akb.search`, `execution.prepare`, and `contract.issue`.
5. Run a read-only prompt first. Do not use lifecycle-changing tools without a returned durable approval reference.

This is the remaining manual UI step only after the separate server-side staging proof has passed.
