# Step 2: account context and search-term diagnosis

Requires a passing `output/step1/` (run `python3 src/compute_metrics.py` first).

## Files

| File | Role | Who edits |
|---|---|---|
| `config/account_context.json` | business model (known facts vs `unknown`), strategic posture (`selected: null` until chosen), allowable ($181, from the brief), benchmark (scope cost/sub from step 1, not a target) | operator |
| `authoring/diagnosis_v1.json` | model-authored interpretation; numbers are `{placeholders}` only | model (new versions as new files) |
| `src/build_diagnosis.py` | fills placeholders from step 1, validates every term_id / placeholder / benchmark, renders outputs | code |
| `output/step2/diagnosis.json` | structured result; each term has `final_decision: null` and `human_amendments: null` for the next phase | generated |
| `output/step2/diagnosis.md` | readable version | generated |

## Run

```bash
python3 src/build_diagnosis.py                 # -> output/step2/
python3 src/build_diagnosis.py --output-dir /path/for/repeat
python3 -m unittest tests.test_build_diagnosis tests.test_compute_metrics -v
```

Exit `2` with a message if: step 1 checks did not pass, a term_id in the authoring file is not in step 1, a step 1 term has no diagnosis, a search_term label disagrees, a placeholder is unknown, or the config benchmark drifts from step 1.

## Guarantees

- Every figure in the diagnosis is filled from `output/step1/` or `config/account_context.json`; none is typed by hand.
- Posture is not chosen and the allowable is not adjusted; each term shows handling under both `scale` and `maintain_efficiency`.
- Negatives are conditional (no quota); additions/isolations require a coverage check; nothing is an import-ready Editor file (no campaign/ad-group IDs).

## Review v2 (independent baseline check)

`authoring/review_v2.json` + `src/build_review_v2.py` → `output/step2/review_v2.{json,md}`. Written from step 1, the account context and methodology priors only; no operator answers; v1 files are not read for content or modified. Adds computed group aggregates, Spearman rank correlations and break-even subs at the allowable, all filled from step 1.

```bash
python3 src/build_review_v2.py
python3 -m unittest tests.test_build_review_v2 -v
```

## Review v2.1 (correction pass)

`authoring/review_v2_1.json` → `output/step2/review_v2_1.{json,md}` plus `output/step2/review_v2_1_changelog.md`. Same builder, same inputs, no operator answers; v2 and v1 preserved.

```bash
python3 src/build_review_v2.py --authoring authoring/review_v2_1.json
```

## Review v2.2 and canonical artifact (UI-ready)

```bash
python3 src/build_review_v2.py --authoring authoring/review_v2_2.json   # -> output/step2/review_v2_2.{json,md}
python3 src/build_canonical.py                                          # -> output/canonical/search_ops_analysis.json
python3 -m unittest tests.test_build_canonical tests.test_build_review_v2 tests.test_build_diagnosis tests.test_compute_metrics
```
Schema: `output/canonical/SCHEMA.md`. Change logs: `output/step2/review_v2_1_changelog.md`, `output/step2/review_v2_2_changelog.md`.
