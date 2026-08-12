# Architecture Convergence 02 — Recovered Approval Details

Status: WORKING / MANDATORY APPROVAL-PRESERVATION INPUT
Authority: Product Owner sequential approvals recovered during completeness audit
Canonical effect: NONE until closure approval and merge

## Purpose

This register captures approved semantic detail discovered to have been compressed too aggressively in the first lossless reconstruction.

**Rule:** an entry in this file is not an optional clarification. Where its status is `ACCEPTED — RECOVERED DETAIL`, the final Lossless Approved Decision Ledger, Approval Coverage Matrix, Codex Closure Specification and constitutional wording MUST preserve the full semantic detail. A shorter summary is insufficient if it loses responsibility, strategy-selection, authority, lifecycle, negative-invariant or boundary semantics.

This file is deliberately append-oriented. Recovered details remain visible even after they are folded back into the primary ledger, so the completeness audit can prove what was previously missing.

---

# RD-CU-06 — Understanding Policy defines the required interpretation; stateless Understanding chooses processing strategy

**Status:** ACCEPTED — RECOVERED DETAIL  
**Parent decision:** CU-06 — Profile declares requirements, not LLM workflow

## Approved decision

> **Understanding SHALL NOT be canonically bound either to a single-prompt architecture or to a multi-agent/pipeline architecture. The Processing/Cognitive Profile `Understanding Policy` declares the desired interpretation result, requirements and required checks. The stateless Understanding capability chooses an appropriate processing strategy capable of satisfying that policy.**

## Required semantics

### 1. The canonical contract is outcome/requirement-oriented

The `Understanding Policy` describes **what the Understanding capability must achieve**, not the internal orchestration topology used to achieve it.

It may define, as applicable:

- required interpretation outputs;
- semantic distinctions that must be preserved;
- required confidence/quality expectations where such requirements are defined;
- ambiguity handling requirements;
- required verification/checking expectations;
- constraints relevant to the interpretation;
- other declarative requirements of the Understanding result.

The policy is therefore a **declarative processing requirement**, not an executable workflow graph.

### 2. Single-prompt is not canonical architecture

A compliant implementation MAY satisfy a particular Understanding Policy with one LLM call when that is sufficient.

The Constitution SHALL NOT imply:

```text
Understanding = one prompt
```

or make prompt topology part of the semantic contract.

### 3. Multi-agent / pipeline is not canonical architecture

A compliant implementation MAY use multi-stage or multi-agent processing when required, but the Constitution SHALL NOT prescribe:

```text
Understanding = fixed pipeline
Understanding = mandatory multi-agent system
Understanding = fixed sequence of LLM calls
```

The existence of complex processing requirements does not itself justify making an orchestration topology part of Cognitive Profile semantics.

### 4. Processing strategy belongs to the stateless Understanding capability

Given:

```text
immutable Context Package
+ Effective Cognitive Profile
  └── Understanding Policy
```

The **stateless Understanding capability** selects an appropriate processing strategy for the invocation.

Conceptually:

```text
Understanding Policy
  │
  │ declares desired interpretation,
  │ requirements and required checks
  ▼
Stateless Understanding Capability
  │
  │ selects compliant processing strategy
  ▼
Processing strategy
  ├── deterministic parsing
  ├── classifier
  ├── embedding-based processing
  ├── single LLM call
  ├── multiple LLM calls
  ├── staged processing
  ├── verification / critique
  ├── alternate model strategy
  └── combinations of the above
  │
  ▼
Immutable Understanding Result
```

The listed strategies are architectural examples of allowed implementation freedom, not a frozen canonical strategy taxonomy.

### 5. Strategy selection does not create durable Understanding state

Choosing a processing strategy SHALL NOT turn Understanding into a stateful domain owner.

Durable state remains owned by the invoking domain. Understanding remains a stateless capability operating from explicit inputs.

### 6. Strategy selection does not create business/domain authority

The ability to select a processing strategy is **processing authority**, not business/domain decision authority.

Even if the selected strategy performs multiple checks, model calls or verification stages:

```text
Understanding → interprets
Evaluation → qualifies against applicable policy/contract
Domain Authority → owns consequence/state change
```

CU-03 and CU-13 remain controlling authority boundaries.

### 7. Cognitive Profile must not become workflow configuration

Forbidden canonical interpretation:

```text
Cognitive Profile
  └── Understanding Policy
       └── fixed implementation pipeline / agent graph / prompt chain
```

Required interpretation:

```text
Cognitive Profile
  └── Understanding Policy
       └── desired semantic result + requirements + checks

Understanding Capability
  └── chooses implementation strategy that satisfies the policy
```

Implementation-specific configuration MAY exist below the capability/provider implementation boundary, but it SHALL NOT be confused with the canonical semantic purpose of the Cognitive Profile.

## Why this detail matters

The compressed CU-06 wording — “the same profile may be fulfilled by deterministic processing, classifiers, embeddings, one/multiple LLM calls or verification” — preserved implementation freedom but failed to state **who owns strategy selection**.

Without this recovered detail, a later implementation could incorrectly:

1. encode a fixed prompt/pipeline into Cognitive Profile;
2. make profile authors responsible for provider/orchestration internals;
3. canonicalize today's LLM topology as architecture;
4. duplicate strategy/orchestration responsibility between Profile and Understanding capability;
5. accidentally make Understanding stateful because a multi-step strategy is used.

The approved model avoids these errors by separating:

```text
WHAT must be understood and checked
        = Understanding Policy

HOW this invocation achieves it
        = stateless Understanding capability strategy
```

## Constitutionalization requirement

The final Cognitive Processing / Cognitive Profile constitutional text MUST explicitly state all of the following:

1. Understanding is not bound to canonical single-prompt architecture.
2. Understanding is not bound to canonical multi-agent/pipeline architecture.
3. Understanding Policy declares desired interpretation result, requirements and required checks.
4. Understanding Policy does not prescribe the internal execution topology.
5. Stateless Understanding capability selects a compliant processing strategy.
6. Strategy selection may use deterministic, classifier, embedding, one/multiple LLM, staged, verification, alternate-model or combined approaches.
7. The strategy examples are non-exhaustive implementation options, not canonical taxonomy.
8. Strategy selection does not grant Domain Authority.
9. Strategy selection does not make Understanding a durable state owner.

## Required primary-ledger replacement

The primary ledger's compressed CU-06:

```text
## CU-06 — Profile declares requirements, not LLM workflow — ACCEPTED
The same profile may be fulfilled by deterministic processing, classifiers, embeddings, one/multiple LLM calls or verification.
```

is semantically incomplete and MUST be expanded during the next ledger normalization to include this recovered detail.

## Coverage status

`RECOVERED — MUST BE FOLDED INTO PRIMARY LEDGER AND CONSTITUTIONAL TARGET`

---

# Recovery audit rule for subsequent passes

For every previously approved decision reviewed after this point, compare the original approval against the current ledger at five levels:

```text
1. Concept retained?
2. Responsibility/owner retained?
3. Positive semantics retained?
4. Negative invariants retained?
5. Decision boundary / non-responsibility retained?
```

A decision is not `COVERED` merely because its concept name appears in the ledger.

Example:

```text
"Profile does not prescribe workflow"
```

is NOT losslessly equivalent to:

```text
"Profile declares required interpretation/checks,
while stateless Understanding selects the compliant strategy;
neither single-prompt nor multi-agent/pipeline is canonical."
```

The second contains responsibility and boundary semantics that the first omits.

This five-level test is mandatory for the remaining historical approval sweep.