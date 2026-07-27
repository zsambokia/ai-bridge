# Provider selection proof

Contracts continue to pin `selected_provider_identity`; consumption must match it. `select_provider()` requires an exact identity, enabled ACTIVE execution-agent role, and requested capabilities. Missing, disabled, draft, mismatched-role, or capability-ineligible providers raise `EXECUTOR_PROVIDER_UNAVAILABLE`. There is no silent fallback.
