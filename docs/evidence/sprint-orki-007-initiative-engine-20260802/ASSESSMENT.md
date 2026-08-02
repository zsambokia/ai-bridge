# ORKI-007 Initiative Engine — Independent Release Gate Assessment

**Date:** 2026-08-02
**Result:** **PASS — READY FOR PRODUCT OWNER REVIEW**
**Authority:** Product Owner Factory Development Mode; Executive Checkpoint B accepted; continuation to ORKI-007 directed by the Product Owner.
**Branch / baseline:** `agent/issue-17-conversational-po` / `0f8153ad1e790f40662d5701247e6c5681ddaaa5`

## Capability decision

ORKI-007 proves initiative as a Cognitive State capability, not an occasional
chat suggestion. After a normal Factory Chat conversation records structured
Mission Understanding state, the Initiative Engine independently derives a
project-scoped `INITIATIVE` observation when an applicable risk, opportunity,
or safe assumption exists. The observation is explainable, linked to its
source state, prioritised deterministically, dismissible, rate-limited, and
explicitly non-authoritative.

## Executable behavioural evidence

| Required behaviour | Evidence | Result |
| --- | --- | --- |
| Unprompted initiative | An HTTP Factory Chat turn with a provider-produced safe assumption creates a `MISSING_EVIDENCE` observation without an owner request. | PASS |
| Conversation is not memory | The initiative links the structured source state; confidential raw transcript text is absent from the initiative projection and its state value. | PASS |
| Evidence and explainability | Projection exposes source entry, category, priority, rationale, confidence, dismissal capability, and `authority: NONE`. | PASS |
| Deterministic initiative | Risk, opportunity, and assumption inputs map to deterministic categories and priority order. Re-derivation is idempotent. | PASS |
| Correction / dismissal | Product Owner dismissal changes only the initiative lifecycle and creates attributable dismissal evidence; it cannot erase or recreate source state. | PASS |
| Project isolation | Derivation and projection are project-scoped; another project sees no initiative. | PASS |
| Bounded initiative | Six eligible state entries create only five active observations. | PASS |
| No execution side effect | The end-to-end scenario creates no `FactoryPlan`, governance action, delivery work, approval, or execution. | PASS |

## Final validation record

The following commands are rerun against the final repository state before
closure:

```text
$env:PYTHON_DOTENV_DISABLED='true'; .\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
$env:PYTHON_DOTENV_DISABLED='true'; .\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\ruff.exe check .
$env:PYTHON_DOTENV_DISABLED='true'; .\.venv\Scripts\python.exe manage.py test --verbosity 1
$env:PYTHON_DOTENV_DISABLED='true'; .\.venv\Scripts\python.exe manage.py test projects.tests.test_factory_chat_browser_e2e --verbosity 1
```

Final results: `makemigrations --check --dry-run` reported `No changes
detected`; `manage.py check` reported no issues; `ruff check .` reported `All
checks passed!`; the full backend suite passed **81/81** in 54.748 seconds;
and the real Chromium Factory Chat suite passed **9/9** in 22.720 seconds.
Focused Initiative Engine and end-to-end release-gate tests also pass.

## Gate summary

| Gate | Result | Basis |
| --- | --- | --- |
| Engineering acceptance | PASS | Revisioned model lifecycle, deterministic service, migration, focused tests. |
| Operational acceptance | PASS | Real Factory Chat request proves unsolicited, bounded cognitive behaviour. |
| Cognitive / COO capability | PASS (Initiative capability) | State-only derivation, explanation, dismissal, isolation, cap, and authority boundary proven. |
| Schema, system and static checks | PASS | Final validation record. |
| Backend and browser regression | PASS | Final validation record. |
| Architecture, documentation, AKB, roadmap | PASS | ADR, canonical flow, scorecard, sprint, AKB, and roadmap updated. |
| Self-critique | PASS with retained limits | Limits below are explicit and do not weaken the Sprint scope. |

## Self-critique and retained limits

This Sprint is deliberately not a claim that Orki has complete initiative
intelligence. It does not yet prove semantic detection of inconsistencies,
duplicate work, reusable components, simplifications, or Sprint-size issues.
It supplies no dedicated Product Owner initiative UI, no immediate same-turn
chat rendering, no cross-provider conformance suite, and no governance or
execution integration. Those are separate capability scopes. The five-item cap
protects Product Owner attention, but the future UX capability must prove that
the ranking is useful in realistic multi-signal portfolios.

## DCMI impact

The accepted Executive Checkpoint B baseline remains **58/100**. The
[DCMI scorecard](../../architecture/ORKI_DCMI_SCORECARD.md) records an
evidence-backed Initiative score of 8/10 and a post-ORKI-007 total of
**66/100**. This is a progress measure, not an Epic completion claim.

## Product Owner acceptance boundary

The Product Owner accepted Engineering Acceptance, Operational Acceptance and
the Initiative Engine at **66/100 DCMI**. The accepted evidence establishes
only Initiative **Level 1 — Observation**. Recommendation, Alternative
proposal and Cross-project strategic initiative remain separate, evidence-gated
capabilities under [Orki Initiative Maturity](../../architecture/ORKI_INITIATIVE_MATURITY.md).
