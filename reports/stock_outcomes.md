# If I had bought every scanner stock

Generated 2026-10-22 18:50 UTC by `scripts/stock_outcomes.py` from `data/backtest/*.csv` plus the bot's live triggers.

**Rule:** buy when price crosses the signal candle's high within 3 sessions (5 for `Wkly_upswing`), filled at the trigger or at the open on a gap-up; then hold. No stop, no target, no costs. **Short** = 2 weeks / 1 month, **Medium** = 3 / 6 months, **Long** = 1 / 2 years. **Beat Nifty 500** = share of buys that did better than the index over the same days. Recent buys only count for horizons that have fully passed.

Per-trade data: `data/model/stock_outcomes.csv`; per-stock: `data/model/stock_summary.csv`.

## All scanners at a glance

| Scanner | Signals | Bought | 1 month avg | 6 months avg | 1 year avg | 2 years avg | 1 year vs Nifty 500 |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 1832 | 1439 | +3.3% | +14.6% | +24.1% | +46.7% | +9.7% |
| Bullish_Scanner | 5084 | 4204 | +3.7% | +15.4% | +27.4% | +48.3% | +13.0% |
| Wkly_upswing | 1119 | 750 | +2.8% | +16.0% | +30.4% | +52.6% | +19.0% |

## 63_30_daily

1832 signals (31 Dec 2020 to 21 Oct 2026): 1439 bought, 389 never crossed the trigger, 3 without Yahoo prices, 1 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 1437 | 52% | +1.6% | +0.2% | +5.4% / -3.7% | +0.7% | 47% | +0.9% |
| Short | 1 month | 1435 | 56% | +3.3% | +1.8% | +9.1% / -5.5% | +1.5% | 49% | +1.8% |
| Medium | 3 months | 1416 | 62% | +8.2% | +4.7% | +19.7% / -9.2% | +4.4% | 51% | +3.8% |
| Medium | 6 months | 1366 | 64% | +14.6% | +7.9% | +31.6% / -12.4% | +7.5% | 48% | +7.1% |
| Long | 1 year | 1266 | 62% | +24.1% | +11.1% | +50.6% / -16.3% | +14.5% | 49% | +9.7% |
| Long | 2 years | 1113 | 67% | +46.7% | +28.5% | +89.4% / -20.9% | +28.2% | 50% | +18.5% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Largecap | 655 / 56% / +1.9% / +0.4% | 630 / 64% / +12.2% / +6.1% | 568 / 68% / +25.0% / +11.4% |
| Midcap | 410 / 59% / +4.8% / +3.6% | 384 / 70% / +22.6% / +14.8% | 353 / 64% / +34.5% / +20.1% |
| Smallcap | 370 / 54% / +4.2% / +2.3% | 352 / 57% / +10.3% / +0.6% | 345 / 50% / +12.1% / -4.0% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2021 | 221 / 52% / +4.1% / +1.9% | 221 / 52% / +10.0% / +1.7% | 221 / 47% / +9.5% / +4.5% |
| 2022 | 168 / 45% / -1.4% / +1.1% | 168 / 43% / +1.5% / +3.5% | 168 / 63% / +24.3% / +17.4% |
| 2023 | 429 / 66% / +5.2% / +1.5% | 429 / 86% / +30.6% / +14.3% | 429 / 83% / +52.8% / +18.9% |
| 2024 | 333 / 54% / +3.3% / +2.2% | 333 / 59% / +8.1% / +3.3% | 333 / 50% / +4.2% / +0.1% |
| 2025 | 170 / 57% / +2.5% / +1.1% | 170 / 51% / +2.9% / +1.8% | 115 / 50% / +2.7% / +1.6% |
| 2026 | 114 / 52% / +2.4% / +3.6% | 45 / 69% / +26.6% / +26.6% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Auto | 116 / 62% / +6.6% / +4.7% | 115 / 78% / +26.5% / +15.7% | 115 / 76% / +38.1% / +19.4% |
| Bank | 98 / 61% / +1.8% / -0.0% | 91 / 73% / +11.2% / +5.2% | 82 / 73% / +19.6% / +1.4% |
| Building Materials | 77 / 52% / +4.8% / +1.9% | 76 / 58% / +7.9% / -3.3% | 71 / 52% / +11.4% / -9.7% |
| Chemicals | 83 / 40% / +0.6% / +0.1% | 83 / 45% / +4.0% / -2.7% | 74 / 47% / +15.8% / +7.9% |
| Consumer Discretionary | 68 / 63% / +3.6% / +2.0% | 66 / 59% / +14.6% / +9.0% | 66 / 67% / +14.3% / +1.0% |
| Energy | 57 / 56% / +0.8% / -0.1% | 56 / 39% / +0.9% / -2.8% | 49 / 41% / +6.9% / +0.3% |
| FMCG | 94 / 57% / +2.7% / +0.7% | 90 / 64% / +18.4% / +7.5% | 84 / 56% / +22.9% / +6.2% |
| Financials | 189 / 49% / +1.4% / +0.5% | 174 / 56% / +7.9% / +2.4% | 155 / 60% / +14.7% / +3.7% |
| Healthcare | 125 / 68% / +4.3% / +1.7% | 120 / 79% / +17.6% / +10.6% | 104 / 68% / +22.2% / +8.4% |
| I.T | 66 / 58% / +3.4% / +1.9% | 61 / 69% / +7.1% / +2.1% | 59 / 46% / +2.2% / -5.0% |
| Industrials | 74 / 65% / +4.1% / +2.2% | 67 / 75% / +25.8% / +16.8% | 59 / 59% / +29.0% / +12.1% |
| Metals & Mining | 78 / 55% / +1.5% / +0.3% | 69 / 70% / +27.8% / +19.0% | 63 / 75% / +37.1% / +19.6% |
| Miscellaneous | 29 / 52% / +0.8% / -0.3% | 27 / 67% / +5.0% / -3.3% | 27 / 52% / +25.2% / +1.7% |
| Realty | 90 / 59% / +4.2% / +3.2% | 85 / 67% / +19.3% / +11.1% | 82 / 66% / +53.4% / +35.6% |
| Services | 37 / 57% / +8.8% / +7.9% | 37 / 70% / +19.9% / +13.3% | 37 / 84% / +38.0% / +28.3% |
| Telecom-Service | 21 / 76% / +4.8% / +2.6% | 21 / 86% / +7.4% / -3.3% | 20 / 45% / +1.4% / -8.6% |
| Textiles | 29 / 52% / +4.9% / +3.4% | 26 / 38% / -3.8% / -11.8% | 26 / 58% / +5.6% / -10.3% |

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| IRCON | Realty | Midcap | 4 | +18.3% | +93.4% | +214.4% | 75% |
| GOKEX | Readymade Garments/Apparels | Midcap | 3 | +23.2% | +115.4% | +165.3% | 100% |
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
| STAR | Healthcare | Midcap | 8 | +10.3% | +4.5% | -65.0% | 0% |
| DELTACORP | Miscellaneous | Smallcap | 4 | +4.1% | -41.1% | -50.2% | 0% |
| IONEXCHANG | Realty | Midcap | 3 | -12.9% | -25.7% | -48.7% | 0% |
| MUNJALSHOW | Auto | Smallcap | 3 | -11.4% | -27.3% | -42.1% | 0% |
| GUJENERGY | Energy | Largecap | 3 | -9.7% | -36.7% | -36.8% | 0% |
| HDFCAMC | Financials | Largecap | 3 | -6.7% | -28.4% | -36.5% | 0% |
| CHEMCON | Chemicals | Smallcap | 3 | -11.2% | -12.8% | -29.9% | 0% |
| HINDPETRO | Energy | Largecap | 9 | +5.6% | -13.1% | -29.0% | 0% |
| STARHEALTH | Financials | Largecap | 7 | +0.3% | -16.9% | -28.9% | 0% |

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

5084 signals (31 Dec 2020 to 22 Oct 2026): 4204 bought, 857 never crossed the trigger, 20 without Yahoo prices, 3 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 4196 | 55% | +2.1% | +0.8% | +6.0% / -3.4% | +0.7% | 50% | +1.4% |
| Short | 1 month | 4184 | 59% | +3.7% | +2.0% | +9.6% / -5.1% | +1.6% | 51% | +2.1% |
| Medium | 3 months | 4112 | 63% | +8.7% | +5.7% | +19.8% / -8.5% | +4.3% | 53% | +4.4% |
| Medium | 6 months | 3972 | 65% | +15.4% | +9.2% | +31.8% / -11.4% | +8.0% | 52% | +7.4% |
| Long | 1 year | 3735 | 64% | +27.4% | +13.5% | +53.7% / -15.4% | +14.4% | 52% | +13.0% |
| Long | 2 years | 3400 | 69% | +48.3% | +26.9% | +90.1% / -19.6% | +26.6% | 51% | +21.7% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Largecap | 2019 / 59% / +2.7% / +1.2% | 1943 / 68% / +14.6% / +7.3% | 1769 / 71% / +29.4% / +15.2% |
| Midcap | 1133 / 60% / +4.7% / +3.1% | 1061 / 66% / +19.1% / +10.8% | 1012 / 62% / +32.6% / +18.7% |
| Smallcap | 1032 / 57% / +4.5% / +2.7% | 968 / 58% / +13.0% / +3.7% | 954 / 53% / +18.4% / +3.1% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2021 | 854 / 56% / +4.2% / +2.0% | 854 / 59% / +13.2% / +5.8% | 854 / 54% / +15.9% / +10.3% |
| 2022 | 403 / 48% / +1.4% / +3.3% | 403 / 51% / +4.4% / +6.2% | 403 / 69% / +25.7% / +18.0% |
| 2023 | 1235 / 68% / +5.5% / +2.2% | 1235 / 85% / +30.1% / +12.9% | 1235 / 84% / +58.6% / +24.8% |
| 2024 | 1007 / 55% / +2.8% / +1.3% | 1007 / 59% / +8.2% / +3.4% | 1007 / 50% / +4.4% / +0.3% |
| 2025 | 373 / 57% / +2.6% / +1.9% | 373 / 48% / +2.8% / +2.1% | 236 / 47% / +7.7% / +6.7% |
| 2026 | 312 / 54% / +1.9% / +3.3% | 100 / 49% / +15.6% / +15.9% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Aerospace & Defence | 75 / 63% / +8.1% / +6.9% | 74 / 92% / +47.4% / +39.2% | 73 / 93% / +78.1% / +62.8% |
| Auto | 310 / 64% / +3.7% / +1.5% | 291 / 69% / +18.4% / +8.5% | 281 / 78% / +30.2% / +12.9% |
| Bank | 271 / 53% / +0.6% / +0.1% | 248 / 63% / +9.4% / +4.7% | 188 / 68% / +16.5% / +3.4% |
| Building Materials | 212 / 50% / +2.9% / +1.2% | 204 / 46% / +2.8% / -5.4% | 199 / 40% / +4.7% / -8.6% |
| Castings, Forgings & Fasteners | 32 / 66% / +6.9% / +4.9% | 30 / 43% / -0.5% / -9.1% | 28 / 43% / +2.2% / -15.1% |
| Chemicals | 215 / 51% / +3.1% / +1.8% | 210 / 60% / +13.5% / +5.5% | 198 / 58% / +17.6% / +6.8% |
| Consumer Discretionary | 159 / 55% / +4.3% / +3.5% | 151 / 61% / +14.0% / +9.1% | 149 / 57% / +17.9% / +6.4% |
| Energy | 175 / 61% / +3.7% / +2.2% | 173 / 53% / +9.5% / +2.9% | 149 / 51% / +21.0% / +8.0% |
| FMCG | 332 / 59% / +3.1% / +1.1% | 310 / 67% / +15.0% / +4.4% | 303 / 62% / +21.4% / +6.3% |
| Financials | 437 / 53% / +1.9% / +0.5% | 420 / 58% / +11.2% / +3.6% | 383 / 57% / +28.3% / +14.5% |
| Healthcare | 458 / 64% / +4.9% / +2.6% | 416 / 71% / +13.1% / +4.1% | 410 / 68% / +24.3% / +8.9% |
| I.T | 218 / 60% / +3.1% / +1.4% | 209 / 61% / +11.4% / +5.2% | 204 / 48% / +10.8% / +0.3% |
| Industrials | 325 / 64% / +4.7% / +3.0% | 310 / 76% / +23.5% / +15.8% | 294 / 80% / +55.0% / +38.8% |
| Media | 34 / 38% / -1.6% / -2.1% | 34 / 24% / -1.9% / -8.0% | 34 / 21% / -10.3% / -19.0% |
| Metals & Mining | 169 / 57% / +3.4% / +3.1% | 162 / 61% / +15.7% / +9.4% | 136 / 71% / +27.8% / +13.9% |
| Miscellaneous | 93 / 58% / +3.4% / +1.8% | 86 / 58% / +16.6% / +8.3% | 79 / 58% / +25.3% / +9.5% |
| Plastic products | 22 / 68% / +9.0% / +8.2% | 22 / 77% / +18.8% / +7.3% | 22 / 68% / +27.0% / +4.7% |
| Power & Utilities | 126 / 57% / +3.8% / +2.9% | 119 / 76% / +27.7% / +19.8% | 113 / 79% / +57.5% / +40.4% |
| Realty | 208 / 60% / +3.9% / +2.0% | 195 / 80% / +26.6% / +15.5% | 193 / 72% / +41.9% / +24.7% |
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
| GOKEX | Readymade Garments/Apparels | Midcap | 5 | +23.9% | +97.3% | +159.9% | 80% |
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

1119 signals (14 Aug 2017 to 14 Oct 2026): 750 bought, 365 never crossed the trigger, 3 without Yahoo prices, 1 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 747 | 47% | +1.1% | -0.7% | +6.9% / -5.7% | +0.7% | 42% | +0.3% |
| Short | 1 month | 742 | 53% | +2.8% | +0.9% | +11.6% / -8.2% | +1.2% | 46% | +1.6% |
| Medium | 3 months | 721 | 54% | +9.0% | +1.9% | +25.6% / -13.0% | +3.4% | 48% | +5.7% |
| Medium | 6 months | 693 | 52% | +16.0% | +1.4% | +42.2% / -17.3% | +5.7% | 46% | +10.3% |
| Long | 1 year | 663 | 56% | +30.4% | +7.2% | +71.0% / -23.6% | +11.4% | 47% | +19.0% |
| Long | 2 years | 616 | 60% | +52.6% | +15.7% | +120.6% / -29.5% | +26.3% | 43% | +26.3% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Unknown | 0 / – / – / – | 0 / – / – / – | 0 / – / – / – |
| Largecap | 212 / 57% / +2.6% / +1.3% | 195 / 59% / +14.0% / +9.1% | 189 / 66% / +26.3% / +14.9% |
| Midcap | 180 / 54% / +3.1% / +2.0% | 173 / 51% / +16.0% / +11.8% | 158 / 55% / +48.7% / +38.6% |
| Smallcap | 350 / 50% / +2.7% / +1.5% | 325 / 48% / +17.3% / +10.3% | 316 / 51% / +23.6% / +11.7% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2017 | 44 / 64% / +8.1% / +6.5% | 44 / 57% / +12.5% / +9.4% | 44 / 43% / +21.9% / +19.4% |
| 2018 | 46 / 30% / -4.2% / -2.5% | 46 / 30% / -10.3% / -7.8% | 46 / 30% / -10.6% / -9.5% |
| 2019 | 39 / 41% / -2.9% / -4.1% | 39 / 18% / -16.3% / -5.3% | 39 / 36% / -6.7% / -1.3% |
| 2020 | 45 / 60% / +7.2% / +4.7% | 45 / 71% / +37.5% / +17.5% | 45 / 91% / +122.8% / +76.1% |
| 2021 | 101 / 56% / +6.0% / +3.7% | 101 / 60% / +52.2% / +42.6% | 100 / 57% / +38.3% / +31.4% |
| 2022 | 94 / 45% / +1.6% / +2.7% | 94 / 44% / +0.7% / +1.4% | 94 / 64% / +24.2% / +16.7% |
| 2023 | 112 / 63% / +4.9% / +1.1% | 112 / 73% / +32.1% / +13.9% | 112 / 87% / +75.7% / +43.6% |
| 2024 | 152 / 58% / +2.5% / +1.2% | 152 / 51% / +6.7% / +3.1% | 152 / 38% / -0.3% / -4.2% |
| 2025 | 43 / 51% / +0.2% / -0.9% | 43 / 28% / -8.3% / -8.6% | 31 / 39% / -4.7% / -5.2% |
| 2026 | 66 / 41% / -0.4% / +0.5% | 17 / 59% / +22.2% / +24.4% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Auto | 36 / 72% / +7.4% / +5.3% | 34 / 65% / +45.3% / +39.5% | 31 / 68% / +67.1% / +55.6% |
| Bank | 25 / 32% / +0.3% / -0.9% | 23 / 61% / +4.5% / -0.2% | 20 / 45% / -2.2% / -8.3% |
| Building Materials | 39 / 41% / -0.4% / -1.7% | 38 / 42% / -3.8% / -10.4% | 37 / 43% / -6.2% / -18.5% |
| Chemicals | 57 / 46% / +1.5% / +0.3% | 53 / 47% / +2.8% / -1.2% | 52 / 62% / +27.2% / +16.8% |
| Consumer Discretionary | 42 / 64% / +6.3% / +4.5% | 39 / 51% / +11.2% / +8.6% | 39 / 64% / +37.6% / +26.3% |
| Energy | 22 / 64% / +1.7% / +0.7% | 21 / 38% / +3.4% / +0.3% | 20 / 40% / +6.3% / -2.0% |
| FMCG | 44 / 48% / -0.6% / -2.2% | 42 / 43% / +1.6% / -3.5% | 41 / 49% / +9.6% / -1.3% |
| Financials | 55 / 60% / +2.8% / +1.5% | 52 / 54% / +19.4% / +14.6% | 51 / 61% / +28.8% / +18.8% |
| Healthcare | 57 / 65% / +4.7% / +3.3% | 55 / 62% / +19.9% / +11.2% | 53 / 70% / +44.0% / +27.0% |
| I.T | 54 / 52% / +1.1% / +0.2% | 49 / 43% / +3.0% / -1.8% | 48 / 50% / +12.6% / +4.7% |
| Industrials | 55 / 55% / +3.7% / +3.0% | 52 / 58% / +25.7% / +20.1% | 49 / 61% / +71.0% / +56.0% |
| Metals & Mining | 40 / 38% / -2.2% / -2.8% | 34 / 56% / +16.0% / +8.6% | 31 / 65% / +30.4% / +19.4% |
| Miscellaneous | 24 / 50% / -0.7% / -2.4% | 24 / 46% / +18.4% / +10.1% | 23 / 43% / +65.1% / +53.3% |
| Realty | 56 / 48% / +1.6% / +0.3% | 52 / 58% / +39.5% / +33.3% | 48 / 54% / +18.7% / +10.2% |
| Services | 28 / 54% / +3.1% / +1.8% | 25 / 52% / +4.0% / -4.4% | 24 / 54% / +16.1% / +0.8% |

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| LAURUSLABS | Healthcare | Largecap | 4 | +9.0% | +132.5% | +297.2% | 75% |
| HUBTOWN | Realty | Smallcap | 3 | +8.6% | +47.6% | +119.6% | 67% |
| MSPL | Metals & Mining | Smallcap | 3 | -2.4% | +28.4% | +110.9% | 67% |
| MINDTECK | I.T | Smallcap | 3 | -0.9% | +11.8% | +106.8% | 33% |
| MCX | Financials | Largecap | 5 | +10.0% | +37.8% | +92.4% | 100% |
| PRICOLLTD | Auto | Midcap | 4 | +7.5% | +24.4% | +79.5% | 50% |
| COFORGE | I.T | Largecap | 3 | +1.8% | +8.1% | +70.3% | 100% |
| TI | FMCG | Midcap | 3 | +2.7% | +21.3% | +61.5% | 67% |
| PRECWIRE | Metals & Mining | Midcap | 3 | +6.6% | +43.5% | +51.5% | 67% |
| JUBLFOOD | Consumer Discretionary | Largecap | 3 | +8.5% | +19.5% | +42.9% | 67% |

**Worst repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| SEJALLTD | Building Materials | Smallcap | 3 | -19.9% | -14.7% | -63.1% | 0% |
| CSBBANK | Bank | Midcap | 3 | -3.0% | -5.8% | -17.9% | 0% |
| ASALCBR | FMCG | Smallcap | 3 | -4.6% | -5.6% | -15.1% | 33% |
| BALRAMCHIN | FMCG | Midcap | 3 | -6.7% | -22.9% | -12.2% | 0% |
| OBEROIRLTY | Realty | Largecap | 4 | -6.4% | -7.6% | -10.2% | 25% |
| PENIND | Metals & Mining | Smallcap | 3 | -15.9% | -4.4% | -9.2% | 33% |
| PETRONET | Energy | Largecap | 5 | +1.7% | +0.2% | -7.3% | 20% |
| ZYDUSWELL | FMCG | Midcap | 3 | +2.4% | +3.3% | -6.0% | 33% |
| IFBIND | Consumer Discretionary | Smallcap | 3 | +18.7% | +22.7% | -2.0% | 67% |
| HCLTECH | I.T | Largecap | 5 | -7.3% | -2.1% | -1.3% | 60% |

**Biggest single winners after 1 year**

| Stock | Bought | Price | Return | Nifty 500 |
|---|---|---|---|---|
| IBULLSLTD | 2017-09-18 | 41.33 | +1001.5% | +4.0% |
| TIPSMUSIC | 2020-06-30 | 13.09 | +949.7% | +58.5% |
| TARIL | 2023-05-29 | 40.47 | +829.0% | +38.6% |
| ASAL | 2021-06-14 | 49.95 | +677.2% | -4.2% |
| SKYGOLD | 2023-10-16 | 56.40 | +518.3% | +29.4% |
| LAURUSLABS | 2020-06-22 | 108.80 | +465.1% | +59.7% |
| MBAPL | 2021-06-14 | 6.10 | +406.7% | -4.2% |
| THOMASCOTT | 2023-06-12 | 59.60 | +390.3% | +40.4% |
| TTML | 2021-06-14 | 25.05 | +382.2% | -4.2% |
| MINDTECK | 2020-12-24 | 36.56 | +367.1% | +33.6% |

## Trigger-price stop with re-entry

Buy when price crosses above the trigger (the signal candle's high). No target and no time limit. Sell when price falls below the trigger; buy again each time it climbs back above it, for 63 sessions (3 months) after the signal. A position bought inside those 3 months is held until the stop, however long that takes; open positions are valued at the latest close. Every buy/sell pays 0.25% costs. Two versions of the stop:

- **close**: sell at the next open after a daily close below the trigger
- **intraday**: sell the moment price trades below the trigger (at the trigger, or the open on a gap-down)

Return = all the buys and sells of one signal compounded. Nifty 500 = from the first buy to the last sell (or today).

### Stop on a close below the trigger

| Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | Worst 10% avg | Avg days invested | Still holding | Nifty 500 avg | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 1751 | 5.3 | 24% | +28.3% | -5.4% | -22.6% | 258 | 435 | +10.6% | +17.7% |
| Bullish_Scanner | 4948 | 5.5 | 22% | +23.0% | -5.7% | -23.0% | 250 | 1135 | +9.9% | +13.1% |
| Wkly_upswing | 1010 | 5.3 | 18% | +39.9% | -8.0% | -25.4% | 228 | 173 | +11.4% | +28.5% |
| **All** | 7709 | 5.4 | 22% | +26.4% | -5.9% | -23.3% | 249 | 1743 | +10.3% | +16.2% |

| Scanner | Cap | Signals | Profitable | Avg return | Median | Avg days invested |
|---|---|---|---|---|---|---|
| 63_30_daily | Largecap | 777 | 28% | +43.8% | -4.5% | 272 |
| 63_30_daily | Midcap | 501 | 28% | +30.0% | -5.3% | 295 |
| 63_30_daily | Smallcap | 473 | 13% | +1.0% | -7.9% | 194 |
| Bullish_Scanner | Largecap | 2364 | 28% | +34.6% | -4.4% | 277 |
| Bullish_Scanner | Midcap | 1357 | 22% | +23.0% | -6.4% | 251 |
| Bullish_Scanner | Smallcap | 1227 | 13% | +0.8% | -7.7% | 196 |
| Wkly_upswing | Largecap | 272 | 25% | +53.2% | -5.7% | 301 |
| Wkly_upswing | Midcap | 241 | 20% | +80.4% | -7.5% | 258 |
| Wkly_upswing | Smallcap | 495 | 13% | +13.1% | -9.7% | 175 |

| Buys per signal | Signals | Profitable | Avg return |
|---|---|---|---|
| 1 | 1195 | 38% | +52.4% |
| 2 | 1023 | 29% | +36.2% |
| 3 | 828 | 23% | +36.6% |
| 4 | 786 | 19% | +32.3% |
| 5 | 666 | 21% | +25.8% |
| 6+ | 3211 | 15% | +9.7% |

### Stop on any trade below the trigger

| Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | Worst 10% avg | Avg days invested | Still holding | Nifty 500 avg | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 1751 | 6.6 | 21% | +25.3% | -5.8% | -23.7% | 236 | 387 | +10.0% | +15.4% |
| Bullish_Scanner | 4948 | 6.9 | 19% | +19.3% | -6.2% | -23.8% | 224 | 998 | +9.3% | +10.0% |
| Wkly_upswing | 1010 | 6.5 | 15% | +30.1% | -7.5% | -28.7% | 204 | 153 | +10.7% | +19.4% |
| **All** | 7709 | 6.8 | 19% | +22.1% | -6.2% | -24.5% | 224 | 1538 | +9.7% | +12.5% |

| Scanner | Cap | Signals | Profitable | Avg return | Median | Avg days invested |
|---|---|---|---|---|---|---|
| 63_30_daily | Largecap | 777 | 24% | +40.0% | -5.1% | 245 |
| 63_30_daily | Midcap | 501 | 25% | +26.7% | -5.5% | 279 |
| 63_30_daily | Smallcap | 473 | 11% | -0.2% | -7.6% | 175 |
| Bullish_Scanner | Largecap | 2364 | 24% | +30.0% | -5.0% | 247 |
| Bullish_Scanner | Midcap | 1357 | 19% | +18.7% | -6.4% | 229 |
| Bullish_Scanner | Smallcap | 1227 | 11% | -0.5% | -8.3% | 176 |
| Wkly_upswing | Largecap | 272 | 21% | +48.5% | -5.3% | 268 |
| Wkly_upswing | Midcap | 241 | 18% | +64.2% | -8.1% | 231 |
| Wkly_upswing | Smallcap | 495 | 9% | +3.6% | -8.9% | 157 |

| Buys per signal | Signals | Profitable | Avg return |
|---|---|---|---|
| 1 | 797 | 27% | +45.9% |
| 2 | 861 | 30% | +42.2% |
| 3 | 728 | 24% | +57.8% |
| 4 | 674 | 23% | +25.7% |
| 5 | 613 | 19% | +12.5% |
| 6+ | 4036 | 13% | +7.6% |


## The pullback after the breakout

For every signal that crossed its trigger, the 20 sessions after the first crossing. **Back at the trigger** = the low came within 2% of the trigger (or below).

| Scanner | Breakouts | Back at the trigger | Median days to get there | Closed below the trigger | Closed 5%+ below | Median dip from the high | 3 months later: retested / not |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 1745 | 96% | 1 | 82% | 42% | -11.6% | +7.7% / +27.7% |
| Bullish_Scanner | 4926 | 96% | 1 | 80% | 41% | -11.4% | +7.7% / +30.0% |
| Wkly_upswing | 999 | 93% | 1 | 82% | 55% | -15.1% | +5.9% / +46.0% |
| **All** | 7670 | 96% | 1 | 81% | 43% | -11.8% | +7.5% / +32.6% |

## Why a stop at the buy price still loses

Every round trip of the *breakout* rule (buy above the trigger, sell after a close below it). Entry and exit are shown against the trigger price.

| Scanner | Stopped round trips | Avg bought above trigger | Avg sold below trigger | Costs | Avg loss per stop | Bought on a gap-up | Sold 3%+ below trigger | Avg days held |
|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 8934 | +0.2% | -1.3% | -0.25% | -1.7% | 9% | 11% | 16 |
| Bullish_Scanner | 26129 | +0.2% | -1.2% | -0.25% | -1.6% | 9% | 11% | 16 |
| Wkly_upswing | 5191 | +0.3% | -1.6% | -0.25% | -2.1% | 14% | 19% | 14 |
| **All** | 40254 | +0.2% | -1.3% | -0.25% | -1.7% | 10% | 12% | 16 |

Signals are bought 5.4 times on average under this rule, so the small loss per stop (-1.7%) repeats: 5 stops in a row is about -8.2%.


## Buying the pullback: rules compared

Same signals, every market cap, no target, no time limit, new buys for 3 months after the signal, 0.25% costs per round trip, open positions valued at the latest close.

- **breakout**: Buy above the trigger, sell on a close below it, buy again above it
- **breakout5**: Same, stop on a close 5% below the trigger
- **retest**: Buy the dip back to the trigger (within 2%) that closes above it; stop 5% below
- **dip5**: Buy a 5% dip from the post-breakout high; stop 5% below the trigger
- **ema20**: Buy the dip to the 20-day average that closes above it; stop 5% below the trigger

| Rule | Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | Worst 10% avg | Avg days invested |
|---|---|---|---|---|---|---|---|---|
| breakout | 63_30_daily | 1751 | 5.3 | 24% | +28.3% | -5.4% | -22.6% | 258 |
| breakout | Bullish_Scanner | 4946 | 5.5 | 22% | +23.1% | -5.8% | -23.0% | 250 |
| breakout | Wkly_upswing | 1010 | 5.3 | 18% | +39.9% | -8.0% | -25.4% | 228 |
| breakout | **All** | 7707 | 5.4 | 22% | +26.4% | -5.9% | -23.4% | 249 |
| breakout5 | 63_30_daily | 1751 | 1.5 | 29% | +33.4% | -6.4% | -23.3% | 308 |
| breakout5 | Bullish_Scanner | 4946 | 1.5 | 28% | +30.3% | -6.4% | -23.5% | 312 |
| breakout5 | Wkly_upswing | 1010 | 1.7 | 20% | +47.1% | -8.5% | -26.6% | 267 |
| breakout5 | **All** | 7707 | 1.6 | 27% | +33.2% | -6.6% | -23.9% | 305 |
| retest | 63_30_daily | 1538 | 1.3 | 31% | +34.7% | -7.4% | -24.5% | 324 |
| retest | Bullish_Scanner | 4465 | 1.3 | 29% | +28.9% | -7.8% | -24.6% | 316 |
| retest | Wkly_upswing | 847 | 1.4 | 21% | +48.9% | -9.2% | -28.4% | 275 |
| retest | **All** | 6850 | 1.3 | 28% | +32.7% | -7.9% | -25.2% | 313 |
| dip5 | 63_30_daily | 1457 | 1.7 | 28% | +31.2% | -6.5% | -26.7% | 308 |
| dip5 | Bullish_Scanner | 4293 | 1.8 | 29% | +27.3% | -6.8% | -27.6% | 310 |
| dip5 | Wkly_upswing | 865 | 1.8 | 22% | +51.5% | -8.7% | -31.4% | 288 |
| dip5 | **All** | 6615 | 1.8 | 28% | +31.3% | -6.9% | -28.0% | 307 |
| ema20 | 63_30_daily | 1662 | 1.5 | 29% | +32.2% | -6.6% | -25.1% | 306 |
| ema20 | Bullish_Scanner | 4729 | 1.6 | 29% | +28.6% | -7.4% | -25.5% | 313 |
| ema20 | Wkly_upswing | 883 | 1.6 | 21% | +50.8% | -8.3% | -29.3% | 281 |
| ema20 | **All** | 7274 | 1.6 | 28% | +32.1% | -7.3% | -26.0% | 307 |

| Rule | Cap | Signals bought | Profitable | Avg return | Median |
|---|---|---|---|---|---|
| breakout | Largecap | 3412 | 28% | +38.2% | -4.5% |
| breakout | Midcap | 2098 | 23% | +31.3% | -6.3% |
| breakout | Smallcap | 2195 | 13% | +3.6% | -8.2% |
| breakout5 | Largecap | 3412 | 36% | +49.2% | -5.7% |
| breakout5 | Midcap | 2098 | 26% | +36.6% | -6.7% |
| breakout5 | Smallcap | 2195 | 15% | +5.2% | -9.3% |
| dip5 | Largecap | 2847 | 36% | +46.9% | -4.5% |
| dip5 | Midcap | 1825 | 27% | +37.2% | -7.3% |
| dip5 | Smallcap | 1942 | 15% | +3.1% | -10.4% |
| ema20 | Largecap | 3250 | 36% | +48.2% | -5.8% |
| ema20 | Midcap | 2006 | 27% | +34.8% | -7.4% |
| ema20 | Smallcap | 2017 | 15% | +3.6% | -10.1% |
| retest | Largecap | 3130 | 37% | +49.5% | -6.6% |
| retest | Midcap | 1856 | 27% | +33.8% | -7.8% |
| retest | Smallcap | 1863 | 14% | +3.4% | -10.8% |

## Buy-the-dip rule (the live alert rule)

After the breakout, buy at the next open once a close is 3% below the highest close since the breakout (5% for Wkly_upswing), within 20 sessions and no more than 5% below the trigger. Exit at +8%, a 12% stop, or after 40 sessions. Filter: 63_30_daily only within 10% of the 52-week high. 0.25% costs.

| Group | Trades | Win rate | Avg | Avg win / loss | Target / stop / time | Avg days | ₹ on ₹1L a trade |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 1220 | 71% | +2.32% | +7.6% / -10.5% | 67% / 22% / 11% | 18 | 2,834,950 |
| Bullish_Scanner | 3610 | 68% | +1.88% | +7.6% / -10.3% | 65% / 23% / 12% | 18 | 6,770,750 |
| Wkly_upswing | 473 | 62% | +0.36% | +7.9% / -12.0% | 60% / 35% / 5% | 13 | 172,050 |
| Largecap | 2325 | 68% | +1.92% | +7.3% / -9.7% | 62% / 21% / 17% | 22 | 4,452,800 |
| Midcap | 1478 | 70% | +2.23% | +7.7% / -10.8% | 69% / 23% / 8% | 16 | 3,293,880 |
| Smallcap | 1499 | 66% | +1.36% | +7.9% / -11.5% | 66% / 29% / 6% | 13 | 2,043,320 |
| **All** | 5303 | 68% | +1.84% | +7.6% / -10.5% | 65% / 24% / 11% | 18 | 9,777,750 |

## Reading this

- Average vs median: a high average with a low median means a few big winners carry the result; most buys did worse than the average.
- Compare with the Nifty 500 column: a scanner adds value only when its picks beat the index.
- Stocks Yahoo no longer lists (delisted, renamed) are missing, which flatters long-term results a little (survivorship bias).
- No costs, taxes or stop-loss are included; real results will be lower, and holding with no stop means sitting through every drawdown shown in 'Avg best / worst'.
