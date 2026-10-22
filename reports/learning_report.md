# What the system learned

Updated 2026-10-22. For each scanner 144 exit rules were tried; the setup filter skips market-cap x market-regime groups that lost money (at least 20 trades).

**Walk-forward test:** every month the rule and filter were picked using only trades that had already closed, then used on that month's signals. These are the only numbers that count; the in-sample best always looks better than it is. Trades still open are valued at the last close.

**Status:** *proven* = beat the base rule on the same signals by at least 1.65 standard errors (t); *promising* = ahead but could be luck; *not better* = the base rule is kept.

## 63_30_daily

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 4221 trades, avg +2.85%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 3996 | 35% | -0.28% | -0.68% | -1,101,500 |  |
| Learned rule | 3996 | 48% | +2.46% | +1.05% | +9,828,100 | +2.74% (t 11.5) |
| Learned rule + filter | 3383 | 48% | +2.43% | +1.00% | +8,226,000 | +2.33% (t 10.4) |

## Bullish_Scanner

- **Learned rule:** 12% stop, target 3x risk, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 1310 trades, avg +1.77%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 1228 | 37% | -0.28% | -0.87% | -340,600 |  |
| Learned rule | 1228 | 45% | +1.15% | -0.14% | +1,408,600 | +1.42% (t 4.1) |
| Learned rule + filter | 1085 | 46% | +1.13% | -0.16% | +1,225,600 | +1.28% (t 3.9) |

## Wkly_upswing

- **Learned rule:** 12% stop, no target, out after 40 days
- **Skips:** nothing
- **Status:** proven (best candidate in sample: 1212 trades, avg +2.56%)

| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |
|---|---|---|---|---|---|---|
| Base rule, every signal | 1123 | 38% | -0.09% | -0.65% | -103,900 |  |
| Learned rule | 1123 | 39% | +1.47% | +0.64% | +1,649,200 | +1.56% (t 3.0) |
| Learned rule + filter | 822 | 41% | +1.67% | +0.63% | +1,372,500 | +1.31% (t 2.9) |
