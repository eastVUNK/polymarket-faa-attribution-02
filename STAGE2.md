# Stage 2 — Write main.py and verify it

Date: Sat 2026-11-14 ~10:30–10:40 WIB. Deadline: 21:00 WIB.

## Implementation

`main.py` (Python 3.13, stdlib only, deterministic, no network), exactly per
the Stage 1 design:
- Median: last price at the checkpoint (persistence). No drift.
- Spread: empirical quantiles of realised h-minute changes over the
  trailing 24h (1440 min), recentered on their own median, shrink **0.60**.
- Fallbacks: horizon with <20 realised changes → 1-minute-change quantiles
  × sqrt(h), recentered; market with <2 prices → house baseline spread
  (sigma 0.0025). Clamp [0,1], round 6 decimals, monotone rows enforced.
- No sum-to-1 renorm (FAA markets independent), no house-band floor.
- Reads `$MAKEFUN_INPUT_DIR` (else `/input`), writes `$MAKEFUN_OUTPUT_DIR`
  (else `/output`), one `.out` per `.in`.

## Verification (practice data, local evaluator)

- Format: OK — 6 cases, all markets present, 240 rows × 5 quantiles,
  monotone, in [0,1], every file ≤1 MiB.
- **main.py v1: pinball 0.345950, med_err 0.8795, cov90 0.8646** — exactly
  the Stage 1 eval prediction for recentered 24h shrink 0.60 (0.345950).
  The design holds with zero deviation: the shipped code reproduces the
  evaluated variant bit for bit in score terms.
- House baseline (same local scorer): pinball 0.392518, med_err 0.8795,
  cov90 0.9382. **v1 is 11.9% better than the baseline locally.**
  (Official 6-case baseline is 0.363589; local is 5-case because p05's
  future is not in the kit.)
- Determinism: two full runs (`run1/` vs `run2/`) byte-identical.
- Runtime per case (single-case invocations, as the grader runs them):
  CPU 0.46–1.03 s (p00 0.46, p03 0.80, p04 0.97, p05 1.03) — well under
  the 8 s cap. Wall clock on this shared VM reads up to 5.4 s because of
  descheduling (wall ≈ 5× CPU here); the CPU figure is the real budget
  and leaves ~8× headroom. Final cases hold only 4 markets (vs up to 24
  in practice), so they will be faster still. No optimisation needed.

## Verdict

v1 holds as designed. It beats the house baseline by ~12% locally but
would sit near the bottom of the practice board (best 0.251, rank-100
0.276) — practice rank pays nothing, so the next work is Stage 3:
jump-stress test + tune for the FINAL regime (jumpy, news-driven,
4 independent markets), not for the practice board.
