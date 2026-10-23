# Scanner signal model report

Generated 2026-10-23 18:59 UTC by `scripts/signal_model.py train`.

## The rule being tested

- **Trigger price** = high of the signal candle (the day's candle for the daily scanners, the completed week's candle for `Wkly_upswing`).
- **Entry**: buy-stop at the trigger, valid for 3 sessions after a daily signal (5 after a weekly one). Filled at the trigger, or at the open on a gap-up.
- **Stop** = signal candle low, kept between 2% and 8% below entry. **Target** = 2× that risk. Otherwise exit at the close after 20 sessions.
- Stop assumed hit first when a candle touches both levels, including on the entry day.
- Returns are after 0.25% round-trip costs. A win = return > 0.

## Data coverage

| Scanner | Hits | With prices | Triggered & closed | Not triggered | Still open / pending |
|---|---|---|---|---|---|
| 63_30_daily | 1831 | 1828 | 1438 | 389 | 1 |
| Bullish_Scanner | 5083 | 5065 | 4195 | 858 | 12 |
| Wkly_upswing | 615 | 615 | 414 | 199 | 2 |

## 1. Does buying every trigger make money?

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 1438 | 34% | -0.20% | +6.91% / -3.83% | 0.92 | -0.03 | 4.7 | -1.3 | -0.57% (t -4.1) |
| Bullish_Scanner | 4195 | 42% | +0.72% | +7.89% / -4.51% | 1.28 | +0.19 | 6.8 | +6.7 | +0.21% (t +2.0) |
| Wkly_upswing | 414 | 41% | +0.14% | +10.75% / -7.18% | 1.03 | +0.05 | 10.5 | +0.3 | -0.31% (t -0.7) |
| **All scanners** | 6047 | 40% | +0.46% | +7.89% / -4.51% | 1.17 | +0.13 | 6.5 | +5.2 | -0.01% (t -0.2) |

t-stat: average return divided by its standard error; below ~2 the average could easily be noise. **vs index**: average return minus what the Nifty 500 did over the same days. A scanner that only matches the index adds nothing over buying an index fund.

### By market-cap tier

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Largecap | 656 | 33% | -0.39% | +5.47% / -3.31% | 0.82 | -0.05 | 5.2 | -2.2 | -0.80% (t -4.9) |
| 63_30_daily · Midcap | 409 | 34% | +0.04% | +7.85% / -4.03% | 1.01 | +0.00 | 4.2 | +0.1 | -0.22% (t -0.8) |
| 63_30_daily · Smallcap | 372 | 34% | -0.10% | +8.34% / -4.53% | 0.97 | -0.01 | 4.3 | -0.3 | -0.53% (t -1.6) |
| Bullish_Scanner · Largecap | 2029 | 42% | +0.50% | +6.37% / -3.74% | 1.23 | +0.18 | 7.0 | +4.0 | +0.01% (t +0.1) |
| Bullish_Scanner · Midcap | 1131 | 44% | +0.90% | +8.47% / -5.00% | 1.32 | +0.20 | 6.9 | +4.0 | +0.38% (t +1.8) |
| Bullish_Scanner · Smallcap | 1033 | 41% | +0.92% | +10.26% / -5.46% | 1.28 | +0.17 | 6.0 | +3.5 | +0.38% (t +1.5) |
| Wkly_upswing · Largecap | 163 | 51% | +1.57% | +9.20% / -6.34% | 1.51 | +0.24 | 13.6 | +2.2 | +0.82% (t +1.2) |
| Wkly_upswing · Midcap | 94 | 43% | +0.85% | +11.58% / -7.09% | 1.21 | +0.15 | 10.4 | +0.8 | +0.43% (t +0.4) |
| Wkly_upswing · Smallcap | 152 | 30% | -1.56% | +12.83% / -7.80% | 0.71 | -0.16 | 7.6 | -1.9 | -1.75% (t -2.2) |

### By market regime at signal time (Nifty vs its 50-day average)

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Nifty above 50DMA | 1245 | 33% | -0.33% | +6.74% / -3.78% | 0.87 | -0.05 | 4.6 | -2.2 | -0.68% (t -4.7) |
| 63_30_daily · Nifty below 50DMA | 193 | 40% | +0.68% | +7.81% / -4.16% | 1.27 | +0.16 | 5.1 | +1.5 | +0.14% (t +0.3) |
| Bullish_Scanner · Nifty above 50DMA | 3602 | 42% | +0.70% | +7.80% / -4.50% | 1.27 | +0.19 | 6.7 | +6.1 | +0.22% (t +2.0) |
| Bullish_Scanner · Nifty below 50DMA | 593 | 41% | +0.85% | +8.44% / -4.53% | 1.32 | +0.14 | 7.1 | +2.9 | +0.16% (t +0.5) |
| Wkly_upswing · Nifty above 50DMA | 340 | 42% | +0.43% | +10.86% / -7.23% | 1.10 | +0.09 | 10.5 | +0.8 | -0.13% (t -0.3) |
| Wkly_upswing · Nifty below 50DMA | 74 | 34% | -1.20% | +10.13% / -6.98% | 0.74 | -0.10 | 10.9 | -1.1 | -1.14% (t -1.1) |

### Exit reasons

| Scanner | Target | Stop | Time exit |
|---|---|---|---|
| 63_30_daily | 31% | 65% | 4% |
| Bullish_Scanner | 34% | 54% | 12% |
| Wkly_upswing | 23% | 50% | 28% |

### Other exit rules (same entries)

Fixed set of alternatives, not optimized. Cells: trades · avg return · vs index (t-stat of the excess).

| Exit rule | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| Candle-low stop, 2R target, 20d | 1438 · -0.20% · -0.57% (t -4.1) | 4195 · +0.72% · +0.21% (t +2.0) | 414 · +0.14% · -0.31% (t -0.7) |
| Candle-low stop, no target, 20d | 1437 · +0.66% · -0.05% (t -0.2) | 4193 · +1.47% · +0.68% (t +4.4) | 414 · +1.07% · +0.39% (t +0.6) |
| Wide stop (≤15%), no target, 20d | 1437 · +0.67% · -0.05% (t -0.2) | 4192 · +1.51% · +0.70% (t +4.5) | 411 · +1.31% · +0.61% (t +0.8) |
| No stop, exit after 10d | 1436 · +1.38% · +0.65% (t +2.8) | 4196 · +1.88% · +1.14% (t +8.1) | 411 · +0.79% · +0.24% (t +0.4) |
| No stop, exit after 20d | 1434 · +2.86% · +1.48% (t +4.8) | 4183 · +3.23% · +1.75% (t +9.5) | 406 · +1.81% · +0.96% (t +1.3) |

## 2. Model: which triggers to take

Model: `hgb` predicting P(trade ends in profit) from price/volume features at the signal candle, market regime, repeat/confluence counts, scanner and market-cap tier. Validated **walk-forward**: each month is scored by a model trained only on trades that had closed before that month, so these are honest out-of-sample numbers (5885 scored trades from Feb 2021).

- Walk-forward ROC-AUC: logistic regression 0.55, gradient boosting 0.56 (0.50 = coin flip; the filter is only switched on at ≥ 0.55).
- **Validated.** BUY threshold: P(profit) ≥ 0.325

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| All scored trades (no filter) | 5885 | 40% | +0.50% | +7.87% / -4.48% | 1.19 | +0.14 | 6.5 | +5.6 | +0.01% (t +0.1) |
| Model says BUY | 3860 | 43% | +0.83% | +8.35% / -4.92% | 1.30 | +0.21 | 7.3 | +7.0 | +0.37% (t +3.2) |
| Model says SKIP | 2025 | 34% | -0.15% | +6.71% / -3.75% | 0.94 | -0.00 | 4.9 | -1.2 | -0.67% (t -5.7) |
| 63_30_daily · BUY | 811 | 36% | -0.04% | +7.58% / -4.23% | 0.99 | +0.01 | 5.0 | -0.2 | -0.26% (t -1.3) |
| 63_30_daily · SKIP | 621 | 32% | -0.39% | +5.95% / -3.33% | 0.83 | -0.07 | 4.3 | -2.1 | -0.96% (t -5.4) |
| Bullish_Scanner · BUY | 2838 | 45% | +1.07% | +8.35% / -4.99% | 1.39 | +0.26 | 7.6 | +7.6 | +0.54% (t +4.0) |
| Bullish_Scanner · SKIP | 1301 | 36% | +0.06% | +6.60% / -3.62% | 1.03 | +0.04 | 4.9 | +0.4 | -0.43% (t -3.0) |
| Wkly_upswing · BUY | 211 | 46% | +1.02% | +10.58% / -7.11% | 1.27 | +0.18 | 11.5 | +1.5 | +0.51% (t +0.8) |
| Wkly_upswing · SKIP | 103 | 32% | -1.28% | +12.68% / -7.86% | 0.76 | -0.13 | 7.8 | -1.3 | -1.90% (t -1.9) |

### Out-of-sample return by probability quintile

| Quintile | P(profit) range | Trades | Win rate | Avg return |
|---|---|---|---|---|
| Q1 | 0.02–0.27 | 1177 | 34% | -0.15% |
| Q2 | 0.27–0.34 | 1177 | 36% | -0.09% |
| Q3 | 0.34–0.41 | 1177 | 41% | +0.46% |
| Q4 | 0.41–0.49 | 1177 | 44% | +0.83% |
| Q5 | 0.49–0.91 | 1177 | 47% | +1.43% |

Returns should rise steadily from Q1 to Q5 if the model has found something real. When validated, the threshold is picked on these same predictions, so the BUY row is slightly optimistic; the quintiles are the fairer check.

## Caveats

- Only ~8 months of history for the two daily scanners, all in one market phase. Treat every number here as provisional and re-run training as more signals accumulate.
- Yahoo Finance data: symbols it doesn't carry are skipped (survivorship bias), and daily candles can't tell whether the stop or the target came first inside a day (handled pessimistically).
- Chartink's backtest list is the scanner's output as of today's definition; if the scan was edited, past hits reflect the new version, not what you would have seen live.
- Not investment advice. Size positions so a stop-out costs a small, fixed fraction of capital.