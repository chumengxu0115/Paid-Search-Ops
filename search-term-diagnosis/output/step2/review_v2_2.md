# Braid Search Ops: evidence-led review v2.2 (independent of v1)

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

'Subs needed at $181' = ceil(cost / 181); 'sub rate needed' = that / signups. Arithmetic at current cost, not a forecast. Reaching the allowable is an operator target, not financial break-even: margin and customer value are unknown.

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

## Cross-term patterns

### P1. The subs/signup step, not the cost of a signup, accounts for most of the cost/sub spread

**Observed (fact).** Cost/sub is an identity: cost per signup divided by subs per signup. Cost per signup sits in a narrow band for eight of nine terms ($11.06 to $24.57; enterprise is the outlier at $80.00), while subs/signup ranges from 2.0% (free, github) to 26.5% (scaffold) and cost/sub from $84.78 to $1,400.00. Direct comparison: free ($11.06) and github ($16.63) have the two cheapest signups in the sample but the two lowest subs/signup; scaffold and internal tools pay $22.50 and $22.29 per signup, close to the core term's $21.43, and convert those signups at 26.5% (highest) and 25.0% (second-highest). Because the two factors are mathematically coupled, no correlation is reported; the decomposition itself is the evidence.

**Supporting terms:** free ai app builder, ai app builder github, how to build an ai app, scaffold alternative, internal tool builder, build app without code  
**Counterexamples:** enterprise app development platform

**Possible explanations (hypotheses, not ranked):**
- Intent mismatch: some queries bring people who register but were not going to pay (tutorial seekers, free seekers, developers looking for a repo).
- Post-click mismatch: the landing page or onboarding does not serve those intents even though they could pay.
- Lag: same-window subs undercount terms whose users take longer to convert; the ratio would rise with cohort-aligned data.
- Signup definition: 'Regs' may include very low-commitment registrations for some traffic, inflating signups without intent.
- Note for bidding: whichever explanation holds, cost per signup does not track cost/sub here; whether that matters depends on the account's current bidding event, which is unknown.

**What would distinguish them:** Cohort-aligned subs (60/90-day) separate lag from the rest; an FFT/activation event per term separates dead registrations from engaged ones; landing-page review and the matched keyword per row separate intent from post-click mismatch.

### P2. The sample splits into two performance tiers around the allowable, and the sample as a whole is above it

**Observed (fact).** Five terms below $181 account for 56.6% of sample cost and 80.9% of sample subs at $128.18/sub (sub/signup 17.2%). Four terms above $181 account for 43.4% of cost and 19.1% of subs at $415.77/sub (sub/signup 3.7%). The nine rows together run at $183.11/sub, above the allowable and above the scope benchmark $167.74; by subtraction, the unseen remainder of the scope runs at $145.21.

**Supporting terms:** ai app builder, build app without code, vibe coding app builder, internal tool builder, scaffold alternative, free ai app builder, how to build an ai app, ai app builder github, enterprise app development platform  
**Counterexamples:** vibe coding app builder, how to build an ai app

**Possible explanations (hypotheses, not ranked):**
- Descriptive only: the split uses the same metric it groups by, so it is a summary, not an independent finding. Vibe coding (0.91x) and how-to (1.39x) sit close to the boundary and could move across it with lag or small count changes.
- The nine rows may be a curated 'hardest' subset of the scope rather than a representative slice: the remainder ($145.21) is cheaper per sub than each of the three largest rows, including the core term ($147.83).
- The scope benchmark being below the allowable while the sample is above it means efficiency in the scope is carried by terms not shown.

**What would distinguish them:** The full search-term report for the scope (the remaining ~35% of spend).

### P3. In this sample, the cheapest clicks convert worst; this is an observation, not a rule about price

**Observed (fact).** The three cheapest CPCs in the sample are github ($2.00), free ($2.10) and how-to ($2.40); together they are 38.4% of sample cost, 18.4% of subs, and convert signups at 3.6%. The most expensive click, enterprise ($8.00), converts at 5.7%, third-lowest in the sample. The observation therefore holds for the three cheap terms and fails for the most expensive one; it is not evidence that paying more per click buys better customers.

**Supporting terms:** ai app builder github, free ai app builder, how to build an ai app, scaffold alternative, internal tool builder, build app without code  
**Counterexamples:** enterprise app development platform

**Possible explanations (hypotheses, not ranked):**
- The three cheap terms share modifier words (free, github, how to) that may mark a non-buying stage; the low price and the low conversion could both follow from that, with neither causing the other.
- Braid's landing pages may serve buying intents well and these intents poorly; cheap traffic is not inherently worse.
- Enterprise's price is set by a different set of competitors; its low self-serve conversion may reflect a sales-led buyer rather than intent quality.

**What would distinguish them:** Landing-page review for the three cheap terms; whether enterprise visitors appear in a sales pipeline; the matched keyword and ad group for each row.

### P4. Sample-specific observation: use-case and competitor terms convert best here (hypothesis, not proof of value)

**Observed (fact).** The three use-case/competitor terms (no-code, internal tools, scaffold alternative) are 18.3% of sample cost but 34.3% of subs, at $97.31/sub with subs/signup 22.7%. The three terms built on the head phrase 'ai app builder' (core, free, github) are 53.0% of cost and 44.5% of subs at $217.99/sub; within that group the modifier separates them (core $147.83, free $553.13, github $822.22). This is an observation about nine rows in one period: it says nothing about the value of the subscribers, their retention, or whether the ratio would hold at higher spend.

**Supporting terms:** build app without code, internal tool builder, scaffold alternative, free ai app builder, ai app builder github  
**Counterexamples:** vibe coding app builder, enterprise app development platform

**Possible explanations (hypotheses, not ranked):**
- Specificity of buying intent: someone naming a use case or a competitor may have already decided to buy something (hypothesis).
- Linguistic form is not the driver: 'vibe coding app builder' is head-plus-modifier and converts at 15.0%; 'enterprise app development platform' is use-case-shaped and converts at 5.7%.
- Volume effect: the use-case terms are small ($61,600.00); efficiency at this size does not imply efficiency at a larger size.
- Customer value is unknown: a cheaper sub from a competitor query is not shown to be worth the same as a sub from the core term.

**What would distinguish them:** Impression share for the use-case terms (demand-limited or share-limited), existing keyword coverage, and retention or value by acquisition term if available.

### P5. Allowable-reach arithmetic: which above-allowable terms are within the range of conversion rates observed in the sample

**Observed (fact).** At current cost, meeting the $181 allowable would require: how-to 292 subs (10.2% of its signups, 1.39x its observed subs); free 343 subs (6.1%, 3.06x); github 82 subs (9.2%, 4.56x); enterprise 93 subs (44.3%, 7.75x). The highest subs/signup observed in the sample is 26.5%. Reaching the allowable is not financial break-even; the allowable is an operator target and its relation to margin is unknown.

**Supporting terms:** how to build an ai app, free ai app builder, ai app builder github, enterprise app development platform  
**Counterexamples:** none in the sample

**Possible explanations (hypotheses, not ranked):**
- How-to needs a rate (10.2%) that 5 other sample terms already exceed; a lag or landing-page effect of that size is plausible.
- Free and github need rates that 6 and 5 other terms reach, but 3.06x and 4.56x their own observed subs; lag alone would have to be large to close that.
- Enterprise needs a rate above anything observed in this sample (0 terms exceed it). That is not impossible (enterprise buyers may behave unlike self-serve buyers, and the count is 12 subs), but keeping the term under a Subs KPI at current cost means expecting a conversion rate no term here has shown. A lower cost per click or a different KPI (sales-assisted leads) would change the arithmetic.

**What would distinguish them:** Cohort-aligned conversion by term; whether an enterprise sales path exists and is tracked; the margin behind the allowable.

### P6. Signup rate does not separate good from bad terms; small counts limit two terms

**Observed (fact).** Signup/click runs from 10.0% (enterprise) to 20.0% (scaffold). 'free' has the second-highest signup rate (19.0%) and the third-highest cost/sub ($553.13; enterprise $1,400.00 and github $822.22 are higher). 'github' has a signup rate (12.0%) close to how-to's (13.0%) and vibe's (13.0%) yet the second-highest cost/sub. Two terms have very few subs (enterprise 12, github 18), so their subs/signup rates are the least stable; no operator data-sufficiency threshold has been set.

**Supporting terms:** free ai app builder, how to build an ai app  
**Counterexamples:** scaffold alternative, internal tool builder

**Possible explanations (hypotheses, not ranked):**
- A high signup rate on a 'free' query is expected regardless of intent to pay; signup rate measures the ease of registering, not the intent behind it.
- For scaffold and internal tools, high signup rate and high subs/signup coincide, so signup rate is informative for buying-intent queries and misleading for others.
- Small-count terms could look materially different with one more period of data.

**What would distinguish them:** Operator min_cost / min_subs thresholds; an FFT or activation event that separates engaged signups from registrations.

### P7. Match type shows no pattern and cannot be read as keyword structure

**Observed (fact).** Two rows are Phrase (core, free) and carry 48.6% of sample cost at $204.43/sub; seven are Broad. Broad rows span the best ($84.78) and worst ($1,400.00) cost/sub. The column records the match type that triggered the search term, not the keyword or ad group behind it, and says nothing about how many queries sit in a row.

**Supporting terms:** scaffold alternative, enterprise app development platform  
**Counterexamples:** none in the sample

**Possible explanations (hypotheses, not ranked):**
- Each row is one search term as reported; which keyword matched it, in which ad group, and under which bidding strategy, is not in the data.
- The two Phrase rows may come from one keyword or two; nothing in the data says which.

**What would distinguish them:** Matched keyword, ad group and campaign columns for each row (the standard search-term report fields), plus the bidding strategy per campaign.

## Observed performance vs possible explanations

| Observation (fact) | Possible explanations (hypotheses) | Evidence that would settle it |
|---|---|---|
| free: 5,600 signups (most in sample), 112 subs, subs/signup 2.0%, cost/sub $553.13 (third-highest) | no free tier and searchers leave; free tier exists and converts after a lag; landing page contradicts the 'free' promise | product fact on free tier; 90-day cohort conversion for this term; landing-page review |
| github: cheapest CPC $2.00, subs/signup 2.0%, 18 subs, cost/sub $822.22 (second-highest) | developer audience not served; open-source seekers who never intended to buy; low count instability | product fact on GitHub/code export; ad and landing page for the query; another period of data |
| enterprise: CPC $8.00, cost/signup $80.00, 12 subs, cost/sub $1,400.00 (highest); needs 44.3% subs/signup to reach $181, above the sample maximum 26.5% | enterprise buyers convert through sales, not self-serve; term is off-target; count too small to judge | whether a sales path exists and whether these signups appear as leads |
| how-to: subs/signup 7.3%, needs 10.2% to reach $181 | tutorial seekers; slower conversion for learners; landing page not built for them | matched keyword for the row; cohort-aligned subs; a template/tutorial landing-page test |
| use-case/competitor terms: $97.31/sub on 18.3% of cost (sample-specific) | high buying intent; small terms not yet scaled; already isolated in the account; subscriber value unknown | impression share, existing keyword coverage, value or retention by acquisition term |
| sample $183.11 vs scope $167.74 vs remainder $145.21 | sample is the hardest subset; period misalignment; different attribution | full scope search-term report with dates |

## Actions

### Justified now on the supplied data alone

- **Request the full scope search-term report with dates, matched keyword, ad group, campaign and bidding strategy** — P2 and P7: the sample is 64.9% of scope spend and 59.5% of scope subs, runs above the allowable while the scope runs below it, and no row can be tied to a keyword or a bidding lever.
- **Pull cohort-aligned (60/90-day) subs by search term and an FFT/activation event if one exists** — P1 and P6: the subs/signup step accounts for the spread; lag and dead registrations are the two explanations the data cannot separate.
- **Review the ad and landing page served to the free, github, how-to and enterprise queries** — P1 and P3: intent mismatch and post-click mismatch produce the same numbers; this is the cheapest way to tell them apart and needs no account change.
- **Pull impression share for the five below-allowable terms** — P4: efficient small terms are only expansion candidates if they are share-limited rather than demand-limited.
- **Ask the operator for min_cost / min_subs thresholds and the margin behind the $181 allowable** — P5 and P6: two terms have 12 and 18 subs, and 'reaching the allowable' cannot be read as break-even without the margin.
- **Investigate whether the account optimises bidding to signups or cost per signup** — P1: cost per signup is nearly flat across terms whose cost/sub differs by more than ten times, so a signup-based target could favour the free and github queries. This is a concern to check, not a proven reason to change the bidding event: the current bidding setup, lag and usable signal volume are unknown.

### Requires more evidence before acting

| Candidate action | Missing evidence | Why it cannot be decided from the data |
|---|---|---|
| Any negative keyword (free, github, enterprise, how to) | the product fact named in the conditional recommendation for that term, the matched keyword/ad group, and what the negative would block in the remaining ~35% of scope | the data shows low conversion, not irrelevance; a phrase negative also blocks unseen queries whose performance is unknown |
| Bid or target changes on any term | the bidding strategy in use (manual, tCPA, tROAS, maximise conversions) and the keyword each term maps to | under automated bidding, per-term bid advice is not executable; under tCPA the target, not the bid, is the lever |
| New ad groups or keyword additions for use-case/competitor terms | existing keyword list and structure, impression share, and (for scaffold) trademark policy check | they may already be isolated; adding a duplicate keyword changes nothing except internal competition |
| Scaling the core term | impression share / lost IS (budget vs rank) for its keyword | below-allowable performance says nothing about headroom |
| Treating enterprise as off-target | whether a sales-assisted path exists and whether the 210 signups produced leads | P5: no subs/signup rate seen in this sample would bring it to $181 at current cost, but that is the wrong test if the buyer converts through sales |

## Review of v1 recommendations: unsupported assumptions

| v1 statement | Assumption not supported by the data | v2 position |
|---|---|---|
| 'ai app builder' is 'the core/head keyword' and other rows are 'broad-match spillover' | The data has no keyword column; match type is the triggered type. Which keyword served each row, and whether the two Phrase rows share a keyword, is unknown. | Describe rows as search terms only; matched keyword and structure are requested inputs (P7). |
| Proposed phrase negatives on 'free', 'github', 'enterprise', 'how to' | A phrase negative blocks every query containing the word, including the unseen ~35% of scope spend and any query on other terms (e.g. a 'free' query that converts). Impact outside the nine rows is unknown; ad-group vs campaign scope is unknown. | Keep negatives conditional, and add the requirement to see what each would block in the full report before proposing a match type. |
| 'Bid down', 'lower bid', 'capped bid' for free and how-to | Assumes manual or bid-cap control. The bidding strategy is unknown; under tCPA/maximise conversions there is no per-term bid to lower. | Replace with 'reduce exposure by the lever the bidding strategy allows' and list the strategy as a missing input. |
| 'Isolate into its own ad group' for six terms | Assumes these terms are not already in dedicated ad groups and that the account is structured by intent. Structure is unknown; v1 did flag a coverage check but still framed isolation as the default action. | Coverage check is the action; isolation is one possible outcome of it. |
| 'scaffold alternative' is a 'clear expansion candidate' | 'Clear' overstates: 138 subs on 3.5% of spend with no impression share data. It is the best ratio in the sample; headroom is unknown. | Best-performing small term; expansion depends on impression share and existing competitor coverage. |
| Enterprise: 'route to a demo/contact landing page' | Assumes an enterprise motion and a demo page exist. | P5: state the arithmetic (needs 44.3% sub rate) and make the sales-path question the only decision input. |
| 'Removing free leaves the rest at $159.17' presented as a useful scenario | Arithmetic is correct and was labelled as such, but it implicitly treats the term's spend as removable without affecting other rows or the unseen remainder. | Keep as arithmetic; do not use it to imply a post-negative cost/sub. |
| Reddit 'slightly above' allowable | Judgement word on a channel comparison whose attribution basis is unknown. | Report the ratio only. |
| Least-certain term is 'free ai app builder' | A defensible judgement, but v1 did not show the alternative: how-to is the term closest to the allowable and the most likely to flip on lag or landing page alone (P5). | Present both candidates with the evidence that would resolve each; the operator picks. |

## Conditional recommendations (what the data supports now, and what would change it)

| Term / decision | Current lean on supplied data | Changes the decision | Under scale | Under maintain efficiency |
|---|---|---|---|---|
| free ai app builder | Largest above-allowable term (18.4% of sample cost, 3.06x); needs 6.1% subs/signup vs 2.0% observed. Lean: reduce exposure before scaling anything else. | Keep and isolate instead if product confirms a free tier AND cohort-aligned (90-day) subs/signup for this term reaches about 6.1%. Negative candidate ('free', scoped to the matched keyword's ad group) only if product confirms there is no free tier, OR a free tier is confirmed and the cohort rate stays near 2.0%. Whether a free tier exists is currently unknown, so the negative is pending confirmation. | Same lean; redirect its budget to below-allowable terms with headroom rather than cutting overall spend. | Same lean, highest priority: it is the largest single contributor to the sample running above $181. |
| ai app builder github | Cost/sub $822.22 is the second-highest in the sample (4.54x); needs 9.2% vs 2.0% observed on 18 subs. Lean: negative candidate ('github'), pending confirmation; whether Braid has a GitHub integration, code export or developer audience is unknown, and unknown is not absence. | Becomes an actionable negative only if product confirms there is no GitHub-related capability or developer audience. Becomes keep-and-test (developer landing page) if product confirms one exists. Hold judgement if the operator's min_subs threshold is above 18. | Pending the product fact; if confirmed absent, negative; if confirmed present, landing-page test before any spend increase. | Pending the product fact; if confirmed absent, negative; if present, landing-page test first. |
| enterprise app development platform | Highest cost/sub ($1,400.00); needs 44.3% subs/signup, above the sample maximum 26.5%. Lean: stop judging it on self-serve subs. | If a sales-assisted path is confirmed: move to lead-based measurement and a demo/contact page; the Subs comparison no longer applies. Negative candidate ('enterprise') only if product confirms there is no enterprise offering or sales path; that fact is unknown, so the negative is pending confirmation. If the operator's min_subs threshold is above 12: hold until more data. | Only with lead-based measurement in place. | Pending the product fact; negative if confirmed no enterprise path, otherwise measure on leads. |
| how to build an ai app | Above allowable (1.39x) but closest to it: needs 10.2% vs 7.3% observed, a rate 5 sample terms exceed. Lean: keep, run a tutorial/template landing-page test before any negative. | Reduce exposure (by the lever the bidding strategy allows) if cohort-aligned subs/signup stays at or below 7.3% after the landing-page test. Keep as is if cohort data alone lifts it to about 10.2%. | Not a scaling candidate until it clears $181. | Second priority after free; landing-page test first because the gap is small. |
| ai app builder | Below allowable ($147.83, 0.82x) with the most volume. Lean: keep. | Scale only if lost impression share (rank or budget) shows headroom for its keyword. Revisit if cohort-aligned cost/sub comes in above $181. | First expansion candidate, conditional on headroom. | No change. |
| build app without code | Below allowable ($107.19) with 320 subs. Lean: keep. | Expand (dedicated keyword/ad group) if not already covered and impression share shows headroom. Nothing in the data turns it into a negative candidate. | Expansion candidate after coverage check. | Keep. |
| internal tool builder | Below allowable ($89.14). Lean: keep. | Expand if not already covered, impression share shows headroom, and product confirms internal tools as a supported use case. | Expansion candidate after coverage check. | Keep. |
| scaffold alternative | Lowest cost/sub ($84.78) on 3.5% of cost. Lean: keep. | Expand (dedicated competitor ad group) if not already covered, impression share shows headroom, and competitor ad copy passes policy. Small size means expansion efficiency is unproven. | Expansion candidate after coverage check. | Keep. |
| vibe coding app builder | Below allowable ($163.81, 0.91x) but near the scope benchmark. Lean: hold. | Reduce exposure if cohort-aligned cost/sub moves above $181; expand only if messaging fit is confirmed and headroom exists. | Secondary candidate after the core term. | Hold; monitor. |
| Bidding signal | Concern to investigate, not a conclusion: if the account currently optimises to signups or cost per signup, this sample suggests that signal would favour the free and github queries. The current bidding event, the signup-to-sub lag and the usable signal volume are unknown. In this analysis terms are judged on paid subs. | Confirm the current bidding event and strategy per campaign first. If bidding is already on subs or an activation event, no concern. If bidding is on signups, the next question is whether an FFT/activation event with enough volume tracks subs/signup across terms; only then is a change worth evaluating. | Same: investigate before any bidding-event change. | Same. |

## Least certain

Two terms compete for 'least certain', for different reasons; the data does not rank them.

- **free ai app builder** — Largest swing: 18.4% of sample spend and the most signups. Needs 3.06x its observed subs to meet $181. The one piece of information: cohort-aligned free-to-paid conversion for this term (and whether a free tier exists at all).
- **how to build an ai app** — Closest to the line: needs a subs/signup rate of 10.2% against 7.3% observed, a gap that lag or a landing-page change could close. The one piece of information: cohort-aligned subs/signup for this term after a tutorial/template landing-page test.

## Method note

Cross-term patterns are computed over 9 rows in one period. Groups are arithmetic sums of the rows listed. Rank correlations from v2 are omitted: cost/sub equals cost per signup divided by subs per signup, so correlations among these metrics restate an identity and carry no causal information; the direct comparisons in P1 replace them. 'Subs needed at $181' is cost divided by the allowable, rounded up, at current cost: a statement of what reaching the operator's target would require, not a forecast and not financial break-even. No posture is chosen and the allowable is not adjusted. The methodology prior (bid on an early signal, judge on paid subs) is applied only as a caution in P1/P6: on this sample the early signals (signup rate, cost per signup) do not track paid subs, which is a reason to check the current bidding event, not a finding that it is wrong.
