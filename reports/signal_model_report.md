# Scanner signal model report

Generated 2026-10-22 18:06 UTC by `scripts/signal_model.py train`.

## The rule being tested

- **Trigger price** = high of the signal candle (the day's candle for the daily scanners, the completed week's candle for `Wkly_upswing`).
- **Entry**: buy-stop at the trigger, valid for 3 sessions after a daily signal (5 after a weekly one). Filled at the trigger, or at the open on a gap-up.
- **Stop** = signal candle low, kept between 2% and 8% below entry. **Target** = 2× that risk. Otherwise exit at the close after 20 sessions.
- Stop assumed hit first when a candle touches both levels, including on the entry day.
- Returns are after 0.25% round-trip costs. A win = return > 0.

## Data coverage

| Scanner | Hits | With prices | Triggered & closed | Not triggered | Still open / pending |
|---|---|---|---|---|---|
| 63_30_daily | 6300 | 6286 | 4739 | 1545 | 2 |
| Bullish_Scanner | 5084 | 5066 | 4196 | 858 | 12 |
| Wkly_upswing | 1119 | 1116 | 750 | 365 | 1 |

## 1. Does buying every trigger make money?

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 4739 | 32% | -0.44% | +6.89% / -3.92% | 0.83 | -0.07 | 4.6 | -5.5 | -0.76% (t -9.9) |
| Bullish_Scanner | 4196 | 42% | +0.72% | +7.89% / -4.51% | 1.27 | +0.19 | 6.8 | +6.7 | +0.21% (t +2.0) |
| Wkly_upswing | 750 | 39% | +0.07% | +11.74% / -7.50% | 1.01 | +0.04 | 9.6 | +0.2 | -0.53% (t -1.5) |
| **All scanners** | 9685 | 37% | +0.10% | +7.78% / -4.42% | 1.04 | +0.05 | 5.9 | +1.4 | -0.32% (t -5.0) |

t-stat: average return divided by its standard error; below ~2 the average could easily be noise. **vs index**: average return minus what the Nifty 500 did over the same days. A scanner that only matches the index adds nothing over buying an index fund.

### By market-cap tier

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Largecap | 1761 | 33% | -0.40% | +5.43% / -3.33% | 0.82 | -0.03 | 5.1 | -3.7 | -0.72% (t -7.3) |
| 63_30_daily · Midcap | 1382 | 33% | -0.26% | +7.26% / -3.93% | 0.90 | -0.06 | 4.5 | -1.7 | -0.57% (t -3.9) |
| 63_30_daily · Smallcap | 1596 | 30% | -0.66% | +8.32% / -4.52% | 0.79 | -0.12 | 4.2 | -4.1 | -0.95% (t -6.2) |
| Bullish_Scanner · Largecap | 2023 | 42% | +0.50% | +6.36% / -3.74% | 1.23 | +0.18 | 7.0 | +4.0 | +0.00% (t +0.0) |
| Bullish_Scanner · Midcap | 1138 | 44% | +0.89% | +8.47% / -5.01% | 1.32 | +0.20 | 7.0 | +4.0 | +0.38% (t +1.8) |
| Bullish_Scanner · Smallcap | 1035 | 41% | +0.94% | +10.29% / -5.46% | 1.29 | +0.18 | 6.0 | +3.6 | +0.41% (t +1.6) |
| Wkly_upswing · Largecap | 212 | 49% | +1.20% | +9.07% / -6.38% | 1.37 | +0.19 | 13.0 | +2.0 | +0.33% (t +0.6) |
| Wkly_upswing · Midcap | 180 | 43% | +1.25% | +12.54% / -7.39% | 1.30 | +0.20 | 10.3 | +1.6 | +0.63% (t +0.8) |
| Wkly_upswing · Smallcap | 357 | 32% | -1.18% | +13.64% / -8.05% | 0.78 | -0.12 | 7.2 | -2.1 | -1.60% (t -2.9) |

### By market regime at signal time (Nifty vs its 50-day average)

| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |
|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily · Nifty above 50DMA | 4042 | 32% | -0.41% | +6.75% / -3.83% | 0.84 | -0.06 | 4.6 | -4.8 | -0.68% (t -8.4) |
| 63_30_daily · Nifty below 50DMA | 697 | 31% | -0.62% | +7.72% / -4.41% | 0.80 | -0.12 | 4.9 | -2.7 | -1.17% (t -5.3) |
| Bullish_Scanner · Nifty above 50DMA | 3603 | 42% | +0.69% | +7.80% / -4.50% | 1.27 | +0.19 | 6.7 | +6.0 | +0.21% (t +1.9) |
| Bullish_Scanner · Nifty below 50DMA | 593 | 41% | +0.85% | +8.44% / -4.53% | 1.32 | +0.14 | 7.1 | +2.9 | +0.16% (t +0.5) |
| Wkly_upswing · Nifty above 50DMA | 608 | 40% | +0.23% | +11.83% / -7.49% | 1.05 | +0.06 | 9.4 | +0.5 | -0.37% (t -0.9) |
| Wkly_upswing · Nifty below 50DMA | 142 | 37% | -0.64% | +11.34% / -7.56% | 0.87 | -0.04 | 10.0 | -0.8 | -1.22% (t -1.5) |

### Exit reasons

| Scanner | Target | Stop | Time exit |
|---|---|---|---|
| 63_30_daily | 29% | 66% | 4% |
| Bullish_Scanner | 34% | 54% | 12% |
| Wkly_upswing | 24% | 54% | 22% |

### Other exit rules (same entries)

Fixed set of alternatives, not optimized. Cells: trades · avg return · vs index (t-stat of the excess).

| Exit rule | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| Candle-low stop, 2R target, 20d | 4739 · -0.44% · -0.76% (t -9.9) | 4196 · +0.72% · +0.21% (t +2.0) | 750 · +0.07% · -0.53% (t -1.5) |
| Candle-low stop, no target, 20d | 4737 · +0.29% · -0.23% (t -1.7) | 4194 · +1.47% · +0.68% (t +4.4) | 750 · +0.80% · -0.03% (t -0.1) |
| Wide stop (≤15%), no target, 20d | 4737 · +0.28% · -0.24% (t -1.8) | 4193 · +1.51% · +0.70% (t +4.5) | 746 · +1.66% · +0.65% (t +1.0) |
| No stop, exit after 10d | 4732 · +0.58% · -0.01% (t -0.1) | 4197 · +1.88% · +1.14% (t +8.0) | 747 · +0.81% · +0.09% (t +0.2) |
| No stop, exit after 20d | 4724 · +1.77% · +0.65% (t +3.8) | 4184 · +3.23% · +1.75% (t +9.5) | 742 · +2.31% · +1.17% (t +1.8) |

## 2. Model: which triggers to take

Model: `logreg` predicting P(trade ends in profit) from price/volume features at the signal candle, market regime, repeat/confluence counts, scanner and market-cap tier. Validated **walk-forward**: each month is scored by a model trained only on trades that had closed before that month, so these are honest out-of-sample numbers (9529 scored trades from Jul 2020).

- Walk-forward ROC-AUC: logistic regression 0.55, gradient boosting 0.55 (0.50 = coin flip; the filter is only switched on at ≥ 0.55).
- **Not validated: the model could not tell winning triggers from losing ones out of sample**, so it is *not* used to filter. `predict` lists every setup with its levels and says the filter is off. Training re-checks this every run, so the filter switches itself on if enough new history makes it work.

### Out-of-sample return by probability quintile

| Quintile | P(profit) range | Trades | Win rate | Avg return |
|---|---|---|---|---|
| Q1 | 0.00–0.29 | 1906 | 32% | -0.38% |
| Q2 | 0.29–0.34 | 1906 | 33% | -0.41% |
| Q3 | 0.34–0.38 | 1905 | 36% | -0.08% |
| Q4 | 0.38–0.43 | 1906 | 41% | +0.62% |
| Q5 | 0.43–0.90 | 1906 | 43% | +0.75% |

Returns should rise steadily from Q1 to Q5 if the model has found something real. When validated, the threshold is picked on these same predictions, so the BUY row is slightly optimistic; the quintiles are the fairer check.

## Caveats

- Only ~8 months of history for the two daily scanners, all in one market phase. Treat every number here as provisional and re-run training as more signals accumulate.
- Yahoo Finance data: symbols it doesn't carry are skipped (survivorship bias), and daily candles can't tell whether the stop or the target came first inside a day (handled pessimistically).
- Chartink's backtest list is the scanner's output as of today's definition; if the scan was edited, past hits reflect the new version, not what you would have seen live.
- Not investment advice. Size positions so a stop-out costs a small, fixed fraction of capital.