# Eight-minute walkthrough

## Before you start

- From `search-term-diagnosis/`, run `python3 -m http.server 8781 --bind 127.0.0.1` and open <http://127.0.0.1:8781/ui/>.
- The demo reads the saved canonical artifact; nothing depends on a live model response.
- Use one browser profile so notes persist. Do not open `?selftest=1` in that profile.

## 0:00–1:00 · Why I built it

"At Bubble I built a keyword-diagnosis workflow. For this exercise I carried the principles over to a separate search-term tool and ran it on the supplied Braid data: connect acquisition cost to subscriptions, show exactly what is missing, and keep the decision with the operator."

If asked, show the sibling `keyword-diagnosis/` module (its commits are dated June 22, 2026). The method transferred; the implementation was rebuilt for different inputs.

## 1:00–2:30 · Business Insights

- Four cards: total paid (aggregate), all Google Non-Brand, the "ai app builder" scope, the nine-term sample. The sample runs at **$183.11/sub** and covers **64.9%** of scope spend; it is not the account.
- **$181** is the allowable from the brief; **$167.74** is what the scope actually ran at. Different things.
- Expand P4: no-code, internal tools and "scaffold alternative" take **18.3%** of sample spend and deliver **34.3%** of subscriptions at **$97.31/sub**. Say plainly that this is a sample-specific pattern with counterexamples (vibe coding, enterprise), not proof of customer value or of efficiency at scale.

## 2:30–4:00 · One concrete decision

Click **Review terms & add your input →**, then select **free ai app builder**: the cheapest registrations in the sample (**$11.06** each) and **$553.13** per subscription. Compare **internal tool builder**: **$22.29** per registration, **$89.14** per subscription.

"If I optimised for cheap registrations I would buy the wrong traffic. But the data cannot tell me whether free users convert later, whether there is a free tier, or whether the landing page is the problem."

Show the missing-information list (each item says what it would change) and the conditional recommendation. Do not pretend the product questions are answered.

## 4:00–5:00 · Human judgment

Click **Add my input**. Optionally add a note such as "Cohort and landing-page review before any exclusion of this intent" and leave it marked **Unverified assumption**; switch to **Confirmed fact** only for something the product team actually confirmed.

Go back to Business Insights and switch the posture selector. "It shows the branch that was already written for that posture. It does not call a model and it does not change the allowable."

"My notes stay separate from the model's recommendation, save on this browser only, and export as a feedback file for a later Claude Code review. That reanalysis is a manual handoff." Do not perform or claim a live revision.

## 5:00–6:00 · Action Plan

Conditional negatives are **pending confirmation** with the fact that would make them actionable; additions have pre-checks because existing keywords and structure are unknown; landing-page tests are proposals. The "Operator decision" column shows the human decision from Search Terms and is never marked executed.

## 6:00–7:00 · How it was built

Open `src/compute_metrics.py`, `authoring/review_v2_2.json` and `output/canonical/search_ops_analysis.json`. Python computes and validates; Claude Code authored the interpretation with numeric placeholders that a build step fills and checks; the dashboard reads the saved artifact.

"I built and ran the workflow with Claude Code and reviewed its output. I corrected real mistakes along the way, for example treating search terms as keywords, reading rank correlations between coupled metrics as evidence, and overstating what a nine-row pattern proves. The change logs are in the repo."

## 7:00–8:00 · Self-sufficiency and next step

Open Data & Run Log. Point at a genuine data issue: supplied paid-total cost/sub is **$135.47**, the raw totals give **$135.45**; both are kept and flagged, no cause invented.

"The tool lets me compute what is available, name what is missing, and make the next request specific. The next step would be a reliable input refresh and a feedback-driven rerun, not automating account changes before the evidence is there."

## Likely questions

- **Does the browser call an LLM?** No. Claude Code produced the saved analysis; the page renders it. Reanalysis is a separate Claude Code task.
- **What did you contribute?** The business framework, the target/benchmark distinction, scope and event mappings, the review and corrections of each version, and the decisions.
- **Is this real performance?** No; synthetic interview data. The code, runs and tests are real.
- **Would it work on another account?** The method transfers; schemas, event definitions, targets and reconciliation checks must be configured and the reasoning re-authored.
- **Did it improve anything?** No account was changed, so there is no lift to claim.
