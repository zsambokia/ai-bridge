# Assessment

The consumed contract binds the exact `codex-cli` provider identity as a
`CODE_EXECUTION_AGENT`. The existing OpenAI provider remains an independent
`MODEL_API_SERVICE`; Codex has no credential binding and no duplicate secret
was introduced.

The repair makes readiness operational rather than merely executable-path
based: `codex login status` must succeed before Codex is healthy or an
execution is started. Its stdout and stderr are discarded.
