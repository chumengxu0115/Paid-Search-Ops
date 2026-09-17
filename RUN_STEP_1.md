# Step 1: deterministic metrics and checks

Standard library only (Python 3.9+). Inputs are read-only; every run rewrites `output/step1/`.

## Run

```bash
cd <project root>
python3 src/compute_metrics.py                      # defaults: data/*.csv, context/braid-confirmed.json, config/step1.json -> output/step1
python3 src/compute_metrics.py --output-dir /path/to/other   # repeatability check
```

Options: `--search-terms`, `--channels`, `--context`, `--config`, `--output-dir`. Defaults resolve relative to the project root, not the shell's cwd.

Exit codes: `0` all checks pass · `1` a reconciliation check failed (outputs still written) · `2` input rejected (message on stderr, nothing written).

## Test

```bash
python3 -m unittest tests.test_compute_metrics -v
```

## Outputs

| File | Deterministic | Content |
|---|---|---|
| `metrics_search_terms.csv` | yes | per-term ratios, recomputed vs supplied cost/sub, sample shares, ratio to $181 allowable; sorted by cost |
| `metrics_channels.csv` | yes | per-channel Q2 recomputed vs supplied, QoQ vs supplied Q1, allowable gap, shares; `Paid total` is `is_aggregate=true`, unranked, excluded from sums/shares |
| `scope_summary.json` | yes | three levels (Google Non-Brand / ai-app-builder scope / nine-term sample) + labelled remainder by subtraction |
| `checks.json` | yes | passes, failures, warnings, blocked decision checks, missing-data records with the decision each limits |
| `run_log.json` | no (timestamps) | input/context/config/implementation SHA-256, command, Python version, duration |

Empty cell / `null` means undefined or unavailable, never zero. Supplied values are never altered; a mismatch appears in `warnings` with both values.

## Config (`config/step1.json`)

Column mapping, `money_tolerance` (0.005 = half cent), `coverage_tolerance` (0.01 for the approximate 65%), expected reconciliation totals, aggregate label, and operator-owned `thresholds` that are intentionally `null`. Null thresholds only add `blocked` entries; they never stop descriptive metrics.
