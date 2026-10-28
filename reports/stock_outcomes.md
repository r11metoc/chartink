# If I had bought every scanner stock

Generated 2026-10-28 17:02 UTC by `scripts/stock_outcomes.py` from `data/backtest/*.csv` plus the bot's live triggers.

**Rule:** buy when price crosses the signal candle's high within 3 sessions (5 for `Wkly_upswing`), filled at the trigger or at the open on a gap-up; then hold. No stop, no target, no costs. **Short** = 2 weeks / 1 month, **Medium** = 3 / 6 months, **Long** = 1 / 2 years. **Beat Nifty 500** = share of buys that did better than the index over the same days. Recent buys only count for horizons that have fully passed.

Per-trade data: `data/model/stock_outcomes.csv`; per-stock: `data/model/stock_summary.csv`.

## All scanners at a glance

| Scanner | Signals | Bought | 1 month avg | 6 months avg | 1 year avg | 2 years avg | 1 year vs Nifty 500 |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 1832 | 1440 | +3.3% | +14.6% | +23.8% | +46.5% | +9.5% |
| Bullish_Scanner | 5083 | 4204 | +3.6% | +15.3% | +27.4% | +48.1% | +13.0% |
| Wkly_upswing | 615 | 415 | +2.1% | +14.0% | +35.6% | +53.8% | +22.4% |

## 63_30_daily

1832 signals (01 Jan 2021 to 27 Oct 2026): 1440 bought, 389 never crossed the trigger, 3 without Yahoo prices, 0 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 1437 | 52% | +1.6% | +0.2% | +5.4% / -3.7% | +0.7% | 47% | +0.9% |
| Short | 1 month | 1435 | 56% | +3.3% | +1.8% | +9.1% / -5.4% | +1.5% | 49% | +1.8% |
| Medium | 3 months | 1416 | 62% | +8.2% | +4.7% | +19.7% / -9.2% | +4.4% | 51% | +3.8% |
| Medium | 6 months | 1369 | 64% | +14.6% | +7.8% | +31.5% / -12.4% | +7.5% | 49% | +7.1% |
| Long | 1 year | 1271 | 62% | +23.8% | +10.9% | +50.4% / -16.5% | +14.4% | 49% | +9.5% |
| Long | 2 years | 1115 | 66% | +46.5% | +28.5% | +89.2% / -21.0% | +28.1% | 50% | +18.4% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Unknown | 0 / – / – / – | 0 / – / – / – | 0 / – / – / – |
| Largecap | 648 / 56% / +1.8% / +0.4% | 631 / 64% / +12.3% / +6.2% | 570 / 68% / +24.9% / +11.5% |
| Midcap | 400 / 59% / +4.8% / +3.6% | 370 / 71% / +22.6% / +14.7% | 338 / 65% / +34.5% / +20.1% |
| Smallcap | 387 / 55% / +4.2% / +2.5% | 368 / 55% / +10.4% / +1.0% | 363 / 49% / +12.1% / -3.7% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2021 | 220 / 52% / +4.2% / +2.0% | 220 / 52% / +9.8% / +1.6% | 220 / 46% / +9.3% / +4.4% |
| 2022 | 168 / 45% / -1.4% / +1.1% | 168 / 43% / +1.5% / +3.5% | 168 / 63% / +24.3% / +17.4% |
| 2023 | 429 / 66% / +5.2% / +1.5% | 429 / 86% / +30.6% / +14.3% | 429 / 83% / +52.8% / +18.9% |
| 2024 | 333 / 54% / +3.3% / +2.2% | 333 / 59% / +8.1% / +3.3% | 333 / 50% / +4.2% / +0.1% |
| 2025 | 170 / 57% / +2.5% / +1.1% | 170 / 51% / +2.9% / +1.8% | 121 / 48% / +0.7% / -0.0% |
| 2026 | 115 / 52% / +2.5% / +3.7% | 49 / 69% / +24.6% / +25.0% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Auto | 116 / 62% / +6.6% / +4.7% | 115 / 78% / +26.5% / +15.7% | 115 / 76% / +38.1% / +19.4% |
| Bank | 98 / 61% / +1.8% / -0.0% | 91 / 73% / +11.2% / +5.2% | 82 / 73% / +19.6% / +1.4% |
| Building Materials | 77 / 52% / +4.8% / +1.9% | 76 / 58% / +7.9% / -3.3% | 71 / 52% / +11.4% / -9.7% |
| Chemicals | 83 / 40% / +0.6% / +0.1% | 83 / 45% / +4.0% / -2.7% | 74 / 47% / +15.8% / +7.9% |
| Consumer Discretionary | 67 / 64% / +3.7% / +2.2% | 65 / 58% / +14.1% / +8.6% | 65 / 66% / +13.6% / +0.7% |
| Energy | 57 / 56% / +0.8% / -0.1% | 56 / 39% / +0.9% / -2.8% | 49 / 41% / +6.9% / +0.3% |
| FMCG | 94 / 57% / +2.7% / +0.7% | 91 / 64% / +18.1% / +7.4% | 86 / 55% / +20.8% / +4.7% |
| Financials | 189 / 49% / +1.4% / +0.5% | 177 / 57% / +7.8% / +2.5% | 157 / 60% / +14.4% / +3.5% |
| Healthcare | 125 / 68% / +4.3% / +1.7% | 120 / 79% / +17.6% / +10.6% | 104 / 68% / +22.2% / +8.4% |
| I.T | 67 / 58% / +3.4% / +2.1% | 61 / 69% / +7.1% / +2.1% | 59 / 46% / +2.2% / -5.0% |
| Industrials | 74 / 65% / +4.1% / +2.2% | 67 / 75% / +25.8% / +16.8% | 59 / 59% / +29.0% / +12.1% |
| Metals & Mining | 78 / 55% / +1.5% / +0.3% | 69 / 70% / +27.8% / +19.0% | 64 / 73% / +35.7% / +18.6% |
| Miscellaneous | 29 / 52% / +0.8% / -0.3% | 27 / 67% / +5.0% / -3.3% | 27 / 52% / +25.2% / +1.7% |
| Realty | 90 / 59% / +4.2% / +3.2% | 85 / 67% / +19.3% / +11.1% | 82 / 66% / +53.4% / +35.6% |
| Services | 37 / 57% / +8.8% / +7.9% | 37 / 70% / +19.9% / +13.3% | 37 / 84% / +38.0% / +28.3% |
| Telecom-Service | 21 / 76% / +4.8% / +2.6% | 21 / 86% / +7.4% / -3.3% | 21 / 43% / +0.6% / -8.5% |
| Textiles | 29 / 52% / +4.9% / +3.4% | 26 / 38% / -3.8% / -11.8% | 26 / 58% / +5.6% / -10.3% |

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| IRCON | Realty | Midcap | 4 | +18.3% | +93.4% | +214.4% | 75% |
| GOKEX | Readymade Garments/Apparels | Smallcap | 3 | +23.2% | +115.4% | +165.3% | 100% |
| TECHNOE | Realty | Midcap | 5 | +3.0% | +20.9% | +148.7% | 100% |
| PITTIENG | Industrials | Smallcap | 4 | +6.3% | +96.9% | +146.1% | 100% |
| ARVSMART | Realty | Smallcap | 3 | +15.6% | +61.8% | +144.9% | 100% |
| EXIDEIND | Auto | Largecap | 4 | +8.5% | +33.1% | +140.0% | 100% |
| NAVA | Miscellaneous | Midcap | 3 | +13.3% | +56.2% | +116.6% | 100% |
| PRESTIGE | Realty | Largecap | 4 | -6.3% | -12.7% | +115.6% | 25% |
| SANDHAR | Auto | Smallcap | 3 | +22.9% | +99.6% | +113.9% | 100% |
| BEL | Aerospace & Defence | Largecap | 7 | +6.4% | +25.6% | +110.6% | 86% |

**Worst repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| FUSION | Financials | Smallcap | 3 | -14.6% | -33.0% | -73.3% | 0% |
| INDIAGLYCO | FMCG | Smallcap | 3 | +12.8% | -2.9% | -68.8% | 0% |
| STAR | Healthcare | Midcap | 8 | +10.3% | +4.5% | -65.0% | 0% |
| DELTACORP | Miscellaneous | Smallcap | 4 | +4.1% | -41.1% | -50.2% | 0% |
| IONEXCHANG | Realty | Smallcap | 3 | -12.9% | -25.7% | -48.7% | 0% |
| MUNJALSHOW | Auto | Smallcap | 3 | -11.4% | -27.3% | -42.1% | 0% |
| GUJENERGY | Energy | Largecap | 3 | -9.7% | -36.7% | -36.8% | 0% |
| HDFCAMC | Financials | Largecap | 3 | -6.7% | -28.4% | -36.5% | 0% |
| CHEMCON | Chemicals | Smallcap | 3 | -11.2% | -12.8% | -29.9% | 0% |
| HINDPETRO | Energy | Largecap | 9 | +5.6% | -13.1% | -29.0% | 0% |

**Biggest single winners after 1 year**

| Stock | Bought | Price | Return | Nifty 500 |
|---|---|---|---|---|
| MAZDOCK | 2022-08-18 | 162.32 | +472.5% | +10.1% |
| CUPID | 2023-08-21 | 3.32 | +416.4% | +41.8% |
| GOKEX | 2021-05-05 | 96.30 | +342.8% | +12.0% |
| BSE | 2021-04-28 | 69.11 | +309.1% | +16.4% |
| IRCON | 2023-04-20 | 62.50 | +300.9% | +41.3% |
| IRCON | 2023-04-21 | 63.80 | +294.0% | +41.9% |
| IRCON | 2023-04-24 | 65.00 | +283.8% | +41.2% |
| ZENTEC | 2023-02-15 | 215.00 | +276.3% | +35.3% |
| ZENTEC | 2023-02-15 | 215.90 | +274.7% | +35.3% |
| OIL | 2023-08-01 | 184.90 | +271.7% | +33.1% |

## Bullish_Scanner

5083 signals (01 Jan 2021 to 22 Oct 2026): 4204 bought, 861 never crossed the trigger, 18 without Yahoo prices, 0 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 4198 | 55% | +2.1% | +0.7% | +6.0% / -3.4% | +0.7% | 50% | +1.4% |
| Short | 1 month | 4189 | 59% | +3.6% | +2.0% | +9.6% / -5.1% | +1.6% | 51% | +2.1% |
| Medium | 3 months | 4114 | 63% | +8.7% | +5.6% | +19.8% / -8.5% | +4.3% | 53% | +4.4% |
| Medium | 6 months | 3987 | 65% | +15.3% | +9.2% | +31.7% / -11.4% | +8.0% | 52% | +7.3% |
| Long | 1 year | 3743 | 64% | +27.4% | +13.5% | +53.7% / -15.4% | +14.4% | 52% | +13.0% |
| Long | 2 years | 3405 | 69% | +48.1% | +26.7% | +90.0% / -19.6% | +26.5% | 51% | +21.6% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Unknown | 0 / – / – / – | 0 / – / – / – | 0 / – / – / – |
| Largecap | 2009 / 59% / +2.7% / +1.2% | 1947 / 68% / +14.6% / +7.5% | 1766 / 71% / +29.5% / +15.4% |
| Midcap | 1116 / 59% / +4.5% / +2.9% | 1041 / 66% / +18.9% / +10.6% | 991 / 62% / +32.6% / +18.5% |
| Smallcap | 1064 / 58% / +4.6% / +2.8% | 999 / 58% / +12.9% / +3.7% | 986 / 53% / +18.4% / +3.2% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2021 | 853 / 56% / +4.2% / +2.0% | 853 / 59% / +13.2% / +5.8% | 853 / 54% / +15.9% / +10.3% |
| 2022 | 403 / 48% / +1.4% / +3.3% | 403 / 51% / +4.4% / +6.2% | 403 / 69% / +25.7% / +18.0% |
| 2023 | 1235 / 68% / +5.5% / +2.2% | 1235 / 85% / +30.1% / +12.9% | 1235 / 84% / +58.6% / +24.8% |
| 2024 | 1007 / 55% / +2.8% / +1.3% | 1007 / 59% / +8.2% / +3.4% | 1007 / 50% / +4.4% / +0.3% |
| 2025 | 373 / 57% / +2.6% / +1.9% | 373 / 48% / +2.8% / +2.1% | 245 / 47% / +7.8% / +7.1% |
| 2026 | 318 / 53% / +1.8% / +3.2% | 116 / 48% / +13.0% / +14.0% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Aerospace & Defence | 75 / 63% / +8.1% / +6.9% | 74 / 92% / +47.4% / +39.2% | 73 / 93% / +78.1% / +62.8% |
| Auto | 310 / 64% / +3.7% / +1.5% | 291 / 69% / +18.4% / +8.5% | 281 / 78% / +30.2% / +12.9% |
| Bank | 272 / 53% / +0.7% / +0.1% | 249 / 63% / +9.3% / +4.7% | 189 / 68% / +16.4% / +3.4% |
| Building Materials | 212 / 50% / +2.9% / +1.2% | 204 / 46% / +2.8% / -5.4% | 199 / 40% / +4.7% / -8.6% |
| Castings, Forgings & Fasteners | 32 / 66% / +6.9% / +4.9% | 30 / 43% / -0.5% / -9.1% | 28 / 43% / +2.2% / -15.1% |
| Chemicals | 215 / 51% / +3.1% / +1.8% | 211 / 60% / +13.4% / +5.5% | 198 / 58% / +17.6% / +6.8% |
| Consumer Discretionary | 159 / 55% / +4.3% / +3.5% | 151 / 61% / +14.0% / +9.1% | 149 / 57% / +17.9% / +6.4% |
| Energy | 175 / 61% / +3.7% / +2.2% | 173 / 53% / +9.5% / +2.9% | 149 / 51% / +21.0% / +8.0% |
| FMCG | 333 / 59% / +3.1% / +1.1% | 313 / 66% / +14.7% / +4.3% | 303 / 62% / +21.4% / +6.3% |
| Financials | 437 / 53% / +1.9% / +0.5% | 420 / 58% / +11.2% / +3.6% | 389 / 57% / +28.0% / +14.5% |
| Healthcare | 458 / 64% / +4.9% / +2.6% | 422 / 72% / +13.1% / +4.4% | 411 / 68% / +24.3% / +8.8% |
| I.T | 219 / 60% / +3.1% / +1.4% | 209 / 61% / +11.4% / +5.2% | 204 / 48% / +10.8% / +0.3% |
| Industrials | 325 / 64% / +4.7% / +3.0% | 311 / 76% / +23.4% / +15.8% | 293 / 80% / +55.0% / +38.9% |
| Media | 34 / 38% / -1.6% / -2.1% | 34 / 24% / -1.9% / -8.0% | 34 / 21% / -10.3% / -19.0% |
| Metals & Mining | 170 / 56% / +3.3% / +3.1% | 162 / 61% / +15.7% / +9.4% | 137 / 72% / +27.7% / +13.9% |
| Miscellaneous | 93 / 58% / +3.4% / +1.8% | 86 / 58% / +16.6% / +8.3% | 79 / 58% / +25.3% / +9.5% |
| Plastic products | 22 / 68% / +9.0% / +8.2% | 22 / 77% / +18.8% / +7.3% | 22 / 68% / +27.0% / +4.7% |
| Power & Utilities | 126 / 57% / +3.8% / +2.9% | 122 / 74% / +26.4% / +18.8% | 113 / 79% / +57.5% / +40.4% |
| Realty | 209 / 59% / +3.8% / +1.9% | 195 / 80% / +26.6% / +15.5% | 193 / 72% / +41.9% / +24.7% |
| Services | 99 / 65% / +5.3% / +3.5% | 97 / 81% / +16.5% / +8.1% | 97 / 87% / +35.9% / +18.6% |
| Telecom-Service | 34 / 76% / +4.2% / -0.4% | 34 / 91% / +17.1% / +4.0% | 34 / 76% / +27.1% / +7.2% |
| Textiles | 70 / 46% / +3.7% / +2.7% | 70 / 41% / +4.2% / -0.7% | 70 / 39% / +3.9% / -4.1% |
| Transportation | 85 / 67% / +7.8% / +6.3% | 83 / 61% / +21.1% / +13.2% | 74 / 54% / +27.6% / +15.0% |

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| KPIGREEN | Power & Utilities | Midcap | 3 | +25.9% | +116.4% | +395.3% | 100% |
| ANANDRATHI | Financials | Largecap | 21 | +6.6% | +56.8% | +243.0% | 71% |
| RECLTD | Financials | Largecap | 7 | +1.3% | +71.6% | +221.5% | 86% |
| KOVAI | Healthcare | Midcap | 3 | -4.0% | +39.5% | +206.7% | 100% |
| TECHNOE | Realty | Midcap | 9 | +2.7% | +35.5% | +174.9% | 100% |
| TALBROAUTO | Auto | Smallcap | 3 | +30.9% | +161.6% | +173.7% | 100% |
| WABAG | Realty | Midcap | 3 | +10.4% | +44.4% | +170.6% | 100% |
| SALZERELEC | Industrials | Smallcap | 4 | +1.1% | +54.1% | +164.6% | 100% |
| GOKEX | Readymade Garments/Apparels | Smallcap | 5 | +23.9% | +97.3% | +159.9% | 80% |
| WHEELS | Auto | Midcap | 7 | +4.2% | +70.6% | +154.3% | 43% |

**Worst repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| AAVAS | Financials | Midcap | 6 | +7.2% | -14.4% | -42.2% | 0% |
| MUNJALSHOW | Auto | Smallcap | 3 | -11.4% | -27.3% | -42.1% | 0% |
| MAHLIFE | Realty | Midcap | 3 | -2.4% | +0.2% | -36.7% | 0% |
| EQUITASBNK | Bank | Midcap | 4 | +1.4% | -2.3% | -36.3% | 0% |
| TANLA | I.T | Midcap | 5 | +21.8% | +19.0% | -34.7% | 0% |
| ELECTCAST | Castings, Forgings & Fasteners | Smallcap | 3 | -0.6% | -31.6% | -34.2% | 0% |
| ANDHRAPAP | Building Materials | Smallcap | 3 | -12.9% | -14.8% | -32.9% | 0% |
| BIRLACORPN | Building Materials | Midcap | 6 | -11.5% | -25.4% | -30.0% | 0% |
| GRMOVER | FMCG | Smallcap | 6 | +8.0% | +7.0% | -29.2% | 0% |
| TRIGYN | I.T | Smallcap | 4 | -3.9% | -9.8% | -29.1% | 0% |

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

615 signals (28 Aug 2017 to 14 Oct 2026): 415 bought, 200 never crossed the trigger, 0 without Yahoo prices, 0 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 413 | 47% | +1.0% | -0.4% | +6.2% / -5.1% | +0.5% | 43% | +0.4% |
| Short | 1 month | 406 | 51% | +2.1% | +0.3% | +10.0% / -7.2% | +0.9% | 46% | +1.2% |
| Medium | 3 months | 391 | 52% | +6.4% | +1.8% | +20.6% / -12.3% | +2.9% | 49% | +3.5% |
| Medium | 6 months | 375 | 54% | +14.0% | +2.7% | +35.5% / -16.0% | +6.1% | 50% | +7.9% |
| Long | 1 year | 348 | 58% | +35.6% | +9.0% | +69.4% / -21.5% | +13.2% | 47% | +22.4% |
| Long | 2 years | 315 | 64% | +53.8% | +21.4% | +117.3% / -26.7% | +28.0% | 46% | +25.8% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Unknown | 0 / – / – / – | 0 / – / – / – | 0 / – / – / – |
| Largecap | 162 / 59% / +2.2% / +1.1% | 150 / 62% / +14.8% / +9.2% | 138 / 71% / +36.4% / +22.6% |
| Midcap | 94 / 49% / +3.1% / +2.0% | 87 / 47% / +11.1% / +6.5% | 76 / 54% / +29.6% / +18.4% |
| Smallcap | 150 / 45% / +1.2% / +0.7% | 138 / 49% / +15.1% / +7.4% | 134 / 48% / +38.2% / +24.5% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2017 | 11 / 55% / +3.6% / +2.3% | 11 / 45% / +3.6% / +2.0% | 11 / 45% / -3.6% / -2.6% |
| 2018 | 30 / 37% / -2.7% / +0.0% | 30 / 37% / -5.9% / -1.7% | 30 / 40% / -6.8% / -3.7% |
| 2019 | 24 / 46% / -1.2% / -2.7% | 24 / 38% / -5.2% / +3.2% | 24 / 33% / -5.8% / +5.0% |
| 2020 | 31 / 58% / +2.7% / +1.0% | 31 / 61% / +26.5% / +10.1% | 31 / 87% / +80.8% / +37.1% |
| 2021 | 47 / 51% / +0.5% / -2.1% | 47 / 53% / +29.5% / +17.2% | 47 / 64% / +63.2% / +54.0% |
| 2022 | 38 / 50% / +4.0% / +3.5% | 38 / 61% / +9.8% / +10.5% | 38 / 79% / +48.5% / +36.8% |
| 2023 | 73 / 59% / +6.4% / +3.9% | 73 / 71% / +36.0% / +18.5% | 73 / 81% / +81.5% / +48.3% |
| 2024 | 72 / 53% / -0.5% / -1.2% | 72 / 53% / +4.5% / -0.1% | 72 / 35% / -5.2% / -9.2% |
| 2025 | 32 / 59% / +6.5% / +5.5% | 32 / 38% / -1.4% / -1.4% | 22 / 32% / -5.7% / -6.3% |
| 2026 | 48 / 42% / +0.3% / +1.5% | 17 / 41% / +2.3% / +5.5% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Building Materials | 28 / 32% / -0.5% / -2.0% | 27 / 44% / -0.4% / -5.9% | 26 / 50% / +5.8% / -7.5% |
| Chemicals | 29 / 38% / -5.7% / -5.6% | 24 / 50% / +15.9% / +10.1% | 24 / 62% / +37.5% / +28.8% |
| Consumer Discretionary | 23 / 57% / +4.9% / +3.0% | 21 / 48% / +11.6% / +8.6% | 21 / 52% / +47.3% / +33.2% |
| FMCG | 25 / 44% / +1.5% / +1.1% | 24 / 38% / -4.0% / -8.1% | 22 / 50% / +6.8% / -5.0% |
| Financials | 33 / 55% / +1.8% / +0.4% | 30 / 67% / +26.6% / +15.9% | 30 / 63% / +38.6% / +25.0% |
| Healthcare | 34 / 68% / +4.8% / +3.3% | 33 / 61% / +24.4% / +15.3% | 33 / 67% / +48.7% / +32.0% |
| I.T | 31 / 45% / +4.7% / +5.5% | 29 / 52% / +20.5% / +16.7% | 28 / 57% / +55.4% / +48.5% |
| Industrials | 24 / 58% / +3.3% / +3.0% | 24 / 54% / +27.5% / +21.3% | 20 / 45% / +82.4% / +62.5% |
| Realty | 26 / 58% / -0.7% / -1.9% | 23 / 65% / +17.0% / +8.8% | 21 / 67% / +27.5% / +14.6% |

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
| GESHIP | Transportation | Largecap | 3 | -10.8% | -19.4% | -12.4% | 67% |
| PETRONET | Energy | Largecap | 3 | -1.0% | +1.4% | -4.5% | 33% |
| SIEMENS | Industrials | Largecap | 3 | +5.1% | -0.7% | +4.2% | 33% |
| HCLTECH | I.T | Largecap | 6 | -6.8% | +3.0% | +5.1% | 67% |
| HIKAL | Healthcare | Smallcap | 3 | +22.0% | +37.1% | +7.6% | 33% |
| MARICO | FMCG | Largecap | 3 | +1.6% | +4.0% | +9.2% | 100% |

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

## Trigger-price stop with re-entry

Buy when price crosses above the trigger (the signal candle's high). No target and no time limit. Sell when price falls below the trigger; buy again each time it climbs back above it, for 63 sessions (3 months) after the signal. A position bought inside those 3 months is held until the stop, however long that takes; open positions are valued at the latest close. Every buy/sell pays 0.25% costs. Two versions of the stop:

- **close**: sell at the next open after a daily close below the trigger
- **intraday**: sell the moment price trades below the trigger (at the trigger, or the open on a gap-down)

Return = all the buys and sells of one signal compounded. Nifty 500 = from the first buy to the last sell (or today).

### Stop on a close below the trigger

| Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | Worst 10% avg | Avg days invested | Still holding | Nifty 500 avg | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 1752 | 5.3 | 24% | +27.3% | -5.4% | -22.7% | 258 | 422 | +10.4% | +17.0% |
| Bullish_Scanner | 4948 | 5.5 | 22% | +22.8% | -5.8% | -23.0% | 251 | 1101 | +9.8% | +13.1% |
| Wkly_upswing | 560 | 5.3 | 19% | +35.6% | -7.2% | -24.5% | 230 | 105 | +11.0% | +24.6% |
| **All** | 7260 | 5.5 | 22% | +24.9% | -5.8% | -23.1% | 251 | 1628 | +10.0% | +14.9% |

| Scanner | Cap | Signals | Profitable | Avg return | Median | Avg days invested |
|---|---|---|---|---|---|---|
| 63_30_daily | Largecap | 770 | 27% | +43.0% | -4.6% | 275 |
| 63_30_daily | Midcap | 493 | 29% | +28.6% | -5.3% | 292 |
| 63_30_daily | Smallcap | 488 | 13% | +1.4% | -7.6% | 197 |
| Bullish_Scanner | Largecap | 2354 | 28% | +35.0% | -4.3% | 279 |
| Bullish_Scanner | Midcap | 1334 | 22% | +22.2% | -6.5% | 251 |
| Bullish_Scanner | Smallcap | 1257 | 12% | +0.8% | -7.8% | 198 |
| Wkly_upswing | Largecap | 200 | 26% | +80.4% | -5.5% | 302 |
| Wkly_upswing | Midcap | 136 | 21% | +24.2% | -7.3% | 213 |
| Wkly_upswing | Smallcap | 219 | 13% | +2.8% | -9.3% | 179 |

| Buys per signal | Signals | Profitable | Avg return |
|---|---|---|---|
| 1 | 1097 | 39% | +54.7% |
| 2 | 967 | 30% | +35.7% |
| 3 | 773 | 24% | +34.2% |
| 4 | 748 | 19% | +34.2% |
| 5 | 632 | 21% | +24.5% |
| 6+ | 3043 | 15% | +6.2% |

### Stop on any trade below the trigger

| Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | Worst 10% avg | Avg days invested | Still holding | Nifty 500 avg | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 1752 | 6.6 | 20% | +24.5% | -5.9% | -23.7% | 236 | 371 | +9.8% | +14.7% |
| Bullish_Scanner | 4948 | 6.9 | 19% | +19.1% | -6.2% | -23.8% | 225 | 975 | +9.2% | +9.9% |
| Wkly_upswing | 560 | 6.5 | 16% | +31.1% | -6.9% | -24.7% | 201 | 90 | +10.0% | +21.1% |
| **All** | 7260 | 6.8 | 19% | +21.3% | -6.2% | -23.9% | 226 | 1436 | +9.4% | +11.9% |

| Scanner | Cap | Signals | Profitable | Avg return | Median | Avg days invested |
|---|---|---|---|---|---|---|
| 63_30_daily | Largecap | 770 | 23% | +39.3% | -5.1% | 248 |
| 63_30_daily | Midcap | 493 | 26% | +25.5% | -5.5% | 275 |
| 63_30_daily | Smallcap | 488 | 10% | +0.1% | -7.5% | 178 |
| Bullish_Scanner | Largecap | 2354 | 24% | +30.2% | -5.0% | 249 |
| Bullish_Scanner | Midcap | 1334 | 19% | +18.0% | -6.4% | 229 |
| Bullish_Scanner | Smallcap | 1257 | 10% | -0.5% | -8.4% | 178 |
| Wkly_upswing | Largecap | 200 | 21% | +72.4% | -5.5% | 264 |
| Wkly_upswing | Midcap | 136 | 18% | +21.3% | -8.9% | 178 |
| Wkly_upswing | Smallcap | 219 | 10% | +0.3% | -7.5% | 162 |

| Buys per signal | Signals | Profitable | Avg return |
|---|---|---|---|
| 1 | 722 | 28% | +43.9% |
| 2 | 817 | 30% | +48.6% |
| 3 | 693 | 23% | +51.2% |
| 4 | 621 | 23% | +26.3% |
| 5 | 569 | 19% | +11.9% |
| 6+ | 3838 | 13% | +6.5% |


## The pullback after the breakout

For every signal that crossed its trigger, the 20 sessions after the first crossing. **Back at the trigger** = the low came within 2% of the trigger (or below).

| Scanner | Breakouts | Back at the trigger | Median days to get there | Closed below the trigger | Closed 5%+ below | Median dip from the high | 3 months later: retested / not |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 1747 | 96% | 1 | 82% | 42% | -11.6% | +7.7% / +27.7% |
| Bullish_Scanner | 4933 | 96% | 1 | 80% | 41% | -11.4% | +7.6% / +30.0% |
| Wkly_upswing | 552 | 95% | 1 | 83% | 54% | -13.7% | +4.1% / +41.5% |
| **All** | 7232 | 96% | 1 | 81% | 42% | -11.6% | +7.4% / +30.5% |

## Why a stop at the buy price still loses

Every round trip of the *breakout* rule (buy above the trigger, sell after a close below it). Entry and exit are shown against the trigger price.

| Scanner | Stopped round trips | Avg bought above trigger | Avg sold below trigger | Costs | Avg loss per stop | Bought on a gap-up | Sold 3%+ below trigger | Avg days held |
|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 8950 | +0.2% | -1.3% | -0.25% | -1.7% | 9% | 11% | 17 |
| Bullish_Scanner | 26171 | +0.2% | -1.2% | -0.25% | -1.6% | 9% | 11% | 16 |
| Wkly_upswing | 2866 | +0.2% | -1.5% | -0.25% | -1.9% | 10% | 16% | 13 |
| **All** | 37987 | +0.2% | -1.3% | -0.25% | -1.7% | 9% | 11% | 16 |

Signals are bought 5.5 times on average under this rule, so the small loss per stop (-1.7%) repeats: 5 stops in a row is about -8.0%.


## Buying the pullback: rules compared

Same signals, every market cap, no target, no time limit, new buys for 3 months after the signal, 0.25% costs per round trip, open positions valued at the latest close.

- **breakout**: Buy above the trigger, sell on a close below it, buy again above it
- **breakout5**: Same, stop on a close 5% below the trigger
- **retest**: Buy the dip back to the trigger (within 2%) that closes above it; stop 5% below
- **dip5**: Buy a 5% dip from the post-breakout high; stop 5% below the trigger
- **ema20**: Buy the dip to the 20-day average that closes above it; stop 5% below the trigger

| Rule | Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | Worst 10% avg | Avg days invested |
|---|---|---|---|---|---|---|---|---|
| breakout | 63_30_daily | 1751 | 5.3 | 24% | +27.3% | -5.4% | -22.7% | 258 |
| breakout | Bullish_Scanner | 4948 | 5.5 | 22% | +22.8% | -5.8% | -23.0% | 251 |
| breakout | Wkly_upswing | 560 | 5.3 | 19% | +35.6% | -7.2% | -24.5% | 230 |
| breakout | **All** | 7259 | 5.5 | 22% | +24.9% | -5.8% | -23.1% | 251 |
| breakout5 | 63_30_daily | 1751 | 1.5 | 28% | +32.4% | -6.4% | -23.4% | 309 |
| breakout5 | Bullish_Scanner | 4948 | 1.5 | 28% | +30.1% | -6.5% | -23.5% | 313 |
| breakout5 | Wkly_upswing | 560 | 1.6 | 22% | +42.0% | -7.6% | -25.1% | 273 |
| breakout5 | **All** | 7259 | 1.5 | 28% | +31.6% | -6.5% | -23.6% | 309 |
| retest | 63_30_daily | 1537 | 1.3 | 30% | +33.8% | -7.5% | -24.5% | 325 |
| retest | Bullish_Scanner | 4468 | 1.3 | 28% | +28.7% | -7.9% | -24.7% | 317 |
| retest | Wkly_upswing | 477 | 1.3 | 22% | +41.2% | -8.6% | -26.0% | 279 |
| retest | **All** | 6482 | 1.3 | 28% | +30.9% | -7.8% | -24.8% | 316 |
| dip5 | 63_30_daily | 1458 | 1.7 | 28% | +30.1% | -6.7% | -26.8% | 308 |
| dip5 | Bullish_Scanner | 4300 | 1.8 | 28% | +26.9% | -6.8% | -27.6% | 311 |
| dip5 | Wkly_upswing | 470 | 1.8 | 24% | +47.2% | -7.4% | -25.2% | 303 |
| dip5 | **All** | 6228 | 1.8 | 28% | +29.2% | -6.8% | -27.3% | 310 |
| ema20 | 63_30_daily | 1663 | 1.5 | 29% | +31.3% | -6.6% | -25.2% | 306 |
| ema20 | Bullish_Scanner | 4730 | 1.6 | 28% | +28.3% | -7.5% | -25.5% | 314 |
| ema20 | Wkly_upswing | 498 | 1.6 | 24% | +44.7% | -7.5% | -26.8% | 285 |
| ema20 | **All** | 6891 | 1.6 | 28% | +30.2% | -7.3% | -25.6% | 310 |

| Rule | Cap | Signals bought | Profitable | Avg return | Median |
|---|---|---|---|---|---|
| breakout | Largecap | 3323 | 27% | +39.6% | -4.5% |
| breakout | Midcap | 1963 | 23% | +23.9% | -6.2% |
| breakout | Smallcap | 1964 | 13% | +1.2% | -8.0% |
| breakout5 | Largecap | 3323 | 36% | +51.2% | -5.7% |
| breakout5 | Midcap | 1963 | 27% | +28.1% | -6.7% |
| breakout5 | Smallcap | 1964 | 15% | +1.9% | -9.0% |
| dip5 | Largecap | 2771 | 36% | +48.9% | -4.6% |
| dip5 | Midcap | 1710 | 28% | +27.4% | -7.1% |
| dip5 | Smallcap | 1743 | 14% | -0.3% | -10.4% |
| ema20 | Largecap | 3164 | 36% | +50.3% | -5.8% |
| ema20 | Midcap | 1882 | 28% | +25.8% | -7.3% |
| ema20 | Smallcap | 1839 | 14% | +0.3% | -10.0% |
| retest | Largecap | 3055 | 37% | +51.9% | -6.6% |
| retest | Midcap | 1733 | 27% | +24.4% | -7.9% |
| retest | Smallcap | 1689 | 14% | -0.5% | -10.6% |

## If I had bought on the alerts

Every buy alert from 2021-01-11 (when all three scanners have backtest data) to 2026-10-27, starting with ₹10L: each buy is 1/10 of the portfolio's value at the time (profits reinvested), at most 10 open, first come first served, one position per stock, after costs.

| Scanner | Trades | Win rate | Avg | Avg win / loss | Avg days |
|---|---|---|---|---|---|
| 63_30_daily | 1218 | 42% | +5.22% | +20.8% / -6.0% | 38 |
| Bullish_Scanner | 3607 | 41% | +3.82% | +18.7% / -6.3% | 37 |
| Wkly_upswing | 102 | 43% | +2.18% | +13.0% / -6.0% | 35 |
| All | 4927 | 41% | +4.13% | +19.1% / -6.2% | 37 |

| | Alerts portfolio | Nifty 500 |
|---|---|---|
| ₹10L became | ₹31.3L | ₹18.1L |
| Yearly growth (CAGR) | 21.8% | 10.8% |
| Worst fall from a peak | -17.9% | -18.8% |
| Trades taken / skipped (no free slot) | 390 / 4537 | |
| Win rate of trades taken | 38% | |

| Year | Alerts portfolio | Nifty 500 |
|---|---|---|
| 2021 | +32.6% | +24.9% |
| 2022 | +2.4% | +3.0% |
| 2023 | +32.8% | +25.8% |
| 2024 | +26.0% | +15.2% |
| 2025 | +22.6% | +6.7% |
| 2026 | +12.3% | -9.0% |

Open positions are counted at cost until sold. The current year is year-to-date.

### Exit rules compared (same dip buys)

Every rule keeps the starting stop (12%, 15% for Wkly_upswing); the riding rules sell after a year at the latest. Only buys that every rule has closed are counted.

| Exit | Trades | Win rate | Avg | Avg win / loss | Avg days | ₹10L became | Per year | Worst fall |
|---|---|---|---|---|---|---|---|---|
| +8% target, 12% stop, 8 weeks (old rule) | 4830 | 69% | +1.95% | +7.6% / -10.4% | 17 | ₹14.1L | 6.1% | -28.8% |
| 10% trailing stop | 4830 | 43% | +3.41% | +16.7% / -6.7% | 36 | ₹19.1L | 11.9% | -29.7% |
| 15% trailing stop | 4830 | 43% | +6.96% | +28.1% / -9.2% | 68 | ₹13.1L | 4.7% | -20.6% |
| close below 20-day average | 4830 | 39% | +1.36% | +9.3% / -3.7% | 12 | ₹20.2L | 13.0% | -19.7% |
| close below 50-day average (now) | 4830 | 41% | +4.23% | +19.1% / -6.2% | 36 | ₹32.8L | 22.8% | -17.6% |
| half at +8%, rest on close below 20-day average | 4830 | 44% | +1.03% | +7.0% / -3.8% | 12 | ₹18.7L | 11.5% | -17.4% |
| after +8%: stop at cost, sell on close below 20-day average | 4830 | 51% | +2.93% | +12.2% / -6.8% | 27 | ₹15.5L | 7.9% | -31.0% |
| after +8%: stop at cost, sell on close below 50-day average | 4830 | 37% | +4.02% | +19.7% / -5.4% | 37 | ₹16.6L | 9.2% | -28.7% |
| no pullback: buy at the breakout, sell on close below 50-day average | 4830 | 46% | +5.86% | +21.1% / -7.0% | 44 | ₹22.5L | 15.0% | -10.4% |
| no pullback, every breakout (incl. stocks that never dipped) | 5744 | 46% | +5.60% | +20.6% / -7.3% | 43 | ₹19.2L | 11.9% | -13.7% |

| Exit | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| +8% target, 12% stop, 8 weeks (old rule) | 71% · +2.28% | 68% · +1.83% | 72% · +2.14% |
| 10% trailing stop | 44% · +4.04% | 43% · +3.14% | 42% · +5.07% |
| 15% trailing stop | 43% · +7.55% | 43% · +6.77% | 42% · +6.61% |
| close below 20-day average | 38% · +1.46% | 39% · +1.32% | 49% · +1.42% |
| close below 50-day average (now) | 42% · +5.30% | 41% · +3.91% | 44% · +2.34% |
| half at +8%, rest on close below 20-day average | 43% · +1.09% | 44% · +1.01% | 56% · +1.06% |
| after +8%: stop at cost, sell on close below 20-day average | 52% · +3.28% | 51% · +2.82% | 56% · +2.53% |
| after +8%: stop at cost, sell on close below 50-day average | 39% · +4.81% | 37% · +3.81% | 33% · +1.62% |
| no pullback: buy at the breakout, sell on close below 50-day average | 46% · +6.37% | 46% · +5.72% | 44% · +4.68% |
| no pullback, every breakout (incl. stocks that never dipped) | 47% · +6.17% | 46% · +5.44% | 44% · +4.79% |

## Buy-the-dip rule (the live alert rule)

After the breakout, buy at the next open once a close is 3% below the highest close since the breakout (5% for Wkly_upswing), within 20 sessions and no more than 5% below the trigger. Sell at the next open after a close below the 50-day average, a 12% stop (Wkly_upswing 15%), or after 250 sessions. Wkly_upswing only when daily ATR(14) is under 4% of the close. Filter: 63_30_daily only within 10% of the 52-week high. 0.25% costs.

| Group | Trades | Win rate | Avg | Avg win / loss | Average / stop / time | Avg days | ₹ on ₹1L a trade |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 1219 | 42% | +5.21% | +20.7% / -6.0% | 92% / 8% / 0% | 38 | 6,356,280 |
| Bullish_Scanner | 3607 | 41% | +3.82% | +18.7% / -6.3% | 89% / 11% / 0% | 37 | 13,776,180 |
| Wkly_upswing | 135 | 40% | +2.62% | +15.0% / -5.6% | 95% / 5% / 0% | 34 | 353,700 |
| Largecap | 2257 | 43% | +3.54% | +15.8% / -5.6% | 95% / 5% / 0% | 37 | 7,999,550 |
| Midcap | 1367 | 41% | +5.35% | +22.3% / -6.4% | 89% / 11% / 0% | 39 | 7,310,230 |
| Smallcap | 1336 | 38% | +3.88% | +21.9% / -7.0% | 84% / 16% / 0% | 36 | 5,188,630 |
| **All** | 4961 | 41% | +4.13% | +19.1% / -6.2% | 90% / 10% / 0% | 37 | 20,486,160 |

## Reading this

- Average vs median: a high average with a low median means a few big winners carry the result; most buys did worse than the average.
- Compare with the Nifty 500 column: a scanner adds value only when its picks beat the index.
- Stocks Yahoo no longer lists (delisted, renamed) are missing, which flatters long-term results a little (survivorship bias).
- No costs, taxes or stop-loss are included; real results will be lower, and holding with no stop means sitting through every drawdown shown in 'Avg best / worst'.
