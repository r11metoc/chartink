# What the system learned

Updated 2026-10-10. For each scanner 144 exit rules were tried; the setup filter skips market-cap x market-regime groups that lost money (at least 20 trades).

**Walk-forward test:** every month the rule and filter were picked using only trades that had already closed, then used on that month's signals. These are the only numbers that count; the in-sample best always looks better than it is. Trades still open are valued at the last close.

**Status:** *proven* = beat the base rule on the same signals by at least 1.65 standard errors (t); *promising* = ahead but could be luck; *not better* = the base rule is kept.

## 63_30_daily

- **Best candidate:** 12% stop, target 3x risk, out after 40 days - did worse on unseen months, so the base rule is kept: stop at candle low (2-8%), target 2x risk, out after 20 days
- **Skips:** nothing
- **Status:** not better (best candidate in sample: 267 trades, avg +1.95%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 80 | 22% | -3.26% | -2.20% | -260,500 |  |
| Learned rule | 80 | 25% | -5.59% | -3.22% | -447,200 | -2.33% (t -2.0) |
| Learned rule + filter | 57 | 23% | -6.16% | -3.46% | -351,200 | -1.13% (t -1.1) |

## Bullish_Scanner

- **Learned rule:** 12% stop, target 2x risk, out after 40 days
- **Skips:** nothing
- **Status:** promising (best candidate in sample: 159 trades, avg +3.09%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 89 | 40% | +0.76% | +2.01% | +67,600 |  |
| Learned rule | 89 | 45% | +0.90% | +4.79% | +80,400 | +0.14% (t 0.1) |
| Learned rule + filter | 89 | 45% | +0.90% | +4.79% | +80,400 | +0.14% (t 0.1) |

## Wkly_upswing

- **Learned rule:** 12% stop, target 3x risk, out after 40 days
- **Skips:** nothing
- **Status:** promising (best candidate in sample: 513 trades, avg +2.08%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 387 | 36% | -0.49% | -0.52% | -188,200 |  |
| Learned rule | 387 | 39% | +0.60% | +0.36% | +233,100 | +1.09% (t 1.6) |
| Learned rule + filter | 341 | 39% | +0.46% | +0.26% | +155,200 | +0.89% (t 1.4) |
