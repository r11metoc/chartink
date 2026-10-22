# If I had bought every scanner stock

Generated 2026-10-22 17:45 UTC by `scripts/stock_outcomes.py` from `data/backtest/*.csv` plus the bot's live triggers.

**Rule:** buy when price crosses the signal candle's high within 3 sessions (5 for `Wkly_upswing`), filled at the trigger or at the open on a gap-up; then hold. No stop, no target, no costs. **Short** = 2 weeks / 1 month, **Medium** = 3 / 6 months, **Long** = 1 / 2 years. **Beat Nifty 500** = share of buys that did better than the index over the same days. Recent buys only count for horizons that have fully passed.

Per-trade data: `data/model/stock_outcomes.csv`; per-stock: `data/model/stock_summary.csv`.

## All scanners at a glance

| Scanner | Signals | Bought | 1 month avg | 6 months avg | 1 year avg | 2 years avg | 1 year vs Nifty 500 |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 5953 | 4242 | +2.1% | +10.5% | +25.0% | +58.7% | +11.1% |
| Bullish_Scanner | 1701 | 1334 | +1.4% | +12.2% | +25.8% | +32.9% | +8.4% |
| Wkly_upswing | 1838 | 1218 | +2.4% | +15.5% | +30.3% | +52.1% | +18.9% |

## 63_30_daily

5953 signals (31 Dec 2020 to 21 Oct 2026): 4242 bought, 1703 never crossed the trigger, 8 without Yahoo prices, 0 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 4233 | 48% | +0.8% | -0.3% | +5.0% / -4.4% | +0.6% | 43% | +0.2% |
| Short | 1 month | 4222 | 52% | +2.1% | +0.5% | +8.5% / -6.2% | +1.2% | 46% | +1.0% |
| Medium | 3 months | 4132 | 57% | +6.3% | +2.9% | +18.6% / -10.1% | +3.5% | 48% | +2.8% |
| Medium | 6 months | 3864 | 58% | +10.5% | +5.1% | +29.4% / -13.8% | +6.2% | 48% | +4.4% |
| Long | 1 year | 3589 | 60% | +25.0% | +11.3% | +51.7% / -18.7% | +13.9% | 48% | +11.1% |
| Long | 2 years | 2837 | 66% | +58.7% | +25.9% | +107.8% / -22.7% | +32.6% | 48% | +26.1% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Largecap | 1548 / 56% / +2.0% / +0.6% | 1456 / 65% / +12.6% / +6.7% | 1318 / 70% / +32.1% / +17.9% |
| Midcap | 1260 / 52% / +2.9% / +1.9% | 1133 / 62% / +15.6% / +9.5% | 1052 / 63% / +33.2% / +19.1% |
| Smallcap | 1414 / 47% / +1.6% / +0.6% | 1275 / 47% / +3.7% / -2.8% | 1219 / 46% / +10.1% / -3.3% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2021 | 418 / 55% / +3.7% / +1.7% | 418 / 52% / +9.2% / +1.0% | 418 / 45% / +8.3% / +4.0% |
| 2022 | 745 / 39% / -1.1% / -0.0% | 745 / 47% / +3.4% / +4.1% | 745 / 69% / +36.2% / +24.8% |
| 2023 | 1033 / 63% / +4.4% / +1.1% | 1033 / 82% / +27.8% / +11.5% | 1033 / 81% / +54.7% / +19.7% |
| 2024 | 732 / 53% / +2.7% / +1.5% | 732 / 51% / +4.5% / +1.4% | 732 / 43% / +0.4% / -3.6% |
| 2025 | 804 / 50% / +1.3% / +0.1% | 804 / 48% / +0.1% / -2.2% | 661 / 45% / +3.6% / +2.8% |
| 2026 | 490 / 48% / +1.4% / +2.0% | 132 / 59% / +16.9% / +16.9% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Aerospace & Defence | 57 / 72% / +12.3% / +11.4% | 56 / 79% / +39.0% / +34.4% | 56 / 86% / +103.9% / +92.7% |
| Auto | 249 / 59% / +5.2% / +2.8% | 226 / 73% / +18.4% / +9.7% | 223 / 75% / +34.4% / +18.5% |
| Bank | 214 / 50% / -0.1% / -0.9% | 202 / 69% / +13.3% / +8.6% | 173 / 71% / +27.1% / +12.8% |
| Building Materials | 209 / 52% / +2.0% / +0.6% | 205 / 46% / -0.1% / -6.1% | 193 / 47% / +1.5% / -14.4% |
| Castings, Forgings & Fasteners | 33 / 58% / +1.9% / +1.4% | 32 / 66% / +13.2% / +9.5% | 26 / 58% / +31.2% / +19.9% |
| Chemicals | 313 / 39% / -0.2% / -1.3% | 295 / 40% / +0.8% / -6.0% | 279 / 49% / +10.7% / -2.6% |
| Consumer Discretionary | 244 / 55% / +2.8% / +1.3% | 215 / 46% / +6.8% / +1.6% | 207 / 52% / +16.9% / +3.5% |
| Energy | 147 / 49% / +0.9% / +0.1% | 140 / 60% / +7.0% / +1.2% | 124 / 51% / +12.8% / +1.3% |
| FMCG | 309 / 52% / +1.9% / +0.6% | 287 / 60% / +10.3% / +3.0% | 270 / 60% / +16.8% / +3.6% |
| Financials | 429 / 54% / +1.9% / +0.8% | 395 / 59% / +8.9% / +3.5% | 365 / 63% / +21.0% / +7.7% |
| Healthcare | 368 / 56% / +2.3% / +0.8% | 321 / 67% / +12.3% / +6.3% | 290 / 66% / +27.7% / +13.5% |
| I.T | 252 / 48% / +1.5% / +0.5% | 227 / 55% / +6.1% / +0.9% | 212 / 50% / +15.6% / +3.4% |
| Industrials | 224 / 57% / +3.3% / +2.3% | 198 / 66% / +21.0% / +14.8% | 178 / 65% / +48.5% / +34.6% |
| Media | 71 / 51% / +2.5% / +2.0% | 66 / 35% / +0.1% / -5.6% | 64 / 38% / +4.5% / -10.6% |
| Metals & Mining | 200 / 56% / +3.3% / +2.4% | 173 / 64% / +22.6% / +16.2% | 157 / 72% / +39.9% / +25.2% |
| Miscellaneous | 124 / 52% / +0.7% / -0.9% | 114 / 54% / +3.3% / -4.2% | 110 / 51% / +21.5% / +2.7% |
| Plastic products | 44 / 43% / +0.6% / +0.0% | 38 / 34% / +2.8% / -3.0% | 33 / 45% / +12.3% / -2.7% |
| Power & Utilities | 87 / 41% / +0.3% / -0.9% | 87 / 52% / +12.3% / +6.9% | 69 / 80% / +46.9% / +32.7% |
| Readymade Garments/Apparels | 29 / 48% / +2.8% / +0.3% | 27 / 67% / +21.0% / +10.7% | 26 / 65% / +26.5% / +5.9% |
| Realty | 259 / 54% / +2.6% / +1.8% | 233 / 64% / +19.2% / +12.7% | 225 / 62% / +52.4% / +37.9% |
| Services | 87 / 52% / +4.0% / +3.5% | 76 / 59% / +9.0% / +4.0% | 72 / 72% / +25.4% / +17.6% |
| Telecom-Service | 43 / 63% / +3.8% / +2.9% | 38 / 74% / +6.4% / +0.4% | 36 / 67% / +14.4% / +1.6% |
| Textiles | 93 / 42% / -0.0% / -0.9% | 83 / 43% / +0.5% / -4.6% | 76 / 49% / +6.5% / -6.7% |
| Transportation | 114 / 43% / +0.2% / -1.0% | 108 / 56% / +4.9% / -2.3% | 106 / 43% / +13.0% / +0.0% |

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| JINDALSAW | Industrials | Midcap | 3 | +9.2% | +141.3% | +334.8% | 100% |
| MAZDOCK | Aerospace & Defence | Largecap | 3 | +27.0% | +92.7% | +326.6% | 100% |
| NEULANDLAB | Healthcare | Largecap | 3 | +10.6% | +102.0% | +284.4% | 100% |
| ZENTEC | Aerospace & Defence | Midcap | 5 | +11.8% | +120.3% | +270.3% | 100% |
| MTARTECH | Aerospace & Defence | Largecap | 3 | +2.3% | +62.4% | +235.8% | 100% |
| ACE | Industrials | Midcap | 3 | +3.5% | +41.3% | +215.1% | 33% |
| TIMETECHNO | Plastic products | Midcap | 6 | +3.1% | +92.0% | +212.2% | 33% |
| GANESHHOU | Realty | Midcap | 3 | +36.5% | +99.3% | +210.4% | 67% |
| PURVA | Realty | Smallcap | 4 | -5.3% | +36.3% | +205.9% | 75% |
| KALYANKJIL | Consumer Discretionary | Largecap | 4 | +22.5% | +88.7% | +201.4% | 100% |

**Worst repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| REDTAPE | Consumer Discretionary | Midcap | 5 | +1.0% | -82.5% | -83.3% | 0% |
| FUSION | Financials | Smallcap | 3 | -10.6% | -17.3% | -73.1% | 0% |
| LAXMIDENTL | Healthcare | Smallcap | 3 | -25.1% | -50.1% | -54.8% | 0% |
| SUBEXLTD | I.T | Smallcap | 4 | -5.2% | -32.7% | -51.3% | 0% |
| PRINCEPIPE | Plastic products | Smallcap | 3 | +2.4% | -35.2% | -50.7% | 0% |
| DELTACORP | Miscellaneous | Smallcap | 4 | +5.2% | -40.4% | -49.9% | 0% |
| JYOTICNC | Industrials | Largecap | 4 | -4.8% | -23.1% | -47.1% | 0% |
| CGCL | Financials | Largecap | 3 | +1.4% | -4.1% | -46.9% | 0% |
| BSOFT | I.T | Midcap | 3 | -7.5% | -28.2% | -46.8% | 0% |
| SDBL | FMCG | Smallcap | 4 | +2.4% | +5.0% | -45.0% | 0% |

**Biggest single winners after 1 year**

| Stock | Bought | Price | Return | Nifty 500 |
|---|---|---|---|---|
| MAZDOCK | 2022-08-16 | 157.40 | +493.2% | +11.7% |
| MAZDOCK | 2022-08-18 | 162.32 | +472.5% | +10.1% |
| PURVA | 2023-06-21 | 97.95 | +461.2% | +41.1% |
| FORCEMOT | 2023-05-30 | 1559.95 | +428.6% | +44.0% |
| RVNL | 2022-09-09 | 34.00 | +402.8% | +14.0% |
| SHAKTIPUMP | 2023-05-17 | 83.00 | +400.6% | +38.0% |
| JINDALSAW | 2022-11-29 | 47.10 | +384.4% | +18.3% |
| COCHINSHIP | 2023-05-05 | 278.50 | +377.7% | +34.6% |
| MTARTECH | 2025-05-19 | 1668.00 | +376.7% | +0.3% |
| SCHNEIDER | 2023-05-12 | 193.90 | +372.8% | +38.8% |

## Bullish_Scanner

1701 signals (11 Jun 2021 to 19 Oct 2026): 1334 bought, 356 never crossed the trigger, 9 without Yahoo prices, 2 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 1324 | 48% | +0.5% | -0.4% | +4.9% / -4.6% | +0.5% | 45% | +0.0% |
| Short | 1 month | 1308 | 50% | +1.4% | +0.0% | +8.1% / -6.4% | +1.2% | 45% | +0.2% |
| Medium | 3 months | 1249 | 56% | +5.4% | +3.2% | +18.0% / -10.9% | +4.0% | 48% | +1.4% |
| Medium | 6 months | 1182 | 60% | +12.2% | +6.2% | +30.8% / -14.5% | +8.4% | 48% | +3.8% |
| Long | 1 year | 1048 | 64% | +25.8% | +13.0% | +54.0% / -18.3% | +17.4% | 48% | +8.4% |
| Long | 2 years | 877 | 61% | +32.9% | +16.1% | +87.5% / -23.0% | +24.9% | 44% | +8.0% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Largecap | 465 / 54% / +1.8% / +1.0% | 424 / 70% / +16.3% / +9.1% | 353 / 76% / +35.7% / +19.3% |
| Midcap | 415 / 50% / +2.0% / +0.5% | 376 / 62% / +14.8% / +6.4% | 337 / 66% / +32.8% / +14.8% |
| Smallcap | 428 / 46% / +0.3% / -1.2% | 382 / 48% / +4.9% / -4.7% | 358 / 51% / +9.5% / -8.3% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2021 | 1 / – / – / – | 1 / – / – / – | 1 / – / – / – |
| 2022 | 32 / 44% / +0.4% / +1.8% | 32 / 56% / +5.6% / +5.2% | 32 / 84% / +61.3% / +44.7% |
| 2023 | 472 / 58% / +3.0% / +0.1% | 472 / 74% / +23.5% / +5.9% | 470 / 83% / +49.3% / +15.1% |
| 2024 | 428 / 46% / +0.9% / -0.6% | 428 / 53% / +6.4% / +1.8% | 428 / 47% / +2.5% / -1.4% |
| 2025 | 178 / 49% / -0.4% / -0.6% | 178 / 44% / -1.6% / +0.2% | 117 / 48% / +7.7% / +7.9% |
| 2026 | 197 / 43% / +0.4% / +2.1% | 71 / 58% / +9.2% / +9.9% | 0 / – / – / – |

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
| Financials | 128 / 52% / +1.3% / -0.3% | 117 / 61% / +12.8% / +4.5% | 107 / 67% / +27.2% / +10.5% |
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

1838 signals (14 Aug 2017 to 12 Oct 2026): 1218 bought, 611 never crossed the trigger, 7 without Yahoo prices, 2 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 1214 | 46% | +0.9% | -0.7% | +7.1% / -6.1% | +0.7% | 42% | +0.2% |
| Short | 1 month | 1209 | 51% | +2.4% | +0.4% | +12.0% / -8.7% | +1.2% | 45% | +1.3% |
| Medium | 3 months | 1184 | 53% | +7.8% | +1.5% | +25.6% / -13.9% | +3.3% | 46% | +4.5% |
| Medium | 6 months | 1152 | 53% | +15.5% | +2.3% | +41.9% / -18.3% | +5.8% | 47% | +9.7% |
| Long | 1 year | 1107 | 55% | +30.3% | +5.9% | +73.0% / -24.4% | +11.4% | 46% | +18.9% |
| Long | 2 years | 1024 | 59% | +52.1% | +13.9% | +122.1% / -30.6% | +25.6% | 43% | +26.5% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Unknown | 0 / – / – / – | 0 / – / – / – | 0 / – / – / – |
| Largecap | 295 / 58% / +2.5% / +1.2% | 275 / 60% / +14.6% / +9.0% | 260 / 67% / +30.0% / +17.6% |
| Midcap | 274 / 55% / +4.0% / +2.8% | 267 / 55% / +17.4% / +13.0% | 250 / 55% / +46.3% / +36.2% |
| Smallcap | 640 / 46% / +1.8% / +0.6% | 610 / 49% / +15.2% / +8.6% | 597 / 50% / +23.7% / +12.1% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2017 | 71 / 56% / +6.1% / +4.6% | 71 / 51% / +10.0% / +7.5% | 71 / 34% / +6.5% / +4.3% |
| 2018 | 71 / 32% / -4.8% / -3.0% | 71 / 28% / -14.9% / -11.7% | 71 / 30% / -15.6% / -13.2% |
| 2019 | 49 / 45% / -1.9% / -3.1% | 49 / 20% / -14.8% / -3.5% | 49 / 35% / -4.9% / +0.9% |
| 2020 | 66 / 59% / +5.0% / +3.0% | 66 / 70% / +33.2% / +14.0% | 66 / 91% / +114.0% / +68.8% |
| 2021 | 179 / 53% / +3.6% / +1.1% | 179 / 61% / +43.5% / +33.4% | 178 / 58% / +50.5% / +43.1% |
| 2022 | 162 / 43% / +0.7% / +1.6% | 162 / 47% / +2.1% / +3.2% | 162 / 65% / +25.0% / +16.8% |
| 2023 | 193 / 61% / +6.0% / +2.6% | 193 / 74% / +34.5% / +16.5% | 193 / 82% / +72.7% / +40.2% |
| 2024 | 269 / 54% / +2.1% / +0.8% | 269 / 49% / +6.4% / +3.0% | 269 / 38% / -1.3% / -5.2% |
| 2025 | 64 / 52% / +1.8% / +1.0% | 64 / 34% / -2.4% / -3.1% | 48 / 42% / +4.1% / +3.4% |
| 2026 | 85 / 44% / +0.4% / +1.4% | 28 / 50% / +14.8% / +17.0% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Auto | 66 / 65% / +6.7% / +5.1% | 63 / 65% / +32.7% / +25.7% | 61 / 62% / +45.3% / +32.5% |
| Bank | 34 / 44% / +1.5% / +0.2% | 32 / 62% / +4.9% / +0.1% | 27 / 41% / +0.1% / -5.1% |
| Building Materials | 64 / 39% / +0.1% / -1.2% | 63 / 46% / -0.2% / -6.6% | 62 / 45% / +1.3% / -10.8% |
| Chemicals | 81 / 46% / +0.6% / -0.8% | 76 / 50% / +9.1% / +3.8% | 75 / 60% / +32.1% / +21.0% |
| Consumer Discretionary | 58 / 60% / +3.7% / +2.3% | 54 / 56% / +13.7% / +11.6% | 52 / 63% / +40.6% / +30.2% |
| Energy | 28 / 64% / +2.3% / +1.4% | 26 / 38% / +2.7% / -0.9% | 25 / 40% / +8.1% / -1.8% |
| FMCG | 76 / 50% / +0.3% / -1.0% | 74 / 47% / +6.1% / -0.6% | 73 / 56% / +26.2% / +14.7% |
| Financials | 102 / 56% / +0.6% / -0.8% | 98 / 53% / +13.3% / +7.4% | 96 / 59% / +27.0% / +16.7% |
| Healthcare | 87 / 59% / +3.2% / +1.7% | 85 / 59% / +16.4% / +8.3% | 83 / 63% / +37.5% / +22.1% |
| I.T | 83 / 46% / +3.0% / +2.8% | 78 / 42% / +7.7% / +3.8% | 77 / 47% / +23.6% / +15.3% |
| Industrials | 104 / 49% / +1.7% / +0.4% | 101 / 53% / +24.7% / +18.5% | 97 / 58% / +66.0% / +51.5% |
| Metals & Mining | 74 / 46% / +1.5% / +0.8% | 66 / 56% / +20.4% / +15.1% | 59 / 64% / +31.5% / +20.9% |
| Miscellaneous | 38 / 53% / +3.7% / +1.9% | 38 / 53% / +20.3% / +12.8% | 36 / 53% / +51.3% / +38.3% |
| Power & Utilities | 27 / 52% / +4.6% / +1.8% | 26 / 62% / +34.9% / +27.1% | 24 / 67% / +35.0% / +19.1% |
| Realty | 100 / 48% / +2.1% / +0.9% | 96 / 55% / +26.6% / +20.5% | 92 / 51% / +16.3% / +6.5% |
| Services | 41 / 46% / +0.8% / -0.8% | 38 / 61% / +7.1% / -0.4% | 37 / 54% / +14.9% / +0.3% |
| Textiles | 38 / 53% / +8.2% / +8.7% | 34 / 44% / +9.4% / +4.8% | 34 / 44% / +17.6% / +7.2% |

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| LAURUSLABS | Healthcare | Largecap | 5 | +5.2% | +111.4% | +238.9% | 80% |
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
| 63_30_daily | 5534 | 5.5 | 20% | +19.9% | -6.2% | -23.4% | 214 | 1151 | +8.5% | +11.4% |
| Bullish_Scanner | 1593 | 5.5 | 20% | +14.0% | -7.0% | -24.1% | 179 | 348 | +6.1% | +7.9% |
| Wkly_upswing | 1642 | 5.2 | 18% | +43.0% | -8.2% | -27.0% | 227 | 276 | +10.7% | +32.3% |
| **All** | 8769 | 5.5 | 19% | +23.1% | -6.7% | -24.4% | 210 | 1775 | +8.5% | +14.7% |

| Scanner | Cap | Signals | Profitable | Avg return | Median | Avg days invested |
|---|---|---|---|---|---|---|
| 63_30_daily | Largecap | 1962 | 27% | +42.2% | -4.7% | 270 |
| 63_30_daily | Midcap | 1671 | 23% | +19.7% | -5.9% | 226 |
| 63_30_daily | Smallcap | 1901 | 10% | -3.0% | -8.5% | 144 |
| Bullish_Scanner | Largecap | 562 | 29% | +33.5% | -4.6% | 229 |
| Bullish_Scanner | Midcap | 494 | 22% | +13.2% | -7.4% | 184 |
| Bullish_Scanner | Smallcap | 537 | 9% | -5.6% | -9.6% | 123 |
| Wkly_upswing | Largecap | 375 | 25% | +65.2% | -5.6% | 293 |
| Wkly_upswing | Midcap | 369 | 20% | +86.9% | -7.2% | 273 |
| Wkly_upswing | Smallcap | 897 | 13% | +15.7% | -9.8% | 181 |

| Buys per signal | Signals | Profitable | Avg return |
|---|---|---|---|
| 1 | 1377 | 30% | +48.7% |
| 2 | 1137 | 25% | +33.5% |
| 3 | 985 | 23% | +46.0% |
| 4 | 833 | 19% | +19.6% |
| 5 | 764 | 18% | +15.6% |
| 6+ | 3673 | 13% | +6.6% |

### Stop on any trade below the trigger

| Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | Worst 10% avg | Avg days invested | Still holding | Nifty 500 avg | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 5534 | 6.7 | 17% | +17.2% | -6.2% | -24.9% | 192 | 1027 | +7.9% | +9.3% |
| Bullish_Scanner | 1593 | 7.0 | 15% | +10.1% | -7.4% | -25.2% | 152 | 281 | +5.6% | +4.5% |
| Wkly_upswing | 1642 | 6.4 | 15% | +34.8% | -7.7% | -30.2% | 204 | 249 | +10.1% | +24.7% |
| **All** | 8769 | 6.7 | 16% | +19.2% | -6.6% | -26.2% | 187 | 1557 | +7.9% | +11.3% |

| Scanner | Cap | Signals | Profitable | Avg return | Median | Avg days invested |
|---|---|---|---|---|---|---|
| 63_30_daily | Largecap | 1962 | 23% | +38.2% | -5.1% | 244 |
| 63_30_daily | Midcap | 1671 | 20% | +16.5% | -5.9% | 206 |
| 63_30_daily | Smallcap | 1901 | 8% | -3.8% | -8.1% | 127 |
| Bullish_Scanner | Largecap | 562 | 22% | +28.3% | -5.0% | 191 |
| Bullish_Scanner | Midcap | 494 | 17% | +7.9% | -8.2% | 160 |
| Bullish_Scanner | Smallcap | 537 | 7% | -6.9% | -9.2% | 103 |
| Wkly_upswing | Largecap | 375 | 21% | +59.5% | -5.3% | 260 |
| Wkly_upswing | Midcap | 369 | 18% | +72.8% | -8.0% | 241 |
| Wkly_upswing | Smallcap | 897 | 11% | +8.9% | -9.1% | 166 |

| Buys per signal | Signals | Profitable | Avg return |
|---|---|---|---|
| 1 | 997 | 18% | +34.4% |
| 2 | 946 | 26% | +49.3% |
| 3 | 844 | 23% | +49.1% |
| 4 | 778 | 18% | +18.9% |
| 5 | 654 | 17% | +18.5% |
| 6+ | 4550 | 12% | +4.3% |


## The pullback after the breakout

For every signal that crossed its trigger, the 20 sessions after the first crossing. **Back at the trigger** = the low came within 2% of the trigger (or below).

| Scanner | Breakouts | Back at the trigger | Median days to get there | Closed below the trigger | Closed 5%+ below | Median dip from the high | 3 months later: retested / not |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 5502 | 97% | 1 | 84% | 49% | -11.9% | +5.9% / +28.2% |
| Bullish_Scanner | 1564 | 97% | 1 | 85% | 50% | -12.3% | +4.9% / +30.9% |
| Wkly_upswing | 1629 | 93% | 1 | 82% | 57% | -15.9% | +5.7% / +49.1% |
| **All** | 8695 | 96% | 1 | 84% | 50% | -12.6% | +5.7% / +35.4% |

## Why a stop at the buy price still loses

Every round trip of the *breakout* rule (buy above the trigger, sell after a close below it). Entry and exit are shown against the trigger price.

| Scanner | Stopped round trips | Avg bought above trigger | Avg sold below trigger | Costs | Avg loss per stop | Bought on a gap-up | Sold 3%+ below trigger | Avg days held |
|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 29365 | +0.2% | -1.3% | -0.25% | -1.7% | 9% | 12% | 14 |
| Bullish_Scanner | 8494 | +0.2% | -1.4% | -0.25% | -1.8% | 10% | 14% | 14 |
| Wkly_upswing | 8255 | +0.3% | -1.6% | -0.25% | -2.2% | 16% | 20% | 14 |
| **All** | 46114 | +0.2% | -1.4% | -0.25% | -1.8% | 10% | 14% | 14 |

Signals are bought 5.5 times on average under this rule, so the small loss per stop (-1.8%) repeats: 5 stops in a row is about -8.7%.


## Buying the pullback: rules compared

Same signals, every market cap, no target, no time limit, new buys for 3 months after the signal, 0.25% costs per round trip, open positions valued at the latest close.

- **breakout**: Buy above the trigger, sell on a close below it, buy again above it
- **breakout5**: Same, stop on a close 5% below the trigger
- **retest**: Buy the dip back to the trigger (within 2%) that closes above it; stop 5% below
- **dip5**: Buy a 5% dip from the post-breakout high; stop 5% below the trigger
- **ema20**: Buy the dip to the 20-day average that closes above it; stop 5% below the trigger

| Rule | Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | Worst 10% avg | Avg days invested |
|---|---|---|---|---|---|---|---|---|
| breakout | 63_30_daily | 5533 | 5.5 | 20% | +19.9% | -6.2% | -23.4% | 214 |
| breakout | Bullish_Scanner | 1593 | 5.5 | 20% | +14.0% | -7.0% | -24.1% | 179 |
| breakout | Wkly_upswing | 1642 | 5.2 | 18% | +43.0% | -8.2% | -27.0% | 227 |
| breakout | **All** | 8768 | 5.5 | 19% | +23.1% | -6.7% | -24.4% | 210 |
| breakout5 | 63_30_daily | 5533 | 1.6 | 24% | +25.3% | -6.7% | -24.1% | 260 |
| breakout5 | Bullish_Scanner | 1593 | 1.7 | 25% | +17.0% | -7.0% | -25.1% | 221 |
| breakout5 | Wkly_upswing | 1642 | 1.7 | 20% | +50.4% | -9.0% | -28.3% | 269 |
| breakout5 | **All** | 8768 | 1.6 | 23% | +28.5% | -7.0% | -25.2% | 255 |
| retest | 63_30_daily | 4800 | 1.3 | 26% | +27.0% | -7.9% | -25.0% | 277 |
| retest | Bullish_Scanner | 1391 | 1.3 | 26% | +18.4% | -8.1% | -25.5% | 231 |
| retest | Wkly_upswing | 1363 | 1.4 | 21% | +45.3% | -9.5% | -29.3% | 276 |
| retest | **All** | 7554 | 1.3 | 25% | +28.7% | -8.1% | -26.1% | 269 |
| dip5 | 63_30_daily | 4604 | 1.8 | 26% | +25.4% | -6.5% | -27.2% | 265 |
| dip5 | Bullish_Scanner | 1338 | 1.8 | 26% | +17.9% | -6.8% | -27.2% | 225 |
| dip5 | Wkly_upswing | 1403 | 1.8 | 22% | +54.0% | -8.8% | -32.9% | 293 |
| dip5 | **All** | 7345 | 1.8 | 25% | +29.5% | -6.9% | -28.5% | 263 |
| ema20 | 63_30_daily | 5137 | 1.6 | 24% | +25.1% | -7.1% | -24.9% | 261 |
| ema20 | Bullish_Scanner | 1477 | 1.7 | 25% | +18.1% | -7.4% | -25.9% | 221 |
| ema20 | Wkly_upswing | 1423 | 1.6 | 22% | +48.4% | -9.0% | -30.4% | 282 |
| ema20 | **All** | 8037 | 1.6 | 24% | +27.9% | -7.4% | -26.4% | 258 |

| Rule | Cap | Signals bought | Profitable | Avg return | Median |
|---|---|---|---|---|---|
| breakout | Largecap | 2898 | 27% | +43.5% | -4.8% |
| breakout | Midcap | 2534 | 22% | +28.2% | -6.3% |
| breakout | Smallcap | 3335 | 11% | +1.6% | -9.1% |
| breakout5 | Largecap | 2898 | 34% | +53.4% | -5.8% |
| breakout5 | Midcap | 2534 | 26% | +33.5% | -6.7% |
| breakout5 | Smallcap | 3335 | 13% | +3.1% | -10.1% |
| dip5 | Largecap | 2475 | 35% | +53.8% | -4.4% |
| dip5 | Midcap | 2108 | 28% | +36.6% | -6.8% |
| dip5 | Smallcap | 2761 | 14% | +2.4% | -10.1% |
| ema20 | Largecap | 2732 | 33% | +53.7% | -5.6% |
| ema20 | Midcap | 2358 | 27% | +30.7% | -7.0% |
| ema20 | Smallcap | 2946 | 13% | +1.8% | -9.8% |
| retest | Largecap | 2632 | 35% | +55.4% | -6.7% |
| retest | Midcap | 2176 | 28% | +32.1% | -7.9% |
| retest | Smallcap | 2745 | 13% | +0.5% | -10.2% |

## Buy-the-dip rule (the live alert rule)

After the breakout, buy at the next open once a close is 3% below the highest close since the breakout (5% for Wkly_upswing), within 20 sessions and no more than 5% below the trigger. Exit at +8%, a 12% stop, or after 40 sessions. 0.25% costs.

| Group | Trades | Win rate | Avg | Avg win / loss | Target / stop / time | Avg days | ₹ on ₹1L a trade |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 3550 | 67% | +1.58% | +7.5% / -10.6% | 63% / 24% / 12% | 18 | 5,605,290 |
| Bullish_Scanner | 1106 | 66% | +1.37% | +7.7% / -10.6% | 63% / 27% / 11% | 18 | 1,520,150 |
| Wkly_upswing | 781 | 62% | +0.31% | +8.0% / -12.1% | 60% / 35% / 4% | 12 | 242,840 |
| Largecap | 1794 | 70% | +2.18% | +7.3% / -9.8% | 63% / 20% / 18% | 22 | 3,905,580 |
| Midcap | 1619 | 67% | +1.53% | +7.7% / -10.9% | 65% / 26% / 9% | 16 | 2,477,330 |
| Smallcap | 2023 | 62% | +0.49% | +7.8% / -11.5% | 61% / 33% / 6% | 14 | 997,620 |
| **All** | 5437 | 66% | +1.36% | +7.6% / -10.8% | 63% / 27% / 11% | 17 | 7,368,280 |

## Candidate scanner versions

A new Chartink export in `data/backtest/candidates/` compared with the scanner the bot uses now, over the same dates. The bot does not use the candidate until it is moved to `data/backtest/`.

### 63_30_daily: current vs mod1_2026-10-22 (31 Dec 2020 to 21 Oct 2026)

| Version | Signals | Signals a year | Dip rule trades | Dip win rate | Dip avg | Dip total (₹1L a trade) | Hold 1 month | Hold 6 months | Hold 1 year (median) |
|---|---|---|---|---|---|---|---|---|---|
| current | 5953 | 1025 | 3550 | 67% | +1.6% | 5,605,290 | +2.1% | +10.5% | +25.0% (+11.3%) |
| mod1_2026-10-22 | 6298 | 1084 | 3932 | 67% | +1.7% | 6,701,920 | +2.1% | +10.5% | +24.7% (+11.6%) |

| Version | Year | Dip trades | Dip win rate | Dip avg |
|---|---|---|---|---|
| current | 2020 | 1 | 0% | -12.2% |
| current | 2021 | 361 | 66% | +1.3% |
| current | 2022 | 625 | 55% | -0.7% |
| current | 2023 | 819 | 79% | +3.9% |
| current | 2024 | 618 | 68% | +1.6% |
| current | 2025 | 689 | 64% | +1.3% |
| current | 2026 | 437 | 66% | +1.2% |
| mod1_2026-10-22 | 2020 | 2 | 100% | +7.8% |
| mod1_2026-10-22 | 2021 | 354 | 64% | +1.1% |
| mod1_2026-10-22 | 2022 | 693 | 57% | -0.3% |
| mod1_2026-10-22 | 2023 | 926 | 80% | +4.1% |
| mod1_2026-10-22 | 2024 | 670 | 65% | +1.0% |
| mod1_2026-10-22 | 2025 | 813 | 64% | +1.4% |
| mod1_2026-10-22 | 2026 | 474 | 69% | +1.7% |

| Version | Cap | Dip trades | Dip win rate | Dip avg |
|---|---|---|---|---|
| current | Largecap | 1251 | 71% | +2.3% |
| current | Midcap | 1087 | 67% | +1.4% |
| current | Smallcap | 1212 | 64% | +0.9% |
| mod1_2026-10-22 | Largecap | 1418 | 69% | +2.0% |
| mod1_2026-10-22 | Midcap | 1166 | 68% | +1.9% |
| mod1_2026-10-22 | Smallcap | 1348 | 65% | +1.2% |
### Bullish_Scanner: current vs mod1_2026-10-22 (31 Dec 2020 to 22 Oct 2026)

| Version | Signals | Signals a year | Dip rule trades | Dip win rate | Dip avg | Dip total (₹1L a trade) | Hold 1 month | Hold 6 months | Hold 1 year (median) |
|---|---|---|---|---|---|---|---|---|---|
| current | 1701 | 293 | 1106 | 66% | +1.4% | 1,520,150 | +1.4% | +12.2% | +25.8% (+13.0%) |
| mod1_2026-10-22 | 5070 | 872 | 3613 | 68% | +1.9% | 6,734,000 | +3.7% | +15.4% | +27.4% (+13.5%) |

| Version | Year | Dip trades | Dip win rate | Dip avg |
|---|---|---|---|---|
| current | 2021 | 1 | 0% | -12.2% |
| current | 2022 | 28 | 43% | -2.9% |
| current | 2023 | 399 | 74% | +3.2% |
| current | 2024 | 359 | 60% | +0.0% |
| current | 2025 | 150 | 59% | +0.7% |
| current | 2026 | 169 | 67% | +1.3% |
| mod1_2026-10-22 | 2020 | 1 | 100% | +7.8% |
| mod1_2026-10-22 | 2021 | 748 | 65% | +1.2% |
| mod1_2026-10-22 | 2022 | 360 | 57% | -0.5% |
| mod1_2026-10-22 | 2023 | 1046 | 81% | +4.7% |
| mod1_2026-10-22 | 2024 | 874 | 64% | +0.8% |
| mod1_2026-10-22 | 2025 | 312 | 61% | +0.6% |
| mod1_2026-10-22 | 2026 | 272 | 65% | +0.8% |

| Version | Cap | Dip trades | Dip win rate | Dip avg |
|---|---|---|---|---|
| current | Largecap | 378 | 67% | +1.8% |
| current | Midcap | 360 | 68% | +1.9% |
| current | Smallcap | 368 | 62% | +0.4% |
| mod1_2026-10-22 | Largecap | 1668 | 67% | +1.8% |
| mod1_2026-10-22 | Midcap | 1013 | 70% | +2.1% |
| mod1_2026-10-22 | Smallcap | 932 | 68% | +1.7% |

## Reading this

- Average vs median: a high average with a low median means a few big winners carry the result; most buys did worse than the average.
- Compare with the Nifty 500 column: a scanner adds value only when its picks beat the index.
- Stocks Yahoo no longer lists (delisted, renamed) are missing, which flatters long-term results a little (survivorship bias).
- No costs, taxes or stop-loss are included; real results will be lower, and holding with no stop means sitting through every drawdown shown in 'Avg best / worst'.
