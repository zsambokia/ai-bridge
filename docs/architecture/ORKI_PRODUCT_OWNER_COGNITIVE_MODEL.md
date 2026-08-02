# Orki Product Owner Cognitive Model

**Status:** Canonical architecture; ORKI-008 foundation and ORKI-009 evolution contract.
**Authority:** Product Owner strategic directive, 2026-08-02.

## Purpose

Orki must understand not only the mission and project, but also the Product
Owner's evidence-backed operational working patterns. This enables adaptive
Digital COO behaviour: the same business request can receive a different safe
default when a different, reviewable owner working model justifies it.

This is **not** personalisation, a personality model, surveillance, or a
conversation transcript. It is an operational working relationship model.

## Four coordinated cognitive models

| Model | Answers | Scope | Authority |
| --- | --- | --- | --- |
| Mission Model | What outcome is sought? | Project | Cognitive State; Product Owner corrects business meaning. |
| Project Model | What is true now about delivery, architecture, risk and constraints? | Project | Cognitive State and canonical project evidence. |
| Product Owner Model | How does the owner normally make and review operational decisions? | Owner profile plus explicit project-aware context | Cognitive State evidence; Product Owner corrects. |
| Factory Model | What AI Bridge capabilities, components and proven lessons are available? | AI Bridge, governed and explicitly referenced | Canonical Factory architecture and AKB. |

The models cooperate but are not merged. A Project Model cannot silently
rewrite an owner pattern, and an owner pattern cannot override project facts,
governance, material uncertainty, or a required Product Owner decision.

## Permitted profile dimensions

The bounded profile may contain only operational collaboration patterns:

- decision style and risk tolerance;
- planning and documentation depth;
- preferred Sprint size;
- architecture and technology preferences;
- governance and evidence expectations; and
- communication style relevant to an operational recommendation.

It must not retain special-category, personal, demographic, health, political,
financial, credential, or raw conversation information. A preference is never
treated as a business fact or as authority to bypass governance.

## State and provenance contract

Each profile observation is a revisioned Cognitive State artefact with a stable
identity, allowed profile dimension, scope, evidence references, rationale,
confidence, status, timestamps and correction/supersession trail. The artefact
references attributed state evidence only; it never copies the transcript.

There are two scopes:

1. **Owner baseline:** a portable working pattern only when its source evidence
   is explicitly marked reusable and the projection is authorized by policy.
2. **Project-aware context:** a project-isolated pattern or override. It is the
   default scope and never appears in another project merely because the owner
   is the same.

No profile is created from a single unsupported model assertion. A missing
evidence reference, an unsupported scope transfer, or conflicting active
evidence must yield no active inference (or an explicit conflict), never a
hidden preference.

## Adaptive behaviour boundary

An active profile may help Orki choose a reversible default, depth of an
explanation, or a proposed Sprint decomposition. Orki must disclose when that
profile influenced a recommendation, identify its evidence and confidence, and
show what correction would change the result.

It must not change a Product Owner decision, create governance/execution
authority, suppress a material question, or override Mission, project evidence,
legal/privacy policy, or an explicit current instruction.

## Review and correction

The Product Owner can inspect a bounded projection of every active pattern,
its evidence, confidence, scope and revision history; correct, reject or
supersede it; and see the changed adaptive result. Corrections are additive and
attributable. They never erase prior evidence or silently alter another
project's state.

## Confidence, history and cognitive drift (ORKI-009)

Every profile revision carries a declared confidence and the confidence of its
referenced Cognitive State evidence. The canonical projection exposes the
result and its deterministic weighting: 60% declared confidence and 40% mean
evidence confidence. If referenced evidence has no numeric confidence, the
projection explicitly reports it as unscored and relies solely on the declared
confidence; it never invents a score. This is a review aid, not a claim of
objective truth; the Product Owner can inspect the inputs and correct the
profile.

The model retains chronological revisions for each dimension. When a later,
evidence-backed preference differs from its prior revision, the projection
emits a **cognitive drift** record with both states, their evidence references,
confidence explanations, statuses and timestamps. It never overwrites or
silently recasts the earlier working pattern. A correction remains separately
attributable as a Product Owner correction.

The projection exposes only Cognitive State identifiers, allowed attributes,
confidence and message identifiers for provenance. It never includes raw
conversation text or converts a preference into decision, recommendation,
planning, governance or execution authority.

## Release-gate evidence

ORKI-008 and ORKI-009 must independently prove the applicable items below:

1. Ten attributed, non-transcript Cognitive State interactions can produce a
   bounded profile projection with no unsupported dimensions.
2. The Product Owner can inspect, correct and supersede a profile observation;
   the resulting projection and adaptive recommendation change explainably.
3. Equivalent requests adapt only when the relevant active profile evidence
   justifies it; without such evidence, Orki uses a neutral safe default.
4. Project-aware observations remain isolated. Owner-baseline reuse requires
   explicit portable evidence and never exposes project facts.
5. Conflicting evidence is visible and prevents a false high-confidence
   conclusion.
6. No scenario uses raw conversation history as memory or creates a plan,
   decision acceptance, governance action, delivery work or execution.
7. A profile's confidence evolution, evidence weighting, revision history and
   evidence-backed drift are independently executable and explainable.

Only independently rerun final-state scenarios and retained evidence may award
the Product Owner Understanding DCMI score.
