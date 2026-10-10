# Scanner signal model report

Generated 2026-10-10 09:58 UTC by `scripts/signal_model.py train`.

## The rule being tested

- **Trigger price** = high of the signal candle (the day's candle for the daily scanners, the completed week's candle for `Wkly_upswing`).
- **Entry**: buy-stop at the trigger, valid for 3 sessions after a daily signal (5 after a weekly one). Filled at the trigger, or at the open on a gap-up.
- **Stop** = signal candle low, kept between 2% and 8% below entry. **Target** = 2× that risk. Otherwise exit at the close after 20 sessions.
- Stop assumed hit first when a candle touches both levels, including on the entry day.
- Returns are after 0.25% round-trip costs. A win = return > 0.

## Data coverage

| Scanner | Hits | With prices | Triggered & closed | Not triggered | Still open / pending |
|---|---|---|---|---|---|
| 63_30_daily | 427 | 426 | 280 | 142 | 4 |
| Bullish_Scanner | 247 | 247 | 179 | 58 | 10 |
| Wkly_upswing | 768 | 767 | 521 | 243 | 3 |

## 1. Does buying every trigger make money?

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 280 | 37% | -0.04% | +11.84% / -6.96% | 0.99 | +0.03 | 7.1 | -0.1 | +0.47% (t +0.8) |
| Bullish_Scanner | 179 | 40% | +0.46% | +10.16% / -6.07% | 1.13 | +0.11 | 8.4 | +0.7 | +1.04% (t +1.6) |
| Wkly_upswing | 521 | 37% | -0.33% | +12.41% / -7.71% | 0.93 | -0.00 | 9.2 | -0.7 | -0.77% (t -1.7) |
| **All scanners** | 980 | 37% | -0.11% | +11.81% / -7.21% | 0.98 | +0.03 | 8.4 | -0.3 | -0.08% (t -0.3) |

t-stat: average return divided by its standard error; below ~2 the average could easily be noise. **vs index**: average return minus what the Nifty 500 did over the same days. A scanner that only matches the index adds nothing over buying an index fund.

### By market-cap tier

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Largecap | 59 | 34% | -0.34% | +9.51% / -5.39% | 0.90 | -0.05 | 7.6 | -0.3 | +0.44% (t +0.4) |
| 63_30_daily · Midcap | 92 | 49% | +1.68% | +11.46% / -7.68% | 1.43 | +0.35 | 7.5 | +1.5 | +2.22% (t +2.1) |
| 63_30_daily · Smallcap | 129 | 29% | -1.13% | +13.52% / -7.25% | 0.78 | -0.17 | 6.5 | -1.3 | -0.77% (t -0.9) |
| Bullish_Scanner · Largecap | 67 | 45% | +0.87% | +7.55% / -4.54% | 1.35 | +0.20 | 9.5 | +1.0 | +1.27% (t +1.5) |
| Bullish_Scanner · Midcap | 57 | 40% | +0.19% | +10.79% / -6.97% | 1.05 | +0.11 | 7.6 | +0.1 | +0.82% (t +0.6) |
| Bullish_Scanner · Smallcap | 55 | 35% | +0.24% | +13.54% / -6.78% | 1.05 | +0.01 | 7.8 | +0.2 | +1.00% (t +0.7) |
| Wkly_upswing · Largecap | 112 | 52% | +1.54% | +9.25% / -6.74% | 1.48 | +0.25 | 13.2 | +1.8 | +0.85% (t +1.0) |
| Wkly_upswing · Midcap | 113 | 36% | -0.27% | +12.68% / -7.65% | 0.94 | +0.01 | 9.8 | -0.3 | -0.80% (t -0.9) |
| Wkly_upswing · Smallcap | 296 | 31% | -1.07% | +14.28% / -7.99% | 0.81 | -0.10 | 7.4 | -1.7 | -1.37% (t -2.2) |

### By market regime at signal time (Nifty vs its 50-day average)

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Nifty above 50DMA | 154 | 34% | -0.66% | +11.30% / -6.76% | 0.85 | -0.07 | 6.9 | -0.9 | +0.22% (t +0.3) |
| 63_30_daily · Nifty below 50DMA | 126 | 40% | +0.72% | +12.39% / -7.22% | 1.17 | +0.14 | 7.3 | +0.8 | +0.78% (t +0.9) |
| Bullish_Scanner · Nifty above 50DMA | 102 | 37% | -0.76% | +8.67% / -6.37% | 0.81 | -0.02 | 8.6 | -0.9 | -0.12% (t -0.1) |
| Bullish_Scanner · Nifty below 50DMA | 77 | 44% | +2.08% | +11.83% / -5.62% | 1.66 | +0.29 | 8.0 | +1.9 | +2.59% (t +2.5) |
| Wkly_upswing · Nifty above 50DMA | 406 | 36% | -0.41% | +12.36% / -7.73% | 0.92 | -0.01 | 9.1 | -0.8 | -0.85% (t -1.7) |
| Wkly_upswing · Nifty below 50DMA | 115 | 37% | -0.07% | +12.58% / -7.63% | 0.98 | +0.03 | 9.3 | -0.1 | -0.48% (t -0.5) |

### Exit reasons

| Scanner | Target | Stop | Time exit |
|---|---|---|---|
| 63_30_daily | 30% | 59% | 11% |
| Bullish_Scanner | 31% | 53% | 16% |
| Wkly_upswing | 24% | 56% | 20% |

### Other exit rules (same entries)

Fixed set of alternatives, not optimized. Cells: trades · avg return · vs index (t-stat of the excess).

| Exit rule | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| Candle-low stop, 2R target, 20d | 280 · -0.04% · +0.47% (t +0.8) | 179 · +0.46% · +1.04% (t +1.6) | 521 · -0.33% · -0.77% (t -1.7) |
| Candle-low stop, no target, 20d | 280 · -0.62% · -0.00% (t -0.0) | 175 · -0.24% · +0.69% (t +0.8) | 521 · +0.34% · -0.36% (t -0.6) |
| Wide stop (≤15%), no target, 20d | 279 · -0.34% · +0.25% (t +0.4) | 173 · -0.11% · +0.95% (t +1.1) | 519 · +1.00% · -0.04% (t -0.1) |
| No stop, exit after 10d | 281 · -0.79% · -0.28% (t -0.4) | 179 · +1.49% · +2.26% (t +2.7) | 517 · +0.54% · -0.20% (t -0.4) |
| No stop, exit after 20d | 272 · +0.90% · +1.26% (t +1.5) | 166 · +0.42% · +1.96% (t +2.0) | 515 · +2.00% · +0.62% (t +0.9) |

## 2. Model: which triggers to take

Model: `logreg` predicting P(trade ends in profit) from price/volume features at the signal candle, market regime, repeat/confluence counts, scanner and market-cap tier. Validated **walk-forward**: each month is scored by a model trained only on trades that had closed before that month, so these are honest out-of-sample numbers (826 scored trades from Apr 2024).

- Walk-forward ROC-AUC: logistic regression 0.50, gradient boosting 0.49 (0.50 = coin flip; the filter is only switched on at ≥ 0.55).
- **Not validated: the model could not tell winning triggers from losing ones out of sample**, so it is *not* used to filter. `predict` lists every setup with its levels and says the filter is off. Training re-checks this every run, so the filter switches itself on if enough new history makes it work.

### Out-of-sample return by probability quintile

| Quintile | P(profit) range | Trades | Win rate | Avg return |
|---|---|---|---|---|
| Q1 | 0.01–0.26 | 166 | 40% | +1.26% |
| Q2 | 0.26–0.32 | 165 | 34% | -0.23% |
| Q3 | 0.32–0.38 | 165 | 38% | -0.48% |
| Q4 | 0.38–0.45 | 165 | 35% | -1.26% |
| Q5 | 0.45–0.79 | 165 | 41% | +0.49% |

Returns should rise steadily from Q1 to Q5 if the model has found something real. When validated, the threshold is picked on these same predictions, so the BUY row is slightly optimistic; the quintiles are the fairer check.

## Caveats

- Only ~8 months of history for the two daily scanners, all in one market phase. Treat every number here as provisional and re-run training as more signals accumulate.
- Yahoo Finance data: symbols it doesn't carry are skipped (survivorship bias), and daily candles can't tell whether the stop or the target came first inside a day (handled pessimistically).
- Chartink's backtest list is the scanner's output as of today's definition; if the scan was edited, past hits reflect the new version, not what you would have seen live.
- Not investment advice. Size positions so a stop-out costs a small, fixed fraction of capital.