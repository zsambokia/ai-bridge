# Integration validation

`CodexCliAdapter` resolves the configured executable, checks its authenticated
runtime state, and only then invokes `codex exec` with a workspace-write
sandbox. The persisted provider remains the existing active `codex-cli`
execution-agent record. The OpenAI model provider is not selected or changed.

The governed execution record is `ae54d0e6-9fad-41f6-b751-e4f6e537f608` and
uses provider identity `codex-cli`.
