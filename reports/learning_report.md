# What the system learned

Updated 2026-10-21. For each scanner 144 exit rules were tried; the setup filter skips market-cap x market-regime groups that lost money (at least 20 trades).

**Walk-forward test:** every month the rule and filter were picked using only trades that had already closed, then used on that month's signals. These are the only numbers that count; the in-sample best always looks better than it is. Trades still open are valued at the last close.

**Status:** *proven* = beat the base rule on the same signals by at least 1.65 standard errors (t); *promising* = ahead but could be luck; *not better* = the base rule is kept.

## 63_30_daily

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 4218 trades, avg +2.86%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 3995 | 35% | -0.27% | -0.68% | -1,097,800 |  |
| Learned rule | 3995 | 48% | +2.47% | +1.07% | +9,878,200 | +2.75% (t 11.6) |
| Learned rule + filter | 3382 | 48% | +2.44% | +1.01% | +8,266,400 | +2.34% (t 10.5) |

## Bullish_Scanner

- **Learned rule:** 12% stop, target 3x risk, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 1303 trades, avg +1.83%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 1227 | 37% | -0.28% | -0.87% | -344,600 |  |
| Learned rule | 1227 | 45% | +1.18% | -0.11% | +1,446,800 | +1.46% (t 4.2) |
| Learned rule + filter | 1084 | 46% | +1.15% | -0.15% | +1,242,400 | +1.29% (t 3.9) |

## Wkly_upswing

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 1209 trades, avg +2.57%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 1125 | 38% | -0.11% | -0.66% | -120,000 |  |
| Learned rule | 1125 | 39% | +1.46% | +0.63% | +1,639,400 | +1.56% (t 3.0) |
| Learned rule + filter | 823 | 41% | +1.67% | +0.64% | +1,376,300 | +1.33% (t 3.0) |
