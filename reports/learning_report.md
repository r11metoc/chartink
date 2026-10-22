# What the system learned

Updated 2026-10-22. For each scanner 144 exit rules were tried; the setup filter skips market-cap x market-regime groups that lost money (at least 20 trades).

**Walk-forward test:** every month the rule and filter were picked using only trades that had already closed, then used on that month's signals. These are the only numbers that count; the in-sample best always looks better than it is. Trades still open are valued at the last close.

**Status:** *proven* = beat the base rule on the same signals by at least 1.65 standard errors (t); *promising* = ahead but could be luck; *not better* = the base rule is kept.

## 63_30_daily

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 4720 trades, avg +2.93%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 4493 | 32% | -0.49% | -0.77% | -2,192,800 |  |
| Learned rule | 4493 | 49% | +2.47% | +1.01% | +11,101,400 | +2.96% (t 13.3) |
| Learned rule + filter | 4115 | 50% | +2.66% | +0.94% | +10,955,600 | +2.93% (t 13.7) |

## Bullish_Scanner

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 4176 trades, avg +4.58%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 4117 | 42% | +0.73% | +0.21% | +3,011,900 |  |
| Learned rule | 4117 | 56% | +4.44% | +2.37% | +18,261,900 | +3.70% (t 16.5) |
| Learned rule + filter | 3941 | 55% | +4.39% | +2.45% | +17,316,500 | +3.47% (t 15.6) |

## Wkly_upswing

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 746 trades, avg +3.03%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 688 | 39% | +0.03% | -0.61% | +17,600 |  |
| Learned rule | 688 | 42% | +1.94% | +0.89% | +1,332,800 | +1.91% (t 2.8) |
| Learned rule + filter | 507 | 42% | +1.52% | +0.32% | +771,400 | +1.10% (t 2.0) |
