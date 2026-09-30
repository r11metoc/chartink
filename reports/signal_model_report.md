# Scanner signal model report

Generated 2026-09-30 16:08 UTC by `scripts/signal_model.py train`.

## The rule being tested

- **Trigger price** = high of the signal candle (the day's candle for the daily scanners, the completed week's candle for `Wkly_upswing`).
- **Entry**: buy-stop at the trigger, valid for 3 sessions after a daily signal (5 after a weekly one). Filled at the trigger, or at the open on a gap-up.
- **Stop** = signal candle low, kept between 2% and 8% below entry. **Target** = 2× that risk. Otherwise exit at the close after 20 sessions.
- Stop assumed hit first when a candle touches both levels, including on the entry day.
- Returns are after 0.25% round-trip costs. A win = return > 0.

## Data coverage

| Scanner | Hits | With prices | Triggered & closed | Not triggered | Still open / pending |
|---|---|---|---|---|---|
| 63_30_daily | 426 | 425 | 273 | 143 | 9 |
| Bullish_Scanner | 244 | 244 | 170 | 61 | 13 |
| Wkly_upswing | 765 | 764 | 517 | 241 | 6 |

## 1. Does buying every trigger make money?

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 273 | 37% | +0.03% | +11.65% / -6.91% | 1.01 | +0.04 | 7.2 | +0.0 | +0.45% (t +0.8) |
| Bullish_Scanner | 170 | 39% | +0.28% | +9.89% / -5.97% | 1.08 | +0.09 | 8.7 | +0.4 | +0.77% (t +1.1) |
| Wkly_upswing | 517 | 37% | -0.34% | +12.43% / -7.70% | 0.93 | -0.00 | 9.2 | -0.7 | -0.81% (t -1.8) |
| **All scanners** | 960 | 37% | -0.13% | +11.73% / -7.18% | 0.97 | +0.03 | 8.5 | -0.4 | -0.17% (t -0.5) |

t-stat: average return divided by its standard error; below ~2 the average could easily be noise. **vs index**: average return minus what the Nifty 500 did over the same days. A scanner that only matches the index adds nothing over buying an index fund.

### By market-cap tier

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Largecap | 59 | 34% | -0.51% | +8.93% / -5.35% | 0.86 | -0.07 | 7.7 | -0.5 | +0.29% (t +0.3) |
| 63_30_daily · Midcap | 88 | 50% | +1.75% | +11.21% / -7.71% | 1.45 | +0.37 | 7.5 | +1.5 | +2.18% (t +2.1) |
| 63_30_daily · Smallcap | 126 | 30% | -0.93% | +13.60% / -7.20% | 0.82 | -0.14 | 6.7 | -1.0 | -0.67% (t -0.8) |
| Bullish_Scanner · Largecap | 66 | 41% | +0.83% | +8.10% / -4.21% | 1.33 | +0.20 | 9.7 | +1.0 | +1.17% (t +1.4) |
| Bullish_Scanner · Midcap | 52 | 42% | -0.02% | +9.89% / -7.29% | 0.99 | +0.10 | 7.8 | -0.0 | +0.44% (t +0.3) |
| Bullish_Scanner · Smallcap | 52 | 35% | -0.11% | +12.58% / -6.83% | 0.98 | -0.04 | 8.4 | -0.1 | +0.57% (t +0.4) |
| Wkly_upswing · Largecap | 112 | 52% | +1.46% | +9.08% / -6.73% | 1.45 | +0.24 | 13.3 | +1.7 | +0.75% (t +0.9) |
| Wkly_upswing · Midcap | 113 | 36% | -0.20% | +12.82% / -7.61% | 0.96 | +0.02 | 9.8 | -0.2 | -0.73% (t -0.8) |
| Wkly_upswing · Smallcap | 292 | 31% | -1.09% | +14.41% / -7.99% | 0.80 | -0.11 | 7.3 | -1.7 | -1.45% (t -2.3) |

### By market regime at signal time (Nifty vs its 50-day average)

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Nifty above 50DMA | 153 | 33% | -0.76% | +11.22% / -6.74% | 0.83 | -0.08 | 7.1 | -1.0 | +0.09% (t +0.1) |
| 63_30_daily · Nifty below 50DMA | 120 | 42% | +1.02% | +12.09% / -7.15% | 1.25 | +0.19 | 7.3 | +1.1 | +0.92% (t +1.1) |
| Bullish_Scanner · Nifty above 50DMA | 101 | 37% | -0.83% | +8.59% / -6.28% | 0.79 | -0.03 | 8.7 | -1.0 | -0.25% (t -0.3) |
| Bullish_Scanner · Nifty below 50DMA | 69 | 43% | +1.91% | +11.49% / -5.47% | 1.62 | +0.28 | 8.7 | +1.7 | +2.26% (t +2.0) |
| Wkly_upswing · Nifty above 50DMA | 406 | 36% | -0.40% | +12.34% / -7.71% | 0.92 | -0.01 | 9.1 | -0.8 | -0.85% (t -1.7) |
| Wkly_upswing · Nifty below 50DMA | 111 | 37% | -0.12% | +12.75% / -7.65% | 0.98 | +0.03 | 9.3 | -0.1 | -0.67% (t -0.7) |

### Exit reasons

| Scanner | Target | Stop | Time exit |
|---|---|---|---|
| 63_30_daily | 30% | 58% | 12% |
| Bullish_Scanner | 31% | 53% | 16% |
| Wkly_upswing | 24% | 56% | 20% |

### Other exit rules (same entries)

Fixed set of alternatives, not optimized. Cells: trades · avg return · vs index (t-stat of the excess).

| Exit rule | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| Candle-low stop, 2R target, 20d | 273 · +0.03% · +0.45% (t +0.8) | 170 · +0.28% · +0.77% (t +1.1) | 517 · -0.34% · -0.81% (t -1.8) |
| Candle-low stop, no target, 20d | 273 · -0.41% · +0.11% (t +0.2) | 166 · -0.69% · +0.02% (t +0.0) | 516 · +0.26% · -0.50% (t -0.8) |
| Wide stop (≤15%), no target, 20d | 272 · -0.06% · +0.40% (t +0.6) | 165 · -0.52% · +0.32% (t +0.4) | 514 · +0.94% · -0.16% (t -0.2) |
| No stop, exit after 10d | 273 · -0.55% · -0.16% (t -0.2) | 167 · +1.31% · +1.81% (t +2.4) | 517 · +0.60% · -0.14% (t -0.3) |
| No stop, exit after 20d | 264 · +1.44% · +1.54% (t +1.8) | 159 · -0.20% · +1.04% (t +1.1) | 511 · +1.98% · +0.54% (t +0.7) |

## 2. Model: which triggers to take

Model: `logreg` predicting P(trade ends in profit) from price/volume features at the signal candle, market regime, repeat/confluence counts, scanner and market-cap tier. Validated **walk-forward**: each month is scored by a model trained only on trades that had closed before that month, so these are honest out-of-sample numbers (806 scored trades from Apr 2024).

- Walk-forward ROC-AUC: logistic regression 0.50, gradient boosting 0.48 (0.50 = coin flip; the filter is only switched on at ≥ 0.55).
- **Not validated: the model could not tell winning triggers from losing ones out of sample**, so it is *not* used to filter. `predict` lists every setup with its levels and says the filter is off. Training re-checks this every run, so the filter switches itself on if enough new history makes it work.

### Out-of-sample return by probability quintile

| Quintile | P(profit) range | Trades | Win rate | Avg return |
|---|---|---|---|---|
| Q1 | 0.01–0.25 | 162 | 41% | +1.07% |
| Q2 | 0.25–0.32 | 161 | 36% | +0.05% |
| Q3 | 0.32–0.37 | 161 | 34% | -1.35% |
| Q4 | 0.37–0.44 | 161 | 37% | -0.42% |
| Q5 | 0.44–0.79 | 161 | 39% | +0.31% |

Returns should rise steadily from Q1 to Q5 if the model has found something real. When validated, the threshold is picked on these same predictions, so the BUY row is slightly optimistic; the quintiles are the fairer check.

## Caveats

- Only ~8 months of history for the two daily scanners, all in one market phase. Treat every number here as provisional and re-run training as more signals accumulate.
- Yahoo Finance data: symbols it doesn't carry are skipped (survivorship bias), and daily candles can't tell whether the stop or the target came first inside a day (handled pessimistically).
- Chartink's backtest list is the scanner's output as of today's definition; if the scan was edited, past hits reflect the new version, not what you would have seen live.
- Not investment advice. Size positions so a stop-out costs a small, fixed fraction of capital.