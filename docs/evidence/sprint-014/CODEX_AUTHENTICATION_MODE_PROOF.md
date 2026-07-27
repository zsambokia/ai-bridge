# Codex authentication-mode proof

The local configured `codex-cli` executable returned a successful exit status
from `codex login status`. The command's standard input, output, and error are
all redirected to null, and only its boolean exit status is retained. This
proves `CODEX_CLI_LOGIN`, not `OPENAI_API_CONNECTION` or an inherited API key.

`CodexCliAdapter` refuses to start an unauthenticated executable with
`CODEX_RUNTIME_UNAVAILABLE`; the health action reports the same condition
without recording command output.
