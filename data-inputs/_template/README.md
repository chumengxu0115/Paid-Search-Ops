# Data Inputs — expected files & schemas

Your real exports go in `data-inputs/[account-slug]/` (gitignored). This folder documents what the 6 files must look like. SETUP.md Phase 2 has the click-by-click export steps; this is the schema + gotcha reference.

## The 6 files

```
data-inputs/[account-slug]/
├── keyword-report-L6M.csv          # UTF-16 LE, TAB-delimited (Campaigns → Keywords view)
├── campaign-report-L6M.csv         # UTF-8 CSV (Reports → Predefined → Campaign)
├── search-terms-L3M.csv            # UTF-8 CSV — Last 3 Months — has Source column
├── search-terms-L6M.csv            # UTF-8 CSV — Last 6 Months — SAME schema as L3M
├── asset-association-L3M.csv       # UTF-8 CSV — has Level column (Ad / Asset group / Campaign)
└── brand-terms.md                  # Markdown (not CSV) — copy of clients/[slug]/brand-terms.md
```

---

## 1. `keyword-report-L6M.csv` — Last 6 Months
- **Export from the Campaigns → Keywords view, NOT Reports → Predefined → Keyword.** The predefined report inserts "Subtotals" rows whose Match type cell reads "Subtotals" / "Total" — that pollutes the Match type column. The Keywords view doesn't.
- **Encoding:** downloads as **UTF-16 LE, tab-delimited**. That's fine — the generator reads it with `encoding='utf-16', sep='\t'`. Don't try to "fix" it to UTF-8 CSV.
- **Required columns (~25+):**
  - Identity: `Keyword status`, `Keyword`, `Match type`, `Campaign`, `Ad group`, `Status`, `Currency code`, `Max. CPC`
  - Performance: `Impr.`, `Clicks`, `Cost`, `Avg. CPC`
  - Auction: `Search impr. share`, `Search lost IS (rank)`, `Top of page impr. share`
  - Quality + sub-components: `Quality Score`, `Exp. CTR`, `Landing page exp.`, `Ad relevance`
  - Conversions: **every** account conversion action, each as its own column, named exactly as in Google Ads (e.g. `Signed Up [Offline]`, `First Free Trial [Offline]`, `First Subs [Offline]`).
- **Do NOT add** `Search lost IS (budget)` — it does not exist at keyword granularity (it's grayed out in the column picker). That's why file 2 exists.

## 2. `campaign-report-L6M.csv` — Last 6 Months
- **UTF-8 CSV**, from Reports → Predefined → Campaign.
- **Required columns:** `Campaign`, `Campaign type`, `Campaign status`, `Cost`, `Avg. CPC`, every conversion action (same names as file 1), `Search impr. share`, **`Search lost IS (rank)`**, **`Search lost IS (budget)`** ⭐ (campaign-level only — this is the file's whole reason for existing), `Budget`.

## 3. `search-terms-L3M.csv` — Last 3 Months
- **UTF-8 CSV**, from Reports → Predefined → Search terms, date range Last 3 Months.
- **Required columns:** `Search term`, `Match type`, `Campaign`, `Ad group`, **`Source`** ⭐ (Search keyword / Performance Max / AI Max / Dynamic Search Ads — the split that powers PMax intent clustering, cannibalization, and the Campaign Health Source mix), `Clicks`, `Impr.`, `Cost`, and **all** conversion actions (same names as file 1).
- Used for: PMax intent clustering, New Keyword Suggestions, cannibalization, negative-keyword candidates — all the *action-oriented* analyses.

## 4. `search-terms-L6M.csv` — Last 6 Months
- **Identical schema to file 3**, just date range = Last 6 Months.
- Used for ONE thing: the **Campaign Health** sheet's campaign-level STR Source mix and "drift" signal, which needs a longer window to be stable. See `diagnose/data-window-rationale.md`.

## 5. `asset-association-L3M.csv` — Last 3 Months
- **UTF-8 CSV**, from Reports → Predefined → Asset association. One file replaces the old separate RSA Performance + PMax Asset Group reports.
- **Required columns:** `Level` ⭐ (`Ad` = RSA headlines/descriptions · `Asset group` = PMax assets · `Campaign` = sitelinks/callouts/structured snippets/etc.), `Campaign`, `Ad group` (where applicable), `Asset`, `Asset type` (`Headline` / `Description` / `Long headline` / `Image` / `YouTube video` / `Logo` / `Business name` / `Sitelink` / `Callout` / ...), `Impr.`, `Clicks`, `Cost`, conversion actions.
- Note: Google Ads does **not** export the Best/Good/Low/Pending performance rating into this report — the diagnosis judges asset performance from CTR + CPA + an impression floor instead, not from Google's ML rating.

## 6. `brand-terms.md`
- Not a CSV — a Markdown list. Copy from `clients/[account-slug]/brand-terms.md` (or just keep it there and point the generator at it). See that file's template for the format.

---

## Data-export warnings (read before processing)

- **Keyword report from the Keywords view, not Predefined** — avoids "Subtotals" rows landing in the Match type column.
- **Keyword report is UTF-16** — the generator handles it; don't re-save it.
- **Strip aggregate rows** — any row whose first cell starts with `Total: ` (e.g. "Total: Account", "Total: Campaign") is a Google Ads summary line, not data. The generator drops these; if you pre-clean, drop them too.
- **Skip `Source = "Unknown"` rows** in the search-terms reports — a data-quality artifact (Google couldn't attribute the term to a channel). Including them double-counts or misattributes spend. The generator skips them automatically.
- **Conversion column names must match** across all CSVs and `conversion-goals.md` exactly — a renamed column ("First Free Trial" vs "First Free Trial [Offline]") breaks the join.
- **One currency** — if the account has mixed-currency campaigns, convert before export or the CPA math is meaningless.
