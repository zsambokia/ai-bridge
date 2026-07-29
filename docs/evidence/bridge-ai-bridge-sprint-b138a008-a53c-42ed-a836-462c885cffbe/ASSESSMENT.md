# Assessment

The reported exception was caused by `CodexCliAdapter._project_activity`
assuming that every successfully decoded JSON line was a mapping. A valid JSON
string therefore reached `decoded.get(...)`, raising `AttributeError` in the
reader thread. The provider subprocess could continue, but activity capture
silently stopped and the thread exception obscured the real provider output.

The repair replaces that assumption with a typed projection boundary. Only a
JSON object is treated as a structured Codex event. JSON scalars, malformed
JSON, and plain text are retained as redacted provider messages. Unexpected
projection and persistence-boundary errors are isolated to one line so the
reader keeps consuming later lines.

Implementation baseline: `56e5a2e94d08c42217ff3eeebf2a663133f377a7` on `main`.
