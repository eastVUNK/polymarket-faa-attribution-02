# Stage 1 — Understand the competition and design v1

Date: Sat 2026-11-14 ~09:40–09:50 WIB. Deadline: Sat 2026-11-14 21:00 WIB
(2026-11-14T14:00:00Z). Status: findings only — `main.py` NOT written yet
(it comes in Stage 2, with a genuine revision in a later stage per the
transcript gate: ≥5 assistant turns, ≥1 revision of the entry file).

## 1. Competition facts (verified via make.fun API, 2026-11-14 ~09:40 WIB)

- Slug `polymarket-faa-attribution-02`, title "Forecast Polymarket's FAA
  outage attribution prices minute by minute, 4 hours ahead", $250 total.
- `status=open`, `acceptingSubmissions=true`, `harnessKind=program/v1`.
- Opened 2026-11-14T02:00:00Z (09:00 WIB), deadline 2026-11-14T14:00:00Z
  (21:00 WIB). 235 submissions at ~09:40 WIB (218 entries on the dev board).
- Payout: 1st $40, 2nd $25, 3rd $15, 4th–10th $5, 11th–100th $1.50.
  Max 10 submissions/day, 10 total; last submission before deadline is final.
- Prize needs a final loss strictly below the best house entry (house
  baseline OR house model forecast, whichever is lower) + every case valid.
- Practice (dev phase): 6 cases p00–p05, checkpoints 2026-11-12T06:00Z to
  2026-11-13T02:00Z, cut from Polymarket's "Next CEO of NVIDIA?" event —
  NOT the FAA markets. The rules state explicitly: "a practice score is no
  guide to the final."
- Final: 12 cases h00–h11, checkpoints from the deadline every 4h to +44h,
  scored on the minutes after each to +48h (or to the minute every market
  settled). Each case: 4 FAA markets (Iran / foreign actor / hack / AI
  sandbox escape), 72h of 1-minute Yes prices up to the checkpoint.
  If all 4 markets stop trading before/at the deadline: no final, no prize.
- Score: mean pinball loss in percentage points over every
  (case, market, minute, quantile 5/25/50/75/95%). Ties → faster program.
- Entry: public GitHub repo created after the competition opened
  (`repo_created_after_open`, opens_at 2026-11-14T02:00:00Z), OSI licence
  with SPDX line, `main.py` (Python 3.13) or `main.ts` (Node 22) at root,
  stdlib only, offline, deterministic (2 runs byte-identical), ≤8 s / 1 CPU /
  1024 MB per case. Transcripts required (`transcripts_present`,
  `thinking_turns` min 5 assistant turns, `thinking_revised` min 2 file
  writes, `thinking_reproduces` min 0.3, `handed_over_places: none`).

## 2. Kit structure

`GET /c/<slug>/kit` (4.8 MB tarball, verified sha256s in `kit.json`):
`RULES.txt`, `competition.yaml`, `cli/makefun.mjs`, `harness/` (harness
source), `input/NOTICE.txt` + `p00.in`–`p05.in`, `starter/` (house baseline
`main.ts` + MIT `LICENSE`). No local grader: "the server grades every
entry" — the scorer and reference data stay on the server
(`reproduce: null`). So practice numbers below come from the local
evaluator in `eval_faa.py` (same method as the nvidia-ceo work: case p0k
scored against the next case's history, p00–p04 only — p05's future is not
in the kit).

Input format: one JSON case, `schema makefun/polymarket-case/v1`, markets
with `prices` (1/min from `start` to checkpoint `at` inclusive).
Output: `/output/<id>.out`, `{"forecasts":[{"id","q":[[5 numbers] x 240]}]}`,
each row non-decreasing, in [0,1], ≤1 MiB. Invalid case = scored as all-0.5
quantiles and takes no prize.

Practice cases: p00–p02 hold 19 markets, p03 holds 23, p04–p05 hold 24.
Verified: the FAA kit's practice prices are BYTE-IDENTICAL to the
nvidia-ceo kit's (only the `competition` slug string differs). So the
nvidia-ceo findings transfer to the practice — but the FINAL is a different
event, different regime (see §4).

House baseline (starter): `q = x + z_tau * 0.0025 * sqrt(h)`, clamped,
6 decimals. Official practice loss **0.363589** (median error 0.767503,
coverage 0.949642). Local 5-case evaluator gives the baseline 0.392518 —
the gap is p05: the official 6-case score includes p05's window (to
2026-11-13T06:00Z), which is not in the kit, so local numbers are
5-case and NOT directly comparable to official ones. All comparisons below
are local-vs-local.

House model forecast (superbot one-shot, sigma + drift per market, made
once per phase) also enters and sets the prize bar together with the
baseline. It is not in the kit as data — no sigma/drift values to copy.

## 3. Practice numbers (local evaluator, p00–p04, `eval_faa.py`)

| Variant | Pinball | Med err | Cov90 |
|---|---|---|---|
| House baseline | 0.392518 | 0.8795 | 0.9382 |
| Uncentered 24h, shrink 1.00 | 0.411752 | 1.0212 | 0.8910 |
| Uncentered 24h, shrink 0.75 | 0.380547 | 0.9591 | 0.8620 |
| Recentered 24h, shrink 1.00 | 0.373793 | 0.8795 | 0.9168 |
| Recentered 24h, shrink 0.90 | 0.364878 | 0.8795 | 0.8975 |
| Recentered 24h, shrink 0.80 | 0.356891 | 0.8795 | 0.8868 |
| Recentered 24h, shrink 0.75 | 0.353518 | 0.8795 | 0.8820 |
| Recentered 24h, shrink 0.70 | 0.350534 | 0.8795 | 0.8743 |
| Recentered 24h, shrink 0.65 | 0.348065 | 0.8795 | 0.8697 |
| **Recentered 24h, shrink 0.60** | **0.345950** | 0.8795 | 0.8646 |
| Recentered 24h, shrink 0.50 | 0.343133 | 0.8795 | 0.8550 |
| Recentered 24h, shrink 0.40 | 0.342968 | 0.8795 | 0.8290 |
| Recentered 24h, shrink 0.30 | 0.346347 | 0.8795 | 0.7986 |
| Recentered 48h, shrink 0.70 | 0.359601 | 0.8795 | 0.8823 |
| Recentered 48h, shrink 0.60 | 0.354034 | 0.8795 | 0.8728 |
| Recentered 12h, shrink 0.70 | 0.338316 | 0.8795 | 0.8066 |
| Recentered 6h, shrink 0.70 | 0.342948 | 0.8795 | 0.6983 |
| Recentered 24h 0.70 + 24h drift | 0.647958 | 1.6028 | 0.3909 |
| Recentered 24h 0.60 + 24h drift | 0.655041 | 1.6028 | 0.3647 |
| Recentered 24h 0.70, floored by house band | 0.406080 | 0.8795 | 0.9714 |
| Recentered 24h 0.50, floored by house band | 0.396659 | 0.8795 | 0.9621 |
| Recentered 12h 0.70, floored by house band | 0.399247 | 0.8795 | 0.9688 |
| Recentered 24h 0.60, floored by house band | 0.400814 | 0.8795 | 0.9670 |

Notes:
- The nvidia-ceo v1 idea VERIFIES on this practice: recentered 24h
  shrink 0.70 scores 0.3505 locally (nvidia run: 0.3505) — identical,
  as expected since the prices are identical. It beats the local baseline
  by ~11%.
- Shrink curve is U-shaped with a flat bottom at 0.40–0.70
  (0.343–0.351); the minimum (~0.40–0.50) undercovers (0.83–0.86).
- Short windows (12h/6h) win on practice but undercover badly
  (0.81 / 0.70) — they fit the quiet NVIDIA window, not a jumpy market.
- Drift is catastrophic (0.65 vs 0.35): the persistence median is right;
  the 24h drift is noise. Median error is identical (0.8795) for every
  persistence-median variant, as it must be.
- Flooring the band by the house band costs +0.05 practice loss: the
  house sigma is far too wide at long horizons for this data.

## 4. Dev leaderboard context (fetched ~09:47 WIB)

218 entries on the board; best **0.251**, median 0.278, rank 50: 0.271,
rank 100: 0.276, worst 0.38. 189 entries < 0.30. House baseline/model
rows are not listed as rows in this view. Our v1 (~0.32–0.35 on the
official 6-case scale, estimated) would sit near the bottom of the
practice board — the leaders (0.251–0.26) use sub-diffusive logit
quantile models, regime gating, EWMA vol, board-sum reversion. Practice
rank pays nothing; the final does. But the gap says v1 is a
baseline-beating entry, not yet a contender.

Leader titles also warn of a trap: several leaders exploit the NVIDIA
event's structure (markets are mutually exclusive CEO candidates, prices
sum ≈ 1 — "board-sum reversion", "sum-to-1 renorm"). The FAA final's
four markets are INDEPENDENT attribution questions — they do NOT sum to
1. Any sum-to-1 trick that helps on practice is expected to HURT on the
final. Do not use it.

## 5. v1 design (to be built in Stage 2)

`main.py`, Python 3.13, stdlib only, deterministic, no network:
- Median: the market's last price at the checkpoint (persistence).
  Evidence: drift variants score 0.65; persistence median error 0.88
  beats every drifting median tried.
- Spread: for each horizon h = 1..240, the empirical quantiles of the
  realised h-minute changes over the trailing 24h (1440 min), recentered
  on their own median so the band is centred on the last price, shrunk
  by **0.60**.
- Why 0.60, not the practice minimum (0.40–0.50) or the 12h window
  (0.338): 0.60 sits mid-flat-region (0.343–0.351 across 0.40–0.70),
  coverage 0.865 is nearer the nominal 0.90, and it does not chase the
  quiet-practice minimum. The FAA final is news-driven and jumpy — the
  rules document 20-point minute jumps (Iran 0.49→0.275; AI escape
  0.215→0.02) — so a band tuned to the narrowest practice setting is the
  wrong bet for the final.
- Fallbacks: horizon with <20 realised changes → 1-minute-change
  quantiles scaled by sqrt(h), recentered the same way; market with <2
  prices → house baseline spread (sigma 0.0025). Clamp [0,1], round to
  6 decimals, enforce non-decreasing rows.
- Explicitly NOT in v1: drift on the median (catastrophic on practice);
  sum-to-1 / board-sum renorm (NVIDIA-only structure, wrong for FAA);
  house-band floor (costs +0.05 practice; jump minutes are rare in mean
  pinball — one 20-pt jump minute costs ~0.001 of mean loss, so the
  insurance is overpriced at full house width).
- Reads `$MAKEFUN_INPUT_DIR` (else `/input`), writes
  `$MAKEFUN_OUTPUT_DIR` (else `/output`), one `.out` per `.in`.

## 6. Next steps

- Stage 2: write `main.py` per §5, run on the kit practice cases,
  verify determinism (2 runs byte-identical) and runtime (<8 s/case).
- Stage 3: tune + stress — (a) jump-stress test (inject synthetic
  10–20 pt jumps into practice futures, measure how v1 vs narrower
  variants degrade); (b) per-market adaptive vol / EWMA scaling;
  (c) logit-transform for near-boundary markets (FAA prices ~0.02–0.03);
  (d) sub-diffusive spread-growth check. Only adopt a change that
  improves the stress test or the local score WITHOUT relying on
  NVIDIA-only structure.
- Then: final review, bundle transcripts, check, submit before
  21:00 WIB. (Practice rank is not the target — the final is.)
