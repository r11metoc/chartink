# What the system learned

Updated 2026-10-23. For each scanner 144 exit rules were tried; the setup filter skips market-cap x market-regime groups that lost money (at least 20 trades).

**Walk-forward test:** every month the rule and filter were picked using only trades that had already closed, then used on that month's signals. These are the only numbers that count; the in-sample best always looks better than it is. Trades still open are valued at the last close.

**Status:** *proven* = beat the base rule on the same signals by at least 1.65 standard errors (t); *promising* = ahead but could be luck; *not better* = the base rule is kept.

## 63_30_daily

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 1435 trades, avg +4.33%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 1300 | 34% | -0.25% | -0.57% | -329,200 |  |
| Learned rule | 1300 | 53% | +3.82% | +1.77% | +4,961,900 | +4.07% (t 9.8) |
| Learned rule + filter | 1109 | 51% | +3.45% | +1.71% | +3,824,400 | +3.20% (t 8.1) |

## Bullish_Scanner

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 4176 trades, avg +4.58%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 4117 | 42% | +0.73% | +0.21% | +2,984,800 |  |
| Learned rule | 4117 | 56% | +4.41% | +2.35% | +18,154,400 | +3.68% (t 16.4) |
| Learned rule + filter | 3941 | 55% | +4.37% | +2.43% | +17,208,900 | +3.45% (t 15.5) |

## Wkly_upswing

- **Learned rule:** stop at candle low (2-12%), no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 412 trades, avg +2.03%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 350 | 42% | +0.41% | -0.05% | +144,100 |  |
| Learned rule | 350 | 41% | +1.99% | +1.17% | +696,800 | +1.58% (t 2.1) |
| Learned rule + filter | 281 | 41% | +1.21% | +0.59% | +339,200 | +0.56% (t 0.8) |
