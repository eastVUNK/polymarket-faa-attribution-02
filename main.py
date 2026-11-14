"""Forecast Polymarket's FAA outage attribution Yes prices, 4 hours ahead.

Entry for make.fun bounty polymarket-faa-attribution-02 (program/v1).

Method (v1): persistence median + empirical per-horizon spread.
  - Median: the market's last price at the checkpoint. Short-horizon
    prediction-market prices are close to a martingale: on the practice
    cases the persistence median's error (0.88 points) beat every drifting
    median tried, and adding a 24h drift to the median was catastrophic
    (local pinball 0.65 vs 0.35). The median does not drift.
  - Spread: for each horizon h = 1..240, the forecast band comes from the
    market's own recent history, not from a random-walk formula. Take the
    last 24 hours (1440 minutes) of 1-minute prices and, for each h, the
    empirical quantiles of the realised h-minute changes p[t+h] - p[t]
    over that window. The quantiles are recentered on their own median,
    so the band is centred on the last price, and shrunk by 0.60.
  - Why not the textbook random walk: these prices are step functions
    (flat for minutes, then a tick, sometimes a jump) and jumps partly
    revert. A fixed sigma times sqrt(h) is far too wide here: on the
    practice cases the house baseline scores 0.393 locally (0.363589
    officially over all six cases) with 94% coverage, while the empirical
    h-step distribution captures the real shape: narrow for quiet minutes,
    wide where the market actually jumps, and it stops growing like
    sqrt(h) once the horizon passes the market's mean-reversion scale.
  - Why shrink 0.60: the empirical quantiles are computed from heavily
    overlapping windows, so one jumpy day is counted hundreds of times
    and the raw band overstates the dispersion. Shrinking toward the
    median corrects that. On the practice cases (p00-p04, scored against
    the next case's history) the shrink curve is flat-bottomed at
    0.40-0.70 (0.343 at 0.40-0.50, 0.346 at 0.60, 0.351 at 0.70, 0.374
    at 1.00) while the baseline scores 0.393. 0.60 sits in the middle of
    that flat region rather than at the practice minimum, so the choice
    is not tuned to one sample — and it matters, because the final is a
    different event: the FAA markets are news-driven and have already
    jumped 20 points in a minute (Iran 0.49 -> 0.275; AI sandbox escape
    0.215 -> 0.02). A band tuned to the narrowest practice setting
    (shrink 0.40, or a 12h window at 0.338 with 0.81 coverage) would
    undercover exactly when the final jumps. Coverage at 0.60 is 0.865,
    nearer the nominal 0.90 than the minimum-chasing settings.
  - What is deliberately NOT here: no drift on the median (catastrophic
    on practice); no sum-to-1 / board-sum renorm — the practice event's
    markets are mutually exclusive candidates whose prices sum to ~1,
    but the final's four FAA markets are INDEPENDENT attribution
    questions and do not sum to 1, so a renorm that helps on practice
    would hurt on the final; no house-band floor — flooring the band by
    the house sigma costs +0.05 pinball on practice, and a single 20-point
    jump minute costs only ~0.001 of mean pinball, so that insurance is
    overpriced at full house width (Stage 3 stress-tests this properly).
  - Short histories: a market with too few minutes for a horizon falls
    back to the quantiles of its 1-minute changes scaled by sqrt(h),
    recentered the same way; a market with under two prices falls back
    to the house baseline's spread. Practice is no guide to the final,
    which is scored on prices nobody had seen: nothing here is fitted
    to a single case.

Reads every <id>.in in $MAKEFUN_INPUT_DIR (else /input), writes one
<id>.out per case to $MAKEFUN_OUTPUT_DIR (else /output). Python 3.13,
standard library only, no network, no randomness: two runs on the same
case write byte-identical output.
"""

import json
import math
import os

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

# The quantile levels the competition scores, in row order.
QUANTILES = [0.05, 0.25, 0.5, 0.75, 0.95]
# Minutes of history used for the empirical change distribution.
VOL_WINDOW = 1440
# Shrinkage of the empirical band toward the median (see module docstring).
SHRINK = 0.60
# Fallback spread (house baseline's) for markets with under two prices.
FALLBACK_SIGMA = 0.0025
FALLBACK_Z = [-1.644854, -0.67449, 0.0, 0.67449, 1.644854]
# A horizon needs at least this many realised changes to trust its quantiles.
MIN_CHANGES = 20


def round6(x):
    """Clamp to [0, 1] and round to 6 decimals (0, never -0)."""
    v = round(min(1.0, max(0.0, x)) * 1e6) / 1e6
    return v + 0.0


def _quantile(sorted_vals, tau):
    """Linear-interpolation quantile of an already sorted list."""
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    pos = tau * (n - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, n - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


def horizon_offsets(prices, horizon):
    """Per-horizon quantile offsets around the last price, recentered.

    Returns a list of `horizon` rows; row h-1 holds the five offsets for
    the minute h after the checkpoint (offsets[2] is 0 by construction).
    """
    n = len(prices)
    if n < 2:
        return [
            [z * FALLBACK_SIGMA * math.sqrt(h) for z in FALLBACK_Z]
            for h in range(1, horizon + 1)
        ]
    window = prices[-VOL_WINDOW:] if n > VOL_WINDOW else prices
    m = len(window)
    # 1-minute changes, for the short-history fallback below.
    one_min = sorted(window[i + 1] - window[i] for i in range(m - 1))
    one_min_q = [_quantile(one_min, tau) for tau in QUANTILES]
    one_min_med = one_min_q[2]
    rows = []
    for h in range(1, horizon + 1):
        if m - h >= MIN_CHANGES:
            changes = sorted(window[t + h] - window[t] for t in range(m - h))
            qs = [_quantile(changes, tau) for tau in QUANTILES]
            med = qs[2]
            rows.append([q - med for q in qs])
        else:
            root = math.sqrt(h)
            rows.append([(q - one_min_med) * root for q in one_min_q])
    return rows


def forecast_market(prices, horizon):
    """Horizon rows x 5 quantiles around the market's last price."""
    x = prices[-1] if prices else 0.5
    offsets = horizon_offsets(prices, horizon)
    rows = []
    for h in range(horizon):
        row = [round6(x + SHRINK * off) for off in offsets[h]]
        row[2] = round6(x)
        # Rounding can only break monotonicity by a hair; enforce it.
        for j in range(1, len(row)):
            if row[j] < row[j - 1]:
                row[j] = row[j - 1]
        rows.append(row)
    return rows


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    names = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".in"))
    for name in names:
        case_id = name[: -len(".in")]
        with open(os.path.join(INPUT_DIR, name), "r", encoding="utf-8") as fh:
            case = json.load(fh)
        if list(case.get("quantiles", [])) != QUANTILES:
            raise ValueError(
                "%s asks for quantiles %r, not %r"
                % (name, case.get("quantiles"), QUANTILES)
            )
        horizon = int(case["horizon_minutes"])
        forecasts = [
            {"id": m["id"], "q": forecast_market(m["prices"], horizon)}
            for m in case["markets"]
        ]
        out = json.dumps({"forecasts": forecasts}, separators=(",", ":")) + "\n"
        with open(
            os.path.join(OUTPUT_DIR, case_id + ".out"), "w", encoding="utf-8"
        ) as fh:
            fh.write(out)


if __name__ == "__main__":
    main()
