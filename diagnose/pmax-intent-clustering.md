# PMax Intent Clustering

PMax doesn't let you pick keywords, and Google discloses only a fraction of the search terms PMax actually serves against. So PMax is a black box. This file makes the *visible* part legible: every `Source = Performance Max` row in `search-terms-L3M.csv` is matched against the cluster keyword lists below, assigned to one cluster (first match wins; nothing matches → **Other / unclassified**), and the diagnose then reports per PMax campaign: visible-query % (honesty signal), top clusters by spend, and the top converting cluster.

**Black-box reality, stated plainly:** the "Other / unclassified" bucket is partly genuinely-novel queries and partly *queries Google never showed us at all* — there is no way to fully de-opacify PMax from the export. The diagnose therefore surfaces a **visible %** warning in the Campaign Health column (e.g. "PMax · 38% queries visible · top intent: vibe-coding") so a low number is read as low confidence, not as a clean account.

**These clusters are a starting set and are meant to be edited per account.** Add, remove, rename, or re-keyword them here; the generator reads this file. The set below is tuned for a no-code / app-builder vertical (the client-alpha example); replace the keyword lists for other verticals.

---

## The 13 clusters

### 1. Client Brand (placeholder)
- **Match keywords:** [list your target client's brand variants here — e.g., domain, common misspellings, with-and-without-space versions, app/product name combinations]
- **Rationale:** Brand-defense first. Brand queries convert at the highest CR; never let them slip into "Other / unclassified".

### 2. Vibe coding / AI coding
- **Match keywords:** `lovable`, `cursor`, `bolt`, `bolt.new`, `replit`, `emergent`, `v0`, `vercel v0`, `windsurf`, `vibe coding`, `vibe code`, `ai coding`, `code with ai`, `ai code editor`, `prompt to app`, `text to app`
- **Rationale:** the AI-native "describe it and it builds" category — the fastest-growing and most volatile competitive front; high click, often low commercial intent.

### 3. No-code competitors (named)
- **Match keywords:** `flutterflow`, `glide`, `glide apps`, `adalo`, `webflow`, `base44`, `softr`, `bildr`, `wized`, `weweb`, `draftbit`, `thunkable`, `appgyver`, `backendless`, `noloco`
- **Rationale:** direct named-competitor conquesting inside PMax — useful to see which competitors PMax is bidding into and at what efficiency.

### 4. AI app builder
- **Match keywords:** `ai app builder`, `ai app maker`, `ai web app builder`, `build app with ai`, `ai application builder`, `ai software builder`, `ai mobile app builder`
- **Rationale:** the bridge between "no-code" and "vibe coding" — buyers who want AI assistance but still expect a real app platform underneath. Often the best-converting AI-adjacent cluster.

### 5. No-code generic
- **Match keywords:** `no code`, `nocode`, `no-code`, `no code platform`, `no code tool`, `no code development`, `no code software`, `no code website`
- **Rationale:** broad category demand; converts moderately; the volume backbone of PMax for this vertical.

### 6. App builder generic
- **Match keywords:** `app builder`, `app maker`, `app creator`, `build an app`, `make an app`, `create an app`, `web app builder`, `application builder`, `software builder`
- **Rationale:** category demand without the "no-code" qualifier — overlaps platforms (Android Studio etc.); watch for low-intent leakage.

### 7. Database / backend
- **Match keywords:** `airtable`, `airtable alternative`, `database app`, `database builder`, `backend builder`, `backend as a service`, `baas`, `internal database`, `data app`, `relational database app`
- **Rationale:** the Airtable-adjacent buyer; usually higher-intent and higher-LTV (they're building something real with data).

### 8. Internal tools / B2B
- **Match keywords:** `internal tool`, `internal tools builder`, `admin panel builder`, `crm builder`, `build internal app`, `b2b app`, `business app builder`, `ops tool`, `dashboard builder`, `retool` , `retool alternative`
- **Rationale:** the B2B / internal-tools audience — distinct buyer, distinct LTV; worth its own cluster so PMax efficiency here can be compared to a dedicated B2B Search campaign.

### 9. Marketplace / app types
- **Match keywords:** `marketplace app`, `build a marketplace`, `two sided marketplace`, `booking app`, `directory app`, `social network app`, `dating app builder`, `delivery app`, `saas app builder`, `community app`
- **Rationale:** intent expressed as "I want to build *this kind* of app" — high commercial intent, easy to map to use-case landing pages.

### 10. Tutorial / how-to
- **Match keywords:** `how to build an app`, `how to make an app`, `app development tutorial`, `learn no code`, `no code tutorial`, `build app step by step`, `app development guide`, `how to create a website app`
- **Rationale:** mostly research intent — clicks, rarely converts; large share here is a CTR-dilution and budget-waste flag.

### 11. Pricing / comparison
- **Match keywords:** `pricing`, `cost`, `vs`, `alternative`, `comparison`, `which is better`, `cheapest`, `free app builder`, `best app builder`, `best no code platform`, `top no code tools`
- **Rationale:** bottom-funnel comparison shopping — should convert well; if it doesn't, the comparison/pricing landing page is the suspect.

### 12. AI generic / hype
- **Match keywords:** `ai`, `chatgpt`, `gpt`, `artificial intelligence`, `ai tool`, `ai software`, `ai generator`, `ai builder`, `ai automation`, `ai agent`
- **Rationale:** the "AI" hype tail — enormous volume, terrible intent; almost pure CTR dilution. A large share here usually explains a sagging account-level CTR.

### 13. Games / entertainment
- **Match keywords:** `game maker`, `make a game`, `build a game`, `game builder`, `roblox`, `game app`, `2d game maker`, `mobile game builder`, `game engine`
- **Rationale:** consistently off-target for a business-app platform — a fast candidate for negatives; here so its spend is visible rather than buried in "Other".

### (residual) Other / unclassified
- Everything that matches no list above. Reported as a number and a %, never actioned blind. A large "Other" share = either (a) you need more clusters for this account, or (b) PMax is disclosing little — both worth saying out loud in the insights doc.

---

## How to extend per account
1. Add a new `### N. <name>` block here with a `Match keywords` line and a `Rationale` line.
2. Order matters — earlier clusters win ties; put the more specific cluster above the more generic one.
3. Re-run `generators/run-diagnose.md`; the PMax Intent sheet and the Campaign Health STR-signal column pick up the new cluster automatically.
4. For a non-no-code account, replace clusters 1–4 and 7–13's keyword lists wholesale; the *structure* (named-brand cluster, generic-category cluster, hype/dilution cluster, off-target cluster, research/how-to cluster, comparison cluster, plus an Other residual) generalizes.
