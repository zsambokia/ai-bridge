# 02 — Conversation Understanding / Cross-Cutting Foundation Closure Package

Status: **Product Owner approved design package — canonical amendments not yet applied**

## Purpose

This package captures the architecture changes agreed during Architecture Convergence section 02 without performing a repository-wide traversal or claiming that the current canonical documentation has already been amended.

The deliberate workflow boundary is:

1. ChatGPT/Product Owner collaboration defines and records the target architecture and required constitutional deltas.
2. Codex performs the exhaustive repository traversal, contradiction search, impact validation, amendment implementation, diagram/index updates, and closure verification.
3. Canonical documents are considered updated only after that Codex pass is reviewed and accepted.

## Documents

- `01_TARGET_ARCHITECTURE_DECISION_REGISTER.md` — consolidated approved target decisions.
- `02_CONSTITUTION_AMENDMENT_REQUIREMENTS.md` — normative requirements that canonical architecture documents must be changed to express.
- `03_CONSTITUTION_IMPACT_MATRIX.md` — known impact areas and required treatment; Codex must expand/verify this against the full repository.
- `04_CODEX_CLOSURE_HANDOFF.md` — exact assessment → architecture challenge → implementation → verification handoff for Codex.

## Closure rule

This package is **not** itself the Constitution. It is the approved convergence specification from which the Constitution must be amended.

No existing implementation is allowed to override these target decisions merely for backward compatibility. Where current code or documentation conflicts with the approved target, Codex must report the conflict and treat the target architecture as authoritative unless it finds a materially better architecture and explicitly raises it for Product Owner decision before implementing that alternative.
