# Chartink backtest outcome report

Generated 2026-09-24 21:56 UTC.

## Methodology

- **Success rule**: a historical scan trigger is labeled a *real breakout* if price closed at least **+3.0%** above the trigger-day close within **5 trading days**; otherwise it's a *fake trigger* (hold).
- **Price source**: Yahoo Finance (NSE, `.NS` suffix). Symbols that don't resolve (delisted, renamed, or a ticker format Yahoo doesn't recognize) are skipped entirely, which introduces some survivorship bias - stocks that got delisted after a bad move are underrepresented.
- **Each scanner is modeled and reported separately** - they're different strategies with different behavior, so pooling them would blur real differences.
- Win rates below are shown with a 95% confidence interval (Wilson score) - treat any group with a wide interval as noisy, not a reliable edge.
- The model (where trained) uses only sector and market-cap tier as features - no price/volume/technical features - and is validated on a time-ordered holdout (most recent 20% of each scanner's data), not random k-fold, to avoid lookahead bias.
- Sample sizes here are small (hundreds of rows per scanner at most). Take the logistic regression's coefficients as suggestive, not proven; the win-rate tables are the more defensible output.

## 63_30_daily

**Overall**: 121/414 triggers were real breakouts (29%, 95% CI 25%-34%)

### Win rate by sector (n ≥ 5)

| Sector | n | Win rate | 95% CI |
|---|---|---|---|
| Miscellaneous | 8 | 62% | 31%-86% |
| Power & Utilities | 9 | 56% | 27%-81% |
| Healthcare | 42 | 48% | 33%-62% |
| Aerospace & Defence | 5 | 40% | 12%-77% |
| I.T | 31 | 39% | 24%-56% |
| Industrials | 58 | 36% | 25%-49% |
| Consumer Discretionary | 29 | 31% | 17%-49% |
| Realty | 25 | 28% | 14%-48% |
| FMCG | 25 | 28% | 14%-48% |
| Bank | 11 | 27% | 10%-57% |
| Financials | 34 | 26% | 15%-43% |
| Energy | 16 | 25% | 10%-49% |
| Metals & Mining | 18 | 22% | 9%-45% |
| Transportation | 9 | 22% | 6%-55% |
| Building Materials | 10 | 20% | 6%-51% |
| Auto | 18 | 17% | 6%-39% |
| Services | 11 | 9% | 2%-38% |
| Chemicals | 34 | 9% | 3%-23% |
| Textiles | 10 | 0% | 0%-28% |

### Win rate by market-cap tier (n ≥ 5)

| Tier | n | Win rate | 95% CI |
|---|---|---|---|
| Midcap | 144 | 32% | 25%-40% |
| Smallcap | 187 | 30% | 24%-37% |
| Largecap | 83 | 22% | 14%-32% |

### Model (logistic regression, sector + market-cap tier)

Trained on 331 rows, tested on the most recent 83 (time-ordered holdout):

- Accuracy: 59%
- Precision (of predicted breakouts, how many were real): 32%
- Recall (of real breakouts, how many were caught): 50%
- ROC-AUC: 0.61

- Features pushing toward 'real breakout': sector_Miscellaneous (+1.20), sector_Power & Utilities (+0.93), sector_Healthcare (+0.87), sector_Telecom (+0.73), sector_I.T (+0.51)
- Features pushing toward 'fake trigger': sector_Services (-0.56), sector_Building Materials (-0.56), sector_Plastic products (-0.78), sector_Chemicals (-0.91), sector_Textiles (-1.27)

## Bullish_Scanner

**Overall**: 64/220 triggers were real breakouts (29%, 95% CI 23%-35%)

### Win rate by sector (n ≥ 5)

| Sector | n | Win rate | 95% CI |
|---|---|---|---|
| I.T | 6 | 67% | 30%-90% |
| Consumer Discretionary | 12 | 42% | 19%-68% |
| FMCG | 18 | 39% | 20%-61% |
| Bank | 13 | 38% | 18%-64% |
| Auto | 9 | 33% | 12%-65% |
| Power & Utilities | 9 | 33% | 12%-65% |
| Realty | 6 | 33% | 10%-70% |
| Chemicals | 16 | 31% | 14%-56% |
| Healthcare | 34 | 29% | 17%-46% |
| Financials | 20 | 25% | 11%-47% |
| Metals & Mining | 16 | 25% | 10%-49% |
| Industrials | 17 | 24% | 10%-47% |
| Energy | 5 | 20% | 4%-62% |
| Transportation | 5 | 20% | 4%-62% |
| Miscellaneous | 7 | 14% | 3%-51% |
| Textiles | 10 | 10% | 2%-40% |
| Building Materials | 6 | 0% | 0%-39% |

### Win rate by market-cap tier (n ≥ 5)

| Tier | n | Win rate | 95% CI |
|---|---|---|---|
| Midcap | 72 | 33% | 24%-45% |
| Smallcap | 67 | 30% | 20%-42% |
| Largecap | 81 | 25% | 17%-35% |

### Model (logistic regression, sector + market-cap tier)

Trained on 176 rows, tested on the most recent 44 (time-ordered holdout):

- Accuracy: 43%
- Precision (of predicted breakouts, how many were real): 35%
- Recall (of real breakouts, how many were caught): 30%
- ROC-AUC: 0.47

- Features pushing toward 'real breakout': sector_Telecom (+0.73), sector_Consumer Discretionary (+0.63), sector_I.T (+0.59), sector_Services (+0.59), sector_Bank (+0.39)
- Features pushing toward 'fake trigger': sector_Healthcare (-0.32), sector_Media (-0.68), sector_Energy (-0.76), sector_Building Materials (-0.81), sector_Textiles (-1.08)

## Wkly_upswing

**Overall**: 617/756 triggers were real breakouts (82%, 95% CI 79%-84%)

### Win rate by sector (n ≥ 5)

| Sector | n | Win rate | 95% CI |
|---|---|---|---|
| Services | 28 | 93% | 77%-98% |
| Aerospace & Defence | 12 | 92% | 65%-99% |
| Metals & Mining | 49 | 90% | 78%-96% |
| Building Materials | 33 | 88% | 73%-95% |
| Power & Utilities | 16 | 88% | 64%-97% |
| Textiles | 24 | 88% | 69%-96% |
| FMCG | 54 | 85% | 73%-92% |
| Realty | 66 | 85% | 74%-92% |
| I.T | 50 | 84% | 71%-92% |
| Media | 6 | 83% | 44%-97% |
| Industrials | 65 | 83% | 72%-90% |
| Energy | 17 | 82% | 59%-94% |
| Financials | 70 | 81% | 71%-89% |
| Bank | 20 | 80% | 58%-92% |
| Consumer Discretionary | 38 | 79% | 64%-89% |
| Auto | 42 | 79% | 64%-88% |
| Miscellaneous | 22 | 77% | 57%-90% |
| Chemicals | 47 | 72% | 58%-83% |
| Healthcare | 64 | 72% | 60%-81% |
| Telecom | 7 | 71% | 36%-92% |
| Telecom-Service | 6 | 67% | 30%-90% |
| Transportation | 11 | 64% | 35%-85% |
| Plastic products | 8 | 62% | 31%-86% |

### Win rate by market-cap tier (n ≥ 5)

| Tier | n | Win rate | 95% CI |
|---|---|---|---|
| Smallcap | 445 | 83% | 80%-87% |
| Midcap | 168 | 79% | 72%-85% |
| Largecap | 143 | 79% | 72%-85% |

### Model (logistic regression, sector + market-cap tier)

Trained on 604 rows, tested on the most recent 152 (time-ordered holdout):

- Accuracy: 57%
- Precision (of predicted breakouts, how many were real): 78%
- Recall (of real breakouts, how many were caught): 61%
- ROC-AUC: 0.49

- Features pushing toward 'real breakout': sector_Power & Utilities (+1.27), sector_Media (+0.82), sector_Metals & Mining (+0.72), sector_Services (+0.63), sector_Realty (+0.38)
- Features pushing toward 'fake trigger': sector_Chemicals (-0.54), sector_Consumer Discretionary (-0.63), sector_Telecom-Service (-0.64), sector_Transportation (-0.72), sector_Plastic products (-0.95)