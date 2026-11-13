# If I had bought every scanner stock

Generated 2026-11-13 11:27 UTC by `scripts/stock_outcomes.py` from `data/backtest/*.csv` plus the bot's live triggers.

**Rule:** buy when price crosses the signal candle's high within 3 sessions (5 for `Wkly_upswing`), filled at the trigger or at the open on a gap-up; then hold. No stop, no target, no costs. **Short** = 2 weeks / 1 month, **Medium** = 3 / 6 months, **Long** = 1 / 2 years. **Beat Nifty 500** = share of buys that did better than the index over the same days. Recent buys only count for horizons that have fully passed.

Per-trade data: `data/model/stock_outcomes.csv`; per-stock: `data/model/stock_summary.csv`.

## All scanners at a glance

| Scanner | Signals | Bought | 1 month avg | 6 months avg | 1 year avg | 2 years avg | 1 year vs Nifty 500 |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 2061 | 1600 | +2.8% | +13.7% | +24.2% | +52.1% | +9.7% |
| Bullish_Scanner | 5771 | 4746 | +3.5% | +14.4% | +26.8% | +51.1% | +12.9% |
| Wkly_upswing | 621 | 415 | +1.8% | +14.0% | +35.4% | +53.6% | +22.4% |

## 63_30_daily

2061 signals (08 Feb 2019 to 12 Nov 2026): 1600 bought, 444 never crossed the trigger, 13 without Yahoo prices, 4 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 1588 | 51% | +1.5% | +0.2% | +5.2% / -3.7% | +0.8% | 47% | +0.7% |
| Short | 1 month | 1586 | 56% | +2.8% | +1.5% | +8.7% / -5.6% | +1.5% | 48% | +1.3% |
| Medium | 3 months | 1568 | 61% | +7.9% | +4.7% | +19.3% / -9.5% | +4.3% | 51% | +3.5% |
| Medium | 6 months | 1535 | 62% | +13.7% | +7.2% | +31.1% / -13.2% | +7.0% | 49% | +6.7% |
| Long | 1 year | 1447 | 62% | +24.2% | +10.9% | +50.3% / -17.2% | +14.6% | 49% | +9.7% |
| Long | 2 years | 1268 | 68% | +52.1% | +30.1% | +94.4% / -21.5% | +30.8% | 50% | +21.2% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Unknown | 1 / – / – / – | 0 / – / – / – | 0 / – / – / – |
| Largecap | 772 / 56% / +1.6% / +0.2% | 753 / 63% / +11.7% / +6.4% | 711 / 67% / +25.6% / +12.6% |
| Midcap | 422 / 57% / +4.5% / +3.1% | 406 / 70% / +22.6% / +14.4% | 368 / 65% / +35.8% / +19.8% |
| Smallcap | 391 / 54% / +3.3% / +1.5% | 376 / 54% / +8.2% / -1.0% | 368 / 49% / +10.0% / -6.0% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2019 | 71 / 51% / +0.1% / -1.1% | 71 / 42% / +1.7% / +13.8% | 71 / 54% / +26.3% / +29.9% |
| 2020 | 80 / 50% / -3.3% / -6.1% | 80 / 60% / +11.4% / -5.7% | 80 / 75% / +36.7% / -2.7% |
| 2021 | 221 / 52% / +4.1% / +1.9% | 221 / 52% / +10.0% / +1.7% | 221 / 47% / +9.5% / +4.5% |
| 2022 | 168 / 45% / -1.4% / +1.1% | 168 / 43% / +1.5% / +3.5% | 168 / 63% / +24.3% / +17.4% |
| 2023 | 429 / 66% / +5.2% / +1.5% | 429 / 86% / +30.6% / +14.3% | 429 / 83% / +52.8% / +18.9% |
| 2024 | 330 / 54% / +3.3% / +2.2% | 330 / 59% / +8.1% / +3.4% | 330 / 50% / +4.5% / +0.4% |
| 2025 | 170 / 57% / +2.5% / +1.1% | 170 / 51% / +2.9% / +1.8% | 148 / 45% / -0.2% / -0.1% |
| 2026 | 117 / 51% / +2.2% / +3.3% | 66 / 64% / +18.8% / +18.6% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Aerospace & Defence | 21 / 71% / +16.9% / +15.2% | 21 / 86% / +77.1% / +68.8% | 20 / 95% / +132.5% / +108.3% |
| Auto | 117 / 62% / +6.5% / +4.5% | 116 / 78% / +26.1% / +15.0% | 116 / 75% / +37.7% / +18.5% |
| Bank | 106 / 58% / +1.5% / -0.2% | 99 / 69% / +8.6% / +4.1% | 95 / 65% / +14.7% / +0.5% |
| Building Materials | 87 / 53% / +4.1% / +1.7% | 86 / 60% / +11.1% / +0.6% | 81 / 57% / +14.6% / -4.4% |
| Chemicals | 106 / 40% / +0.4% / -0.7% | 105 / 53% / +8.3% / +2.1% | 97 / 59% / +26.3% / +14.8% |
| Consumer Discretionary | 74 / 62% / +2.5% / +2.0% | 74 / 54% / +12.0% / +8.1% | 72 / 67% / +15.6% / +2.3% |
| Energy | 67 / 57% / +1.3% / -0.2% | 66 / 39% / +2.8% / -1.3% | 66 / 45% / +10.7% / +2.7% |
| FMCG | 99 / 59% / +2.6% / +0.6% | 96 / 62% / +17.6% / +6.8% | 92 / 54% / +20.3% / +3.1% |
| Financials | 213 / 52% / +1.4% / +0.1% | 207 / 56% / +7.6% / +1.6% | 188 / 61% / +15.3% / +2.4% |
| Healthcare | 148 / 69% / +4.2% / +1.5% | 144 / 79% / +19.1% / +12.8% | 128 / 71% / +31.0% / +15.8% |
| I.T | 72 / 57% / +3.1% / +1.8% | 66 / 65% / +5.7% / +1.7% | 64 / 45% / +2.3% / -4.0% |
| Industrials | 80 / 65% / +4.1% / +2.2% | 76 / 68% / +21.4% / +15.5% | 66 / 59% / +31.6% / +16.0% |
| Metals & Mining | 78 / 54% / +0.9% / -0.1% | 71 / 72% / +27.6% / +19.1% | 64 / 73% / +36.0% / +19.2% |
| Miscellaneous | 29 / 52% / +0.8% / -0.3% | 27 / 67% / +5.0% / -3.3% | 27 / 52% / +25.2% / +1.7% |
| Power & Utilities | 34 / 26% / -2.2% / -2.6% | 34 / 56% / +4.4% / +1.5% | 30 / 63% / +22.3% / +7.9% |
| Realty | 99 / 55% / +0.9% / -0.4% | 97 / 60% / +11.8% / +2.9% | 94 / 60% / +44.0% / +24.9% |
| Services | 37 / 57% / +8.8% / +7.9% | 37 / 70% / +19.9% / +13.3% | 37 / 84% / +38.0% / +28.3% |
| Telecom-Service | 21 / 76% / +4.8% / +2.6% | 21 / 86% / +7.4% / -3.3% | 21 / 43% / +0.6% / -8.5% |
| Textiles | 29 / 52% / +4.9% / +3.4% | 26 / 38% / -3.8% / -11.8% | 26 / 58% / +5.6% / -10.3% |

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| IRCON | Realty | Midcap | 4 | +18.3% | +93.4% | +214.4% | 75% |
| GOKEX | Readymade Garments/Apparels | Midcap | 3 | +23.2% | +115.4% | +165.3% | 100% |
| TECHNOE | Realty | Midcap | 5 | +3.0% | +20.9% | +148.7% | 100% |
| PITTIENG | Industrials | Smallcap | 4 | +6.3% | +96.9% | +146.1% | 100% |
| LAURUSLABS | Healthcare | Largecap | 6 | +7.0% | +52.7% | +142.5% | 50% |
| EXIDEIND | Auto | Largecap | 4 | +8.5% | +33.1% | +140.0% | 100% |
| TATACHEM | Chemicals | Midcap | 3 | -3.0% | +36.4% | +131.9% | 100% |
| ARVSMART | Realty | Smallcap | 4 | +12.6% | +45.8% | +131.5% | 100% |
| DEEPAKNTR | Chemicals | Largecap | 3 | +3.3% | +45.6% | +116.8% | 100% |
| NAVA | Miscellaneous | Midcap | 3 | +13.3% | +56.2% | +116.6% | 100% |

**Worst repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| FUSION | Financials | Smallcap | 3 | -14.6% | -33.0% | -73.3% | 0% |
| INDIAGLYCO | FMCG | Smallcap | 3 | +12.8% | -2.9% | -68.3% | 0% |
| STAR | Healthcare | Midcap | 8 | +10.3% | +4.5% | -65.0% | 0% |
| OMAXE | Realty | Smallcap | 5 | -54.1% | -59.7% | -57.3% | 0% |
| DELTACORP | Miscellaneous | Smallcap | 4 | +4.1% | -41.1% | -50.2% | 0% |
| IONEXCHANG | Realty | Smallcap | 3 | -12.9% | -25.7% | -48.7% | 0% |
| MUNJALSHOW | Auto | Smallcap | 3 | -11.4% | -27.3% | -42.1% | 0% |
| AUROPHARMA | Healthcare | Largecap | 3 | -1.9% | -19.0% | -37.0% | 0% |
| HDFCAMC | Financials | Largecap | 3 | -6.7% | -28.4% | -36.5% | 0% |
| LICHSGFIN | Financials | Largecap | 8 | -3.9% | -21.2% | -30.1% | 0% |

**Biggest single winners after 1 year**

| Stock | Bought | Price | Return | Nifty 500 |
|---|---|---|---|---|
| MAZDOCK | 2022-08-18 | 162.32 | +472.5% | +10.1% |
| CUPID | 2023-08-21 | 3.32 | +416.4% | +41.8% |
| LAURUSLABS | 2020-01-14 | 81.60 | +353.5% | +18.8% |
| GOKEX | 2021-05-05 | 96.30 | +342.8% | +12.0% |
| BSE | 2021-04-28 | 69.11 | +309.1% | +16.4% |
| IRCON | 2023-04-20 | 62.50 | +300.9% | +41.3% |
| IRCON | 2023-04-21 | 63.80 | +294.0% | +41.9% |
| IRCON | 2023-04-24 | 65.00 | +283.8% | +41.2% |
| ZENTEC | 2023-02-15 | 215.00 | +276.3% | +35.3% |
| ZENTEC | 2023-02-15 | 215.90 | +274.7% | +35.3% |

## Bullish_Scanner

5771 signals (08 Feb 2019 to 13 Nov 2026): 4746 bought, 966 never crossed the trigger, 52 without Yahoo prices, 7 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 4710 | 55% | +2.1% | +0.8% | +5.8% / -3.3% | +0.8% | 50% | +1.3% |
| Short | 1 month | 4702 | 59% | +3.5% | +2.0% | +9.4% / -5.0% | +1.5% | 51% | +2.0% |
| Medium | 3 months | 4641 | 62% | +8.1% | +5.5% | +19.4% / -8.9% | +3.8% | 54% | +4.4% |
| Medium | 6 months | 4527 | 64% | +14.4% | +8.6% | +31.1% / -12.3% | +7.0% | 53% | +7.5% |
| Long | 1 year | 4325 | 64% | +26.8% | +13.4% | +52.9% / -16.4% | +13.9% | 52% | +12.9% |
| Long | 2 years | 3930 | 71% | +51.1% | +30.3% | +92.0% / -20.4% | +29.6% | 52% | +21.5% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Unknown | 3 / – / – / – | 0 / – / – / – | 0 / – / – / – |
| Largecap | 2386 / 59% / +2.5% / +1.2% | 2334 / 66% / +13.6% / +7.8% | 2200 / 70% / +28.7% / +15.4% |
| Midcap | 1224 / 60% / +4.3% / +2.7% | 1163 / 64% / +17.5% / +9.8% | 1113 / 61% / +30.8% / +16.5% |
| Smallcap | 1089 / 58% / +4.7% / +2.9% | 1030 / 57% / +12.8% / +4.1% | 1012 / 53% / +18.2% / +3.3% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2019 | 284 / 65% / +1.9% / +0.3% | 284 / 48% / -1.4% / +9.4% | 284 / 50% / +7.0% / +13.1% |
| 2020 | 246 / 61% / +2.7% / +2.1% | 246 / 59% / +16.7% / +4.6% | 246 / 80% / +45.2% / +11.2% |
| 2021 | 851 / 56% / +4.2% / +2.0% | 851 / 59% / +13.3% / +5.9% | 851 / 54% / +16.0% / +10.5% |
| 2022 | 403 / 48% / +1.4% / +3.3% | 403 / 51% / +4.4% / +6.2% | 403 / 69% / +25.7% / +18.0% |
| 2023 | 1229 / 68% / +5.5% / +2.2% | 1229 / 85% / +30.2% / +12.9% | 1229 / 84% / +58.8% / +25.0% |
| 2024 | 998 / 55% / +2.9% / +1.3% | 998 / 59% / +8.3% / +3.5% | 998 / 50% / +4.6% / +0.5% |
| 2025 | 373 / 57% / +2.6% / +1.9% | 373 / 48% / +2.8% / +2.1% | 314 / 47% / +6.2% / +6.3% |
| 2026 | 318 / 52% / +1.6% / +2.8% | 143 / 52% / +15.6% / +16.2% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Aerospace & Defence | 78 / 60% / +7.3% / +6.3% | 77 / 88% / +44.3% / +36.9% | 76 / 89% / +74.5% / +59.2% |
| Auto | 328 / 64% / +3.8% / +1.4% | 312 / 68% / +17.4% / +6.9% | 301 / 77% / +28.9% / +10.1% |
| Bank | 312 / 53% / +0.6% / -0.0% | 288 / 61% / +6.2% / +3.0% | 260 / 60% / +9.4% / +2.0% |
| Building Materials | 238 / 51% / +2.7% / +1.1% | 230 / 48% / +4.3% / -2.8% | 225 / 43% / +7.1% / -5.4% |
| Castings, Forgings & Fasteners | 33 / 64% / +6.6% / +4.6% | 30 / 43% / -0.5% / -9.1% | 28 / 43% / +2.2% / -15.1% |
| Chemicals | 290 / 57% / +3.5% / +1.9% | 285 / 66% / +15.6% / +8.9% | 272 / 69% / +26.3% / +15.0% |
| Consumer Discretionary | 207 / 57% / +3.5% / +2.9% | 201 / 56% / +10.8% / +9.5% | 197 / 58% / +19.7% / +8.8% |
| Energy | 203 / 62% / +3.9% / +2.2% | 201 / 54% / +10.4% / +4.8% | 188 / 51% / +20.8% / +8.9% |
| FMCG | 392 / 60% / +2.9% / +1.0% | 372 / 65% / +13.0% / +4.2% | 365 / 63% / +19.2% / +3.8% |
| Financials | 482 / 55% / +2.0% / +0.6% | 469 / 58% / +11.1% / +4.2% | 445 / 56% / +27.0% / +14.3% |
| Healthcare | 528 / 63% / +4.1% / +2.1% | 505 / 70% / +13.7% / +6.0% | 480 / 70% / +27.0% / +11.1% |
| I.T | 239 / 57% / +2.8% / +1.3% | 229 / 59% / +11.0% / +5.4% | 224 / 50% / +12.1% / +1.5% |
| Industrials | 352 / 67% / +5.4% / +3.7% | 339 / 72% / +21.2% / +14.7% | 326 / 77% / +52.9% / +37.3% |
| Media | 40 / 42% / -1.2% / -1.5% | 40 / 22% / -3.9% / -8.6% | 40 / 18% / -14.9% / -20.9% |
| Metals & Mining | 173 / 57% / +3.3% / +3.0% | 168 / 61% / +15.5% / +9.0% | 144 / 72% / +27.1% / +13.5% |
| Miscellaneous | 99 / 60% / +3.4% / +1.8% | 92 / 55% / +15.4% / +8.6% | 85 / 55% / +24.1% / +8.7% |
| Plastic products | 29 / 62% / +7.2% / +7.2% | 29 / 69% / +15.2% / +7.4% | 29 / 69% / +26.0% / +6.6% |
| Power & Utilities | 146 / 55% / +3.2% / +2.4% | 146 / 67% / +22.6% / +16.2% | 131 / 75% / +54.5% / +37.5% |
| Realty | 220 / 60% / +3.6% / +1.9% | 208 / 75% / +23.8% / +13.6% | 205 / 70% / +40.0% / +23.1% |
| Services | 99 / 65% / +5.3% / +3.5% | 97 / 81% / +16.5% / +8.1% | 97 / 87% / +35.9% / +18.6% |
| Telecom-Service | 36 / 75% / +3.9% / -0.9% | 36 / 89% / +16.5% / +3.5% | 36 / 75% / +25.5% / +4.3% |
| Textiles | 71 / 45% / +3.6% / +2.6% | 71 / 42% / +5.3% / +0.2% | 71 / 39% / +5.2% / -3.2% |
| Transportation | 79 / 63% / +7.5% / +5.4% | 78 / 59% / +25.3% / +18.0% | 76 / 55% / +29.9% / +17.1% |

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| KPIGREEN | Power & Utilities | Midcap | 3 | +25.9% | +116.4% | +395.3% | 100% |
| ANANDRATHI | Financials | Largecap | 21 | +6.6% | +56.8% | +243.0% | 71% |
| RECLTD | Financials | Largecap | 7 | +1.3% | +71.6% | +221.5% | 86% |
| COSMOFIRST | Industrials | Smallcap | 3 | +22.9% | +121.5% | +214.6% | 100% |
| KOVAI | Healthcare | Midcap | 3 | -4.0% | +39.5% | +206.7% | 100% |
| BSE | Financials | Largecap | 4 | +7.9% | +58.0% | +202.3% | 100% |
| GRINDWELL | Industrials | Largecap | 3 | +14.7% | +82.5% | +178.8% | 100% |
| CDSL | Financials | Largecap | 3 | +12.5% | +62.9% | +174.9% | 100% |
| TECHNOE | Realty | Midcap | 9 | +2.7% | +35.5% | +174.9% | 100% |
| TALBROAUTO | Auto | Smallcap | 3 | +30.9% | +161.6% | +173.7% | 100% |

**Worst repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| RBLBANK | Bank | Largecap | 7 | +0.9% | -47.7% | -77.6% | 0% |
| HEGAM | Power & Utilities | Midcap | 5 | -11.2% | -5.2% | -50.9% | 0% |
| NEWGEN | I.T | Midcap | 5 | -3.7% | -13.5% | -47.1% | 20% |
| MUNJALSHOW | Auto | Smallcap | 3 | -11.4% | -27.3% | -42.1% | 0% |
| AAVAS | Financials | Midcap | 7 | +7.3% | -17.3% | -37.6% | 0% |
| DCBBANK | Bank | Midcap | 5 | -4.0% | +3.7% | -37.1% | 0% |
| MAHLIFE | Realty | Midcap | 3 | -2.4% | +0.2% | -36.7% | 0% |
| EQUITASBNK | Bank | Midcap | 4 | +1.4% | -2.3% | -36.3% | 0% |
| TANLA | I.T | Midcap | 5 | +21.8% | +19.0% | -34.7% | 0% |
| ELECTCAST | Castings, Forgings & Fasteners | Smallcap | 3 | -0.6% | -31.6% | -34.2% | 0% |

**Biggest single winners after 1 year**

| Stock | Bought | Price | Return | Nifty 500 |
|---|---|---|---|---|
| TARIL | 2023-05-26 | 40.22 | +791.0% | +37.4% |
| CUPID | 2023-08-22 | 3.35 | +410.5% | +41.2% |
| KPIGREEN | 2023-05-22 | 120.88 | +402.6% | +37.0% |
| KPIGREEN | 2023-05-17 | 119.56 | +397.9% | +38.0% |
| MIRZAINT | 2021-10-11 | 67.45 | +394.9% | -3.0% |
| KPIGREEN | 2023-05-18 | 123.20 | +385.4% | +37.8% |
| ANANDRATHI | 2023-05-02 | 219.48 | +350.5% | +34.5% |
| GOKEX | 2021-05-05 | 96.30 | +342.8% | +12.0% |
| JWL | 2023-05-15 | 120.45 | +336.0% | +38.8% |
| HUDCO | 2023-05-04 | 54.10 | +332.2% | +35.4% |

## Wkly_upswing

621 signals (28 Aug 2017 to 13 Nov 2026): 415 bought, 200 never crossed the trigger, 0 without Yahoo prices, 6 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 413 | 47% | +0.9% | -0.4% | +6.2% / -5.2% | +0.5% | 43% | +0.4% |
| Short | 1 month | 411 | 51% | +1.8% | +0.2% | +10.0% / -7.4% | +0.9% | 45% | +0.9% |
| Medium | 3 months | 397 | 52% | +6.2% | +1.7% | +20.6% / -12.4% | +2.8% | 49% | +3.5% |
| Medium | 6 months | 377 | 54% | +14.0% | +2.7% | +35.6% / -16.0% | +6.0% | 50% | +8.0% |
| Long | 1 year | 350 | 58% | +35.4% | +9.0% | +69.3% / -21.4% | +13.1% | 47% | +22.4% |
| Long | 2 years | 313 | 64% | +53.6% | +20.9% | +117.5% / -26.7% | +28.1% | 46% | +25.5% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Unknown | 4 / – / – / – | 0 / – / – / – | 0 / – / – / – |
| Largecap | 163 / 59% / +2.5% / +1.4% | 151 / 62% / +16.1% / +10.8% | 138 / 72% / +39.1% / +25.2% |
| Midcap | 89 / 48% / +2.5% / +1.4% | 85 / 46% / +7.1% / +2.2% | 77 / 52% / +24.4% / +13.3% |
| Smallcap | 155 / 45% / +1.1% / +0.5% | 141 / 49% / +16.0% / +8.5% | 135 / 47% / +38.0% / +24.7% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2017 | 11 / 55% / +3.6% / +2.3% | 11 / 45% / +3.6% / +2.0% | 11 / 45% / -3.6% / -2.6% |
| 2018 | 29 / 38% / -2.1% / +0.5% | 29 / 38% / -4.7% / -0.5% | 29 / 41% / -5.7% / -2.7% |
| 2019 | 24 / 46% / -1.2% / -2.7% | 24 / 38% / -5.2% / +3.2% | 24 / 33% / -5.8% / +5.0% |
| 2020 | 31 / 58% / +2.7% / +1.0% | 31 / 61% / +26.5% / +10.1% | 31 / 87% / +80.8% / +37.1% |
| 2021 | 45 / 53% / +0.8% / -1.7% | 45 / 53% / +31.2% / +19.3% | 45 / 62% / +66.0% / +56.9% |
| 2022 | 38 / 50% / +4.0% / +3.5% | 38 / 61% / +9.8% / +10.5% | 38 / 79% / +48.5% / +36.8% |
| 2023 | 73 / 59% / +6.4% / +3.9% | 73 / 71% / +36.0% / +18.5% | 73 / 81% / +81.5% / +48.3% |
| 2024 | 73 / 52% / -0.6% / -1.3% | 73 / 52% / +4.1% / -0.7% | 73 / 34% / -5.6% / -9.7% |
| 2025 | 32 / 59% / +6.5% / +5.5% | 32 / 38% / -1.4% / -1.4% | 26 / 35% / -4.3% / -4.3% |
| 2026 | 55 / 36% / -1.7% / -0.9% | 21 / 43% / +1.4% / +4.2% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Building Materials | 28 / 32% / -0.5% / -2.0% | 27 / 44% / -0.4% / -5.9% | 26 / 50% / +5.8% / -7.5% |
| Chemicals | 29 / 38% / -5.7% / -5.6% | 25 / 48% / +14.7% / +9.3% | 24 / 62% / +37.5% / +28.8% |
| Consumer Discretionary | 22 / 59% / +5.1% / +2.9% | 21 / 48% / +11.6% / +8.6% | 21 / 52% / +47.3% / +33.2% |
| FMCG | 27 / 41% / +0.8% / +0.4% | 24 / 38% / -4.0% / -8.1% | 22 / 50% / +6.8% / -5.0% |
| Financials | 33 / 55% / +1.8% / +0.4% | 30 / 67% / +26.6% / +15.9% | 30 / 63% / +38.6% / +25.0% |
| Healthcare | 34 / 68% / +4.8% / +3.3% | 33 / 61% / +24.4% / +15.3% | 33 / 67% / +48.7% / +32.0% |
| I.T | 31 / 45% / +4.7% / +5.5% | 30 / 53% / +20.6% / +16.9% | 28 / 57% / +55.4% / +48.5% |
| Industrials | 26 / 54% / +1.6% / +1.4% | 24 / 54% / +27.5% / +21.3% | 20 / 45% / +82.4% / +62.5% |
| Realty | 26 / 58% / -0.7% / -1.9% | 23 / 65% / +17.0% / +8.8% | 22 / 64% / +25.5% / +13.2% |

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| LAURUSLABS | Healthcare | Largecap | 4 | +1.7% | +120.2% | +238.9% | 100% |
| MCX | Financials | Largecap | 3 | +6.2% | +38.5% | +93.9% | 100% |
| JUBLFOOD | Consumer Discretionary | Largecap | 3 | +8.5% | +19.5% | +42.9% | 67% |
| DRREDDY | Healthcare | Largecap | 3 | +2.7% | +16.3% | +16.7% | 67% |
| RELIANCE | Energy | Largecap | 3 | +5.4% | -2.3% | +15.5% | 67% |
| MARICO | FMCG | Largecap | 3 | +1.6% | +4.0% | +9.2% | 100% |
| HIKAL | Healthcare | Smallcap | 3 | +22.0% | +37.1% | +7.6% | 33% |
| HCLTECH | I.T | Largecap | 6 | -6.8% | +3.0% | +5.1% | 67% |
| SIEMENS | Industrials | Largecap | 3 | +5.1% | -0.7% | +4.2% | 33% |
| PETRONET | Energy | Largecap | 3 | -1.0% | +1.4% | -4.5% | 33% |

**Worst repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| SIS | Miscellaneous | Midcap | 3 | -5.0% | -21.5% | -23.4% | 0% |
| CSBBANK | Bank | Midcap | 3 | -3.0% | -5.8% | -17.9% | 0% |
| HDFCBANK | Bank | Largecap | 3 | +0.0% | +4.7% | -17.3% | 0% |
| OBEROIRLTY | Realty | Largecap | 3 | -10.6% | -16.2% | -14.1% | 33% |
| PETRONET | Energy | Largecap | 3 | -1.0% | +1.4% | -4.5% | 33% |
| SIEMENS | Industrials | Largecap | 3 | +5.1% | -0.7% | +4.2% | 33% |
| HCLTECH | I.T | Largecap | 6 | -6.8% | +3.0% | +5.1% | 67% |
| HIKAL | Healthcare | Smallcap | 3 | +22.0% | +37.1% | +7.6% | 33% |
| MARICO | FMCG | Largecap | 3 | +1.6% | +4.0% | +9.2% | 100% |
| RELIANCE | Energy | Largecap | 3 | +5.4% | -2.3% | +15.5% | 67% |

**Biggest single winners after 1 year**

| Stock | Bought | Price | Return | Nifty 500 |
|---|---|---|---|---|
| BCG | 2021-03-08 | 5.14 | +1152.0% | +13.4% |
| WEBELSOLAR | 2023-08-08 | 11.10 | +768.8% | +37.8% |
| SKYGOLD | 2023-10-16 | 56.40 | +518.3% | +29.4% |
| LAURUSLABS | 2020-06-22 | 108.80 | +465.1% | +59.7% |
| AURIONPRO | 2023-05-08 | 233.95 | +446.8% | +37.0% |
| LAURUSLABS | 2020-04-27 | 102.64 | +346.3% | +67.2% |
| FORCEMOT | 2023-06-05 | 1951.00 | +317.2% | +43.4% |
| FLUOROCHEM | 2021-04-12 | 715.00 | +293.8% | +17.6% |
| NBCC | 2023-08-07 | 32.07 | +282.4% | +37.8% |
| MIRZAINT | 2021-07-26 | 65.60 | +275.5% | +5.7% |

## If I had bought on the alerts

Every buy alert from 2019-02-11 (when all three scanners have backtest data) to 2026-11-06, starting with ₹10L: each buy is 1/15 of the portfolio's value at the time (profits reinvested), at most 15 open, first come first served, one position per stock, after costs.

| Scanner | Trades | Win rate | Avg | Avg win / loss | Avg days |
|---|---|---|---|---|---|
| 63_30_daily | 1577 | 42% | +4.62% | +19.4% / -6.0% | 31 |
| Bullish_Scanner | 4700 | 44% | +4.06% | +16.4% / -5.7% | 31 |
| Wkly_upswing | 210 | 42% | +3.23% | +16.1% / -6.1% | 31 |
| All | 6487 | 43% | +4.17% | +17.1% / -5.8% | 31 |

| | Alerts portfolio | Nifty 500 |
|---|---|---|
| ₹10L became | ₹61.9L | ₹26.2L |
| Yearly growth (CAGR) | 26.6% | 13.2% |
| Worst fall from a peak | -9.2% | -38.3% |
| Trades taken / skipped (no free slot) | 795 / 5687 | |
| Win rate of trades taken | 43% | |

| Year | Alerts portfolio | Nifty 500 |
|---|---|---|
| 2019 | +1.2% | +10.1% |
| 2020 | +38.6% | +16.7% |
| 2021 | +64.5% | +30.2% |
| 2022 | +22.1% | +3.0% |
| 2023 | +20.5% | +25.8% |
| 2024 | +42.1% | +15.2% |
| 2025 | +7.8% | +6.7% |
| 2026 | +19.2% | -1.7% |

Open positions are counted at cost until sold. The current year is year-to-date.

### Exit rules compared (same dip buys)

Every rule keeps the starting 15% stop; the riding rules sell after a year at the latest. Only buys that every rule has closed are counted.

| Exit | Trades | Win rate | Avg | Avg win / loss | Avg days | ₹10L became | Per year | Worst fall |
|---|---|---|---|---|---|---|---|---|
| wait for pullback, +8% target, 8 weeks (older) | 5448 | 71% | +2.15% | +7.6% / -11.0% | 19 | ₹28.0L | 14.3% | -20.8% |
| 10% trailing stop | 5448 | 43% | +3.27% | +16.4% / -6.6% | 37 | ₹25.6L | 13.0% | -20.8% |
| 15% trailing stop | 5448 | 45% | +7.46% | +28.2% / -9.8% | 74 | ₹33.3L | 16.8% | -15.1% |
| close below 20-day average | 5448 | 40% | +1.44% | +9.0% / -3.5% | 12 | ₹32.6L | 16.6% | -16.2% |
| wait for pullback, close below 50-day average (old) | 5448 | 41% | +4.27% | +18.9% / -6.0% | 36 | ₹51.1L | 23.6% | -13.8% |
| half at +8%, rest on close below 20-day average | 5448 | 45% | +1.10% | +6.9% / -3.6% | 12 | ₹26.5L | 13.5% | -13.5% |
| after +8%: stop at cost, sell on close below 20-day average | 5448 | 53% | +3.04% | +11.9% / -7.0% | 30 | ₹26.7L | 13.6% | -26.1% |
| after +8%: stop at cost, sell on close below 50-day average | 5448 | 39% | +4.13% | +19.4% / -5.4% | 40 | ₹26.3L | 13.4% | -26.7% |
| buy at the breakout, close below the 30-day EMA (now) | 5448 | 42% | +4.07% | +17.0% / -5.4% | 29 | ₹55.1L | 24.7% | -11.4% |
| no pullback, every breakout (incl. stocks that never dipped) | 6487 | 43% | +4.17% | +17.1% / -5.8% | 30 | ₹61.9L | 26.6% | -9.2% |

| Exit | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| wait for pullback, +8% target, 8 weeks (older) | 73% · +2.44% | 70% · +2.05% | 72% · +2.13% |
| 10% trailing stop | 44% · +3.90% | 43% · +3.01% | 42% · +5.18% |
| 15% trailing stop | 45% · +8.00% | 46% · +7.30% | 40% · +6.51% |
| close below 20-day average | 39% · +1.62% | 40% · +1.34% | 48% · +2.65% |
| wait for pullback, close below 50-day average (old) | 42% · +5.12% | 41% · +4.02% | 42% · +3.28% |
| half at +8%, rest on close below 20-day average | 45% · +1.23% | 45% · +1.05% | 53% · +1.53% |
| after +8%: stop at cost, sell on close below 20-day average | 54% · +3.36% | 53% · +2.90% | 56% · +4.20% |
| after +8%: stop at cost, sell on close below 50-day average | 40% · +4.73% | 38% · +3.97% | 34% · +2.68% |
| buy at the breakout, close below the 30-day EMA (now) | 41% · +4.60% | 43% · +3.88% | 38% · +4.72% |
| no pullback, every breakout (incl. stocks that never dipped) | 42% · +4.62% | 44% · +4.06% | 42% · +3.23% |

## Breakout rule (the live alert rule)

Buy when the price trades above the trigger (the signal candle's high) within 3 sessions (5 after a weekly signal), filled at the trigger or the open on a gap-up. Sell at the next open after a close below the 30-day EMA, a 15% stop (), or after 250 sessions. Wkly_upswing only when daily ATR(14) is under 4% of the close. Filter: 63_30_daily only within 10% of the 52-week high. 0.25% costs.

| Group | Trades | Win rate | Avg | Avg win / loss | Average / stop / time | Avg days | ₹ on ₹1L a trade |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 1577 | 42% | +4.62% | +19.4% / -6.0% | 99% / 1% / 0% | 31 | 7,280,040 |
| Bullish_Scanner | 4700 | 44% | +4.06% | +16.4% / -5.7% | 98% / 2% / 0% | 31 | 19,063,930 |
| Wkly_upswing | 239 | 42% | +3.01% | +15.5% / -6.0% | 97% / 3% / 0% | 31 | 719,020 |
| Largecap | 3294 | 44% | +3.71% | +14.9% / -5.0% | 100% / 0% / 0% | 33 | 12,230,510 |
| Midcap | 1698 | 44% | +4.43% | +18.4% / -6.4% | 97% / 3% / 0% | 31 | 7,518,100 |
| Smallcap | 1522 | 42% | +4.80% | +20.5% / -6.8% | 97% / 3% / 0% | 30 | 7,308,850 |
| **All** | 6516 | 43% | +4.15% | +17.1% / -5.8% | 98% / 2% / 0% | 31 | 27,062,990 |

## Reading this

- Average vs median: a high average with a low median means a few big winners carry the result; most buys did worse than the average.
- Compare with the Nifty 500 column: a scanner adds value only when its picks beat the index.
- Stocks Yahoo no longer lists (delisted, renamed) are missing, which flatters long-term results a little (survivorship bias).
- No costs, taxes or stop-loss are included; real results will be lower, and holding with no stop means sitting through every drawdown shown in 'Avg best / worst'.
