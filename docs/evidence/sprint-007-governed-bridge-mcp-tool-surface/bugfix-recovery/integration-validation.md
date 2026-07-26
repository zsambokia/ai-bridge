# External integration and Cloudflare validation

## Observed Cloudflare behavior

- The default Python urllib client identification (`Python-urllib/3.12`) was
  rejected by Cloudflare with HTTP 403 / error `1010`
  (`browser_signature_banned`).
- The same HTTPS MCP flow using the external acceptance client's explicit
  `mcp-external-acceptance/1.0` User-Agent passed initialization, initialized
  notification, discovery, and Bearer-token rejection checks.

This demonstrates that Cloudflare is not globally blocking the endpoint or all
non-browser MCP traffic. It does **not** prove that every standards-compliant
MCP client, nor the actual ChatGPT Business client User-Agent/egress path, is
allowed. No ChatGPT workspace traffic or Cloudflare rule-management access is
available to this execution.

## Required targeted follow-up

After migration, an operator must capture the actual ChatGPT request outcome.
If it receives 403/1010, add the narrowest Cloudflare WAF/Bot exception for the
MCP endpoint and verified ChatGPT client signature/egress characteristics, then
rerun the acceptance. Do not disable global Bot or WAF protection.
