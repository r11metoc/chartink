# What the system learned

Updated 2026-10-28. For each scanner 144 exit rules were tried; the setup filter skips market-cap x market-regime groups that lost money (at least 20 trades).

**Walk-forward test:** every month the rule and filter were picked using only trades that had already closed, then used on that month's signals. These are the only numbers that count; the in-sample best always looks better than it is. Trades still open are valued at the last close.

**Status:** *proven* = beat the base rule on the same signals by at least 1.65 standard errors (t); *promising* = ahead but could be luck; *not better* = the base rule is kept.

## 63_30_daily

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 1435 trades, avg +4.33%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 1301 | 33% | -0.26% | -0.57% | -333,100 |  |
| Learned rule | 1301 | 53% | +3.83% | +1.78% | +4,983,100 | +4.09% (t 9.9) |
| Learned rule + filter | 1111 | 51% | +3.46% | +1.71% | +3,844,600 | +3.21% (t 8.2) |

## Bullish_Scanner

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 4179 trades, avg +4.57%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 4118 | 42% | +0.73% | +0.21% | +2,988,200 |  |
| Learned rule | 4118 | 56% | +4.43% | +2.37% | +18,253,700 | +3.71% (t 16.5) |
| Learned rule + filter | 3984 | 55% | +4.44% | +2.42% | +17,670,600 | +3.57% (t 16.0) |

## Wkly_upswing

- **Learned rule:** stop at candle low (2-12%), no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 413 trades, avg +1.99%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 350 | 42% | +0.42% | -0.05% | +146,600 |  |
| Learned rule | 350 | 41% | +2.02% | +1.17% | +707,300 | +1.60% (t 2.1) |
| Learned rule + filter | 274 | 41% | +1.28% | +0.75% | +349,500 | +0.58% (t 0.9) |
