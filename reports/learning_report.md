# What the system learned

Updated 2026-10-01. For each scanner 144 exit rules were tried; the setup filter skips market-cap x market-regime groups that lost money (at least 20 trades).

**Walk-forward test:** every month the rule and filter were picked using only trades that had already closed, then used on that month's signals. These are the only numbers that count; the in-sample best always looks better than it is. Trades still open are valued at the last close.

**Status:** *proven* = beat the base rule on the same signals by at least 1.65 standard errors (t); *promising* = ahead but could be luck; *not better* = the base rule is kept.

## 63_30_daily

- **Best candidate:** 12% stop, target 2x risk, out after 40 days - did worse on unseen months, so the base rule is kept: stop at candle low (2-8%), target 2x risk, out after 20 days
- **Skips:** nothing
- **Status:** not better (best candidate in sample: 256 trades, avg +2.02%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 79 | 25% | -2.70% | -1.77% | -213,300 |  |
| Learned rule | 79 | 28% | -3.95% | -1.91% | -312,200 | -1.25% (t -1.1) |
| Learned rule + filter | 56 | 27% | -4.18% | -1.89% | -234,100 | -0.26% (t -0.2) |

## Bullish_Scanner

- **Learned rule:** 12% stop, target 2x risk, out after 40 days
- **Skips:** nothing
- **Status:** promising (best candidate in sample: 145 trades, avg +3.10%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 84 | 42% | +0.93% | +2.03% | +77,700 |  |
| Learned rule | 84 | 45% | +1.53% | +4.28% | +128,100 | +0.60% (t 0.6) |
| Learned rule + filter | 84 | 45% | +1.53% | +4.28% | +128,100 | +0.60% (t 0.6) |

## Wkly_upswing

- **Learned rule:** 12% stop, target 3x risk, out after 40 days
- **Skips:** nothing
- **Status:** promising (best candidate in sample: 509 trades, avg +2.03%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 386 | 36% | -0.49% | -0.54% | -189,100 |  |
| Learned rule | 386 | 39% | +0.57% | +0.28% | +218,500 | +1.06% (t 1.6) |
| Learned rule + filter | 341 | 39% | +0.41% | +0.19% | +140,400 | +0.85% (t 1.3) |
