# Scanner signal model report

Generated 2026-10-21 08:18 UTC by `scripts/signal_model.py train`.

## The rule being tested

- **Trigger price** = high of the signal candle (the day's candle for the daily scanners, the completed week's candle for `Wkly_upswing`).
- **Entry**: buy-stop at the trigger, valid for 3 sessions after a daily signal (5 after a weekly one). Filled at the trigger, or at the open on a gap-up.
- **Stop** = signal candle low, kept between 2% and 8% below entry. **Target** = 2× that risk. Otherwise exit at the close after 20 sessions.
- Stop assumed hit first when a candle touches both levels, including on the entry day.
- Returns are after 0.25% round-trip costs. A win = return > 0.

## Data coverage

| Scanner | Hits | With prices | Triggered & closed | Not triggered | Still open / pending |
|---|---|---|---|---|---|
| 63_30_daily | 2998 | 2992 | 2122 | 869 | 1 |
| Bullish_Scanner | 1701 | 1692 | 1323 | 356 | 13 |
| Wkly_upswing | 1838 | 1836 | 1218 | 614 | 4 |

## 1. Does buying every trigger make money?

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 2122 | 36% | -0.29% | +10.77% / -6.54% | 0.93 | -0.00 | 8.0 | -1.5 | -0.71% (t -3.8) |
| Bullish_Scanner | 1323 | 38% | -0.22% | +9.55% / -6.13% | 0.94 | +0.00 | 9.5 | -0.9 | -0.75% (t -3.2) |
| Wkly_upswing | 1218 | 38% | -0.13% | +12.33% / -7.66% | 0.97 | +0.02 | 8.9 | -0.4 | -0.66% (t -2.2) |
| **All scanners** | 4663 | 37% | -0.23% | +10.84% / -6.72% | 0.95 | +0.00 | 8.6 | -1.6 | -0.71% (t -5.3) |

t-stat: average return divided by its standard error; below ~2 the average could easily be noise. **vs index**: average return minus what the Nifty 500 did over the same days. A scanner that only matches the index adds nothing over buying an index fund.

### By market-cap tier

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Largecap | 511 | 39% | +0.10% | +7.94% / -4.98% | 1.03 | +0.06 | 9.3 | +0.3 | -0.47% (t -1.6) |
| 63_30_daily · Midcap | 585 | 40% | +0.39% | +10.71% / -6.45% | 1.10 | +0.10 | 8.6 | +1.0 | -0.15% (t -0.4) |
| 63_30_daily · Smallcap | 1026 | 32% | -0.87% | +12.53% / -7.28% | 0.82 | -0.09 | 6.9 | -2.8 | -1.15% (t -3.9) |
| Bullish_Scanner · Largecap | 467 | 41% | +0.13% | +7.17% / -4.74% | 1.05 | +0.07 | 10.0 | +0.4 | -0.24% (t -0.8) |
| Bullish_Scanner · Midcap | 420 | 41% | +0.66% | +10.48% / -6.22% | 1.18 | +0.11 | 9.9 | +1.5 | -0.06% (t -0.1) |
| Bullish_Scanner · Smallcap | 436 | 31% | -1.43% | +11.74% / -7.34% | 0.72 | -0.17 | 8.6 | -2.9 | -1.96% (t -4.1) |
| Wkly_upswing · Largecap | 295 | 49% | +1.24% | +9.31% / -6.47% | 1.37 | +0.19 | 12.8 | +2.3 | +0.40% (t +0.8) |
| Wkly_upswing · Midcap | 274 | 43% | +1.14% | +12.68% / -7.45% | 1.27 | +0.18 | 9.9 | +1.8 | +0.57% (t +0.9) |
| Wkly_upswing · Smallcap | 649 | 31% | -1.28% | +14.33% / -8.14% | 0.77 | -0.13 | 6.6 | -3.0 | -1.65% (t -3.9) |

### By market regime at signal time (Nifty vs its 50-day average)

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Nifty above 50DMA | 1748 | 36% | -0.28% | +10.51% / -6.44% | 0.93 | +0.00 | 8.1 | -1.3 | -0.71% (t -3.5) |
| 63_30_daily · Nifty below 50DMA | 374 | 35% | -0.33% | +12.03% / -7.00% | 0.93 | -0.03 | 7.4 | -0.7 | -0.69% (t -1.5) |
| Bullish_Scanner · Nifty above 50DMA | 1030 | 37% | -0.45% | +9.18% / -6.18% | 0.88 | -0.02 | 9.5 | -1.7 | -1.03% (t -3.9) |
| Bullish_Scanner · Nifty below 50DMA | 293 | 39% | +0.62% | +10.81% / -5.96% | 1.17 | +0.09 | 9.6 | +1.2 | +0.24% (t +0.5) |
| Wkly_upswing · Nifty above 50DMA | 992 | 39% | +0.03% | +12.33% / -7.68% | 1.01 | +0.04 | 8.9 | +0.1 | -0.55% (t -1.7) |
| Wkly_upswing · Nifty below 50DMA | 226 | 34% | -0.81% | +12.37% / -7.62% | 0.84 | -0.06 | 8.8 | -1.2 | -1.12% (t -1.6) |

### Exit reasons

| Scanner | Target | Stop | Time exit |
|---|---|---|---|
| 63_30_daily | 27% | 58% | 15% |
| Bullish_Scanner | 25% | 54% | 22% |
| Wkly_upswing | 25% | 56% | 19% |

### Other exit rules (same entries)

Fixed set of alternatives, not optimized. Cells: trades · avg return · vs index (t-stat of the excess).

| Exit rule | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| Candle-low stop, 2R target, 20d | 2122 · -0.29% · -0.71% (t -3.8) | 1323 · -0.22% · -0.75% (t -3.2) | 1218 · -0.13% · -0.66% (t -2.2) |
| Candle-low stop, no target, 20d | 2121 · +0.01% · -0.55% (t -2.0) | 1320 · -0.30% · -0.99% (t -3.6) | 1218 · +0.75% · -0.03% (t -0.1) |
| Wide stop (≤15%), no target, 20d | 2121 · +0.13% · -0.44% (t -1.5) | 1317 · -0.06% · -0.85% (t -2.9) | 1214 · +1.26% · +0.26% (t +0.5) |
| No stop, exit after 10d | 2119 · +0.05% · -0.51% (t -2.2) | 1323 · +0.26% · -0.24% (t -1.0) | 1216 · +0.59% · -0.12% (t -0.3) |
| No stop, exit after 20d | 2112 · +1.45% · +0.46% (t +1.4) | 1308 · +1.13% · -0.06% (t -0.2) | 1211 · +1.94% · +0.81% (t +1.5) |

## 2. Model: which triggers to take

Model: `logreg` predicting P(trade ends in profit) from price/volume features at the signal candle, market regime, repeat/confluence counts, scanner and market-cap tier. Validated **walk-forward**: each month is scored by a model trained only on trades that had closed before that month, so these are honest out-of-sample numbers (4508 scored trades from May 2019).

- Walk-forward ROC-AUC: logistic regression 0.55, gradient boosting 0.53 (0.50 = coin flip; the filter is only switched on at ≥ 0.55).
- **Not validated: the model could not tell winning triggers from losing ones out of sample**, so it is *not* used to filter. `predict` lists every setup with its levels and says the filter is off. Training re-checks this every run, so the filter switches itself on if enough new history makes it work.

### Out-of-sample return by probability quintile

| Quintile | P(profit) range | Trades | Win rate | Avg return |
|---|---|---|---|---|
| Q1 | 0.08–0.30 | 902 | 32% | -1.12% |
| Q2 | 0.30–0.35 | 901 | 34% | -0.34% |
| Q3 | 0.35–0.39 | 902 | 37% | -0.17% |
| Q4 | 0.39–0.44 | 901 | 39% | +0.18% |
| Q5 | 0.44–0.77 | 902 | 42% | +0.39% |

Returns should rise steadily from Q1 to Q5 if the model has found something real. When validated, the threshold is picked on these same predictions, so the BUY row is slightly optimistic; the quintiles are the fairer check.

## Caveats

- Only ~8 months of history for the two daily scanners, all in one market phase. Treat every number here as provisional and re-run training as more signals accumulate.
- Yahoo Finance data: symbols it doesn't carry are skipped (survivorship bias), and daily candles can't tell whether the stop or the target came first inside a day (handled pessimistically).
- Chartink's backtest list is the scanner's output as of today's definition; if the scan was edited, past hits reflect the new version, not what you would have seen live.
- Not investment advice. Size positions so a stop-out costs a small, fixed fraction of capital.