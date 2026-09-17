# Search Ops dashboard (local preview)

Plain HTML/CSS/JavaScript, no dependencies, no build step. Reads `output/canonical/search_ops_analysis.json` (read-only) and stores operator feedback in the browser's localStorage.

## Run

From the module folder `search-term-diagnosis/` (the page fetches `../output/canonical/...`, so the server must serve that folder or a parent of it):

```bash
python3 src/build_canonical.py            # only if output/canonical/ is missing or stale
python3 -m http.server 8781 --bind 127.0.0.1
```

Open <http://127.0.0.1:8781/ui/> (or <http://127.0.0.1:8781/search-term-diagnosis/ui/> if you serve the repository root). Views are addressable: `#insights`, `#terms`, `#plan`, `#log`. Port 8765 is used by the reference prototype; pick any other free port.

## What it does / does not do

- Shows verified step 1 metrics, the reviewed cross-term insights (v2.2), all nine terms with evidence, hypotheses, comparisons, missing information and conditional recommendations, and the action plan.
- The posture selector (Not selected / Scale / Maintain efficiency) only chooses which saved branch to display. It does not run a model or change the $181 allowable.
- Operator input per term (missing-data notes, product Q&A, insight, final decision, rationale) is saved on this browser only, keyed by analysis identity and term_id. It never modifies the canonical JSON.
- **Export feedback for Claude Code** downloads `operator_feedback.json`. **Import feedback JSON** validates the file (format, analysis identity, term ids, field types) and refuses mismatched or malformed files without touching existing notes.
- No live model call, no "AI reanalyze" button, no ad-account connection, no simulated execution.

## Reanalysis handoff

1. Export `operator_feedback.json` from the dashboard.
2. Save it into the project, e.g. `operator/operator_feedback.json`.
3. Ask Claude Code to build a new review version that consumes it; the canonical baseline stays unchanged and a new version is produced alongside it.

## Self-test (development only)

`http://127.0.0.1:8781/ui/?selftest=1` runs DOM-driven checks (nine rows, selection, posture branches, autosave, safe rendering, export/import validation) and prints results at the bottom of the page; `&phase=2` verifies persistence after a fresh load; `&phase=layout` reports horizontal overflow. `selftest.js` is only loaded with that parameter.
