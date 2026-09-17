# Search Ops

An AI-assisted paid-search diagnostic workflow built with Claude Code: calculate the evidence, interpret search intent, expose missing information, and review conditional actions in a local dashboard.

The methodology builds on my [keyword-diagnose project](https://github.com/chumengxu0115/paid-search-keyword-diagnose), first committed on June 22, 2026, and my experience managing paid search for Bubble. This is a separate search-term implementation, not a claim that the original keyword tool directly runs these inputs.

## The problem

Cheap registrations are not necessarily cheap subscribers. An operator needs to connect acquisition metrics to downstream outcomes, understand which customer intents differ, and decide what is justified when product context or attribution data is missing.

This example uses Braid synthetic interview data: nine search terms and a paid-channel summary. It contains no actual Bubble or Runway account performance. Braid and Scaffold are names supplied by the exercise. Product capabilities that were not supplied remain unknown.

## Open the demo

Python 3.9+ is sufficient. No package installation or API key is required to view the saved example.

```bash
python3 -m http.server 8781 --bind 127.0.0.1
```

Open http://127.0.0.1:8781/ui/ from the repository root.

- **Business Insights:** distinct account/scope/sample metrics, cross-term patterns and strategic posture.
- **Search Terms:** evidence and conditional recommendations, plus editable human notes and decisions.
- **Action Plan:** negative candidates, additions/isolation candidates and landing-page tests.
- **Data & Run Log:** missing information, validation results and analysis provenance.

Choose a term and click **Add my input**. Notes save in that browser only. Export/import preserves a feedback file tied to the analysis identity. Selecting Scale or Maintain efficiency displays a saved recommendation branch; it does not call a model or change the allowable.

## How the workflow works

```text
CSV + confirmed account context
          ↓
Python: validate inputs and calculate metrics
          ↓
Claude Code: author evidence-linked interpretation
          ↓
Python: resolve numeric references and validate outputs
          ↓
Dashboard: inspect evidence, compare options, record human judgment
          ↓
Optional exported feedback → a subsequent Claude Code review
```

Claude Code built the calculation and diagnostic tooling and authored the saved analysis in actual sessions. The initial visual prototype was explored with Codex; Claude Code implemented the integrated UI. Codex also reviewed the outputs and prepared the final documentation.

The Python builders **render and validate saved model-authored reasoning**. They do not make a live model call. Updated data or business context requires a fresh reasoning review in Claude Code, not just replacing numbers. The browser has no autonomous reanalysis or advertising-account execution. The optional feedback-to-reanalysis loop is a manual handoff, not an integrated or verified automatic feature.

## Evidence, targets and uncertainty

The exercise confirms a Non-Brand allowable of **$181/sub** and Scaffold as the main competitor. Keep three levels separate:

| Scope | Spend | Subscriptions | Recomputed cost/sub |
|---|---:|---:|---:|
| All Google Non-Brand | $701,000 | 4,348 | $161.22 |
| Non-Brand ai app builder scope | $520,000 | 3,100 | $167.74 |
| Nine-term sample | $337,470 | 1,843 | $183.11 |

The $167.74 figure is observed performance, not the $181 allowable. Scale and efficiency are operator choices; neither automatically changes the allowable. Regs maps to Signup and Subs provisionally to Paid Sub for the exercise. FFT is unavailable. Subs/Signup is a descriptive ratio, not a verified mature-cohort conversion rate.

Example independent finding: no-code, internal tools and competitor-alternative terms together use **18.3% of sample spend** and produce **34.3% of subscriptions**, at **$97.31/sub**. This supports investigating intent-specific messaging; it does not establish higher LTV or future efficiency at scale.

Missing context affects decisions: enterprise traffic may need sales-assisted measurement; free traffic may have a longer paid-conversion lag; negative keywords need product relevance and account scope checks. Unknown does not mean confirmed absent.

## Reproduce the saved analysis

```bash
python3 src/compute_metrics.py
python3 src/build_diagnosis.py
python3 src/build_review_v2.py --authoring authoring/review_v2_2.json
python3 src/build_canonical.py
python3 -m unittest discover -s tests -v
```

The canonical builder reads the historical v1 artifact for provenance but uses the reviewed v2.2 interpretation for the current recommendations. Historical authored versions remain available. Rebuilding records new local run provenance; the committed demo snapshot uses repository-relative paths.

For a new dataset, use Claude Code to inspect the schemas, adapt an account profile, execute deterministic calculations, and author a new version referencing the resulting evidence. The supplied configuration includes fixture-specific reconciliation totals; this release is not a universal CSV importer. Do not reuse Braid thresholds or identity mappings silently for another account.

## Repository map

- `data/`: supplied synthetic fixtures.
- `config/`, `context/`: account mappings, confirmed facts and task scope.
- `src/`: deterministic calculations and artifact builders.
- `authoring/`: versioned Claude-authored reasoning with numeric placeholders.
- `output/`: saved example metrics, reviews and canonical UI data.
- `ui/`: dependency-free local dashboard.
- `tests/`: arithmetic, missing-data, references and artifact checks.
- `docs/`: walkthrough and operator comparison.

## Validation and limits

The Python suite checks input parsing, totals, aggregate exclusion, undefined ratios, numeric references, output completeness and canonical constraints. These checks do not establish that a marketing hypothesis is true.

Claude Code reported browser interaction checks for term selection, saved posture branches, browser persistence, safe text rendering and feedback import/export. Real-browser screen-reader behavior, the actual file-picker path and a 390px viewport were not fully verified in that headless environment. Do not run the development `?selftest=1` page in a browser profile with notes you want to preserve: it modifies test feedback.

No live Ads API, automated bidding changes, production warehouse integration, causal lift measurement or deployed backend is included. No live advertising action has been performed.

Start with the [eight-minute walkthrough](docs/INTERVIEW_WALKTHROUGH.md). The [operator comparison](docs/OPERATOR_CROSSCHECK.md) was written after the independent analysis and is not an input to it.
