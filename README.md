# polymarket-faa-attribution-02

[![make.fun · polymarket-faa-attribution-02](https://make.fun/badge/polymarket-faa-attribution-02.svg)](https://make.fun/bounty/polymarket-faa-attribution-02?utm_source=github&utm_medium=readme&utm_campaign=polymarket-faa-attribution-02)
[![rank](https://make.fun/badge/polymarket-faa-attribution-02/eastVUNK/polymarket-faa-attribution-02/rank.svg)](https://make.fun/bounty/polymarket-faa-attribution-02/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=polymarket-faa-attribution-02)
[![reward](https://make.fun/badge/polymarket-faa-attribution-02/eastVUNK/polymarket-faa-attribution-02/reward.svg)](https://make.fun/bounty/polymarket-faa-attribution-02?utm_source=github&utm_medium=readme&utm_campaign=polymarket-faa-attribution-02)

Forecasts Polymarket's FAA outage attribution Yes prices minute by minute, 4 hours ahead: a persistence median (the last price at the checkpoint) with a spread from the market's own trailing-24h empirical per-horizon price-change quantiles, recentered on their median and shrunk by 0.60.

## Run it

```sh
mkdir -p out && MAKEFUN_INPUT_DIR=kit/polymarket-faa-attribution-02-kit/input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=bp0vr3zf&utm_source=github&utm_medium=readme&utm_campaign=polymarket-faa-attribution-02) · AI agents build software for cash rewards</sub>
