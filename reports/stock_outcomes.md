# If I had bought every scanner stock

Generated 2026-10-21 08:25 UTC by `scripts/stock_outcomes.py` from `data/backtest/*.csv` plus the bot's live triggers.

**Rule:** buy when price crosses the signal candle's high within 3 sessions (5 for `Wkly_upswing`), filled at the trigger or at the open on a gap-up; then hold. No stop, no target, no costs. **Short** = 2 weeks / 1 month, **Medium** = 3 / 6 months, **Long** = 1 / 2 years. **Beat Nifty 500** = share of buys that did better than the index over the same days. Recent buys only count for horizons that have fully passed.

Per-trade data: `data/model/stock_outcomes.csv`; per-stock: `data/model/stock_summary.csv`.

## All scanners at a glance

| Scanner | Signals | Bought | 1 month avg | 6 months avg | 1 year avg | 2 years avg | 1 year vs Nifty 500 |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 2998 | 2122 | +1.9% | +10.1% | +25.1% | +63.2% | +12.5% |
| Bullish_Scanner | 1701 | 1333 | +1.4% | +12.2% | +25.8% | +32.9% | +8.4% |
| Wkly_upswing | 1838 | 1220 | +2.4% | +15.5% | +30.3% | +52.2% | +18.9% |

## 63_30_daily

2998 signals (29 Dec 2020 to 16 Oct 2026): 2122 bought, 869 never crossed the trigger, 6 without Yahoo prices, 1 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 2119 | 47% | +0.3% | -0.6% | +5.8% / -5.6% | +0.6% | 43% | -0.3% |
| Short | 1 month | 2111 | 50% | +1.9% | -0.1% | +9.8% / -7.8% | +1.0% | 45% | +0.8% |
| Medium | 3 months | 2071 | 54% | +6.1% | +2.1% | +21.6% / -12.1% | +3.0% | 48% | +3.1% |
| Medium | 6 months | 1868 | 54% | +10.1% | +3.1% | +39.2% / -16.3% | +5.6% | 45% | +4.6% |
| Long | 1 year | 1771 | 56% | +25.1% | +7.5% | +62.7% / -21.9% | +12.6% | 46% | +12.5% |
| Long | 2 years | 1405 | 64% | +63.2% | +25.8% | +134.9% / -26.4% | +30.4% | 48% | +32.8% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Largecap | 511 / 55% / +2.2% / +0.9% | 466 / 69% / +15.6% / +9.6% | 428 / 72% / +43.6% / +29.5% |
| Midcap | 583 / 56% / +3.6% / +2.4% | 504 / 59% / +16.2% / +10.2% | 477 / 62% / +34.9% / +21.1% |
| Smallcap | 1017 / 44% / +0.7% / -0.2% | 898 / 44% / +3.9% / -1.2% | 866 / 46% / +10.6% / -0.6% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2020 | 3 / – / – / – | 3 / – / – / – | 3 / – / – / – |
| 2021 | 229 / 49% / +3.9% / +1.5% | 229 / 58% / +15.8% / +6.5% | 229 / 52% / +17.1% / +10.2% |
| 2022 | 375 / 41% / -1.0% / +0.9% | 375 / 46% / +0.4% / +1.8% | 375 / 66% / +31.3% / +21.3% |
| 2023 | 423 / 62% / +4.6% / +1.5% | 423 / 81% / +33.4% / +16.8% | 423 / 83% / +65.4% / +29.6% |
| 2024 | 416 / 49% / +2.5% / +0.8% | 416 / 46% / +3.0% / +1.2% | 416 / 38% / -0.2% / -3.9% |
| 2025 | 376 / 47% / +0.6% / -0.7% | 376 / 38% / -3.8% / -6.3% | 325 / 38% / +2.5% / +2.0% |
| 2026 | 289 / 47% / +0.7% / +1.3% | 46 / 57% / +24.8% / +24.3% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Aerospace & Defence | 44 / 57% / +5.6% / +3.4% | 42 / 62% / +18.4% / +11.8% | 42 / 69% / +67.9% / +53.8% |
| Auto | 106 / 62% / +4.0% / +2.5% | 92 / 65% / +14.4% / +8.5% | 89 / 72% / +45.4% / +31.0% |
| Bank | 67 / 49% / -0.0% / -1.1% | 61 / 66% / +8.7% / +3.6% | 53 / 79% / +26.3% / +10.0% |
| Building Materials | 96 / 44% / -0.0% / -1.2% | 91 / 33% / -4.2% / -9.0% | 88 / 36% / -5.8% / -18.1% |
| Chemicals | 164 / 41% / +0.5% / -0.3% | 149 / 38% / +0.2% / -4.4% | 141 / 50% / +9.2% / -0.2% |
| Consumer Discretionary | 124 / 57% / +5.7% / +4.2% | 105 / 45% / +9.6% / +5.6% | 102 / 48% / +20.5% / +9.6% |
| Energy | 76 / 54% / +2.9% / +1.7% | 67 / 70% / +10.4% / +4.4% | 60 / 53% / +25.6% / +12.0% |
| FMCG | 140 / 46% / -0.8% / -1.5% | 126 / 59% / +14.6% / +8.2% | 122 / 59% / +24.5% / +11.2% |
| Financials | 186 / 58% / +2.1% / +0.8% | 164 / 58% / +8.9% / +2.5% | 155 / 62% / +21.9% / +8.1% |
| Healthcare | 160 / 54% / +1.9% / +0.8% | 130 / 58% / +10.8% / +4.9% | 124 / 59% / +18.2% / +7.1% |
| I.T | 142 / 38% / +0.1% / -0.5% | 120 / 55% / +13.9% / +8.9% | 115 / 51% / +17.5% / +6.2% |
| Industrials | 165 / 55% / +3.7% / +2.8% | 134 / 60% / +21.9% / +15.9% | 125 / 57% / +60.5% / +48.0% |
| Media | 30 / 43% / -3.3% / -3.6% | 30 / 40% / -9.7% / -16.0% | 29 / 41% / +1.9% / -14.5% |
| Metals & Mining | 123 / 52% / +3.1% / +2.2% | 112 / 60% / +14.8% / +7.6% | 105 / 70% / +37.5% / +23.3% |
| Miscellaneous | 59 / 39% / -0.8% / -2.2% | 54 / 50% / +2.0% / -6.4% | 52 / 52% / +18.2% / +0.4% |
| Power & Utilities | 40 / 45% / +6.5% / +5.0% | 37 / 51% / +17.7% / +11.1% | 33 / 64% / +50.7% / +34.5% |
| Realty | 169 / 49% / +2.6% / +1.5% | 153 / 58% / +12.4% / +6.8% | 150 / 58% / +25.5% / +13.5% |
| Services | 43 / 49% / +3.3% / +2.7% | 36 / 58% / +9.7% / +5.3% | 36 / 56% / +23.2% / +11.1% |
| Textiles | 65 / 45% / -0.7% / -1.5% | 62 / 42% / +5.3% / +1.2% | 57 / 42% / +11.7% / +0.7% |
| Transportation | 39 / 28% / -3.5% / -3.9% | 34 / 38% / -4.1% / -8.7% | 31 / 35% / +2.5% / -8.3% |

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| TARIL | Industrials | Midcap | 4 | +14.9% | +53.8% | +295.9% | 75% |
| FORCEMOT | Auto | Largecap | 3 | +20.8% | +30.6% | +250.9% | 100% |
| KALYANKJIL | Consumer Discretionary | Largecap | 3 | +15.3% | +115.3% | +223.6% | 100% |
| RVNL | Realty | Largecap | 3 | +14.0% | +55.1% | +200.5% | 100% |
| PGEL | Consumer Discretionary | Midcap | 3 | +25.6% | +142.8% | +165.5% | 100% |
| HUDCO | Financials | Largecap | 3 | +1.4% | +22.0% | +156.3% | 100% |
| CEMPRO | Realty | Largecap | 3 | +13.4% | +42.8% | +155.5% | 67% |
| HPL | Industrials | Smallcap | 3 | +18.7% | +53.0% | +141.5% | 100% |
| GVT&D | Industrials | Largecap | 3 | -9.7% | +27.7% | +141.3% | 33% |
| INDIAGLYCO | FMCG | Smallcap | 3 | +4.1% | +63.8% | +136.9% | 67% |

**Worst repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| SHANKARA | Consumer Discretionary | Smallcap | 3 | +17.2% | -59.7% | -59.8% | 0% |
| REDTAPE | Consumer Discretionary | Midcap | 3 | -6.9% | -3.6% | -46.6% | 0% |
| NETWORK18 | Media | Smallcap | 3 | -24.6% | -42.7% | -46.2% | 0% |
| UFLEX | Industrials | Smallcap | 4 | +1.7% | -18.6% | -39.5% | 0% |
| RPPINFRA | Realty | Smallcap | 3 | +4.6% | -21.0% | -38.4% | 0% |
| NECLIFE | Healthcare | Smallcap | 5 | +6.7% | -31.0% | -37.0% | 0% |
| CENTENKA | Textiles | Smallcap | 3 | -10.3% | -28.9% | -34.3% | 0% |
| SFL | Consumer Discretionary | Midcap | 3 | -1.6% | -30.3% | -33.6% | 0% |
| ALLCARGO | Transportation | Smallcap | 3 | -7.5% | -21.1% | -32.2% | 0% |
| KOPRAN | Healthcare | Smallcap | 3 | +0.7% | -21.3% | -28.3% | 0% |

**Biggest single winners after 1 year**

| Stock | Bought | Price | Return | Nifty 500 |
|---|---|---|---|---|
| TARIL | 2023-05-24 | 39.35 | +787.2% | +30.7% |
| WEBELSOLAR | 2023-08-24 | 12.85 | +707.1% | +40.2% |
| CUPID | 2025-05-16 | 18.88 | +537.2% | -0.6% |
| OLECTRA | 2020-12-31 | 139.00 | +481.7% | +32.9% |
| GVT&D | 2023-04-28 | 175.05 | +475.7% | +35.0% |
| MAZDOCK | 2022-08-29 | 179.77 | +431.3% | +13.4% |
| FORCEMOT | 2023-05-30 | 1559.95 | +428.6% | +44.0% |
| SHAKTIPUMP | 2023-05-17 | 83.00 | +400.6% | +38.0% |
| RVNL | 2022-09-22 | 35.75 | +364.6% | +11.8% |
| JINDALSAW | 2023-01-02 | 53.90 | +357.4% | +26.3% |

## Bullish_Scanner

1701 signals (11 Jun 2021 to 19 Oct 2026): 1333 bought, 356 never crossed the trigger, 9 without Yahoo prices, 3 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 1323 | 48% | +0.5% | -0.3% | +4.9% / -4.6% | +0.5% | 45% | +0.0% |
| Short | 1 month | 1308 | 50% | +1.4% | +0.0% | +8.1% / -6.4% | +1.2% | 45% | +0.2% |
| Medium | 3 months | 1249 | 56% | +5.4% | +3.2% | +18.0% / -10.9% | +4.0% | 48% | +1.4% |
| Medium | 6 months | 1181 | 60% | +12.2% | +6.2% | +30.8% / -14.5% | +8.4% | 48% | +3.8% |
| Long | 1 year | 1047 | 64% | +25.8% | +13.0% | +54.1% / -18.3% | +17.4% | 48% | +8.4% |
| Long | 2 years | 877 | 61% | +32.9% | +16.1% | +87.5% / -23.0% | +24.9% | 44% | +8.0% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Largecap | 465 / 54% / +1.8% / +1.0% | 423 / 70% / +16.4% / +9.2% | 352 / 76% / +35.8% / +19.3% |
| Midcap | 415 / 50% / +2.0% / +0.5% | 376 / 62% / +14.8% / +6.4% | 337 / 66% / +32.8% / +14.8% |
| Smallcap | 428 / 46% / +0.3% / -1.2% | 382 / 48% / +4.9% / -4.7% | 358 / 51% / +9.5% / -8.3% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2021 | 1 / – / – / – | 1 / – / – / – | 1 / – / – / – |
| 2022 | 32 / 44% / +0.4% / +1.8% | 32 / 56% / +5.6% / +5.2% | 32 / 84% / +61.3% / +44.7% |
| 2023 | 472 / 58% / +3.0% / +0.1% | 472 / 74% / +23.5% / +5.9% | 470 / 83% / +49.3% / +15.1% |
| 2024 | 428 / 46% / +0.9% / -0.6% | 428 / 53% / +6.4% / +1.8% | 428 / 47% / +2.5% / -1.4% |
| 2025 | 178 / 49% / -0.4% / -0.6% | 178 / 44% / -1.6% / +0.2% | 116 / 48% / +7.8% / +7.9% |
| 2026 | 197 / 43% / +0.4% / +2.1% | 70 / 59% / +9.7% / +10.3% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Auto | 80 / 49% / +1.3% / -0.3% | 74 / 64% / +16.9% / +11.1% | 67 / 76% / +35.7% / +20.9% |
| Bank | 69 / 55% / -0.0% / -0.1% | 64 / 70% / +10.1% / +4.9% | 41 / 66% / +8.2% / -6.4% |
| Building Materials | 60 / 50% / +0.8% / -0.2% | 58 / 43% / +3.0% / -6.3% | 55 / 44% / +7.4% / -12.5% |
| Chemicals | 104 / 43% / -0.1% / -1.6% | 93 / 53% / +4.7% / -3.9% | 84 / 51% / +12.6% / -3.2% |
| Consumer Discretionary | 69 / 45% / +1.3% / -0.2% | 61 / 49% / +7.4% / -2.5% | 58 / 57% / +23.2% / +4.3% |
| Energy | 51 / 47% / -0.0% / -0.6% | 49 / 61% / +10.4% / +0.4% | 45 / 60% / +31.6% / +11.1% |
| FMCG | 87 / 45% / +0.5% / +0.3% | 74 / 50% / +4.0% / -4.1% | 64 / 61% / +16.2% / -2.4% |
| Financials | 128 / 52% / +1.3% / -0.3% | 117 / 61% / +12.8% / +4.5% | 106 / 68% / +27.5% / +10.5% |
| Healthcare | 147 / 60% / +3.2% / +1.9% | 126 / 75% / +18.2% / +10.1% | 111 / 80% / +36.7% / +20.2% |
| I.T | 75 / 45% / +0.1% / -0.9% | 70 / 51% / +6.9% / -1.1% | 63 / 62% / +22.4% / +5.4% |
| Industrials | 89 / 52% / +2.9% / +1.6% | 82 / 70% / +20.8% / +11.0% | 73 / 66% / +41.5% / +20.7% |
| Metals & Mining | 74 / 55% / +4.0% / +3.7% | 65 / 69% / +15.7% / +9.0% | 50 / 76% / +26.4% / +12.3% |
| Miscellaneous | 31 / 58% / +2.3% / +0.2% | 28 / 54% / +11.6% / +3.0% | 28 / 50% / +9.7% / -9.8% |
| Realty | 76 / 55% / +2.5% / +0.2% | 72 / 75% / +20.6% / +11.6% | 66 / 71% / +43.9% / +26.3% |
| Services | 27 / 48% / +0.5% / -0.8% | 25 / 68% / +21.0% / +9.9% | 24 / 58% / +22.6% / +7.1% |
| Textiles | 36 / 39% / -0.6% / -1.6% | 31 / 42% / +3.2% / -5.5% | 29 / 52% / +11.9% / -5.2% |

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| TORNTPOWER | Power & Utilities | Largecap | 3 | +5.7% | +41.0% | +128.4% | 67% |
| KIRLOSENG | Industrials | Largecap | 3 | +5.1% | +40.5% | +111.4% | 33% |
| MARKSANS | Healthcare | Midcap | 4 | +2.8% | +40.7% | +109.6% | 75% |
| GLENMARK | Healthcare | Largecap | 3 | +15.0% | +61.7% | +100.5% | 100% |
| OIL | Energy | Largecap | 3 | +3.6% | +35.4% | +100.2% | 67% |
| CHENNPETRO | Energy | Largecap | 3 | +2.9% | +25.0% | +94.1% | 67% |
| NATIONALUM | Metals & Mining | Largecap | 3 | +6.9% | +65.3% | +87.9% | 100% |
| ZYDUSLIFE | Healthcare | Largecap | 3 | -0.6% | +36.6% | +87.2% | 33% |
| COHANCE | Healthcare | Midcap | 4 | +10.9% | +17.5% | +86.4% | 100% |
| ACUTAAS | Healthcare | Largecap | 3 | +2.1% | +46.8% | +84.9% | 67% |

**Worst repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| SENCO | Consumer Discretionary | Midcap | 3 | -11.8% | +19.1% | -30.0% | 0% |
| PVRINOX | Media | Midcap | 4 | -2.5% | -22.2% | -28.0% | 0% |
| AETHER | Chemicals | Largecap | 4 | -0.8% | +6.3% | -22.3% | 0% |
| MANYAVAR | Readymade Garments/Apparels | Midcap | 4 | -12.3% | -28.4% | -18.6% | 0% |
| IGL | Energy | Midcap | 3 | -1.4% | -5.6% | -14.9% | 0% |
| MATRIMONY | Miscellaneous | Smallcap | 3 | +3.0% | -5.8% | -13.6% | 0% |
| ARVINDFASN | Services | Midcap | 3 | -7.1% | -19.1% | -12.9% | 0% |
| KIRIINDUS | Chemicals | Smallcap | 3 | -8.0% | -10.0% | -12.7% | 33% |
| EPL | Industrials | Midcap | 4 | -5.6% | +0.5% | -10.6% | 25% |
| NESTLEIND | FMCG | Largecap | 3 | -4.7% | -0.9% | -10.3% | 0% |

**Biggest single winners after 1 year**

| Stock | Bought | Price | Return | Nifty 500 |
|---|---|---|---|---|
| FACT | 2022-11-24 | 146.95 | +396.9% | +16.6% |
| SHAKTIPUMP | 2023-08-31 | 150.83 | +374.6% | +40.9% |
| HBLENGINE | 2023-06-06 | 124.65 | +310.6% | +40.8% |
| TECHNOE | 2023-07-13 | 425.65 | +292.8% | +37.7% |
| RECLTD | 2023-05-02 | 133.90 | +283.8% | +34.5% |
| NBCC | 2023-08-02 | 31.00 | +273.4% | +33.0% |
| JBMA | 2023-02-21 | 292.50 | +266.3% | +36.2% |
| CHENNPETRO | 2023-04-21 | 278.25 | +264.6% | +41.9% |
| IRCON | 2023-04-25 | 69.65 | +253.0% | +39.8% |
| ZENTEC | 2023-02-17 | 242.00 | +244.2% | +32.7% |

## Wkly_upswing

1838 signals (14 Aug 2017 to 12 Oct 2026): 1220 bought, 614 never crossed the trigger, 2 without Yahoo prices, 2 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 1216 | 46% | +0.8% | -0.8% | +7.1% / -6.1% | +0.7% | 42% | +0.1% |
| Short | 1 month | 1211 | 51% | +2.4% | +0.4% | +12.0% / -8.8% | +1.2% | 45% | +1.2% |
| Medium | 3 months | 1186 | 53% | +7.8% | +1.5% | +25.6% / -14.0% | +3.3% | 46% | +4.4% |
| Medium | 6 months | 1150 | 53% | +15.5% | +2.3% | +41.9% / -18.3% | +5.8% | 47% | +9.7% |
| Long | 1 year | 1108 | 55% | +30.3% | +6.0% | +72.9% / -24.4% | +11.5% | 46% | +18.9% |
| Long | 2 years | 1026 | 59% | +52.2% | +14.1% | +122.0% / -30.6% | +25.6% | 43% | +26.5% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Largecap | 295 / 58% / +2.5% / +1.2% | 273 / 60% / +14.5% / +8.9% | 260 / 67% / +30.0% / +17.6% |
| Midcap | 274 / 55% / +4.0% / +2.8% | 266 / 55% / +17.4% / +13.0% | 250 / 55% / +46.3% / +36.2% |
| Smallcap | 642 / 46% / +1.6% / +0.5% | 611 / 49% / +15.1% / +8.6% | 598 / 50% / +23.8% / +12.2% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2017 | 71 / 56% / +6.1% / +4.6% | 71 / 51% / +10.0% / +7.5% | 71 / 34% / +6.5% / +4.3% |
| 2018 | 71 / 32% / -4.8% / -3.0% | 71 / 28% / -14.9% / -11.7% | 71 / 30% / -15.6% / -13.2% |
| 2019 | 49 / 45% / -1.9% / -3.1% | 49 / 20% / -14.8% / -3.5% | 49 / 35% / -4.9% / +0.9% |
| 2020 | 66 / 59% / +5.0% / +3.0% | 66 / 70% / +33.2% / +14.0% | 66 / 91% / +114.0% / +68.8% |
| 2021 | 181 / 52% / +3.2% / +0.7% | 181 / 61% / +42.8% / +32.8% | 180 / 58% / +50.0% / +42.6% |
| 2022 | 162 / 43% / +0.7% / +1.6% | 162 / 47% / +2.1% / +3.2% | 162 / 65% / +25.0% / +16.8% |
| 2023 | 193 / 61% / +6.0% / +2.6% | 193 / 74% / +34.5% / +16.5% | 193 / 82% / +72.7% / +40.2% |
| 2024 | 269 / 54% / +2.1% / +0.8% | 269 / 49% / +6.4% / +3.0% | 269 / 38% / -1.3% / -5.2% |
| 2025 | 64 / 52% / +1.8% / +1.0% | 64 / 34% / -2.4% / -3.1% | 47 / 43% / +5.1% / +4.2% |
| 2026 | 85 / 44% / +0.4% / +1.4% | 24 / 54% / +16.1% / +17.9% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Auto | 66 / 65% / +6.7% / +5.1% | 63 / 65% / +32.7% / +25.7% | 60 / 63% / +46.8% / +33.7% |
| Bank | 34 / 44% / +1.5% / +0.2% | 32 / 62% / +4.9% / +0.1% | 27 / 41% / +0.1% / -5.1% |
| Building Materials | 64 / 39% / +0.1% / -1.2% | 63 / 46% / -0.2% / -6.6% | 62 / 45% / +1.3% / -10.8% |
| Chemicals | 81 / 46% / +0.6% / -0.8% | 76 / 50% / +9.1% / +3.8% | 75 / 60% / +32.1% / +21.0% |
| Consumer Discretionary | 58 / 60% / +3.7% / +2.3% | 53 / 55% / +13.0% / +10.7% | 52 / 63% / +40.6% / +30.2% |
| Energy | 28 / 64% / +2.3% / +1.4% | 26 / 38% / +2.7% / -0.9% | 25 / 40% / +8.1% / -1.8% |
| FMCG | 76 / 50% / +0.3% / -1.0% | 74 / 47% / +6.1% / -0.6% | 73 / 56% / +26.2% / +14.7% |
| Financials | 102 / 56% / +0.6% / -0.8% | 98 / 53% / +13.3% / +7.4% | 96 / 59% / +27.0% / +16.7% |
| Healthcare | 87 / 59% / +3.2% / +1.7% | 85 / 59% / +16.4% / +8.3% | 83 / 63% / +37.5% / +22.1% |
| I.T | 83 / 46% / +3.0% / +2.8% | 78 / 42% / +7.7% / +3.8% | 77 / 47% / +23.6% / +15.3% |
| Industrials | 104 / 49% / +1.7% / +0.4% | 101 / 53% / +24.7% / +18.5% | 97 / 58% / +66.0% / +51.5% |
| Metals & Mining | 76 / 45% / +0.6% / -0.2% | 66 / 58% / +19.9% / +14.4% | 61 / 64% / +30.6% / +20.2% |
| Miscellaneous | 38 / 53% / +3.7% / +1.9% | 38 / 53% / +20.3% / +12.8% | 36 / 53% / +51.3% / +38.3% |
| Power & Utilities | 27 / 52% / +4.6% / +1.8% | 26 / 62% / +34.9% / +27.1% | 24 / 67% / +35.0% / +19.1% |
| Realty | 100 / 48% / +2.1% / +0.9% | 96 / 55% / +26.5% / +20.5% | 92 / 51% / +16.3% / +6.5% |
| Services | 41 / 46% / +0.8% / -0.8% | 38 / 61% / +7.1% / -0.4% | 37 / 54% / +14.9% / +0.3% |
| Textiles | 38 / 53% / +8.2% / +8.7% | 34 / 44% / +9.4% / +4.8% | 34 / 44% / +17.6% / +7.2% |

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| LAURUSLABS | Healthcare | Largecap | 5 | +5.2% | +111.2% | +238.9% | 80% |
| NORBTEAEXP | FMCG | Smallcap | 3 | +14.5% | +44.0% | +180.4% | 100% |
| JSL | Metals & Mining | Largecap | 3 | -0.6% | +41.7% | +131.2% | 67% |
| AURIONPRO | I.T | Smallcap | 4 | +24.0% | +79.9% | +125.2% | 50% |
| HUBTOWN | Realty | Smallcap | 3 | +8.6% | +47.6% | +119.6% | 67% |
| TI | FMCG | Midcap | 4 | +9.5% | +32.9% | +119.6% | 75% |
| MINDTECK | I.T | Smallcap | 3 | -0.9% | +11.8% | +106.8% | 33% |
| TRIVENI | FMCG | Midcap | 4 | +7.5% | +32.7% | +101.1% | 50% |
| TDPOWERSYS | Industrials | Largecap | 5 | -0.2% | +64.5% | +98.4% | 80% |
| MCX | Financials | Largecap | 5 | +10.0% | +37.8% | +92.4% | 100% |

**Worst repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| SEJALLTD | Building Materials | Smallcap | 3 | -19.9% | -14.7% | -63.1% | 0% |
| BIGBLOC | Building Materials | Smallcap | 3 | -11.1% | -31.5% | -62.3% | 0% |
| DHAMPURSUG | FMCG | Smallcap | 3 | +4.9% | -41.3% | -40.9% | 0% |
| JUSTDIAL | I.T | Midcap | 3 | -2.9% | -15.3% | -31.9% | 0% |
| SIS | Miscellaneous | Midcap | 3 | -5.0% | -21.5% | -23.4% | 0% |
| TEXINFRA | Realty | Smallcap | 3 | -7.5% | -12.9% | -23.4% | 0% |
| MANAKALUCO | Metals & Mining | Smallcap | 3 | -6.5% | -11.9% | -20.4% | 0% |
| VIDHIING | Chemicals | Smallcap | 3 | -10.6% | -15.8% | -20.1% | 33% |
| CSBBANK | Bank | Midcap | 3 | -3.0% | -5.8% | -17.9% | 0% |
| HDFCBANK | Bank | Largecap | 3 | +0.0% | +4.7% | -17.3% | 0% |

**Biggest single winners after 1 year**

| Stock | Bought | Price | Return | Nifty 500 |
|---|---|---|---|---|
| BCG | 2021-03-08 | 5.14 | +1152.0% | +13.4% |
| LLOYDSENGG | 2021-03-08 | 1.30 | +1096.3% | +13.4% |
| IBULLSLTD | 2017-09-18 | 41.33 | +1001.5% | +4.0% |
| TIPSMUSIC | 2020-06-30 | 13.09 | +949.7% | +58.5% |
| TARIL | 2023-05-29 | 40.47 | +829.0% | +38.6% |
| WEBELSOLAR | 2023-08-08 | 11.10 | +768.8% | +37.8% |
| ASAL | 2021-06-14 | 49.95 | +677.2% | -4.2% |
| SKYGOLD | 2023-10-16 | 56.40 | +518.3% | +29.4% |
| LAURUSLABS | 2020-06-22 | 108.80 | +465.1% | +59.7% |
| AURIONPRO | 2023-05-08 | 233.95 | +446.8% | +37.0% |

## Trigger-price stop with re-entry

Buy when price crosses above the trigger (the signal candle's high). No target and no time limit. Sell when price falls below the trigger; buy again each time it climbs back above it, for 63 sessions (3 months) after the signal. A position bought inside those 3 months is held until the stop, however long that takes; open positions are valued at the latest close. Every buy/sell pays 0.25% costs. Two versions of the stop:

- **close**: sell at the next open after a daily close below the trigger
- **intraday**: sell the moment price trades below the trigger (at the trigger, or the open on a gap-down)

Return = all the buys and sells of one signal compounded. Nifty 500 = from the first buy to the last sell (or today).

### Stop on a close below the trigger

| Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | Worst 10% avg | Avg days invested | Still holding | Nifty 500 avg | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 2765 | 5.4 | 18% | +27.2% | -7.3% | -26.4% | 196 | 546 | +7.4% | +19.8% |
| Bullish_Scanner | 1592 | 5.5 | 20% | +14.4% | -7.0% | -24.1% | 179 | 357 | +6.1% | +8.2% |
| Wkly_upswing | 1647 | 5.2 | 18% | +44.1% | -8.2% | -27.0% | 227 | 280 | +10.7% | +33.4% |
| **All** | 6004 | 5.4 | 19% | +28.4% | -7.4% | -26.0% | 200 | 1183 | +8.0% | +20.5% |

| Scanner | Cap | Signals | Profitable | Avg return | Median | Avg days invested |
|---|---|---|---|---|---|---|
| 63_30_daily | Largecap | 670 | 29% | +81.3% | -5.0% | 279 |
| 63_30_daily | Midcap | 778 | 23% | +31.6% | -6.1% | 215 |
| 63_30_daily | Smallcap | 1317 | 10% | -3.0% | -9.1% | 142 |
| Bullish_Scanner | Largecap | 561 | 29% | +34.1% | -4.5% | 230 |
| Bullish_Scanner | Midcap | 494 | 22% | +13.5% | -7.3% | 184 |
| Bullish_Scanner | Smallcap | 537 | 9% | -5.5% | -9.6% | 123 |
| Wkly_upswing | Largecap | 375 | 25% | +65.8% | -5.6% | 292 |
| Wkly_upswing | Midcap | 369 | 20% | +89.0% | -7.2% | 272 |
| Wkly_upswing | Smallcap | 903 | 13% | +16.8% | -9.8% | 181 |

| Buys per signal | Signals | Profitable | Avg return |
|---|---|---|---|
| 1 | 961 | 29% | +55.0% |
| 2 | 781 | 23% | +33.8% |
| 3 | 705 | 22% | +68.3% |
| 4 | 583 | 17% | +17.2% |
| 5 | 537 | 16% | +16.0% |
| 6+ | 2437 | 13% | +10.1% |

### Stop on any trade below the trigger

| Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | Worst 10% avg | Avg days invested | Still holding | Nifty 500 avg | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 2765 | 6.5 | 16% | +23.7% | -7.2% | -27.7% | 174 | 478 | +6.8% | +16.9% |
| Bullish_Scanner | 1592 | 7.0 | 15% | +10.4% | -7.4% | -25.2% | 151 | 288 | +5.6% | +4.8% |
| Wkly_upswing | 1647 | 6.4 | 15% | +35.8% | -7.7% | -30.2% | 204 | 251 | +10.1% | +25.7% |
| **All** | 6004 | 6.6 | 15% | +23.5% | -7.4% | -27.8% | 176 | 1017 | +7.4% | +16.1% |

| Scanner | Cap | Signals | Profitable | Avg return | Median | Avg days invested |
|---|---|---|---|---|---|---|
| 63_30_daily | Largecap | 670 | 25% | +74.3% | -5.0% | 246 |
| 63_30_daily | Midcap | 778 | 21% | +27.4% | -6.0% | 195 |
| 63_30_daily | Smallcap | 1317 | 8% | -4.4% | -8.8% | 124 |
| Bullish_Scanner | Largecap | 561 | 22% | +28.9% | -5.0% | 191 |
| Bullish_Scanner | Midcap | 494 | 17% | +8.2% | -8.0% | 160 |
| Bullish_Scanner | Smallcap | 537 | 7% | -6.8% | -9.1% | 103 |
| Wkly_upswing | Largecap | 375 | 21% | +60.0% | -5.3% | 259 |
| Wkly_upswing | Midcap | 369 | 18% | +74.6% | -8.0% | 241 |
| Wkly_upswing | Smallcap | 903 | 11% | +9.9% | -9.1% | 165 |

| Buys per signal | Signals | Profitable | Avg return |
|---|---|---|---|
| 1 | 719 | 18% | +39.6% |
| 2 | 658 | 24% | +46.7% |
| 3 | 561 | 23% | +63.4% |
| 4 | 544 | 17% | +13.8% |
| 5 | 460 | 17% | +37.4% |
| 6+ | 3062 | 11% | +7.0% |


## The pullback after the breakout

For every signal that crossed its trigger, the 20 sessions after the first crossing. **Back at the trigger** = the low came within 2% of the trigger (or below).

| Scanner | Breakouts | Back at the trigger | Median days to get there | Closed below the trigger | Closed 5%+ below | Median dip from the high | 3 months later: retested / not |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 2750 | 96% | 1 | 84% | 55% | -14.3% | +5.3% / +35.6% |
| Bullish_Scanner | 1562 | 97% | 1 | 85% | 50% | -12.3% | +4.9% / +30.9% |
| Wkly_upswing | 1634 | 93% | 1 | 82% | 57% | -15.9% | +5.7% / +48.4% |
| **All** | 5946 | 95% | 1 | 84% | 54% | -14.1% | +5.3% / +40.0% |

## Why a stop at the buy price still loses

Every round trip of the *breakout* rule (buy above the trigger, sell after a close below it). Entry and exit are shown against the trigger price.

| Scanner | Stopped round trips | Avg bought above trigger | Avg sold below trigger | Costs | Avg loss per stop | Bought on a gap-up | Sold 3%+ below trigger | Avg days held |
|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 14304 | +0.2% | -1.5% | -0.25% | -2.0% | 11% | 16% | 13 |
| Bullish_Scanner | 8481 | +0.2% | -1.4% | -0.25% | -1.8% | 10% | 14% | 14 |
| Wkly_upswing | 8262 | +0.3% | -1.6% | -0.25% | -2.2% | 16% | 20% | 14 |
| **All** | 31047 | +0.2% | -1.5% | -0.25% | -2.0% | 12% | 16% | 14 |

Signals are bought 5.4 times on average under this rule, so the small loss per stop (-2.0%) repeats: 5 stops in a row is about -9.5%.


## Buying the pullback: rules compared

Same signals, every market cap, no target, no time limit, new buys for 3 months after the signal, 0.25% costs per round trip, open positions valued at the latest close.

- **breakout**: Buy above the trigger, sell on a close below it, buy again above it
- **breakout5**: Same, stop on a close 5% below the trigger
- **retest**: Buy the dip back to the trigger (within 2%) that closes above it; stop 5% below
- **dip5**: Buy a 5% dip from the post-breakout high; stop 5% below the trigger
- **ema20**: Buy the dip to the 20-day average that closes above it; stop 5% below the trigger

| Rule | Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | Worst 10% avg | Avg days invested |
|---|---|---|---|---|---|---|---|---|
| breakout | 63_30_daily | 2765 | 5.4 | 18% | +27.2% | -7.3% | -26.4% | 196 |
| breakout | Bullish_Scanner | 1590 | 5.5 | 20% | +14.4% | -7.0% | -24.2% | 180 |
| breakout | Wkly_upswing | 1647 | 5.2 | 18% | +44.1% | -8.2% | -27.0% | 227 |
| breakout | **All** | 6002 | 5.4 | 19% | +28.4% | -7.4% | -26.0% | 200 |
| breakout5 | 63_30_daily | 2765 | 1.7 | 21% | +31.3% | -7.8% | -26.6% | 231 |
| breakout5 | Bullish_Scanner | 1590 | 1.7 | 25% | +17.4% | -7.0% | -25.1% | 221 |
| breakout5 | Wkly_upswing | 1647 | 1.7 | 20% | +51.5% | -9.0% | -28.3% | 269 |
| breakout5 | **All** | 6002 | 1.7 | 22% | +33.1% | -7.9% | -26.7% | 239 |
| retest | 63_30_daily | 2355 | 1.4 | 22% | +32.2% | -8.9% | -27.3% | 242 |
| retest | Bullish_Scanner | 1389 | 1.3 | 26% | +18.8% | -8.0% | -25.6% | 231 |
| retest | Wkly_upswing | 1365 | 1.4 | 21% | +46.0% | -9.5% | -29.3% | 276 |
| retest | **All** | 5109 | 1.4 | 23% | +32.2% | -8.8% | -27.5% | 248 |
| dip5 | 63_30_daily | 2330 | 1.8 | 24% | +32.9% | -7.9% | -30.9% | 243 |
| dip5 | Bullish_Scanner | 1335 | 1.8 | 26% | +18.3% | -6.8% | -27.1% | 225 |
| dip5 | Wkly_upswing | 1403 | 1.8 | 22% | +54.9% | -8.8% | -32.9% | 293 |
| dip5 | **All** | 5068 | 1.8 | 24% | +35.2% | -7.8% | -30.6% | 252 |
| ema20 | 63_30_daily | 2529 | 1.7 | 22% | +31.2% | -8.4% | -28.5% | 236 |
| ema20 | Bullish_Scanner | 1477 | 1.7 | 25% | +18.5% | -7.3% | -25.9% | 221 |
| ema20 | Wkly_upswing | 1423 | 1.6 | 21% | +49.2% | -8.9% | -30.4% | 282 |
| ema20 | **All** | 5429 | 1.7 | 23% | +32.5% | -8.2% | -28.4% | 244 |

| Rule | Cap | Signals bought | Profitable | Avg return | Median |
|---|---|---|---|---|---|
| breakout | Largecap | 1605 | 28% | +61.2% | -5.0% |
| breakout | Midcap | 1640 | 22% | +39.1% | -6.7% |
| breakout | Smallcap | 2757 | 11% | +3.0% | -9.5% |
| breakout5 | Largecap | 1605 | 35% | +71.5% | -5.8% |
| breakout5 | Midcap | 1640 | 25% | +43.8% | -7.1% |
| breakout5 | Smallcap | 2757 | 12% | +4.5% | -10.9% |
| dip5 | Largecap | 1374 | 36% | +75.2% | -4.1% |
| dip5 | Midcap | 1399 | 27% | +47.9% | -7.4% |
| dip5 | Smallcap | 2295 | 14% | +3.4% | -10.6% |
| ema20 | Largecap | 1505 | 35% | +71.9% | -5.6% |
| ema20 | Midcap | 1531 | 26% | +40.1% | -7.6% |
| ema20 | Smallcap | 2393 | 13% | +2.8% | -10.8% |
| retest | Largecap | 1440 | 36% | +72.0% | -6.8% |
| retest | Midcap | 1429 | 26% | +41.2% | -8.4% |
| retest | Smallcap | 2240 | 13% | +0.9% | -11.3% |

## Buy-the-dip rule (the live alert rule)

After the breakout, buy at the next open once a close is 3% below the highest close since the breakout (5% for Wkly_upswing), within 20 sessions and no more than 5% below the trigger. Exit at +8%, a 12% stop, or after 40 sessions. 0.25% costs.

| Group | Trades | Win rate | Avg | Avg win / loss | Target / stop / time | Avg days | ₹ on ₹1L a trade |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 1784 | 65% | +1.20% | +7.7% / -11.1% | 63% / 28% / 8% | 15 | 2,141,620 |
| Bullish_Scanner | 1105 | 66% | +1.39% | +7.7% / -10.6% | 63% / 27% / 11% | 18 | 1,532,260 |
| Wkly_upswing | 781 | 62% | +0.31% | +8.0% / -12.1% | 60% / 35% / 4% | 12 | 242,680 |
| Largecap | 971 | 69% | +2.06% | +7.4% / -9.6% | 62% / 20% / 18% | 21 | 2,004,730 |
| Midcap | 1035 | 68% | +1.88% | +7.8% / -10.8% | 67% / 25% / 8% | 15 | 1,946,980 |
| Smallcap | 1664 | 60% | -0.02% | +8.0% / -12.1% | 60% / 37% / 3% | 12 | -35,150 |
| **All** | 3670 | 65% | +1.07% | +7.7% / -11.2% | 62% / 29% / 8% | 15 | 3,916,560 |

## Candidate scanner versions

A new Chartink export in `data/backtest/candidates/` compared with the scanner the bot uses now, over the same dates. The bot does not use the candidate until it is moved to `data/backtest/`.

### 63_30_daily: current vs change1_2026-10-21 (29 Dec 2020 to 19 Oct 2026)

| Version | Signals | Signals a year | Dip rule trades | Dip win rate | Dip avg | Dip total (₹1L a trade) | Hold 1 month | Hold 6 months | Hold 1 year (median) |
|---|---|---|---|---|---|---|---|---|---|
| current | 2998 | 516 | 1784 | 65% | +1.2% | 2,141,620 | +1.9% | +10.1% | +25.1% (+7.5%) |
| change1_2026-10-21 | 7356 | 1266 | 4407 | 67% | +1.6% | 6,956,530 | +2.4% | +10.8% | +25.1% (+11.1%) |

| Version | Year | Dip trades | Dip win rate | Dip avg |
|---|---|---|---|---|
| change1_2026-10-21 | 2020 | 2 | 50% | -2.2% |
| change1_2026-10-21 | 2021 | 469 | 68% | +1.6% |
| change1_2026-10-21 | 2022 | 772 | 55% | -0.7% |
| change1_2026-10-21 | 2023 | 965 | 80% | +4.0% |
| change1_2026-10-21 | 2024 | 788 | 66% | +1.2% |
| change1_2026-10-21 | 2025 | 849 | 65% | +1.3% |
| change1_2026-10-21 | 2026 | 562 | 67% | +1.4% |
| current | 2020 | 7 | 86% | +4.3% |
| current | 2021 | 195 | 65% | +1.1% |
| current | 2022 | 306 | 59% | -0.2% |
| current | 2023 | 350 | 77% | +3.7% |
| current | 2024 | 360 | 64% | +0.8% |
| current | 2025 | 310 | 61% | +0.3% |
| current | 2026 | 256 | 65% | +1.1% |

| Version | Cap | Dip trades | Dip win rate | Dip avg |
|---|---|---|---|---|
| change1_2026-10-21 | Largecap | 1410 | 71% | +2.3% |
| change1_2026-10-21 | Midcap | 1344 | 68% | +1.6% |
| change1_2026-10-21 | Smallcap | 1653 | 64% | +0.9% |
| current | Largecap | 428 | 70% | +2.4% |
| current | Midcap | 503 | 69% | +2.0% |
| current | Smallcap | 853 | 61% | +0.1% |
### 63_30_daily: current vs change2_2026-10-21 (31 Dec 2020 to 21 Oct 2026)

| Version | Signals | Signals a year | Dip rule trades | Dip win rate | Dip avg | Dip total (₹1L a trade) | Hold 1 month | Hold 6 months | Hold 1 year (median) |
|---|---|---|---|---|---|---|---|---|---|
| current | 2990 | 515 | 1780 | 65% | +1.2% | 2,107,780 | +1.9% | +10.0% | +24.8% (+7.4%) |
| change2_2026-10-21 | 5951 | 1025 | 3545 | 67% | +1.6% | 5,646,850 | +2.1% | +10.6% | +25.0% (+11.3%) |

| Version | Year | Dip trades | Dip win rate | Dip avg |
|---|---|---|---|---|
| change2_2026-10-21 | 2020 | 1 | 0% | -12.2% |
| change2_2026-10-21 | 2021 | 361 | 66% | +1.3% |
| change2_2026-10-21 | 2022 | 625 | 55% | -0.7% |
| change2_2026-10-21 | 2023 | 819 | 79% | +3.9% |
| change2_2026-10-21 | 2024 | 618 | 68% | +1.6% |
| change2_2026-10-21 | 2025 | 689 | 64% | +1.3% |
| change2_2026-10-21 | 2026 | 432 | 67% | +1.3% |
| current | 2020 | 3 | 67% | -1.1% |
| current | 2021 | 195 | 65% | +1.1% |
| current | 2022 | 306 | 59% | -0.2% |
| current | 2023 | 350 | 77% | +3.7% |
| current | 2024 | 360 | 64% | +0.8% |
| current | 2025 | 310 | 61% | +0.3% |
| current | 2026 | 256 | 65% | +1.1% |

| Version | Cap | Dip trades | Dip win rate | Dip avg |
|---|---|---|---|---|
| change2_2026-10-21 | Largecap | 1251 | 71% | +2.3% |
| change2_2026-10-21 | Midcap | 1086 | 67% | +1.4% |
| change2_2026-10-21 | Smallcap | 1208 | 64% | +1.0% |
| current | Largecap | 428 | 70% | +2.4% |
| current | Midcap | 501 | 69% | +2.0% |
| current | Smallcap | 851 | 61% | +0.1% |

## Reading this

- Average vs median: a high average with a low median means a few big winners carry the result; most buys did worse than the average.
- Compare with the Nifty 500 column: a scanner adds value only when its picks beat the index.
- Stocks Yahoo no longer lists (delisted, renamed) are missing, which flatters long-term results a little (survivorship bias).
- No costs, taxes or stop-loss are included; real results will be lower, and holding with no stop means sitting through every drawdown shown in 'Avg best / worst'.
