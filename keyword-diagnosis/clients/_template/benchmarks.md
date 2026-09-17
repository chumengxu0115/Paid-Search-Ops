# Benchmarks — [ACCOUNT NAME]

> These calibrate the criteria. `recommend-criteria.md` reads this file to set thresholds; the diagnosis uses them as "normal" reference lines. Fill what you have; mark the rest `[VERIFY]`.

## Search-only CTR baseline
- **Search (Keyword) campaigns CTR, account blended:** [...]%
  > Use Search-only — don't average in PMax/Display/Video impressions, which crush the number.
- **By campaign type:** brand [...]% · non-brand [...]% · competitor [...]%
- **By geo (if it varies materially):** [...]

## Per-keyword spend distribution (trailing 30 days)
The shape of this distribution sets `spend_min_30d` and `dormant_definition`.
- **Median 30d cost per enabled keyword:** [...]
- **p75:** [...]   **p90:** [...]   **p95:** [...]
- **How many keywords clear $X/30d** (pick a few X relevant to your scale): [...]

## Per-funnel-stage conversion rates (account blended)
| Transition | CR |
|---|---|
| Click → [step 1] | [...]% |
| [step 1] → [step 2] | [...]% |
| ... → ... | [...]% |
| [penultimate] → [KPI] | [...]% |

## Per-audience bidding-signal → KPI CR
| Audience / segment | bidding-signal → KPI CR |
|---|---|
| [...] | [...]% |

## Per-geo CTR + CPA bands
| Geo | CTR band | Target CPA (bidding signal) | Target CPA (KPI) | Notes |
|---|---|---|---|---|
| [...] | [...]% | [...] | [...] | [...] |

## Quality Score distribution (Search keywords, by spend)
- **% of QS-tagged spend at QS ≤ 4:** [...]%
- **% at QS 5–6:** [...]%
- **% at QS ≥ 7:** [...]%

## Anything else that defines "normal" for this account
- [Seasonality, typical IS Lost ranges, typical PMax share of conversions, etc.]
