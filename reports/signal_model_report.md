# Scanner signal model report

Generated 2026-10-22 17:39 UTC by `scripts/signal_model.py train`.

## The rule being tested

- **Trigger price** = high of the signal candle (the day's candle for the daily scanners, the completed week's candle for `Wkly_upswing`).
- **Entry**: buy-stop at the trigger, valid for 3 sessions after a daily signal (5 after a weekly one). Filled at the trigger, or at the open on a gap-up.
- **Stop** = signal candle low, kept between 2% and 8% below entry. **Target** = 2× that risk. Otherwise exit at the close after 20 sessions.
- Stop assumed hit first when a candle touches both levels, including on the entry day.
- Returns are after 0.25% round-trip costs. A win = return > 0.

## Data coverage

| Scanner | Hits | With prices | Triggered & closed | Not triggered | Still open / pending |
|---|---|---|---|---|---|
| 63_30_daily | 5953 | 5945 | 4240 | 1703 | 2 |
| Bullish_Scanner | 1701 | 1692 | 1324 | 356 | 12 |
| Wkly_upswing | 1838 | 1831 | 1217 | 611 | 3 |

## 1. Does buying every trigger make money?

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 4240 | 35% | -0.25% | +8.36% / -4.97% | 0.92 | -0.02 | 7.0 | -2.3 | -0.69% (t -6.6) |
| Bullish_Scanner | 1324 | 38% | -0.22% | +9.55% / -6.13% | 0.94 | +0.00 | 9.5 | -0.9 | -0.75% (t -3.2) |
| Wkly_upswing | 1217 | 38% | -0.12% | +12.33% / -7.66% | 0.97 | +0.02 | 8.9 | -0.4 | -0.65% (t -2.2) |
| **All scanners** | 6781 | 36% | -0.22% | +9.34% / -5.66% | 0.94 | -0.01 | 7.8 | -2.2 | -0.69% (t -7.2) |

t-stat: average return divided by its standard error; below ~2 the average could easily be noise. **vs index**: average return minus what the Nifty 500 did over the same days. A scanner that only matches the index adds nothing over buying an index fund.

### By market-cap tier

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Largecap | 1550 | 37% | -0.16% | +6.45% / -4.02% | 0.94 | +0.01 | 7.2 | -1.1 | -0.67% (t -4.9) |
| 63_30_daily · Midcap | 1263 | 38% | +0.25% | +8.72% / -5.02% | 1.08 | +0.06 | 7.1 | +1.2 | -0.17% (t -0.9) |
| 63_30_daily · Smallcap | 1427 | 31% | -0.79% | +10.41% / -5.88% | 0.81 | -0.12 | 6.7 | -3.6 | -1.16% (t -5.5) |
| Bullish_Scanner · Largecap | 468 | 41% | +0.12% | +7.17% / -4.75% | 1.04 | +0.07 | 9.9 | +0.4 | -0.25% (t -0.9) |
| Bullish_Scanner · Midcap | 420 | 41% | +0.66% | +10.48% / -6.22% | 1.18 | +0.11 | 9.9 | +1.5 | -0.06% (t -0.1) |
| Bullish_Scanner · Smallcap | 436 | 31% | -1.43% | +11.74% / -7.34% | 0.72 | -0.17 | 8.6 | -2.9 | -1.96% (t -4.1) |
| Wkly_upswing · Largecap | 295 | 49% | +1.24% | +9.31% / -6.47% | 1.37 | +0.19 | 12.8 | +2.3 | +0.40% (t +0.8) |
| Wkly_upswing · Midcap | 274 | 43% | +1.14% | +12.68% / -7.45% | 1.27 | +0.18 | 9.9 | +1.8 | +0.57% (t +0.9) |
| Wkly_upswing · Smallcap | 647 | 31% | -1.26% | +14.33% / -8.13% | 0.78 | -0.13 | 6.6 | -2.9 | -1.62% (t -3.8) |

### By market regime at signal time (Nifty vs its 50-day average)

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Nifty above 50DMA | 3621 | 35% | -0.29% | +8.22% / -4.92% | 0.91 | -0.02 | 7.0 | -2.5 | -0.72% (t -6.4) |
| 63_30_daily · Nifty below 50DMA | 619 | 37% | -0.01% | +9.11% / -5.26% | 1.00 | -0.00 | 7.0 | -0.0 | -0.50% (t -1.7) |
| Bullish_Scanner · Nifty above 50DMA | 1030 | 37% | -0.45% | +9.18% / -6.18% | 0.88 | -0.02 | 9.5 | -1.7 | -1.03% (t -3.9) |
| Bullish_Scanner · Nifty below 50DMA | 294 | 39% | +0.60% | +10.81% / -5.96% | 1.17 | +0.09 | 9.6 | +1.1 | +0.22% (t +0.4) |
| Wkly_upswing · Nifty above 50DMA | 991 | 39% | +0.04% | +12.33% / -7.67% | 1.01 | +0.04 | 8.9 | +0.1 | -0.54% (t -1.7) |
| Wkly_upswing · Nifty below 50DMA | 226 | 34% | -0.81% | +12.37% / -7.62% | 0.84 | -0.06 | 8.9 | -1.2 | -1.11% (t -1.6) |

### Exit reasons

| Scanner | Target | Stop | Time exit |
|---|---|---|---|
| 63_30_daily | 28% | 60% | 12% |
| Bullish_Scanner | 25% | 54% | 22% |
| Wkly_upswing | 25% | 56% | 19% |

### Other exit rules (same entries)

Fixed set of alternatives, not optimized. Cells: trades · avg return · vs index (t-stat of the excess).

| Exit rule | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| Candle-low stop, 2R target, 20d | 4240 · -0.25% · -0.69% (t -6.6) | 1324 · -0.22% · -0.75% (t -3.2) | 1217 · -0.12% · -0.65% (t -2.2) |
| Candle-low stop, no target, 20d | 4237 · +0.36% · -0.24% (t -1.6) | 1321 · -0.30% · -1.00% (t -3.7) | 1217 · +0.76% · -0.02% (t -0.0) |
| Wide stop (≤15%), no target, 20d | 4237 · +0.40% · -0.22% (t -1.4) | 1319 · -0.07% · -0.86% (t -3.0) | 1213 · +1.28% · +0.29% (t +0.6) |
| No stop, exit after 10d | 4233 · +0.54% · -0.06% (t -0.5) | 1324 · +0.25% · -0.25% (t -1.0) | 1214 · +0.61% · -0.10% (t -0.3) |
| No stop, exit after 20d | 4222 · +1.80% · +0.65% (t +3.5) | 1310 · +1.10% · -0.07% (t -0.2) | 1209 · +1.99% · +0.86% (t +1.6) |

## 2. Model: which triggers to take

Model: `logreg` predicting P(trade ends in profit) from price/volume features at the signal candle, market regime, repeat/confluence counts, scanner and market-cap tier. Validated **walk-forward**: each month is scored by a model trained only on trades that had closed before that month, so these are honest out-of-sample numbers (6626 scored trades from May 2019).

- Walk-forward ROC-AUC: logistic regression 0.55, gradient boosting 0.54 (0.50 = coin flip; the filter is only switched on at ≥ 0.55).
- **Validated.** BUY threshold: P(profit) ≥ 0.375

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| All scored trades (no filter) | 6626 | 36% | -0.21% | +9.30% / -5.63% | 0.94 | -0.01 | 7.8 | -2.1 | -0.69% (t -7.2) |
| Model says BUY | 2701 | 40% | +0.34% | +9.33% / -5.73% | 1.10 | +0.08 | 9.2 | +2.1 | -0.16% (t -1.0) |
| Model says SKIP | 3925 | 34% | -0.59% | +9.28% / -5.57% | 0.84 | -0.07 | 6.9 | -4.6 | -1.05% (t -8.6) |
| 63_30_daily · BUY | 1372 | 39% | +0.23% | +8.38% / -5.00% | 1.07 | +0.07 | 8.0 | +1.1 | -0.10% (t -0.5) |
| 63_30_daily · SKIP | 2868 | 34% | -0.48% | +8.34% / -4.96% | 0.85 | -0.06 | 6.6 | -3.6 | -0.97% (t -7.7) |
| Bullish_Scanner · BUY | 816 | 41% | +0.38% | +9.53% / -5.93% | 1.11 | +0.09 | 10.3 | +1.3 | -0.27% (t -0.9) |
| Bullish_Scanner · SKIP | 508 | 33% | -1.18% | +9.60% / -6.42% | 0.73 | -0.14 | 8.2 | -2.9 | -1.54% (t -4.0) |
| Wkly_upswing · BUY | 513 | 43% | +0.58% | +11.32% / -7.48% | 1.14 | +0.11 | 10.5 | +1.3 | -0.13% (t -0.3) |
| Wkly_upswing · SKIP | 549 | 34% | -0.62% | +13.91% / -7.95% | 0.88 | -0.05 | 7.1 | -1.3 | -1.07% (t -2.3) |

### Out-of-sample return by probability quintile

| Quintile | P(profit) range | Trades | Win rate | Avg return |
|---|---|---|---|---|
| Q1 | 0.02–0.28 | 1326 | 30% | -1.09% |
| Q2 | 0.28–0.33 | 1325 | 34% | -0.41% |
| Q3 | 0.33–0.38 | 1325 | 37% | -0.23% |
| Q4 | 0.38–0.42 | 1325 | 40% | +0.42% |
| Q5 | 0.42–0.81 | 1325 | 41% | +0.26% |

Returns should rise steadily from Q1 to Q5 if the model has found something real. When validated, the threshold is picked on these same predictions, so the BUY row is slightly optimistic; the quintiles are the fairer check.

## Caveats

- Only ~8 months of history for the two daily scanners, all in one market phase. Treat every number here as provisional and re-run training as more signals accumulate.
- Yahoo Finance data: symbols it doesn't carry are skipped (survivorship bias), and daily candles can't tell whether the stop or the target came first inside a day (handled pessimistically).
- Chartink's backtest list is the scanner's output as of today's definition; if the scan was edited, past hits reflect the new version, not what you would have seen live.
- Not investment advice. Size positions so a stop-out costs a small, fixed fraction of capital.