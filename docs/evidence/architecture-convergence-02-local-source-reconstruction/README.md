# Architecture Convergence 02 — local source reconstruction

This package reconstructs the Product Owner's approved architecture from the
locally acquired ChatGPT conversation before comparing it with the repository
or the Constitution. It is a documentation-only Factory Development Mode
work item; it neither changes runtime code nor amends the Constitution.

## Scope and source discipline

Primary historical evidence is the local acquisition at
`C:\Users\User\.codex\chatgpt-acquisition`. No ChatGPT browser scrape,
re-download, or backend acquisition was performed in this work. The raw private
corpus is not copied into this repository.

The package uses deterministic locators of the form `CHAT-0001` through
`CHAT-0443`. A locator maps to the matching 1-based record in
`conversation-source.txt` and the same `acquisition_sequence` record in
`conversation-manifest.json`; the manifest also carries its message UUID and
content hash. The source has no original timestamps or reply-parent relations.

Read the documents in this order:

1. `CONVERSATION_ACQUISITION_REPORT.md` — source format, integrity and limits.
2. `CONVERSATION_TIMELINE.md` — chronological topical map.
3. `DECISION_LEDGER.md`, `DECISION_LINEAGE_REGISTER.md`,
   `APPROVAL_REGISTER.md`, `REJECTED_ALTERNATIVES_REGISTER.md`, and
   `NEGATIVE_INVARIANTS.md` — source-derived decision semantics.
4. `TARGET_ARCHITECTURE.md` — the resulting architecture, still independent of
   the current repository baseline.

Repository comparison documents are deliberately subsequent work. They must
not be treated as proof of the target architecture.

## Integrity status

The corpus is sufficient for a traceable semantic reconstruction, subject to
the limits recorded in the acquisition report. It is not a byte-for-byte,
formally proven lossless export: one terminal-record line-ending discrepancy
and one failed re-audit anchor remain recorded. Neither is silently repaired.

## Process-integrity exception

Before the replacement source rules were applied, the existing
`ARCHITECTURE_CONVERGENCE_PROGRAM_MASTER_PLAN.md` was opened as methodology
context. That document contains target claims. It is quarantined from this
source-derived reconstruction, but the prescribed gate “source reconstruction
before old convergence documents were inspected” cannot truthfully be marked
PASS. `EXECUTION_RECORD.md` retains this exception for final closure.
