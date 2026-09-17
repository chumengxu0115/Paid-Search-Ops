# Braid Search Ops: search-term diagnosis (v1, model-authored)

Posture selected: **none** (not chosen by operator; both options shown per term). Allowable: **$181/sub** (candidate brief (Task 1); applies to Non-Brand search terms). Benchmark: **$167.74/sub** (descriptive benchmark of the scope the terms belong to; not a business target).

Legend: **fact** = supplied data/confirmed context; **hypothesis** = model interpretation; **to confirm** = needs product/data/operator input. All figures come from `output/step1/`.

## Account context (editable: `config/account_context.json`)

| Field | Value | Status |
|---|---|---|
| target_customer | — | unknown |
| product_category | ai app builder (from the scope label) | confirmed |
| subscription_model | — | unknown |
| free_to_paid_path | — | unknown |
| enterprise_offering | — | unknown |
| developer_integrations | — | unknown |
| no_code_positioning | — | unknown |
| customer_value | — | unknown |
| conversion_cycle | — | unknown |
| main_competitor | Scaffold | confirmed |
| strategic_posture | — | not_selected_by_operator |

## Scope levels (fact)

| Level | Spend | Subs | Cost/sub (recomputed) |
|---|---|---|---|
| Google Non-Brand (Q2 label; period alignment unverified) | $701,000 | 4348 | $161.22 |
| Scope: Non-Brand ai app builder | $520,000 | 3100 | $167.74 |
| Nine-term sample (64.9% of scope spend; reported ~65.0%) | $337,470 | 1843 | $183.11 |
| Remainder (subtraction within scope; no terms known) | $182,530 | 1257 | $145.21 |

## Channel context (descriptive, from `metrics_channels.csv`)

- Google Non-Brand is the largest channel (43.2% of paid spend) at $161.22/sub, below its $181 allowable, and up from supplied Q1 $147.50. Q1 cannot be recomputed.
- Google Performance Max ($287.80/sub vs $181 allowable) and Meta prospecting ($198.90/sub vs $142) are the channels above allowable. Reddit is slightly above ($158). These are descriptive comparisons; causes are not established here.
- Paid total supplied cost/sub ($135.47) differs from the recomputed $135.45; cause unknown, both retained.
- TikTok has no allowable; no gap is computed.

## Terms, sorted by spend

### 1. ai app builder  (`st_dd3412fed286`, Phrase match)

**Evidence (fact).** Largest term: 30.2% of sample spend and 37.4% of sample subs. Cost/sub $147.83 is 0.82x of the $181 allowable and 0.88x of the scope benchmark ($167.74). Signup rate 14.0%, signup->sub 14.5%. Phrase match on the core category term.

| Clicks | Cost | Signups | Subs | CPC | Cost/signup | Signup/click | Sub/signup | Cost/sub | vs $181 | vs benchmark |
|---|---|---|---|---|---|---|---|---|---|---|
| 34,000 | $102,000.00 | 4,760 | 690 | $3.00 | $21.43 | 14.0% | 14.5% | $147.83 | 0.82x (below) | 0.88x (below) |

**Intent (hypothesis, high confidence).** Core category intent: user wants a tool that builds AI apps. Closest match to the scope label itself.

**Missing information (to confirm).**
- existing keyword and match type this term is served by — limits: whether it is already the head keyword or a broad-match spillover; bid/isolation decisions
- impression share / lost IS — limits: whether there is headroom to scale on this term at all
- conversion lag — limits: whether 690 subs are mature for the same-period 4,760 signups

**If posture = scale.** Primary expansion candidate: below allowable with the most volume. Confirm headroom (impression share) before raising bids or budget; adding spend without headroom would not add subs.

**If posture = maintain efficiency.** Keep as is. It anchors the sample below the benchmark; no change unless a cohort-aligned cost/sub comes in above $181.

**Investigate now (either posture).**
- Pull impression share and top-of-page rate for the matching keyword(s).
- Confirm which keyword/ad group serves this phrase-match term.

### 2. free ai app builder  (`st_7397eeb3716a`, Phrase match)

**Evidence (fact).** Second-largest spend (18.4% of sample). Highest signup count in the sample (5,600, 19.0% of clicks) and cheapest signups ($11.06), but signup->sub is 2.0%, so cost/sub is $553.13: 3.06x of allowable and 3.30x of the benchmark. Removing it arithmetically leaves the rest of the sample at $159.17/sub (arithmetic, not a forecast).

| Clicks | Cost | Signups | Subs | CPC | Cost/signup | Signup/click | Sub/signup | Cost/sub | vs $181 | vs benchmark |
|---|---|---|---|---|---|---|---|---|---|---|
| 29,500 | $61,950.00 | 5,600 | 112 | $2.10 | $11.06 | 19.0% | 2.0% | $553.13 | 3.06x (above) | 3.30x (above) |

**Intent (hypothesis, medium confidence).** Price-sensitive or exploratory intent: wants to try without paying. Whether that is on-path depends entirely on whether Braid has a free tier and how long free->paid takes.

**Missing information (to confirm).**
- does Braid have a free tier, and what is the free->paid conversion window — limits: whether the 112 subs are immature (lag) or the intent is genuinely low-value; the whole negative-vs-keep decision
- FFT or activation events for these signups — limits: whether the 5,600 signups show product usage or are dead accounts
- landing page shown — limits: whether the 'free' promise on the SERP is matched or contradicted post-click

**If posture = scale.** Do not scale on cost/sub; the signup volume is attractive only if a bidding signal (FFT/activation) confirms these signups progress. Candidate to isolate into its own ad group with a free-tier landing page and a lower bid so it stops sharing budget with the core term.

**If posture = maintain efficiency.** Conditional negative on 'free' (phrase) if the product has no free tier or the free cohort does not convert after the lag window. If a free tier exists, isolate and cap rather than negate: this term produces the most signups in the sample.

**Investigate now (either posture).**
- Ask product: free tier yes/no, and the median days from free signup to paid.
- Pull cohort-aligned subs for these signups (60/90-day) instead of same-window subs.
- Check the landing page for this term against the 'free' promise.

### 3. how to build an ai app  (`st_2fe617db21cf`, Broad match)

**Evidence (fact).** 15.6% of sample spend, cost/sub $251.43: 1.39x of allowable and 1.50x of the benchmark. Cheap clicks ($2.40) and a 13.0% signup rate, but signup->sub only 7.3%.

| Clicks | Cost | Signups | Subs | CPC | Cost/signup | Signup/click | Sub/signup | Cost/sub | vs $181 | vs benchmark |
|---|---|---|---|---|---|---|---|---|---|---|
| 22,000 | $52,800.00 | 2,860 | 210 | $2.40 | $18.46 | 13.0% | 7.3% | $251.43 | 1.39x (above) | 1.50x (above) |

**Intent (hypothesis, medium confidence).** Informational / learning intent; a share of searchers are looking for a tutorial rather than a product. Broad match may also be pulling adjacent 'how to' queries not visible here.

**Missing information (to confirm).**
- the actual queries grouped under this broad-match term and the matched keyword — limits: whether this is one intent or a mixed bucket; negative scoping
- landing page for informational queries — limits: whether a tutorial/template page could lift signup->sub
- conversion lag — limits: informational visitors may convert later; same-window subs may understate

**If posture = scale.** Not a scaling candidate at $251.43. Test a how-to/template landing page first; if signup->sub moves toward the sample average, revisit.

**If posture = maintain efficiency.** Bid down or move to a separate ad group with its own budget. A 'how to' phrase negative in the core ad group is conditional on confirming the queries are mostly tutorial-seeking.

**Investigate now (either posture).**
- Export the search-term report for the matching keyword to see the query mix.
- Run a landing-page test: template/tutorial page vs current page, measured on signup->sub.

### 4. build app without code  (`st_98934dc150fb`, Broad match)

**Evidence (fact).** Cost/sub $107.19 (0.59x of allowable, 0.64x of benchmark) with the second-highest sub count (320, 17.4% of sample subs). Signup->sub 20.4% is above the sample's larger terms.

| Clicks | Cost | Signups | Subs | CPC | Cost/signup | Signup/click | Sub/signup | Cost/sub | vs $181 | vs benchmark |
|---|---|---|---|---|---|---|---|---|---|---|
| 9,800 | $34,300.00 | 1,570 | 320 | $3.50 | $21.85 | 16.0% | 20.4% | $107.19 | 0.59x (below) | 0.64x (below) |

**Intent (hypothesis, medium confidence).** No-code builder intent. Efficient here, but whether Braid positions itself as no-code is unknown; if not, this may be an adjacent audience converting on a different promise.

**Missing information (to confirm).**
- no-code positioning and whether a no-code keyword/ad group already exists — limits: add vs already-covered; landing-page choice
- impression share — limits: scaling headroom

**If posture = scale.** Expansion candidate: check existing coverage, then consider a dedicated no-code ad group and landing page to protect the 20.4% signup->sub rate while adding volume.

**If posture = maintain efficiency.** Keep; consider isolating so its efficiency is not diluted by broad-match neighbours.

**Investigate now (either posture).**
- Check the existing keyword list for 'no code' / 'without code' variants before adding anything.
- Confirm product positioning on no-code with product/marketing.

### 5. vibe coding app builder  (`st_a3029027e1c6`, Broad match)

**Evidence (fact).** Cost/sub $163.81: 0.91x of allowable (below it) but 0.98x of the benchmark (close to it). 8.2% of sample spend, signup->sub 15.0%.

| Clicks | Cost | Signups | Subs | CPC | Cost/signup | Signup/click | Sub/signup | Cost/sub | vs $181 | vs benchmark |
|---|---|---|---|---|---|---|---|---|---|---|
| 8,600 | $27,520.00 | 1,120 | 168 | $3.20 | $24.57 | 13.0% | 15.0% | $163.81 | 0.91x (below) | 0.98x (below) |

**Intent (hypothesis, medium confidence).** Trend-driven intent ('vibe coding') for an AI-assisted builder. Likely aligned with the product category, but the phrase is new and its searcher mix may shift quickly.

**Missing information (to confirm).**
- whether Braid's messaging uses or fits 'vibe coding' — limits: landing-page/ad-copy alignment
- trend stability (search volume over time) — limits: whether to invest in a dedicated keyword

**If posture = scale.** Secondary expansion candidate, below allowable. Isolate with matching ad copy before adding budget so that efficiency can be observed separately.

**If posture = maintain efficiency.** Hold. It is within allowable; monitor since it sits near the benchmark.

**Investigate now (either posture).**
- Check existing keyword coverage for 'vibe coding'.
- Confirm messaging fit with marketing.

### 6. enterprise app development platform  (`st_6de9a251f911`, Broad match)

**Evidence (fact).** Highest cost/sub in the sample: $1,400.00, 7.73x of allowable. Most expensive clicks ($8.00) and signups ($80.00); only 12 subs from 210 signups (5.7%). 5.0% of sample spend. Small counts: no operator data-sufficiency threshold has been set, so 'low data' is a judgement, not a rule.

| Clicks | Cost | Signups | Subs | CPC | Cost/signup | Signup/click | Sub/signup | Cost/sub | vs $181 | vs benchmark |
|---|---|---|---|---|---|---|---|---|---|---|
| 2,100 | $16,800.00 | 210 | 12 | $8.00 | $80.00 | 10.0% | 5.7% | $1,400.00 | 7.73x (above) | 8.35x (above) |

**Intent (hypothesis, low confidence).** Enterprise buyer / evaluator intent. If Braid sells to enterprises via sales, these visitors would appear as leads, not self-serve subs, and cost/sub would not be the right KPI for this term. If Braid has no enterprise motion, the term is off-target.

**Missing information (to confirm).**
- enterprise offering and sales-assisted path (demo requests, SQLs) — limits: the entire keep/negative decision; whether Subs is even the right KPI
- operator min_cost / min_subs thresholds — limits: whether 12 subs is enough evidence to act on
- CPC driver (competition on 'enterprise') — limits: whether the high CPC is avoidable

**If posture = scale.** Not scaled on cost/sub. If an enterprise motion exists, route to a demo/contact landing page and judge on leads; otherwise exclude.

**If posture = maintain efficiency.** Conditional negative on 'enterprise' (phrase) if there is no enterprise offering or sales path. If there is one, move the term to a separate ad group with enterprise-specific measurement instead of negating.

**Investigate now (either posture).**
- Ask sales/product: is there an enterprise plan or sales-assisted path, and are demo requests tracked?
- Check whether any of these 210 signups became sales leads.

### 7. internal tool builder  (`st_a9cf56135541`, Broad match)

**Evidence (fact).** Second-lowest cost/sub in the sample: $89.14 (0.49x of allowable). Second-highest signup->sub in the sample (25.0%) and 175 subs on 4.6% of spend.

| Clicks | Cost | Signups | Subs | CPC | Cost/signup | Signup/click | Sub/signup | Cost/sub | vs $181 | vs benchmark |
|---|---|---|---|---|---|---|---|---|---|---|
| 3,900 | $15,600.00 | 700 | 175 | $4.00 | $22.29 | 17.9% | 25.0% | $89.14 | 0.49x (below) | 0.53x (below) |

**Intent (hypothesis, medium confidence).** Use-case intent: build internal business tools. Converts well, which suggests the product serves this use case, but that is inferred from the data, not confirmed by product.

**Missing information (to confirm).**
- whether internal tools is a supported/promoted use case — limits: landing-page and ad-copy investment
- existing keyword coverage — limits: add vs already covered

**If posture = scale.** Expansion candidate: confirm coverage, then dedicated ad group + use-case landing page.

**If posture = maintain efficiency.** Keep; isolate to protect efficiency.

**Investigate now (either posture).**
- Check keyword list and landing pages for an internal-tools use case.
- Confirm with product whether internal tools is a target use case.

### 8. ai app builder github  (`st_429e31f7f0f8`, Broad match)

**Evidence (fact).** Cost/sub $822.22: 4.54x of allowable. Cheapest clicks in the sample ($2.00) and a normal signup rate (12.0%), but signup->sub is only 2.0% (18 subs from 890 signups). 4.4% of sample spend.

| Clicks | Cost | Signups | Subs | CPC | Cost/signup | Signup/click | Sub/signup | Cost/sub | vs $181 | vs benchmark |
|---|---|---|---|---|---|---|---|---|---|---|
| 7,400 | $14,800.00 | 890 | 18 | $2.00 | $16.63 | 12.0% | 2.0% | $822.22 | 4.54x (above) | 4.90x (above) |

**Intent (hypothesis, medium confidence).** Developer intent: looking for an open-source repo, a GitHub-integrated builder, or code export. If Braid has no GitHub integration or does not target developers, this is off-target; if it does, the landing page may be failing this audience.

**Missing information (to confirm).**
- GitHub integration / code export / developer targeting — limits: negative vs landing-page fix
- landing page shown to this query — limits: whether developers see anything GitHub-related

**If posture = scale.** Not scaled. If developers are a target, test a developer/GitHub landing page before deciding.

**If posture = maintain efficiency.** Conditional negative on 'github' (phrase) if there is no GitHub-related feature or developer targeting. If there is, fix the landing page first and re-measure.

**Investigate now (either posture).**
- Ask product: GitHub integration or code export, yes/no.
- Check what the ad and landing page promise for this query.

### 9. scaffold alternative  (`st_66770c31f114`, Broad match)

**Evidence (fact).** Lowest cost/sub in the sample: $84.78 (0.47x of allowable, 0.51x of benchmark). Highest signup rate (20.0%) and highest signup->sub (26.5%). Small spend (3.5% of sample) at a $4.50 CPC.

| Clicks | Cost | Signups | Subs | CPC | Cost/signup | Signup/click | Sub/signup | Cost/sub | vs $181 | vs benchmark |
|---|---|---|---|---|---|---|---|---|---|---|
| 2,600 | $11,700.00 | 520 | 138 | $4.50 | $22.50 | 20.0% | 26.5% | $84.78 | 0.47x (below) | 0.51x (below) |

**Intent (hypothesis, high confidence).** Competitor-switching intent: Scaffold is the confirmed main competitor, so these are evaluators comparing alternatives. High readiness to buy is consistent with the ratios.

**Missing information (to confirm).**
- existing competitor keywords / campaign — limits: whether this is already targeted or is broad-match spillover
- impression share on competitor queries — limits: scaling headroom
- trademark/policy constraints on competitor ad copy — limits: ad copy for a dedicated ad group

**If posture = scale.** Clear expansion candidate: check coverage, then a dedicated competitor ad group with a comparison landing page and its own budget.

**If posture = maintain efficiency.** Keep and isolate; still worth a dedicated ad group so the efficient volume is protected.

**Investigate now (either posture).**
- Check whether a competitor campaign or 'scaffold' keywords already exist.
- Pull impression share for competitor queries.

## Summary

### Conditional negative candidates

| Term | Proposed negative | Match type | Condition | Scope |
|---|---|---|---|---|
| free ai app builder | free | phrase | only if product confirms no free tier OR cohort-aligned free->paid conversion stays near the same-window rate after the lag window; otherwise isolate, do not negate | campaign/ad-group IDs unknown; not import-ready |
| ai app builder github | github | phrase | only if product confirms no GitHub integration/code export and developers are not a target; otherwise fix landing page first | campaign/ad-group IDs unknown; not import-ready |
| enterprise app development platform | enterprise | phrase | only if there is no enterprise offering or sales-assisted path; if there is, Subs is the wrong KPI and the term should be measured on leads instead | campaign/ad-group IDs unknown; small counts, no data-sufficiency threshold set |
| how to build an ai app | how to | phrase | only under maintain_efficiency and only after the query mix confirms mostly tutorial-seeking; a landing-page test is the preferred first step | would apply to the core ad group only; IDs unknown |

### Addition / isolation candidates and landing-page tests

| Term | Action | Landing-page test | Check before adding |
|---|---|---|---|
| scaffold alternative | isolate into a competitor ad group | comparison page vs current | existing competitor keywords/campaign |
| internal tool builder | isolate into a use-case ad group | internal-tools use-case page vs current | existing keyword coverage; product confirms use case |
| build app without code | isolate into a no-code ad group | no-code page vs current | existing 'no code' keywords; positioning |
| vibe coding app builder | isolate with matching ad copy | vibe-coding messaging vs current | existing coverage; messaging fit |
| free ai app builder | isolate with free-tier landing page and capped bid (if free tier exists) | free-tier page vs current, measured on cohort-aligned subs | free tier exists |
| how to build an ai app | separate ad group for informational queries | tutorial/template page vs current | query mix from search-term report |

### Least certain term: free ai app builder

It is 18.4% of sample spend, produces the most signups, and its decision flips entirely on one product fact. Every other high cost/sub term has a smaller spend footprint.

**The one piece of information that would change the decision:** Whether Braid has a free tier and, if so, the cohort-aligned free->paid conversion after the lag window. If free signups convert later at a rate that brings cost/sub under $181, the term is an isolation candidate; if not, it is the largest negative candidate.

### Questions for product / data / operator

| To | Question | Unblocks |
|---|---|---|
| product | Is there a free tier? What is the median and 90-day free->paid conversion? | free ai app builder decision |
| product | Is there a GitHub integration, code export, or developer audience? | ai app builder github decision |
| sales/product | Is there an enterprise plan or sales-assisted path, and are demo requests tracked as conversions? | enterprise app development platform decision and KPI choice |
| product/marketing | Are no-code, internal tools and vibe coding positioning the product supports? | isolation and landing-page choices for three efficient terms |
| data | What are the exact dates, attribution model, and lag between Regs and Subs? Are Subs cohort-aligned to Regs in the same window? | whether signup->sub ratios are comparable across terms |
| data | Is there an FFT/activation event available per search term? | the inherited bidding-signal method |
| data/finance | Customer value or margin behind the $181 allowable, and whether it differs by plan? | whether $181 is right for enterprise or free-tier intents |
| account owner | Existing keyword list, match types, campaign/ad-group structure and IDs; impression share by keyword | add-vs-covered decisions, negative scoping, and any Editor file |
| operator | min_cost / min_subs data-sufficiency thresholds | whether 12-sub terms are actionable |

### Other hypotheses and tests

- **Hypothesis:** The sample cost/sub ($183.11) is above the scope benchmark ($167.74); by subtraction the unseen ~35% of scope spend runs at $145.21. The nine rows may be the harder part of the scope, not representative of it. **Test:** Request the full search-term report for the scope.
- **Hypothesis:** Three low-converting terms (free / github / enterprise) share a pattern: normal or high signup rate, very low signup->sub. That is consistent with either intent mismatch or post-click mismatch; the data cannot separate the two. **Test:** Landing-page audit per term before any negative.
- **Hypothesis:** Broad match may be grouping several intents under one row (e.g. 'how to build an ai app'). **Test:** Search-term report by keyword.
- **Hypothesis:** Non-Brand Q2 cost/sub ($161.22) rose versus supplied Q1 ($147.50); the scope's contribution to that change cannot be isolated without period alignment. **Test:** Confirm the scope period equals Q2 and get Q1 scope figures.

### Notes

- No forced negative quota; every negative is conditional on a product or data fact listed with it.
- Existing keywords and account structure are unknown: every addition/isolation requires a coverage check first.
- Campaign/ad-group IDs are unknown: nothing here is an import-ready file.

## Step 1 missing-data register (carried forward)

- `exact_dates_and_year` (missing) — limits: confirming that the sample, the scope and the Non-Brand Q2 row cover the same period; any seasonality reading
- `fft` (unavailable_not_zero) — limits: applying the inherited FFT bidding-signal method; signup->FFT->paid stage diagnosis
- `conversion_maturity_and_lag` (missing) — limits: whether paid_sub_per_signup ratios are comparable across terms; cohort alignment of Subs to the same-period Regs
- `attribution_definition` (missing) — limits: comparing channel cost/sub across channels and to allowables; whether Regs/Subs are last-click or otherwise
- `customer_value_ltv_or_margin` (missing) — limits: judging whether $181 allowable is appropriate per term; any payback interpretation
- `landing_page_and_product_context` (missing) — limits: intent hypotheses for 'free', 'github', 'enterprise', 'internal tool' terms; post-click tests
- `existing_keywords_and_account_structure` (missing) — limits: deciding whether a term is already covered, should be isolated, or added; match-type interpretation
- `campaign_and_ad_group_ids` (missing) — limits: any Editor-importable negative or keyword file; scoping negatives
- `impressions` (missing) — limits: CTR and impression share; cannot be computed from the supplied columns
- `q1_raw_spend_and_subs` (missing) — limits: verifying q1_cost_per_sub; QoQ change uses supplied Q1 as-is
- `tiktok_allowable_cost_per_sub` (unavailable_not_zero) — limits: TikTok gap-to-allowable and ratio
- `remaining_scope_search_terms` (missing) — limits: the ~35% of scope spend outside the sample is only a subtraction; no term-level view of it
- `paid_total_supplied_cost_per_sub_basis` (unexplained) — limits: which figure (supplied 135.47 or recomputed) to cite for the account; cause not assumed
- `operator_thresholds_min_cost_min_subs` (unset) — limits: data-sufficiency tiering; deferred to operator configuration
