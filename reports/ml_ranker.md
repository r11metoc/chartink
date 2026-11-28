# ML signal ranker

Trained 2026-11-28 on 2,616 closed trades (2017-09-18 to 2026-11-27) by `scripts/ranker.py`.

**Status: ON**: it decides which signals get a free slot first.

## Walk-forward test (each year scored by a model trained only on earlier years)

1,937 trades. AUC 0.514 (0.5 = coin toss). Average return per trade by score, lowest fifth to highest: +0.9%, +2.4%, +3.7%, +4.3%, +3.3%.

| ₹10L, 15 slots | Fixed order | ML order |
|---|---|---|
| Per year | 24.2% | 26.6% |
| 2022-2023 | 42.8% | 43.6% |
| 2024-2026 | 13.1% | 16.4% |
| Worst fall | -11.1% | -10.2% |

| Year | Trades | Top half | Bottom half |
|---|---|---|---|
| 2022 | 249 | +0.00% | -0.79% |
| 2023 | 507 | +11.73% | +6.27% |
| 2024 | 841 | +1.80% | +0.87% |
| 2025 | 154 | +4.85% | +0.02% |
| 2026 | 186 | -2.57% | -0.97% |

## Checks

- ✓ beats in first half
- ✓ beats in second half
- ✓ worst fall no more than 1 pt worse
- ✓ top half beat bottom half in 2/3 of years

## What it leans on (standardised weights; + = more likely to work)

- RSI(14): +0.14
- distance above the 50-day average: -0.12
- traded value (size/liquidity): -0.11
- distance above the 200-day average: -0.10
- smallcap: -0.10
- move on the signal day: +0.09
- daily range (ATR %): +0.09
- scanner 63_30_daily: +0.08
- volume vs its 20-day average: -0.07
- Nifty vs its 50-day average: +0.07

Tested 13 Nov 2026 and rejected: gradient-boosted trees (AUC 0.48-0.49, worse portfolios), the repeat/confluence counts (no gain). With 60 random orders the portfolio ranged 21-30% a year (median 25%), so a few points either way can be luck: the ranker must win in both halves, every week it retrains.
