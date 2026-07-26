# ChatGPT setup checklist

- [x] Remote endpoint is Streamable HTTP: `https://stage.artificial-software-factory.com/mcp/`.
- [x] MCP initialization, discovery, and safe tool invocation are covered by automated tests.
- [x] The discovered tool is `factory.get_status`.
- [x] Cloudflare staging endpoint is externally reachable and returns JSON, not HTML.
- [x] The repository documents client authentication, token rotation, and the OAuth production direction.
- [ ] Product Owner: create/store a staging `MCP_API_TOKEN` in the deployment secret manager and redeploy/restart the staging service.
- [ ] Product Owner: configure the ChatGPT Business custom MCP app with the endpoint and its supported Bearer credential field, then run **Scan tools**.
- [ ] Product Owner: prompt the app to call `factory.get_status` and record the workspace result.

The incomplete items require access to the deployment secret manager and ChatGPT
Business workspace.  No token value is recorded here.
