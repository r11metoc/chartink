# What the system learned

Updated 2026-10-17. For each scanner 144 exit rules were tried; the setup filter skips market-cap x market-regime groups that lost money (at least 20 trades).

**Walk-forward test:** every month the rule and filter were picked using only trades that had already closed, then used on that month's signals. These are the only numbers that count; the in-sample best always looks better than it is. Trades still open are valued at the last close.

**Status:** *proven* = beat the base rule on the same signals by at least 1.65 standard errors (t); *promising* = ahead but could be luck; *not better* = the base rule is kept.

## 63_30_daily

- **Best candidate:** 12% stop, target 3x risk, out after 40 days - did worse on unseen months, so the base rule is kept: stop at candle low (2-8%), target 2x risk, out after 20 days
- **Skips:** nothing
- **Status:** not better (best candidate in sample: 273 trades, avg +1.79%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 80 | 21% | -3.41% | -2.42% | -273,100 |  |
| Learned rule | 80 | 22% | -5.74% | -3.62% | -459,400 | -2.33% (t -2.0) |
| Learned rule + filter | 57 | 23% | -6.36% | -3.93% | -362,600 | -1.12% (t -1.0) |

## Bullish_Scanner

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** promising (best candidate in sample: 158 trades, avg +2.77%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 91 | 41% | +0.66% | +1.72% | +59,600 |  |
| Learned rule | 91 | 46% | +0.87% | +4.12% | +79,300 | +0.22% (t 0.2) |
| Learned rule + filter | 91 | 46% | +0.87% | +4.12% | +79,300 | +0.22% (t 0.2) |

## Wkly_upswing

- **Learned rule:** 12% stop, target 3x risk, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 515 trades, avg +2.05%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 389 | 37% | -0.49% | -0.53% | -189,900 |  |
| Learned rule | 389 | 39% | +0.65% | +0.36% | +251,400 | +1.13% (t 1.7) |
| Learned rule + filter | 341 | 39% | +0.46% | +0.25% | +155,300 | +0.89% (t 1.4) |
