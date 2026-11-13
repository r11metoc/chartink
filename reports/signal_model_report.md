# Scanner signal model report

Generated 2026-11-13 11:24 UTC by `scripts/signal_model.py train`.

## The rule being tested

- **Trigger price** = high of the signal candle (the day's candle for the daily scanners, the completed week's candle for `Wkly_upswing`).
- **Entry**: buy-stop at the trigger, valid for 3 sessions after a daily signal (5 after a weekly one). Filled at the trigger, or at the open on a gap-up.
- **Stop** = signal candle low, kept between 2% and 8% below entry. **Target** = 2× that risk. Otherwise exit at the close after 20 sessions.
- Stop assumed hit first when a candle touches both levels, including on the entry day.
- Returns are after 0.25% round-trip costs. A win = return > 0.

## Data coverage

| Scanner | Hits | With prices | Triggered & closed | Not triggered | Still open / pending |
|---|---|---|---|---|---|
| 63_30_daily | 2061 | 2048 | 1592 | 444 | 12 |
| Bullish_Scanner | 5771 | 5719 | 4719 | 966 | 34 |
| Wkly_upswing | 621 | 621 | 412 | 200 | 9 |

## 1. Does buying every trigger make money?

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 1592 | 34% | -0.21% | +6.76% / -3.80% | 0.92 | -0.02 | 4.7 | -1.5 | -0.60% (t -4.6) |
| Bullish_Scanner | 4719 | 42% | +0.68% | +7.72% / -4.44% | 1.26 | +0.18 | 6.9 | +6.8 | +0.16% (t +1.7) |
| Wkly_upswing | 412 | 41% | +0.17% | +10.75% / -7.19% | 1.04 | +0.06 | 10.5 | +0.3 | -0.26% (t -0.6) |
| **All scanners** | 6723 | 40% | +0.44% | +7.72% / -4.44% | 1.16 | +0.12 | 6.6 | +5.3 | -0.04% (t -0.6) |

t-stat: average return divided by its standard error; below ~2 the average could easily be noise. **vs index**: average return minus what the Nifty 500 did over the same days. A scanner that only matches the index adds nothing over buying an index fund.

### By market-cap tier

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Largecap | 775 | 33% | -0.41% | +5.42% / -3.32% | 0.81 | -0.05 | 5.2 | -2.6 | -0.85% (t -5.5) |
| 63_30_daily · Midcap | 424 | 33% | -0.13% | +7.85% / -4.06% | 0.95 | -0.04 | 4.1 | -0.4 | -0.36% (t -1.3) |
| 63_30_daily · Smallcap | 392 | 36% | +0.10% | +8.13% / -4.50% | 1.04 | +0.04 | 4.4 | +0.3 | -0.36% (t -1.1) |
| Bullish_Scanner · Largecap | 2399 | 42% | +0.44% | +6.25% / -3.72% | 1.20 | +0.16 | 7.2 | +3.9 | -0.09% (t -0.9) |
| Bullish_Scanner · Midcap | 1228 | 43% | +0.85% | +8.45% / -4.97% | 1.30 | +0.19 | 6.9 | +4.0 | +0.38% (t +1.8) |
| Bullish_Scanner · Smallcap | 1089 | 42% | +1.00% | +10.09% / -5.45% | 1.31 | +0.20 | 6.1 | +3.9 | +0.45% (t +1.8) |
| Wkly_upswing · Largecap | 163 | 52% | +1.76% | +9.27% / -6.22% | 1.59 | +0.26 | 13.8 | +2.5 | +1.05% (t +1.5) |
| Wkly_upswing · Midcap | 89 | 40% | +0.16% | +11.12% / -7.29% | 1.04 | +0.06 | 10.0 | +0.2 | -0.11% (t -0.1) |
| Wkly_upswing · Smallcap | 155 | 32% | -1.23% | +13.01% / -7.81% | 0.77 | -0.12 | 7.7 | -1.5 | -1.51% (t -1.9) |

### By market regime at signal time (Nifty vs its 50-day average)

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Nifty above 50DMA | 1379 | 33% | -0.35% | +6.62% / -3.77% | 0.86 | -0.05 | 4.6 | -2.4 | -0.72% (t -5.2) |
| 63_30_daily · Nifty below 50DMA | 213 | 41% | +0.67% | +7.51% / -4.05% | 1.28 | +0.16 | 5.2 | +1.6 | +0.18% (t +0.4) |
| Bullish_Scanner · Nifty above 50DMA | 4033 | 42% | +0.68% | +7.67% / -4.44% | 1.26 | +0.19 | 6.8 | +6.3 | +0.18% (t +1.8) |
| Bullish_Scanner · Nifty below 50DMA | 686 | 41% | +0.70% | +8.05% / -4.46% | 1.27 | +0.13 | 7.2 | +2.6 | +0.06% (t +0.2) |
| Wkly_upswing · Nifty above 50DMA | 338 | 43% | +0.47% | +10.86% / -7.24% | 1.11 | +0.09 | 10.5 | +0.9 | -0.07% (t -0.1) |
| Wkly_upswing · Nifty below 50DMA | 74 | 34% | -1.20% | +10.13% / -6.98% | 0.74 | -0.10 | 10.9 | -1.1 | -1.14% (t -1.1) |

### Exit reasons

| Scanner | Target | Stop | Time exit |
|---|---|---|---|
| 63_30_daily | 31% | 65% | 4% |
| Bullish_Scanner | 34% | 54% | 12% |
| Wkly_upswing | 23% | 50% | 27% |

### Other exit rules (same entries)

Fixed set of alternatives, not optimized. Cells: trades · avg return · vs index (t-stat of the excess).

| Exit rule | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| Candle-low stop, 2R target, 20d | 1592 · -0.21% · -0.60% (t -4.6) | 4719 · +0.68% · +0.16% (t +1.7) | 412 · +0.17% · -0.26% (t -0.6) |
| Candle-low stop, no target, 20d | 1592 · +0.49% · -0.24% (t -1.1) | 4707 · +1.37% · +0.58% (t +4.1) | 412 · +1.10% · +0.44% (t +0.7) |
| Wide stop (≤15%), no target, 20d | 1592 · +0.51% · -0.23% (t -1.1) | 4707 · +1.41% · +0.60% (t +4.2) | 412 · +1.23% · +0.56% (t +0.8) |
| No stop, exit after 10d | 1588 · +1.27% · +0.47% (t +2.2) | 4710 · +1.84% · +1.05% (t +8.1) | 413 · +0.69% · +0.16% (t +0.3) |
| No stop, exit after 20d | 1586 · +2.39% · +0.95% (t +3.2) | 4702 · +3.09% · +1.63% (t +9.7) | 411 · +1.57% · +0.71% (t +0.9) |

## 2. Model: which triggers to take

Model: `logreg` predicting P(trade ends in profit) from price/volume features at the signal candle, market regime, repeat/confluence counts, scanner and market-cap tier. Validated **walk-forward**: each month is scored by a model trained only on trades that had closed before that month, so these are honest out-of-sample numbers (6544 scored trades from Jun 2019).

- Walk-forward ROC-AUC: logistic regression 0.55, gradient boosting 0.55 (0.50 = coin flip; the filter is only switched on at ≥ 0.55).
- **Validated.** BUY threshold: P(profit) ≥ 0.300

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| All scored trades (no filter) | 6544 | 40% | +0.47% | +7.76% / -4.45% | 1.18 | +0.13 | 6.5 | +5.6 | -0.01% (t -0.1) |
| Model says BUY | 5350 | 42% | +0.67% | +7.90% / -4.57% | 1.25 | +0.17 | 6.8 | +7.0 | +0.20% (t +2.1) |
| Model says SKIP | 1194 | 32% | -0.46% | +6.93% / -3.98% | 0.83 | -0.07 | 5.1 | -2.8 | -0.93% (t -6.0) |
| 63_30_daily · BUY | 1128 | 35% | -0.08% | +6.88% / -3.89% | 0.97 | +0.01 | 4.9 | -0.5 | -0.41% (t -2.5) |
| 63_30_daily · SKIP | 444 | 32% | -0.44% | +6.42% / -3.62% | 0.82 | -0.06 | 4.3 | -1.8 | -0.97% (t -4.1) |
| Bullish_Scanner · BUY | 3927 | 44% | +0.92% | +7.94% / -4.59% | 1.36 | +0.23 | 7.1 | +8.1 | +0.39% (t +3.6) |
| Bullish_Scanner · SKIP | 685 | 32% | -0.58% | +6.50% / -3.88% | 0.78 | -0.10 | 5.3 | -2.9 | -0.99% (t -5.2) |
| Wkly_upswing · BUY | 295 | 42% | +0.32% | +10.61% / -7.25% | 1.08 | +0.08 | 10.9 | +0.6 | -0.11% (t -0.2) |
| Wkly_upswing · SKIP | 65 | 40% | +0.60% | +13.31% / -7.87% | 1.13 | +0.11 | 8.1 | +0.4 | -0.13% (t -0.1) |

### Out-of-sample return by probability quintile

| Quintile | P(profit) range | Trades | Win rate | Avg return |
|---|---|---|---|---|
| Q1 | 0.00–0.31 | 1309 | 33% | -0.39% |
| Q2 | 0.31–0.36 | 1309 | 38% | +0.13% |
| Q3 | 0.36–0.41 | 1308 | 42% | +0.51% |
| Q4 | 0.41–0.48 | 1309 | 41% | +0.47% |
| Q5 | 0.48–0.99 | 1309 | 48% | +1.60% |

Returns should rise steadily from Q1 to Q5 if the model has found something real. When validated, the threshold is picked on these same predictions, so the BUY row is slightly optimistic; the quintiles are the fairer check.

## Caveats

- Only ~8 months of history for the two daily scanners, all in one market phase. Treat every number here as provisional and re-run training as more signals accumulate.
- Yahoo Finance data: symbols it doesn't carry are skipped (survivorship bias), and daily candles can't tell whether the stop or the target came first inside a day (handled pessimistically).
- Chartink's backtest list is the scanner's output as of today's definition; if the scan was edited, past hits reflect the new version, not what you would have seen live.
- Not investment advice. Size positions so a stop-out costs a small, fixed fraction of capital.