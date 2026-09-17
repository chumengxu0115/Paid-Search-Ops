# Eight-minute interview walkthrough

## Prepare

Open the local dashboard and this repository. Keep the saved canonical example available so the demo does not depend on a live model response. Use the same browser origin to retain notes. Do not open the self-test URL in your presentation browser profile.

## 0:00–1:00 — Why I built it

“I previously built a keyword-diagnosis workflow from my work on Bubble. For this interview, I adapted those principles into a separate search-term tool and tested it on the supplied Braid exercise. I wanted a repeatable way to connect acquisition efficiency to subscription outcomes, without needing an analyst for every question.”

Show the original repository and its June 22, 2026 history if useful. Explain that the methodology transferred; the implementation was rebuilt for different inputs.

## 1:00–2:30 — Business Insights

Show the distinction between the $181 allowable and the $167.74 observed scope benchmark. The nine-row sample costs $183.11/sub and covers approximately 65% of scope spend; it is not the full account.

Open the use-case/competitor finding: 18.3% of sample spend produces 34.3% of subscriptions at $97.31/sub. Explain that this is a sample-specific pattern, not proof of customer value or a promise of scalable efficiency.

## 2:30–4:00 — One concrete decision

Select free ai app builder. It has $11.06 registrations but $553.13 subscriptions. Compare internal tool builder at $22.29 per registration and $89.14 per subscription.

“Optimizing for cheap registrations could lead me toward the wrong traffic. But the data does not tell me whether free users convert later, whether the product has a free tier, or which activation step is missing.”

Show the missing-information section and conditional action, rather than pretending those questions have been answered.

## 4:00–5:00 — Human judgment

Click Add my input. Optionally enter: “Prioritize a cohort and landing-page review before deciding whether to exclude this intent.” Mark it as operator judgment, not a confirmed product fact.

Show the Scale/Maintain efficiency selector. Explain that it displays already-authored branches, not a live model response.

“My context and decision stay separate from the model's recommendation. Notes save locally and can be exported to Claude Code for a subsequent review. That reanalysis handoff is currently manual.”

Do not perform or claim an untested revision live.

## 5:00–6:00 — Action Plan

Show conditional negatives, isolation/addition candidates and landing-page tests. Point out pending confirmations and unknown campaign scope. The tool proposes actions; it does not execute them.

## 6:00–7:00 — How it was built

Show `src/compute_metrics.py`, one authored review and the canonical artifact. Python computes the metrics; Claude Code authored interpretations; validation links numbers to evidence; the UI reads the saved artifact.

“I used Claude Code to build and run the workflow, then reviewed its output. I corrected real mistakes, including confusing search terms with keywords and overstating what small-sample patterns prove.”

## 7:00–8:00 — Self-sufficiency and next step

Open Data & Run Log. Show a genuine data issue: the supplied paid-total cost/sub is $135.47, while raw totals calculate to about $135.45. Both are retained and the difference is flagged without inventing a cause.

“The tool helps me calculate what is available, identify exactly what is missing, and make the next request specific. If I extended it, I would first add reliable input refresh and a feedback-driven rerun—not automate account changes before the evidence is ready.”

## Likely questions

- **Does this call an LLM from the browser?** No. Claude Code generated the saved analysis; the browser presents it. Reanalysis is a separate Claude Code task.
- **What did you contribute?** The business framework, target/benchmark distinction, scope, data mappings, review and corrections, and operator decisions.
- **Is this real company performance?** No. It is the supplied synthetic interview exercise; the code and runs are real.
- **Will it work on another account?** The method transfers, but schemas, event meanings, targets and reconciliation checks must be configured and the model reasoning regenerated.
- **Has it improved performance?** No account changes were made, so there is no lift claim.
