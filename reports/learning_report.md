# What the system learned

Updated 2026-10-03. For each scanner 144 exit rules were tried; the setup filter skips market-cap x market-regime groups that lost money (at least 20 trades).

**Walk-forward test:** every month the rule and filter were picked using only trades that had already closed, then used on that month's signals. These are the only numbers that count; the in-sample best always looks better than it is. Trades still open are valued at the last close.

**Status:** *proven* = beat the base rule on the same signals by at least 1.65 standard errors (t); *promising* = ahead but could be luck; *not better* = the base rule is kept.

## 63_30_daily

- **Best candidate:** 12% stop, target 2x risk, out after 40 days - did worse on unseen months, so the base rule is kept: stop at candle low (2-8%), target 2x risk, out after 20 days
- **Skips:** nothing
- **Status:** not better (best candidate in sample: 259 trades, avg +1.85%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 79 | 24% | -2.90% | -1.87% | -229,000 |  |
| Learned rule | 79 | 28% | -4.41% | -2.07% | -348,100 | -1.51% (t -1.3) |
| Learned rule + filter | 56 | 27% | -4.75% | -2.09% | -265,700 | -0.46% (t -0.4) |

## Bullish_Scanner

- **Learned rule:** 12% stop, target 2x risk, out after 40 days
- **Skips:** nothing
- **Status:** promising (best candidate in sample: 148 trades, avg +3.16%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 85 | 42% | +0.81% | +2.04% | +68,600 |  |
| Learned rule | 85 | 46% | +1.10% | +4.19% | +93,100 | +0.29% (t 0.3) |
| Learned rule + filter | 85 | 46% | +1.10% | +4.19% | +93,100 | +0.29% (t 0.3) |

## Wkly_upswing

- **Learned rule:** 12% stop, target 3x risk, out after 40 days
- **Skips:** nothing
- **Status:** promising (best candidate in sample: 510 trades, avg +2.00%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 386 | 36% | -0.50% | -0.54% | -192,100 |  |
| Learned rule | 386 | 39% | +0.55% | +0.29% | +210,900 | +1.04% (t 1.6) |
| Learned rule + filter | 341 | 39% | +0.41% | +0.20% | +139,000 | +0.86% (t 1.3) |
