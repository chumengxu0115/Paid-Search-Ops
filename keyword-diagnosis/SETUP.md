# SETUP — keyword-diagnose-v2

Five phases. Phases 1–2 are manual (context + exports). Phases 3–5 are paste-a-prompt-into-Claude.

---

## Phase 1 — Set up account context

1. Copy the template:
   ```
   cp -r clients/_template clients/[your-account-slug]
   ```
   Use a short kebab-case slug, e.g. `acme-us`, `client-alpha`.

2. Fill the 6 context files in `clients/[your-account-slug]/`:
   - `account-context.md` — business name, vertical, product, geos, languages
   - `conversion-goals.md` — **bidding signal** (the conversion action Smart Bidding optimizes), **business KPI** (the success metric conversion), target CPA per audience
   - `benchmarks.md` — search-only CTR baseline, per-keyword spend distribution, per-funnel CR baselines, per-audience FFT→KPI CR, per-geo CTR + CPA bands
   - `current-problems.md` — your framing of what's wrong (the diagnosis will reframe it if the data disagrees)
   - `brand-terms.md` — hand-curated brand-defense terms
   - `criteria.yaml` — leave it as the template copy for now; Phase 3 fills it

Mark anything you're unsure of `[VERIFY: ...]`. The diagnosis still runs with `[VERIFY]` values but flags them in the Data Health section.

---

## Phase 2 — Export 6 reports from Google Ads

⚠️ **Data windows matter and are not all the same.** Keyword + campaign reports are **Last 6 Months**. Search terms are pulled **twice — Last 3 Months AND Last 6 Months** (see 2.3 / 2.4). Asset association is **Last 3 Months**.

Save every file under `data-inputs/[your-account-slug]/` (gitignored).

### Step 2.1 — Keyword Performance Report — Last 6 Months
- Use the **Campaigns → Keywords** view (NOT Reports → Predefined → Keyword). The predefined report injects "Subtotals" rows that pollute the Match type column; the Keywords view doesn't.
- Add columns: Keyword status, Keyword, Match type, Campaign, Ad group, Status, Currency code, Max CPC, Impr., Clicks, Cost, Avg CPC, Search impr. share, Search lost IS (rank), Top of page impr. share, Quality Score, Exp. CTR, Landing page exp., Ad relevance, and **all** account conversion actions by exact name.
- Do NOT request "Search lost IS (budget)" here — it doesn't exist at keyword granularity (it's campaign-level only; that's why 2.2 exists).
- Export as CSV. It will download as **UTF-16 LE, tab-delimited** — that's expected; the generator handles it.
- Save as: `data-inputs/[account-slug]/keyword-report-L6M.csv`

### Step 2.2 — Campaign Performance Report — Last 6 Months
- Reports → Predefined → Campaign.
- Columns: Campaign, Campaign type, Campaign status, Cost, Avg CPC, all conversion actions, Search impr. share, **Search lost IS (rank)**, **Search lost IS (budget)**, Budget.
- Save as: `data-inputs/[account-slug]/campaign-report-L6M.csv`

### Step 2.3 — Search Terms Report — Last 3 Months ⭐ DUAL WINDOW
- Reports → Predefined → Search terms.
- Date range: **Last 3 Months**.
- Required columns: Search term, Match type, Campaign, Ad group, **Source**, Clicks, Impr., Cost, and **all 5 conversion actions**.
- Save as: `data-inputs/[account-slug]/search-terms-L3M.csv`
- **Why L3M (not L6M):** query behavior changes fast, and the PMax black-box (the share of PMax-driven queries Google actually discloses) grows staler with time. L3M is the right window for the *action-oriented* analyses: graduation/new-keyword candidates, cannibalization analysis, and new-keyword discovery. Fresh data → actions you can take today.

### Step 2.4 — Search Terms Report — Last 6 Months ⭐ DUAL WINDOW (new in v2)
- Same report, same columns as 2.3, but date range = **Last 6 Months**.
- Save as: `data-inputs/[account-slug]/search-terms-L6M.csv`
- **Why L6M (in addition to L3M):** the **Campaign Health** snapshot reports campaign-level STR **Source mix** (PMax vs Search vs AI Max vs DSA-legacy) and whether that mix is *drifting*. Source mix is a slow-moving structural signal; a 3-month window is too short for it to be stable, so the health snapshot uses the 6-month window. The two windows answer different questions — that's the point of pulling both.

### Step 2.5 — Asset Association Report — Last 3 Months
- Reports → Predefined → Asset association.
- One file replaces what used to be two (separate RSA Performance + PMax Asset Group reports). It carries a **Level** column (Ad / Asset group / Campaign): `Level = Ad` rows are RSA headlines/descriptions, `Level = Asset group` rows are PMax assets, `Level = Campaign` rows are sitelinks/callouts/etc.
- Save as: `data-inputs/[account-slug]/asset-association-L3M.csv`

### Step 2.6 — Brand Terms Manifest
- Not a Google Ads export — a hand-curated Markdown list of your brand-defense terms and known misspellings.
- Save as: `data-inputs/[account-slug]/brand-terms.md` (or copy `clients/_template/brand-terms.md` and edit).

---

## Phase 3 — Recommend criteria (AI fills `criteria.yaml`)

1. Open `generators/recommend-criteria.md` and paste it into Claude in this repo.
2. The AI reads the 6 context files in `clients/[account-slug]/` and the 5 CSVs in `data-inputs/[account-slug]/`, then recommends thresholds for every section of `criteria.yaml`.
3. It writes the `recommended` and `rationale` fields for each threshold and sets `your_value` equal to `recommended` as a starting point.

---

## Phase 4 — Review & adjust `criteria.yaml`

1. Open `clients/[account-slug]/criteria.yaml`.
2. The AI has filled `recommended` (read-only — don't edit) and `rationale` (read-only) for every threshold.
3. **You edit `your_value` only.** Leave anything you agree with as-is. Anything you want to tighten/loosen, change `your_value`. The diagnosis uses `your_value`, never `recommended`.

---

## Phase 5 — Run diagnosis (generates Excel + Doc)

1. Open `generators/run-diagnose.md` and paste it into Claude in this repo.
2. It loads `criteria.yaml` (your edited `your_value` fields) + all 6 data files, runs the full pipeline, and writes:
   ```
   output/[account-slug]/[date]/insights.docx
   output/[account-slug]/[date]/keyword-diagnose.xlsx
   ```
3. Read `diagnose/reading-the-output.md` for the sheet-by-sheet guide.

To explore "what if I were stricter on CPA": change a `your_value` in `criteria.yaml`, re-run Phase 5. Date-stamped output folders mean previous runs aren't overwritten.
