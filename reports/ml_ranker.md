# ML signal ranker

Trained 2026-11-13 on 6,487 closed trades (2019-02-11 to 2026-11-06) by `scripts/ranker.py`.

**Status: ON**: it decides which signals get a free slot first.

## Walk-forward test (each year scored by a model trained only on earlier years)

6,114 trades. AUC 0.511 (0.5 = coin toss). Average return per trade by score, lowest fifth to highest: +3.8%, +2.9%, +4.4%, +3.9%, +6.3%.

| ₹10L, 15 slots | Fixed order | ML order |
|---|---|---|
| Per year | 30.3% | 35.8% |
| 2020-2022 | 40.7% | 41.8% |
| 2023-2026 | 22.8% | 31.4% |
| Worst fall | -9.2% | -7.1% |

| Year | Trades | Top half | Bottom half |
|---|---|---|---|
| 2020 | 343 | +1.19% | +6.45% |
| 2021 | 1093 | +6.56% | +3.36% |
| 2022 | 591 | +1.43% | -1.33% |
| 2023 | 1702 | +9.54% | +8.52% |
| 2024 | 1363 | +2.83% | -0.36% |
| 2025 | 561 | +3.34% | +0.00% |
| 2026 | 461 | +3.23% | +2.31% |

## Checks

- ✓ beats in first half
- ✓ beats in second half
- ✓ worst fall no more than 1 pt worse
- ✓ top half beat bottom half in 2/3 of years

## What it leans on (standardised weights; + = more likely to work)

- traded value (size/liquidity): -0.23
- distance above the 200-day average: -0.19
- nearness to the 52-week high: -0.12
- move on the signal day: +0.10
- largecap: +0.09
- smallcap: -0.08
- Nifty's last 20 days: +0.08
- up days in the last 10: +0.08
- last 5 days' return: +0.08
- scanner 63_30_daily: -0.07

Tested 13 Nov 2026 and rejected: gradient-boosted trees (AUC 0.48-0.49, worse portfolios), the repeat/confluence counts (no gain). With 60 random orders the portfolio ranged 21-30% a year (median 25%), so a few points either way can be luck: the ranker must win in both halves, every week it retrains.
