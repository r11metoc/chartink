# What the system learned

Updated 2026-10-22. For each scanner 144 exit rules were tried; the setup filter skips market-cap x market-regime groups that lost money (at least 20 trades).

**Walk-forward test:** every month the rule and filter were picked using only trades that had already closed, then used on that month's signals. These are the only numbers that count; the in-sample best always looks better than it is. Trades still open are valued at the last close.

**Status:** *proven* = beat the base rule on the same signals by at least 1.65 standard errors (t); *promising* = ahead but could be luck; *not better* = the base rule is kept.

## 63_30_daily

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 1434 trades, avg +4.37%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 1299 | 33% | -0.25% | -0.57% | -329,300 |  |
| Learned rule | 1299 | 54% | +3.87% | +1.80% | +5,032,600 | +4.13% (t 10.0) |
| Learned rule + filter | 1098 | 51% | +3.44% | +1.68% | +3,779,100 | +3.16% (t 8.1) |

## Bullish_Scanner

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 4173 trades, avg +4.59%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 4117 | 42% | +0.73% | +0.21% | +3,011,200 |  |
| Learned rule | 4117 | 56% | +4.44% | +2.37% | +18,281,100 | +3.71% (t 16.6) |
| Learned rule + filter | 3941 | 55% | +4.40% | +2.45% | +17,335,700 | +3.48% (t 15.6) |

## Wkly_upswing

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 743 trades, avg +3.05%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 688 | 39% | +0.04% | -0.60% | +25,400 |  |
| Learned rule | 688 | 42% | +1.96% | +0.91% | +1,351,500 | +1.93% (t 2.9) |
| Learned rule + filter | 507 | 42% | +1.56% | +0.35% | +790,100 | +1.11% (t 2.0) |
