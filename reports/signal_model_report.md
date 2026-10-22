# Scanner signal model report

Generated 2026-10-22 18:46 UTC by `scripts/signal_model.py train`.

## The rule being tested

- **Trigger price** = high of the signal candle (the day's candle for the daily scanners, the completed week's candle for `Wkly_upswing`).
- **Entry**: buy-stop at the trigger, valid for 3 sessions after a daily signal (5 after a weekly one). Filled at the trigger, or at the open on a gap-up.
- **Stop** = signal candle low, kept between 2% and 8% below entry. **Target** = 2× that risk. Otherwise exit at the close after 20 sessions.
- Stop assumed hit first when a candle touches both levels, including on the entry day.
- Returns are after 0.25% round-trip costs. A win = return > 0.

## Data coverage

| Scanner | Hits | With prices | Triggered & closed | Not triggered | Still open / pending |
|---|---|---|---|---|---|
| 63_30_daily | 1832 | 1829 | 1439 | 389 | 1 |
| Bullish_Scanner | 5084 | 5064 | 4196 | 857 | 11 |
| Wkly_upswing | 1119 | 1116 | 749 | 365 | 2 |

## 1. Does buying every trigger make money?

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 1439 | 34% | -0.20% | +6.91% / -3.83% | 0.92 | -0.03 | 4.7 | -1.4 | -0.57% (t -4.1) |
| Bullish_Scanner | 4196 | 42% | +0.72% | +7.89% / -4.51% | 1.27 | +0.19 | 6.8 | +6.7 | +0.21% (t +2.0) |
| Wkly_upswing | 749 | 39% | +0.08% | +11.74% / -7.50% | 1.02 | +0.05 | 9.6 | +0.2 | -0.52% (t -1.4) |
| **All scanners** | 6384 | 40% | +0.43% | +8.15% / -4.69% | 1.15 | +0.12 | 6.6 | +4.9 | -0.06% (t -0.6) |

t-stat: average return divided by its standard error; below ~2 the average could easily be noise. **vs index**: average return minus what the Nifty 500 did over the same days. A scanner that only matches the index adds nothing over buying an index fund.

### By market-cap tier

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Largecap | 655 | 33% | -0.40% | +5.46% / -3.31% | 0.82 | -0.05 | 5.2 | -2.3 | -0.82% (t -5.0) |
| 63_30_daily · Midcap | 411 | 34% | +0.05% | +7.86% / -4.02% | 1.02 | +0.01 | 4.2 | +0.2 | -0.21% (t -0.8) |
| 63_30_daily · Smallcap | 373 | 34% | -0.11% | +8.34% / -4.53% | 0.96 | -0.02 | 4.3 | -0.3 | -0.55% (t -1.7) |
| Bullish_Scanner · Largecap | 2023 | 42% | +0.50% | +6.36% / -3.74% | 1.23 | +0.18 | 7.0 | +4.0 | +0.00% (t +0.0) |
| Bullish_Scanner · Midcap | 1139 | 44% | +0.90% | +8.48% / -5.01% | 1.32 | +0.20 | 7.0 | +4.1 | +0.40% (t +1.8) |
| Bullish_Scanner · Smallcap | 1034 | 41% | +0.93% | +10.28% / -5.46% | 1.29 | +0.17 | 6.0 | +3.5 | +0.39% (t +1.5) |
| Wkly_upswing · Largecap | 212 | 49% | +1.20% | +9.07% / -6.38% | 1.37 | +0.19 | 13.0 | +2.0 | +0.33% (t +0.6) |
| Wkly_upswing · Midcap | 180 | 43% | +1.25% | +12.54% / -7.39% | 1.30 | +0.20 | 10.3 | +1.6 | +0.63% (t +0.8) |
| Wkly_upswing · Smallcap | 355 | 32% | -1.14% | +13.64% / -8.05% | 0.79 | -0.11 | 7.2 | -2.0 | -1.57% (t -2.9) |

### By market regime at signal time (Nifty vs its 50-day average)

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Nifty above 50DMA | 1246 | 33% | -0.33% | +6.74% / -3.78% | 0.87 | -0.05 | 4.6 | -2.2 | -0.69% (t -4.7) |
| 63_30_daily · Nifty below 50DMA | 193 | 40% | +0.68% | +7.81% / -4.16% | 1.27 | +0.16 | 5.1 | +1.5 | +0.14% (t +0.3) |
| Bullish_Scanner · Nifty above 50DMA | 3603 | 42% | +0.69% | +7.80% / -4.50% | 1.27 | +0.19 | 6.7 | +6.0 | +0.21% (t +1.9) |
| Bullish_Scanner · Nifty below 50DMA | 593 | 41% | +0.85% | +8.44% / -4.53% | 1.32 | +0.14 | 7.1 | +2.9 | +0.16% (t +0.5) |
| Wkly_upswing · Nifty above 50DMA | 608 | 40% | +0.23% | +11.83% / -7.49% | 1.05 | +0.06 | 9.4 | +0.5 | -0.37% (t -0.9) |
| Wkly_upswing · Nifty below 50DMA | 141 | 37% | -0.58% | +11.34% / -7.55% | 0.88 | -0.03 | 10.0 | -0.7 | -1.17% (t -1.4) |

### Exit reasons

| Scanner | Target | Stop | Time exit |
|---|---|---|---|
| 63_30_daily | 31% | 65% | 4% |
| Bullish_Scanner | 34% | 54% | 12% |
| Wkly_upswing | 24% | 54% | 22% |

### Other exit rules (same entries)

Fixed set of alternatives, not optimized. Cells: trades · avg return · vs index (t-stat of the excess).

| Exit rule | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| Candle-low stop, 2R target, 20d | 1439 · -0.20% · -0.57% (t -4.1) | 4196 · +0.72% · +0.21% (t +2.0) | 749 · +0.08% · -0.52% (t -1.4) |
| Candle-low stop, no target, 20d | 1438 · +0.65% · -0.06% (t -0.2) | 4193 · +1.47% · +0.68% (t +4.4) | 749 · +0.81% · -0.02% (t -0.0) |
| Wide stop (≤15%), no target, 20d | 1438 · +0.67% · -0.05% (t -0.2) | 4191 · +1.52% · +0.71% (t +4.5) | 745 · +1.67% · +0.66% (t +1.0) |
| No stop, exit after 10d | 1437 · +1.37% · +0.64% (t +2.8) | 4196 · +1.89% · +1.14% (t +8.1) | 747 · +0.81% · +0.09% (t +0.2) |
| No stop, exit after 20d | 1435 · +2.85% · +1.48% (t +4.8) | 4184 · +3.23% · +1.75% (t +9.5) | 742 · +2.31% · +1.17% (t +1.8) |

## 2. Model: which triggers to take

Model: `hgb` predicting P(trade ends in profit) from price/volume features at the signal candle, market regime, repeat/confluence counts, scanner and market-cap tier. Validated **walk-forward**: each month is scored by a model trained only on trades that had closed before that month, so these are honest out-of-sample numbers (6228 scored trades from Jul 2020).

- Walk-forward ROC-AUC: logistic regression 0.54, gradient boosting 0.55 (0.50 = coin flip; the filter is only switched on at ≥ 0.55).
- **Not validated: the model could not tell winning triggers from losing ones out of sample**, so it is *not* used to filter. `predict` lists every setup with its levels and says the filter is off. Training re-checks this every run, so the filter switches itself on if enough new history makes it work.

### Out-of-sample return by probability quintile

| Quintile | P(profit) range | Trades | Win rate | Avg return |
|---|---|---|---|---|
| Q1 | 0.04–0.28 | 1246 | 35% | -0.14% |
| Q2 | 0.28–0.35 | 1245 | 36% | -0.05% |
| Q3 | 0.35–0.41 | 1246 | 40% | +0.42% |
| Q4 | 0.41–0.49 | 1245 | 42% | +0.61% |
| Q5 | 0.49–0.88 | 1246 | 47% | +1.38% |

Returns should rise steadily from Q1 to Q5 if the model has found something real. When validated, the threshold is picked on these same predictions, so the BUY row is slightly optimistic; the quintiles are the fairer check.

## Caveats

- Only ~8 months of history for the two daily scanners, all in one market phase. Treat every number here as provisional and re-run training as more signals accumulate.
- Yahoo Finance data: symbols it doesn't carry are skipped (survivorship bias), and daily candles can't tell whether the stop or the target came first inside a day (handled pessimistically).
- Chartink's backtest list is the scanner's output as of today's definition; if the scan was edited, past hits reflect the new version, not what you would have seen live.
- Not investment advice. Size positions so a stop-out costs a small, fixed fraction of capital.