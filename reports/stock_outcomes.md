# If I had bought every scanner stock

Generated 2026-10-20 17:38 UTC by `scripts/stock_outcomes.py` from `data/backtest/*.csv` plus the bot's live triggers.

**Rule:** buy when price crosses the signal candle's high within 3 sessions (5 for `Wkly_upswing`), filled at the trigger or at the open on a gap-up; then hold. No stop, no target, no costs. **Short** = 2 weeks / 1 month, **Medium** = 3 / 6 months, **Long** = 1 / 2 years. **Beat Nifty 500** = share of buys that did better than the index over the same days. Recent buys only count for horizons that have fully passed.

Per-trade data: `data/model/stock_outcomes.csv`; per-stock: `data/model/stock_summary.csv`.

## All scanners at a glance

| Scanner | Signals | Bought | 1 month avg | 6 months avg | 1 year avg | 2 years avg | 1 year vs Nifty 500 |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 2998 | 2122 | +1.9% | +10.1% | +25.1% | +63.2% | +12.5% |
| Bullish_Scanner | 1701 | 1330 | +1.4% | +12.2% | +25.9% | +32.9% | +8.4% |
| Wkly_upswing | 1838 | 1220 | +2.4% | +15.5% | +30.4% | +52.2% | +18.9% |

## 63_30_daily

2998 signals (29 Dec 2020 to 16 Oct 2026): 2122 bought, 869 never crossed the trigger, 6 without Yahoo prices, 1 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 2118 | 47% | +0.3% | -0.6% | +5.8% / -5.6% | +0.6% | 43% | -0.3% |
| Short | 1 month | 2110 | 50% | +1.9% | -0.1% | +9.8% / -7.8% | +1.0% | 45% | +0.8% |
| Medium | 3 months | 2070 | 54% | +6.1% | +2.2% | +21.6% / -12.1% | +3.0% | 48% | +3.1% |
| Medium | 6 months | 1868 | 54% | +10.1% | +3.1% | +39.2% / -16.3% | +5.6% | 45% | +4.6% |
| Long | 1 year | 1771 | 56% | +25.1% | +7.5% | +62.7% / -21.9% | +12.6% | 46% | +12.5% |
| Long | 2 years | 1405 | 64% | +63.2% | +25.8% | +134.9% / -26.4% | +30.4% | 48% | +32.8% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Largecap | 511 / 55% / +2.2% / +0.9% | 466 / 69% / +15.6% / +9.6% | 428 / 72% / +43.6% / +29.5% |
| Midcap | 582 / 56% / +3.6% / +2.4% | 504 / 59% / +16.2% / +10.2% | 477 / 62% / +34.9% / +21.1% |
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
| 2026 | 288 / 48% / +0.7% / +1.3% | 46 / 57% / +24.8% / +24.3% | 0 / – / – / – |

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
| Industrials | 164 / 55% / +3.8% / +2.9% | 134 / 60% / +21.9% / +15.9% | 125 / 57% / +60.5% / +48.0% |
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

1701 signals (11 Jun 2021 to 19 Oct 2026): 1330 bought, 356 never crossed the trigger, 9 without Yahoo prices, 6 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 1323 | 48% | +0.5% | -0.3% | +4.9% / -4.6% | +0.5% | 45% | +0.0% |
| Short | 1 month | 1306 | 50% | +1.4% | +0.0% | +8.1% / -6.4% | +1.2% | 46% | +0.2% |
| Medium | 3 months | 1247 | 56% | +5.4% | +3.2% | +18.0% / -10.9% | +4.0% | 48% | +1.4% |
| Medium | 6 months | 1180 | 60% | +12.2% | +6.3% | +30.8% / -14.5% | +8.4% | 48% | +3.8% |
| Long | 1 year | 1046 | 64% | +25.9% | +13.1% | +54.1% / -18.2% | +17.4% | 48% | +8.4% |
| Long | 2 years | 877 | 61% | +32.9% | +16.1% | +87.5% / -23.0% | +24.9% | 44% | +8.0% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Largecap | 465 / 54% / +1.8% / +1.0% | 422 / 70% / +16.5% / +9.2% | 351 / 76% / +35.9% / +19.4% |
| Midcap | 414 / 50% / +2.0% / +0.6% | 376 / 62% / +14.8% / +6.4% | 337 / 66% / +32.8% / +14.8% |
| Smallcap | 427 / 46% / +0.3% / -1.2% | 382 / 48% / +4.9% / -4.7% | 358 / 51% / +9.5% / -8.3% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2021 | 1 / – / – / – | 1 / – / – / – | 1 / – / – / – |
| 2022 | 32 / 44% / +0.4% / +1.8% | 32 / 56% / +5.6% / +5.2% | 32 / 84% / +61.3% / +44.7% |
| 2023 | 472 / 58% / +3.0% / +0.1% | 472 / 74% / +23.5% / +5.9% | 470 / 83% / +49.3% / +15.1% |
| 2024 | 428 / 46% / +0.9% / -0.6% | 428 / 53% / +6.4% / +1.8% | 428 / 47% / +2.5% / -1.4% |
| 2025 | 178 / 49% / -0.4% / -0.6% | 178 / 44% / -1.6% / +0.2% | 115 / 49% / +7.9% / +7.9% |
| 2026 | 195 / 43% / +0.5% / +2.2% | 69 / 58% / +9.7% / +10.3% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Auto | 80 / 49% / +1.3% / -0.3% | 74 / 64% / +16.9% / +11.1% | 67 / 76% / +35.7% / +20.9% |
| Bank | 69 / 55% / -0.0% / -0.1% | 64 / 70% / +10.1% / +4.9% | 41 / 66% / +8.2% / -6.4% |
| Building Materials | 60 / 50% / +0.8% / -0.2% | 58 / 43% / +3.0% / -6.3% | 55 / 44% / +7.4% / -12.5% |
| Chemicals | 104 / 43% / -0.1% / -1.6% | 93 / 53% / +4.7% / -3.9% | 84 / 51% / +12.6% / -3.2% |
| Consumer Discretionary | 68 / 46% / +1.4% / -0.1% | 61 / 49% / +7.4% / -2.5% | 58 / 57% / +23.2% / +4.3% |
| Energy | 51 / 47% / -0.0% / -0.6% | 49 / 61% / +10.4% / +0.4% | 45 / 60% / +31.6% / +11.1% |
| FMCG | 87 / 45% / +0.5% / +0.3% | 74 / 50% / +4.0% / -4.1% | 64 / 61% / +16.2% / -2.4% |
| Financials | 128 / 52% / +1.3% / -0.3% | 117 / 61% / +12.8% / +4.5% | 105 / 69% / +27.8% / +10.6% |
| Healthcare | 147 / 60% / +3.2% / +1.9% | 126 / 75% / +18.2% / +10.1% | 111 / 80% / +36.7% / +20.2% |
| I.T | 75 / 45% / +0.1% / -0.9% | 70 / 51% / +6.9% / -1.1% | 63 / 62% / +22.4% / +5.4% |
| Industrials | 88 / 52% / +3.0% / +1.7% | 81 / 69% / +21.0% / +11.0% | 73 / 66% / +41.5% / +20.7% |
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
| Medium | 6 months | 1144 | 53% | +15.5% | +2.3% | +41.9% / -18.4% | +5.9% | 47% | +9.6% |
| Long | 1 year | 1107 | 55% | +30.4% | +6.1% | +73.0% / -24.4% | +11.5% | 46% | +18.9% |
| Long | 2 years | 1025 | 59% | +52.2% | +14.0% | +122.1% / -30.6% | +25.7% | 43% | +26.5% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Largecap | 295 / 58% / +2.5% / +1.2% | 270 / 60% / +14.3% / +8.6% | 260 / 67% / +30.0% / +17.6% |
| Midcap | 274 / 55% / +4.0% / +2.8% | 263 / 55% / +17.6% / +13.1% | 250 / 55% / +46.3% / +36.2% |
| Smallcap | 642 / 46% / +1.6% / +0.5% | 611 / 49% / +15.1% / +8.6% | 597 / 50% / +23.8% / +12.2% |

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
| 2025 | 64 / 52% / +1.8% / +1.0% | 64 / 34% / -2.4% / -3.1% | 46 / 43% / +5.5% / +4.4% |
| 2026 | 85 / 44% / +0.4% / +1.4% | 18 / 50% / +15.7% / +16.5% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Auto | 66 / 65% / +6.7% / +5.1% | 63 / 65% / +32.7% / +25.7% | 60 / 63% / +46.8% / +33.7% |
| Bank | 34 / 44% / +1.5% / +0.2% | 32 / 62% / +4.9% / +0.1% | 27 / 41% / +0.1% / -5.1% |
| Building Materials | 64 / 39% / +0.1% / -1.2% | 63 / 46% / -0.2% / -6.6% | 62 / 45% / +1.3% / -10.8% |
| Chemicals | 81 / 46% / +0.6% / -0.8% | 76 / 50% / +9.1% / +3.8% | 75 / 60% / +32.1% / +21.0% |
| Consumer Discretionary | 58 / 60% / +3.7% / +2.3% | 53 / 55% / +13.0% / +10.7% | 52 / 63% / +40.6% / +30.2% |
| Energy | 28 / 64% / +2.3% / +1.4% | 26 / 38% / +2.7% / -0.9% | 25 / 40% / +8.1% / -1.8% |
| FMCG | 76 / 50% / +0.3% / -1.0% | 74 / 47% / +6.1% / -0.6% | 72 / 57% / +26.7% / +14.9% |
| Financials | 102 / 56% / +0.6% / -0.8% | 98 / 53% / +13.3% / +7.4% | 96 / 59% / +27.0% / +16.7% |
| Healthcare | 87 / 59% / +3.2% / +1.7% | 84 / 58% / +15.7% / +7.5% | 83 / 63% / +37.5% / +22.1% |
| I.T | 83 / 46% / +3.0% / +2.8% | 78 / 42% / +7.7% / +3.8% | 77 / 47% / +23.6% / +15.3% |
| Industrials | 104 / 49% / +1.7% / +0.4% | 99 / 54% / +25.1% / +18.7% | 97 / 58% / +66.0% / +51.5% |
| Metals & Mining | 76 / 45% / +0.6% / -0.2% | 66 / 58% / +19.9% / +14.4% | 61 / 64% / +30.6% / +20.2% |
| Miscellaneous | 38 / 53% / +3.7% / +1.9% | 38 / 53% / +20.3% / +12.8% | 36 / 53% / +51.3% / +38.3% |
| Power & Utilities | 27 / 52% / +4.6% / +1.8% | 25 / 64% / +37.1% / +28.8% | 24 / 67% / +35.0% / +19.1% |
| Realty | 100 / 48% / +2.1% / +0.9% | 95 / 55% / +26.8% / +20.7% | 92 / 51% / +16.3% / +6.5% |
| Services | 41 / 46% / +0.8% / -0.8% | 38 / 61% / +7.1% / -0.4% | 37 / 54% / +14.9% / +0.3% |
| Textiles | 38 / 53% / +8.2% / +8.7% | 34 / 44% / +9.4% / +4.8% | 34 / 44% / +17.6% / +7.2% |

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| LAURUSLABS | Healthcare | Largecap | 5 | +5.2% | +120.2% | +238.9% | 80% |
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
| 63_30_daily | 2765 | 5.4 | 19% | +28.8% | -7.3% | -26.3% | 195 | 548 | +7.7% | +21.0% |
| Bullish_Scanner | 1588 | 5.6 | 21% | +15.6% | -7.0% | -24.2% | 180 | 356 | +6.5% | +9.1% |
| Wkly_upswing | 1647 | 5.2 | 18% | +46.4% | -8.2% | -27.0% | 226 | 287 | +11.1% | +35.4% |
| **All** | 6000 | 5.4 | 19% | +30.1% | -7.4% | -26.0% | 200 | 1191 | +8.3% | +21.8% |

| Scanner | Cap | Signals | Profitable | Avg return | Median | Avg days invested |
|---|---|---|---|---|---|---|
| 63_30_daily | Largecap | 670 | 30% | +83.9% | -5.0% | 278 |
| 63_30_daily | Midcap | 778 | 24% | +33.9% | -6.0% | 214 |
| 63_30_daily | Smallcap | 1317 | 11% | -2.3% | -9.1% | 142 |
| Bullish_Scanner | Largecap | 559 | 30% | +35.7% | -4.5% | 230 |
| Bullish_Scanner | Midcap | 493 | 23% | +15.0% | -7.2% | 184 |
| Bullish_Scanner | Smallcap | 536 | 10% | -4.9% | -9.6% | 123 |
| Wkly_upswing | Largecap | 375 | 25% | +68.6% | -5.6% | 292 |
| Wkly_upswing | Midcap | 369 | 20% | +93.2% | -7.2% | 272 |
| Wkly_upswing | Smallcap | 903 | 14% | +18.1% | -9.8% | 181 |

| Buys per signal | Signals | Profitable | Avg return |
|---|---|---|---|
| 1 | 958 | 30% | +58.2% |
| 2 | 780 | 24% | +35.8% |
| 3 | 705 | 22% | +70.6% |
| 4 | 584 | 17% | +18.6% |
| 5 | 538 | 16% | +17.1% |
| 6+ | 2435 | 14% | +11.2% |

### Stop on any trade below the trigger

| Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | Worst 10% avg | Avg days invested | Still holding | Nifty 500 avg | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 2765 | 6.5 | 16% | +25.1% | -7.1% | -27.7% | 174 | 485 | +7.1% | +18.0% |
| Bullish_Scanner | 1588 | 7.0 | 16% | +11.5% | -7.3% | -25.2% | 152 | 297 | +6.0% | +5.5% |
| Wkly_upswing | 1647 | 6.4 | 15% | +37.8% | -7.7% | -30.2% | 204 | 257 | +10.4% | +27.4% |
| **All** | 6000 | 6.6 | 16% | +25.0% | -7.3% | -27.8% | 176 | 1039 | +7.7% | +17.3% |

| Scanner | Cap | Signals | Profitable | Avg return | Median | Avg days invested |
|---|---|---|---|---|---|---|
| 63_30_daily | Largecap | 670 | 26% | +76.8% | -5.0% | 246 |
| 63_30_daily | Midcap | 778 | 21% | +29.5% | -6.0% | 195 |
| 63_30_daily | Smallcap | 1317 | 8% | -3.7% | -8.7% | 124 |
| Bullish_Scanner | Largecap | 559 | 23% | +30.4% | -5.0% | 192 |
| Bullish_Scanner | Midcap | 493 | 18% | +9.4% | -8.0% | 160 |
| Bullish_Scanner | Smallcap | 536 | 7% | -6.3% | -9.1% | 103 |
| Wkly_upswing | Largecap | 375 | 21% | +62.5% | -5.3% | 259 |
| Wkly_upswing | Midcap | 369 | 18% | +78.3% | -8.0% | 241 |
| Wkly_upswing | Smallcap | 903 | 11% | +11.0% | -9.1% | 165 |

| Buys per signal | Signals | Profitable | Avg return |
|---|---|---|---|
| 1 | 717 | 19% | +41.9% |
| 2 | 657 | 24% | +49.1% |
| 3 | 562 | 23% | +65.7% |
| 4 | 543 | 18% | +15.0% |
| 5 | 460 | 17% | +39.2% |
| 6+ | 3061 | 12% | +8.0% |


## Reading this

- Average vs median: a high average with a low median means a few big winners carry the result; most buys did worse than the average.
- Compare with the Nifty 500 column: a scanner adds value only when its picks beat the index.
- Stocks Yahoo no longer lists (delisted, renamed) are missing, which flatters long-term results a little (survivorship bias).
- No costs, taxes or stop-loss are included; real results will be lower, and holding with no stop means sitting through every drawdown shown in 'Avg best / worst'.
