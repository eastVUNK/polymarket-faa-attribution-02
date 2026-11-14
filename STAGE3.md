# Stage 3 — Jump-stress test + tune

Date: Sat 2026-11-14 ~10:35–11:00 WIB. Deadline: 21:00 WIB.

## Question

v1 (shrink 0.60) was tuned on the quiet NVIDIA practice. The FAA final is
news-driven and has already jumped 20 points in a minute. Does 0.60
survive jumps, or should the band be wider?

## Method

`stress.py` (workspace, not part of the entry), two angles on the practice
cases p00–p04 (scored vs the next case):
- **A. Natural:** split scored minutes into jump minutes (|1-min move|
  ≥ 2 pts) vs calm minutes. Practice is quiet: only 96/24,960 minutes
  (0.38%) are jump minutes; biggest single move 23.6 pts (Colette Kress).
- **B. Synthetic:** inject FAA-style persistent level shifts into the
  futures AFTER the checkpoint (+/−10 and +/−20 pts from minute 120, and
  a transient +20 pts for 30 min, and an early −20 pts from minute 30).
  Forecasts are unchanged — they only see history. This is the final's
  regime: news lands, the price steps and stays.

## Results

### A. Natural jump vs calm (pinball)

| Variant | All | Jump min (n=96) | Calm min | Cov jump |
|---|---|---|---|---|
| House baseline | 0.3925 | 2.479 | 0.3845 | 0.385 |
| shrink 0.50 | 0.3431 | 2.636 | 0.3343 | 0.438 |
| **shrink 0.60 (v1)** | **0.3460** | **2.582** | **0.3373** | **0.500** |
| shrink 0.70 | 0.3505 | 2.540 | 0.3421 | 0.542 |
| shrink 0.80 | 0.3569 | 2.506 | 0.3486 | 0.552 |

### B. Synthetic persistent shifts (pinball, all markets shifted)

| Variant | +0.10 | −0.10 | +0.20 | −0.20 | Transient +0.20 |
|---|---|---|---|---|---|
| House baseline | 1.992 | 0.699 | 4.484 | 0.967 | 1.439 |
| shrink 0.50 | 2.348 | 0.679 | 4.815 | 0.946 | 1.464 |
| **shrink 0.60 (v1)** | **2.308** | **0.665** | **4.758** | **0.930** | **1.452** |
| shrink 0.70 | 2.272 | 0.653 | 4.703 | 0.915 | 1.441 |
| shrink 0.80 | 2.242 | 0.644 | 4.654 | 0.902 | 1.433 |

Every widening helps on jumps and hurts on calm minutes, monotonically.
The +shifts are the dangerous direction: the house baseline beats v1
there (1.99 vs 2.31 at +0.10) because a price that steps up 10 pts sits
above a narrow band for 120 minutes. The −shifts are muted by clipping
at 0 (many practice markets sit near 0.01–0.05 and cannot fall 10 pts).

### C. Asymmetric shrink (upper tail wider)

Upper 0.80 / lower 0.60: natural 0.3584 (worse than 0.3460), +0.10
synthetic 2.235 (better than 2.308), −0.10 synthetic 0.682 (worse than
0.665). Widening the upper tail buys +shift robustness but pays on calm
minutes AND on −shifts (a higher q75/q95 costs when the price falls).
Same trade-off, no free lunch.

### D. Volatility clustering (does a jumpy trailing 24h predict a jumpy future?)

Yes, but weakly in absolute terms: markets above the median trailing
jump count have a 0.60% future jump rate vs 0.17% below; the most
volatile quartile by trailing mean |1-min change| has 1.30% vs 0.00%
for the calmest quartile. An adaptive variant (shrink 0.80 for the
most volatile quartile, 0.60 elsewhere) scored 0.3506 natural (worse
than v1's 0.3460) and 2.291 on the +0.10 synthetic (better than 2.308).
It loses on the world that actually happens ~95% of the time.

## Decision: KEEP shrink 0.60 — no main.py change

The breakeven math: going 0.60 → 0.70 costs +0.005 per calm minute and
saves ~0.036 per displaced minute, so it only wins if >~12% of final
minutes sit in a displaced regime. Going 0.60 → 0.80 needs ~15%.
A realistic final has 1–3 attribution-news jumps; each one displaces
at most one case's window for one market (the next case's checkpoint
resets the median to the new level), i.e. ~2–6% of scored minutes.
Below breakeven — wider loses in expectation.

Two more reasons 0.60 is the right middle:
- It is minimax across worlds: it gives up only ~0.003 to shrink 0.50
  in a fully quiet final, and ~0.01–0.02 to wider variants in an
  every-case-jumpy final, while beating both in the middle world.
- The empirical quantiles ARE the jump adaptation: a market that jumped
  in its trailing 24h already carries those jumps in its h-step
  distribution, so its band is already wide. Extra widening double-counts
  them — that is why the adaptive variant lost on natural data.

`main.py` is therefore unchanged in Stage 3 (deliberately: every
candidate revision tested made the expected final score worse). HEAD
stays 16bcc817. Next: Stage 4 final review + sign-off before submitting.
