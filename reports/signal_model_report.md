# Scanner signal model report

Generated 2026-10-24 18:45 UTC by `scripts/signal_model.py train`.

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
| Bullish_Scanner | 5083 | 5065 | 4198 | 860 | 7 |
| Wkly_upswing | 615 | 615 | 414 | 199 | 2 |

## 1. Does buying every trigger make money?

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 1438 | 34% | -0.20% | +6.91% / -3.83% | 0.92 | -0.03 | 4.7 | -1.3 | -0.57% (t -4.1) |
| Bullish_Scanner | 4198 | 42% | +0.71% | +7.89% / -4.51% | 1.27 | +0.19 | 6.8 | +6.7 | +0.20% (t +2.0) |
| Wkly_upswing | 414 | 41% | +0.14% | +10.75% / -7.18% | 1.03 | +0.05 | 10.5 | +0.3 | -0.31% (t -0.7) |
| **All scanners** | 6050 | 40% | +0.46% | +7.89% / -4.51% | 1.17 | +0.13 | 6.5 | +5.2 | -0.01% (t -0.2) |

t-stat: average return divided by its standard error; below ~2 the average could easily be noise. **vs index**: average return minus what the Nifty 500 did over the same days. A scanner that only matches the index adds nothing over buying an index fund.

### By market-cap tier

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Largecap | 648 | 33% | -0.39% | +5.49% / -3.31% | 0.82 | -0.05 | 5.2 | -2.2 | -0.81% (t -4.9) |
| 63_30_daily · Midcap | 401 | 34% | +0.08% | +7.86% / -4.00% | 1.03 | +0.01 | 4.2 | +0.3 | -0.14% (t -0.5) |
| 63_30_daily · Smallcap | 388 | 34% | -0.15% | +8.24% / -4.53% | 0.95 | -0.02 | 4.3 | -0.5 | -0.60% (t -1.9) |
| Bullish_Scanner · Largecap | 2013 | 42% | +0.51% | +6.35% / -3.74% | 1.23 | +0.18 | 7.0 | +4.1 | +0.00% (t +0.0) |
| Bullish_Scanner · Midcap | 1118 | 43% | +0.82% | +8.48% / -4.99% | 1.29 | +0.18 | 6.9 | +3.7 | +0.33% (t +1.5) |
| Bullish_Scanner · Smallcap | 1065 | 41% | +0.96% | +10.19% / -5.47% | 1.30 | +0.18 | 6.1 | +3.7 | +0.42% (t +1.7) |
| Wkly_upswing · Largecap | 162 | 51% | +1.58% | +9.20% / -6.41% | 1.51 | +0.24 | 13.5 | +2.2 | +0.83% (t +1.2) |
| Wkly_upswing · Midcap | 94 | 41% | +0.68% | +11.48% / -6.98% | 1.17 | +0.13 | 10.4 | +0.7 | +0.28% (t +0.3) |
| Wkly_upswing · Smallcap | 153 | 31% | -1.44% | +12.89% / -7.80% | 0.73 | -0.15 | 7.7 | -1.8 | -1.65% (t -2.1) |

### By market regime at signal time (Nifty vs its 50-day average)

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Nifty above 50DMA | 1245 | 33% | -0.33% | +6.74% / -3.78% | 0.87 | -0.05 | 4.6 | -2.2 | -0.68% (t -4.7) |
| 63_30_daily · Nifty below 50DMA | 193 | 40% | +0.68% | +7.81% / -4.16% | 1.27 | +0.16 | 5.1 | +1.5 | +0.14% (t +0.3) |
| Bullish_Scanner · Nifty above 50DMA | 3602 | 42% | +0.70% | +7.80% / -4.50% | 1.27 | +0.19 | 6.7 | +6.1 | +0.22% (t +2.0) |
| Bullish_Scanner · Nifty below 50DMA | 596 | 41% | +0.81% | +8.44% / -4.55% | 1.30 | +0.13 | 7.1 | +2.8 | +0.14% (t +0.5) |
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
| Candle-low stop, 2R target, 20d | 1438 · -0.20% · -0.57% (t -4.1) | 4198 · +0.71% · +0.20% (t +2.0) | 414 · +0.14% · -0.31% (t -0.7) |
| Candle-low stop, no target, 20d | 1438 · +0.66% · -0.05% (t -0.2) | 4197 · +1.47% · +0.68% (t +4.4) | 414 · +1.07% · +0.39% (t +0.6) |
| Wide stop (≤15%), no target, 20d | 1438 · +0.67% · -0.04% (t -0.2) | 4194 · +1.51% · +0.71% (t +4.5) | 413 · +1.23% · +0.55% (t +0.8) |
| No stop, exit after 10d | 1437 · +1.37% · +0.64% (t +2.8) | 4196 · +1.88% · +1.14% (t +8.1) | 411 · +0.79% · +0.24% (t +0.4) |
| No stop, exit after 20d | 1435 · +2.86% · +1.49% (t +4.8) | 4186 · +3.22% · +1.75% (t +9.5) | 406 · +1.81% · +0.96% (t +1.3) |

## 2. Model: which triggers to take

Model: `hgb` predicting P(trade ends in profit) from price/volume features at the signal candle, market regime, repeat/confluence counts, scanner and market-cap tier. Validated **walk-forward**: each month is scored by a model trained only on trades that had closed before that month, so these are honest out-of-sample numbers (5888 scored trades from Feb 2021).

- Walk-forward ROC-AUC: logistic regression 0.55, gradient boosting 0.56 (0.50 = coin flip; the filter is only switched on at ≥ 0.55).
- **Validated.** BUY threshold: P(profit) ≥ 0.300

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| All scored trades (no filter) | 5888 | 40% | +0.49% | +7.87% / -4.48% | 1.18 | +0.13 | 6.5 | +5.5 | +0.01% (t +0.1) |
| Model says BUY | 4315 | 42% | +0.72% | +8.24% / -4.82% | 1.26 | +0.18 | 7.0 | +6.5 | +0.28% (t +2.6) |
| Model says SKIP | 1573 | 35% | -0.12% | +6.59% / -3.66% | 0.95 | +0.00 | 4.8 | -0.9 | -0.72% (t -5.5) |
| 63_30_daily · BUY | 952 | 35% | -0.11% | +7.39% / -4.12% | 0.96 | -0.00 | 4.8 | -0.5 | -0.34% (t -1.8) |
| 63_30_daily · SKIP | 480 | 32% | -0.36% | +5.89% / -3.28% | 0.84 | -0.07 | 4.3 | -1.7 | -1.01% (t -5.0) |
| Bullish_Scanner · BUY | 3124 | 45% | +0.99% | +8.28% / -4.88% | 1.37 | +0.24 | 7.4 | +7.5 | +0.49% (t +3.9) |
| Bullish_Scanner · SKIP | 1018 | 36% | +0.01% | +6.40% / -3.55% | 1.00 | +0.04 | 4.8 | +0.0 | -0.56% (t -3.6) |
| Wkly_upswing · BUY | 239 | 44% | +0.48% | +10.54% / -7.27% | 1.12 | +0.11 | 11.1 | +0.8 | -0.02% (t -0.0) |
| Wkly_upswing · SKIP | 75 | 35% | -0.40% | +13.42% / -7.73% | 0.92 | -0.02 | 7.8 | -0.3 | -1.12% (t -1.0) |

### Out-of-sample return by probability quintile

| Quintile | P(profit) range | Trades | Win rate | Avg return |
|---|---|---|---|---|
| Q1 | 0.02–0.28 | 1178 | 34% | -0.15% |
| Q2 | 0.28–0.35 | 1177 | 37% | +0.08% |
| Q3 | 0.35–0.41 | 1178 | 40% | +0.31% |
| Q4 | 0.41–0.49 | 1177 | 44% | +0.87% |
| Q5 | 0.49–0.92 | 1178 | 47% | +1.35% |

Returns should rise steadily from Q1 to Q5 if the model has found something real. When validated, the threshold is picked on these same predictions, so the BUY row is slightly optimistic; the quintiles are the fairer check.

## Caveats

- Only ~8 months of history for the two daily scanners, all in one market phase. Treat every number here as provisional and re-run training as more signals accumulate.
- Yahoo Finance data: symbols it doesn't carry are skipped (survivorship bias), and daily candles can't tell whether the stop or the target came first inside a day (handled pessimistically).
- Chartink's backtest list is the scanner's output as of today's definition; if the scan was edited, past hits reflect the new version, not what you would have seen live.
- Not investment advice. Size positions so a stop-out costs a small, fixed fraction of capital.