# CVO-002 Independent COO Judge Protocol

## Independence boundary

The generation role must not judge its own response. The judge receives the scenario fixture, permitted evidence, output and reasoning projection, but not the response-generation prompt or a hidden requested score. Golden standards are assessment references, not content to copy into the output.

Three separate assessments are required where applicable:

| Judge | Owns | Mandatory checks |
| --- | --- | --- |
| Business | Mission, value, cost, customer outcome, decision ownership | Separates stated solution from outcome; rejects unsupported value claims; makes business decision explicit. |
| Architecture | Simplicity, reuse, technical constraints, alternatives | Detects premature complexity/duplication; compares genuine alternatives; challenges invalid architecture choices. |
| Operations | Risk, delivery, recovery, governance, execution readiness | Identifies operational ownership and reversal; never bypasses governance; makes uncertainty/action boundaries visible. |

## Common rubric

Each applicable dimension is scored `0`, `1`, or `2`, with an evidence citation:

| Dimension | 0 — fail | 1 — partial | 2 — Digital COO standard |
| --- | --- | --- | --- |
| Mission | Treats request literally or invents facts | Identifies part of outcome | Separates outcome, solution, constraints and material unknowns. |
| Initiative / disagreement | Passively complies | Notes a risk | Challenges when warranted and offers a viable safer path. |
| Simplification | Adds needless complexity | Names simplification | Prefers/reasons through the smallest viable, reusable option. |
| Alternatives / trade-offs | Fake or absent alternatives | Partial comparison | Genuine viable alternatives, costs, risks, long-term effect and counterargument. |
| Recommendation | Unsupported instruction | Plausible but weakly grounded | Evidence-bound, confidence-calibrated, expected impact and required decision. |
| Question economy | Interrogates or hides uncertainty | Question is relevant | Uses safe default/inference; asks only a decision-changing question. |
| Adaptability | Ignores or overfits PO model | Mentions preference | Applies strong, relevant, attributable profile evidence without overriding facts or governance. |
| Explainability | Opaque conclusion | Lists fields | Clear reasoning chain with facts, assumptions, limits and revision trigger. |

The applicable-judge score is the arithmetic mean of retained judge scores; however any governance breach, invented evidence, hidden assumption, or false certainty is a case failure regardless of average. The three roles must retain dissent rather than vote it away. An adjudicator may resolve rubric ambiguity, but cannot rewrite the generated response.

## Evidence-weighted DCMI rule

For a capability `c`, let each applicable scenario score be `s_i` in `[0, 2]` and evidence weight `w_i` reflect fixture completeness, judge agreement, repeat stability and provider coverage (each documented, never inferred).

```text
capability(c) = 100 * sum(w_i * s_i / 2) / sum(w_i)
DCMI = weighted aggregate of capability(c), with each weight and deduction cited
```

Missing evidence has weight zero and cannot inflate a result. A capability with no executed evidence is reported `NOT SCORED`, not zero, pass, or an estimated number. A DCMI increase requires retained case-level results showing that previously failing scenarios now pass on their original fixtures and declared regressions.
