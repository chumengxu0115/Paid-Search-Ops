# Braid Search Ops: evidence-led review v2 (independent of v1)

Inputs: the two supplied datasets (via `output/step1/`), confirmed account context, methodology priors. No operator interview answers were used. v1 is preserved unchanged as the baseline. Posture: **not selected**. All figures are filled from step 1 by `src/build_review_v2.py`.

## Observed performance (fact), sorted by spend

| # | Term | Match | Cost | Signups | Subs | CPC | Cost/signup | Signup/click | Sub/signup | Cost/sub | vs $181 | Subs needed at $181 | Sub rate needed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ai app builder | Phrase | $102,000.00 | 4,760 | 690 | $3.00 | $21.43 | 14.0% | 14.5% | $147.83 | 0.82x | 564 | 11.8% |
| 2 | free ai app builder | Phrase | $61,950.00 | 5,600 | 112 | $2.10 | $11.06 | 19.0% | 2.0% | $553.13 | 3.06x | 343 | 6.1% |
| 3 | how to build an ai app | Broad | $52,800.00 | 2,860 | 210 | $2.40 | $18.46 | 13.0% | 7.3% | $251.43 | 1.39x | 292 | 10.2% |
| 4 | build app without code | Broad | $34,300.00 | 1,570 | 320 | $3.50 | $21.85 | 16.0% | 20.4% | $107.19 | 0.59x | 190 | 12.1% |
| 5 | vibe coding app builder | Broad | $27,520.00 | 1,120 | 168 | $3.20 | $24.57 | 13.0% | 15.0% | $163.81 | 0.91x | 153 | 13.7% |
| 6 | enterprise app development platform | Broad | $16,800.00 | 210 | 12 | $8.00 | $80.00 | 10.0% | 5.7% | $1,400.00 | 7.73x | 93 | 44.3% |
| 7 | internal tool builder | Broad | $15,600.00 | 700 | 175 | $4.00 | $22.29 | 17.9% | 25.0% | $89.14 | 0.49x | 87 | 12.4% |
| 8 | ai app builder github | Broad | $14,800.00 | 890 | 18 | $2.00 | $16.63 | 12.0% | 2.0% | $822.22 | 4.54x | 82 | 9.2% |
| 9 | scaffold alternative | Broad | $11,700.00 | 520 | 138 | $4.50 | $22.50 | 20.0% | 26.5% | $84.78 | 0.47x | 65 | 12.5% |

'Subs needed at $181' = ceil(cost / 181); 'sub rate needed' = that / signups. Arithmetic at current cost, not a forecast.

## Groups (arithmetic over sample rows)

| Group | Terms | Cost | Subs | Cost/sub | Sub/signup | Share of sample cost | Share of sample subs |
|---|---|---|---|---|---|---|---|
| below_allowable | ai app builder; build app without code; vibe coding app builder; internal tool builder; scaffold alternative | $191,120.00 | 1,491 | $128.18 | 17.2% | 56.6% | 80.9% |
| above_allowable | free ai app builder; how to build an ai app; ai app builder github; enterprise app development platform | $146,350.00 | 352 | $415.77 | 3.7% | 43.4% | 19.1% |
| head_plus_modifier | ai app builder; free ai app builder; ai app builder github | $178,750.00 | 820 | $217.99 | 7.3% | 53.0% | 44.5% |
| use_case_or_competitor | build app without code; internal tool builder; scaffold alternative | $61,600.00 | 633 | $97.31 | 22.7% | 18.3% | 34.3% |
| cheapest_three_cpc | ai app builder github; free ai app builder; how to build an ai app | $129,550.00 | 340 | $381.03 | 3.6% | 38.4% | 18.4% |
| top_three_spend | ai app builder; free ai app builder; how to build an ai app | $216,750.00 | 1,012 | $214.18 | 7.7% | 64.2% | 54.9% |
| phrase_rows | ai app builder; free ai app builder | $163,950.00 | 802 | $204.43 | 7.7% | 48.6% | 43.5% |

## Rank correlations (Spearman, n is small; direction only)

| Name | x | y | Excluded | n | rho |
|---|---|---|---|---|---|
| sub_rate_vs_cost_per_sub | paid_sub_per_signup | cost_per_sub_recomputed | — | 9 | -0.92 |
| cost_per_signup_vs_cost_per_sub | cost_per_signup | cost_per_sub_recomputed | — | 9 | -0.22 |
| signup_rate_vs_cost_per_sub | signup_per_click | cost_per_sub_recomputed | — | 9 | -0.75 |
| cpc_vs_sub_rate | cpc | paid_sub_per_signup | — | 9 | 0.63 |
| cpc_vs_sub_rate_excl_enterprise | cpc | paid_sub_per_signup | enterprise | 8 | 0.98 |

## Cross-term patterns

### P1. Signup-to-sub rate, not cost per signup, separates the sample

**Observed (fact).** Cost per signup sits in a narrow band for eight of nine terms ($11.06 to $24.57; enterprise is the outlier at $80.00), while cost/sub spans $84.78 to $1,400.00. Rank correlation of sub/signup with cost/sub is -0.92 (n=9); of cost/signup with cost/sub only -0.22. Sub/signup ranges from 2.0% (free, github) to 26.5% (scaffold).

**Supporting terms:** free ai app builder, ai app builder github, how to build an ai app, scaffold alternative, internal tool builder, build app without code  
**Counterexamples:** enterprise app development platform

**Possible explanations (hypotheses, not ranked):**
- Intent mismatch: some queries bring people who register but were never going to pay (tutorial seekers, free seekers, developers looking for a repo).
- Post-click mismatch: the landing page or onboarding does not serve those intents even though they could pay.
- Lag: same-window subs undercount terms whose users take longer to convert; the ratio would rise with cohort-aligned data.
- Signup definition: 'Regs' may include very low-commitment registrations for some traffic, inflating signups without intent.

**What would distinguish them:** Cohort-aligned subs (60/90-day) separate lag from the rest; an FFT/activation event per term separates dead registrations from engaged ones; landing-page and query-mix review separates intent from post-click mismatch.

### P2. The sample splits into two performance tiers around the allowable, and the sample as a whole is above it

**Observed (fact).** Five terms below $181 account for 56.6% of sample cost and 80.9% of sample subs at $128.18/sub (sub/signup 17.2%). Four terms above $181 account for 43.4% of cost and 19.1% of subs at $415.77/sub (sub/signup 3.7%). The nine rows together run at $183.11/sub, above the allowable and above the scope benchmark $167.74; by subtraction, the unseen remainder of the scope runs at $145.21.

**Supporting terms:** ai app builder, build app without code, vibe coding app builder, internal tool builder, scaffold alternative, free ai app builder, how to build an ai app, ai app builder github, enterprise app development platform  
**Counterexamples:** vibe coding app builder, how to build an ai app

**Possible explanations (hypotheses, not ranked):**
- Descriptive only: the split uses the same metric it groups by, so it is a summary, not an independent finding. Vibe coding (0.91x) and how-to (1.39x) sit close to the boundary and could move across it with lag or small count changes.
- The nine rows may be a curated 'hardest' subset of the scope rather than a representative slice: the remainder ($145.21) is cheaper per sub than each of the three largest rows, including the core term ($147.83).
- The scope benchmark being below the allowable while the sample is above it means efficiency in the scope is carried by terms not shown.

**What would distinguish them:** The full search-term report for the scope (the remaining ~35% of spend).

### P3. Cheaper clicks, worse conversion

**Observed (fact).** The three cheapest CPCs in the sample are github ($2.00), free ($2.10) and how-to ($2.40); together they are 38.4% of sample cost, 18.4% of subs, and convert signups at 3.6%. Rank correlation of CPC with sub/signup is 0.63 across all nine and 0.98 when enterprise is excluded. The four highest CPCs among non-enterprise terms (scaffold $4.50, internal $4.00, no-code $3.50, vibe $3.20) are also the four highest sub/signup rates in the sample (26.5%, 25.0%, 20.4%, 15.0%).

**Supporting terms:** ai app builder github, free ai app builder, how to build an ai app, scaffold alternative, internal tool builder, build app without code  
**Counterexamples:** enterprise app development platform

**Possible explanations (hypotheses, not ranked):**
- Auction pricing reflects other advertisers' assessment of commercial intent: queries competitors bid up are the ones that convert.
- Modifier words (free, github, how to) mark a non-buying stage regardless of price.
- Braid's landing pages serve buying intents well and non-buying intents poorly; cheap traffic is not inherently worse.
- Enterprise breaks the pattern because its CPC is set by a different competitor set (enterprise platforms) while its self-serve conversion is low for reasons unrelated to price.

**What would distinguish them:** Auction insights and competitor overlap per query; landing-page review; whether enterprise visitors appear in any sales pipeline.

### P4. Specific use-case and competitor terms convert best; head-plus-modifier terms do not

**Observed (fact).** The three use-case/competitor terms (no-code, internal tools, scaffold alternative) are 18.3% of sample cost but 34.3% of subs, at $97.31/sub with sub/signup 22.7%. The three terms built on the head phrase 'ai app builder' (core, free, github) are 53.0% of cost and 44.5% of subs at $217.99/sub; within that group the modifier decides everything (core $147.83, free $553.13, github $822.22).

**Supporting terms:** build app without code, internal tool builder, scaffold alternative, free ai app builder, ai app builder github  
**Counterexamples:** vibe coding app builder, enterprise app development platform

**Possible explanations (hypotheses, not ranked):**
- Specificity of buying intent: someone naming a use case or a competitor has already decided to buy something.
- Linguistic form is not the driver: 'vibe coding app builder' is head-plus-modifier and converts at 15.0%; 'enterprise app development platform' is use-case-shaped and converts at 5.7%.
- Volume effect: the use-case terms are small ($61,600.00); small terms can look efficient because they have not yet been scaled into worse inventory.

**What would distinguish them:** Impression share for the use-case terms (are they small because of low demand or low share?), and the query mix under each broad-match row.

### P5. Break-even arithmetic: which above-allowable terms are within reach of observed conversion rates

**Observed (fact).** At current cost, meeting $181 would require: how-to 292 subs (10.2% of its signups, 1.39x its observed subs); free 343 subs (6.1%, 3.06x); github 82 subs (9.2%, 4.56x); enterprise 93 subs (44.3%, 7.75x). The best sub/signup observed anywhere in the sample is 26.5%.

**Supporting terms:** how to build an ai app, free ai app builder, ai app builder github, enterprise app development platform  
**Counterexamples:** none in the sample

**Possible explanations (hypotheses, not ranked):**
- How-to needs a sub rate (10.2%) that four other terms already exceed; a lag or landing-page effect of that size is plausible and is the cheapest thing to test.
- Free and github need rates that other terms reach, but three to five times their own; lag alone would have to be very large to close that.
- Enterprise needs a sub rate above anything observed in the sample. Under Subs as the KPI it cannot reach $181 through conversion at its current cost per click; only a lower CPC or a different KPI (sales-assisted leads) changes that. This is arithmetic, not a recommendation.

**What would distinguish them:** Cohort-aligned conversion by term; whether an enterprise sales path exists and is tracked.

### P6. Signup rate is a weaker signal than sub rate, and small counts limit two terms

**Observed (fact).** Signup/click ranks against cost/sub at -0.75, weaker than sub/signup (-0.92). 'free' is the clearest counterexample: the second-highest signup rate (19.0%) and the worst cost/sub. Two terms have very few subs (enterprise 12, github 18), so their sub/signup rates are the least stable; no operator data-sufficiency threshold has been set.

**Supporting terms:** free ai app builder, how to build an ai app  
**Counterexamples:** scaffold alternative, internal tool builder

**Possible explanations (hypotheses, not ranked):**
- A high signup rate on a 'free' query is expected regardless of intent to pay; signup rate measures the ease of registering, not the intent behind it.
- For scaffold and internal tools, high signup rate and high sub rate coincide, so signup rate is informative for buying-intent queries and misleading for others.
- Small-count terms could look materially different with one quarter more data.

**What would distinguish them:** Operator min_cost / min_subs thresholds; an FFT or activation event that separates engaged signups from registrations.

### P7. Match type shows no pattern and cannot be read as keyword structure

**Observed (fact).** Two rows are Phrase (core, free) and carry 48.6% of sample cost at $204.43/sub; seven are Broad. Broad rows span the best ($84.78) and worst ($1,400.00) cost/sub. The column records the match type that triggered the search term, not the keyword or ad group behind it.

**Supporting terms:** scaffold alternative, enterprise app development platform  
**Counterexamples:** none in the sample

**Possible explanations (hypotheses, not ranked):**
- Broad match is grouping heterogeneous queries under each row; the row-level ratio may hide better and worse sub-intents.
- The two Phrase rows may come from one keyword or two; nothing in the data says which.

**What would distinguish them:** Keyword and ad-group columns, or the search-term report grouped by keyword.

## Observed performance vs possible explanations

| Observation (fact) | Possible explanations (hypotheses) | Evidence that would settle it |
|---|---|---|
| free: 5,600 signups (most in sample), 112 subs, sub/signup 2.0% | no free tier and searchers leave; free tier exists and converts after a lag; landing page contradicts the 'free' promise | product fact on free tier; 90-day cohort conversion for this term; landing-page review |
| github: cheapest CPC $2.00, sub/signup 2.0%, 18 subs | developer audience not served; open-source seekers who never intended to buy; low count instability | product fact on GitHub/code export; ad and landing page for the query; another period of data |
| enterprise: CPC $8.00, cost/signup $80.00, 12 subs, needs 44.3% sub rate to meet $181 | enterprise buyers convert through sales, not self-serve; term is off-target; count too small to judge | whether a sales path exists and whether these signups appear as leads |
| how-to: sub/signup 7.3%, needs 10.2% to meet $181 | tutorial seekers; broad match mixing intents; slower conversion for learners | query mix under the row; cohort-aligned subs; a template/tutorial landing-page test |
| use-case/competitor terms: $97.31/sub on 18.3% of cost | high buying intent; small terms not yet scaled; already isolated in the account | impression share and existing keyword coverage |
| sample $183.11 vs scope $167.74 vs remainder $145.21 | sample is the hardest subset; period misalignment; different attribution | full scope search-term report with dates |

## Actions

### Justified now on the supplied data alone

- **Request the full scope search-term report with dates, keyword and ad-group columns** — P2 and P7: the sample is 64.9% of scope spend and 59.5% of scope subs, runs above the allowable while the scope runs below it, and no row can be tied to a keyword. Every structural decision depends on this.
- **Pull cohort-aligned (60/90-day) subs by search term and an FFT/activation event if one exists** — P1 and P6: sub/signup drives the whole sample; lag and dead registrations are the two explanations the data cannot separate.
- **Review the ad and landing page served to the free, github, how-to and enterprise queries** — P1 and P3: intent mismatch and post-click mismatch produce the same numbers; this is the cheapest way to tell them apart and needs no account change.
- **Pull impression share for the five below-allowable terms** — P4: efficient small terms are only expansion candidates if they are share-limited rather than demand-limited.
- **Ask the operator for min_cost / min_subs thresholds** — P6: two terms have 12 and 18 subs; whether that is actionable is a policy, not a data, question.
- **Treat cost per signup as unsafe for bidding on this sample until validated** — P1: cost/signup correlates with cost/sub at only -0.22; optimising to it would favour the free and github queries. This is a measurement caution, not an account change.

### Requires more evidence before acting

| Candidate action | Missing evidence | Why it cannot be decided from the data |
|---|---|---|
| Any negative keyword (free, github, enterprise, how to) | product facts (free tier, GitHub feature, enterprise path), the query mix each negative would block in the remaining ~35% of scope, and the campaign/ad-group scope | the data shows low conversion, not irrelevance; a phrase negative would also block unseen queries whose performance is unknown |
| Bid changes on any term | the bidding strategy in use (manual, tCPA, tROAS, maximise conversions) and the keyword each term maps to | under automated bidding, per-term bid advice is not executable; under tCPA the target, not the bid, is the lever |
| New ad groups or keyword additions for use-case/competitor terms | existing keyword list and structure, impression share, and (for scaffold) trademark policy check | they may already be isolated; adding a duplicate keyword changes nothing except internal competition |
| Scaling the core term | impression share / lost IS (budget vs rank) for its keyword | below-allowable performance says nothing about headroom |
| Declaring enterprise off-target | whether a sales-assisted path exists and whether the 210 signups produced leads | P5 shows it cannot meet $181 on self-serve subs, but that is the wrong test if the buyer converts through sales |
| Choosing between the lag and intent explanations for free | cohort-aligned conversion for this term specifically | the term would need 3.06x its observed subs; only cohort data shows whether that is within reach |

## Review of v1 recommendations: unsupported assumptions

| v1 statement | Assumption not supported by the data | v2 position |
|---|---|---|
| 'ai app builder' is 'the core/head keyword' and other rows are 'broad-match spillover' | The data has no keyword column; match type is the triggered type. Which keyword served each row, and whether the two Phrase rows share a keyword, is unknown. | Describe rows as search terms only; keyword structure is a missing input (P7). |
| Proposed phrase negatives on 'free', 'github', 'enterprise', 'how to' | A phrase negative blocks every query containing the word, including the unseen ~35% of scope spend and any query on other terms (e.g. a 'free' query that converts). Impact outside the nine rows is unknown; ad-group vs campaign scope is unknown. | Keep negatives conditional, and add the requirement to see what each would block in the full report before proposing a match type. |
| 'Bid down', 'lower bid', 'capped bid' for free and how-to | Assumes manual or bid-cap control. The bidding strategy is unknown; under tCPA/maximise conversions there is no per-term bid to lower. | Replace with 'reduce exposure by the lever the bidding strategy allows' and list the strategy as a missing input. |
| 'Isolate into its own ad group' for six terms | Assumes these terms are not already in dedicated ad groups and that the account is structured by intent. Structure is unknown; v1 did flag a coverage check but still framed isolation as the default action. | Coverage check is the action; isolation is one possible outcome of it. |
| 'scaffold alternative' is a 'clear expansion candidate' | 'Clear' overstates: 138 subs on 3.5% of spend with no impression share data. It is the best ratio in the sample; headroom is unknown. | Best-performing small term; expansion depends on impression share and existing competitor coverage. |
| Enterprise: 'route to a demo/contact landing page' | Assumes an enterprise motion and a demo page exist. | P5: state the arithmetic (needs 44.3% sub rate) and make the sales-path question the only decision input. |
| 'Removing free leaves the rest at $159.17' presented as a useful scenario | Arithmetic is correct and was labelled as such, but it implicitly treats the term's spend as removable without affecting other rows or the unseen remainder. | Keep as arithmetic; do not use it to imply a post-negative cost/sub. |
| Reddit 'slightly above' allowable | Judgement word on a channel comparison whose attribution basis is unknown. | Report the ratio only. |
| Least-certain term is 'free ai app builder' | A defensible judgement, but v1 did not show the alternative: how-to is the term closest to the allowable and the most likely to flip on lag or landing page alone (P5). | Present both candidates with the evidence that would resolve each; the operator picks. |

## Least certain

Two terms compete for 'least certain', for different reasons; the data does not rank them.

- **free ai app builder** — Largest swing: 18.4% of sample spend and the most signups. Needs 3.06x its observed subs to meet $181. The one piece of information: cohort-aligned free-to-paid conversion for this term (and whether a free tier exists at all).
- **how to build an ai app** — Closest to the line: needs a sub rate of 10.2% against 7.3% observed, a gap that lag or a landing-page change could close. The one piece of information: the query mix under this broad-match row (tutorial vs tool seekers).

## Method note

Cross-term patterns are computed over 9 rows; Spearman rank correlations at this n indicate direction, not strength, and are reported to two decimals only for readability. Groups are arithmetic sums of the rows listed. 'Subs needed at $181' is cost divided by the allowable, rounded up, at current cost: it is a break-even statement, not a forecast, and assumes nothing about what would happen to cost if conversion changed. No posture is chosen and the allowable is not adjusted. The methodology prior (bid on an early signal, judge on paid subs) is applied only as a caution in P1/P6: on this sample the early signals (signup rate, cost per signup) would mislead.
