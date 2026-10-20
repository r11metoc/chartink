# What the system learned

Updated 2026-10-20. For each scanner 144 exit rules were tried; the setup filter skips market-cap x market-regime groups that lost money (at least 20 trades).

**Walk-forward test:** every month the rule and filter were picked using only trades that had already closed, then used on that month's signals. These are the only numbers that count; the in-sample best always looks better than it is. Trades still open are valued at the last close.

**Status:** *proven* = beat the base rule on the same signals by at least 1.65 standard errors (t); *promising* = ahead but could be luck; *not better* = the base rule is kept.

## 63_30_daily

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 2111 trades, avg +2.41%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 1963 | 36% | -0.31% | -0.68% | -607,300 |  |
| Learned rule | 1963 | 43% | +1.98% | +0.98% | +3,883,400 | +2.29% (t 5.9) |
| Learned rule + filter | 1687 | 44% | +2.00% | +0.91% | +3,378,300 | +2.03% (t 5.5) |

## Bullish_Scanner

- **Learned rule:** 12% stop, target 3x risk, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 1303 trades, avg +1.83%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 1224 | 38% | -0.26% | -0.87% | -323,100 |  |
| Learned rule | 1224 | 46% | +1.23% | -0.10% | +1,509,600 | +1.50% (t 4.3) |
| Learned rule + filter | 1081 | 47% | +1.19% | -0.14% | +1,281,800 | +1.31% (t 4.0) |

## Wkly_upswing

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 1208 trades, avg +2.58%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 1125 | 38% | -0.10% | -0.66% | -111,600 |  |
| Learned rule | 1125 | 39% | +1.49% | +0.64% | +1,675,100 | +1.59% (t 3.1) |
| Learned rule + filter | 823 | 41% | +1.72% | +0.66% | +1,412,000 | +1.35% (t 3.0) |
