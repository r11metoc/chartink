# If I had bought every scanner stock

Generated 2026-10-22 18:13 UTC by `scripts/stock_outcomes.py` from `data/backtest/*.csv` plus the bot's live triggers.

**Rule:** buy when price crosses the signal candle's high within 3 sessions (5 for `Wkly_upswing`), filled at the trigger or at the open on a gap-up; then hold. No stop, no target, no costs. **Short** = 2 weeks / 1 month, **Medium** = 3 / 6 months, **Long** = 1 / 2 years. **Beat Nifty 500** = share of buys that did better than the index over the same days. Recent buys only count for horizons that have fully passed.

Per-trade data: `data/model/stock_outcomes.csv`; per-stock: `data/model/stock_summary.csv`.

## All scanners at a glance

| Scanner | Signals | Bought | 1 month avg | 6 months avg | 1 year avg | 2 years avg | 1 year vs Nifty 500 |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 6300 | 4740 | +2.1% | +10.5% | +24.7% | +56.3% | +10.7% |
| Bullish_Scanner | 5084 | 4204 | +3.7% | +15.4% | +27.4% | +48.3% | +13.0% |
| Wkly_upswing | 1119 | 750 | +2.8% | +16.0% | +30.3% | +52.6% | +18.9% |

## 63_30_daily

6300 signals (31 Dec 2020 to 21 Oct 2026): 4740 bought, 1545 never crossed the trigger, 14 without Yahoo prices, 1 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 4732 | 48% | +0.8% | -0.2% | +4.9% / -4.1% | +0.6% | 44% | +0.2% |
| Short | 1 month | 4724 | 52% | +2.1% | +0.4% | +8.3% / -5.9% | +1.2% | 44% | +0.9% |
| Medium | 3 months | 4615 | 57% | +6.6% | +3.3% | +18.4% / -9.7% | +3.4% | 49% | +3.2% |
| Medium | 6 months | 4313 | 58% | +10.5% | +5.5% | +28.9% / -13.3% | +6.0% | 48% | +4.5% |
| Long | 1 year | 4004 | 61% | +24.7% | +11.6% | +50.2% / -18.1% | +14.0% | 48% | +10.7% |
| Long | 2 years | 3141 | 67% | +56.3% | +29.3% | +104.2% / -22.1% | +32.7% | 49% | +23.6% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Largecap | 1759 / 55% / +1.9% / +0.6% | 1661 / 64% / +11.7% / +6.2% | 1506 / 71% / +30.2% / +16.2% |
| Midcap | 1379 / 52% / +2.5% / +1.4% | 1240 / 62% / +14.0% / +7.9% | 1141 / 63% / +29.6% / +15.5% |
| Smallcap | 1586 / 47% / +2.0% / +0.9% | 1412 / 49% / +5.9% / -0.6% | 1357 / 50% / +14.4% / +0.5% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2021 | 413 / 53% / +4.7% / +2.6% | 413 / 50% / +9.0% / +0.8% | 413 / 44% / +6.4% / +1.6% |
| 2022 | 835 / 41% / -0.5% / +0.7% | 835 / 50% / +4.9% / +5.8% | 835 / 73% / +38.4% / +27.4% |
| 2023 | 1172 / 64% / +4.2% / +0.9% | 1172 / 82% / +27.8% / +11.5% | 1172 / 82% / +52.6% / +17.5% |
| 2024 | 806 / 51% / +2.6% / +1.4% | 806 / 50% / +3.1% / +0.7% | 806 / 43% / +0.2% / -3.3% |
| 2025 | 945 / 49% / +1.2% / -0.1% | 945 / 48% / +0.4% / -1.9% | 778 / 46% / +2.9% / +2.0% |
| 2026 | 553 / 44% / +0.7% / +1.2% | 142 / 56% / +13.4% / +13.4% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Aerospace & Defence | 62 / 71% / +14.1% / +12.6% | 58 / 81% / +44.3% / +38.6% | 56 / 86% / +100.1% / +85.1% |
| Auto | 285 / 57% / +4.6% / +2.5% | 268 / 72% / +18.0% / +9.5% | 266 / 75% / +32.9% / +17.9% |
| Bank | 276 / 48% / -0.1% / -1.0% | 263 / 66% / +13.8% / +9.4% | 237 / 74% / +32.5% / +18.2% |
| Building Materials | 223 / 52% / +2.6% / +0.7% | 215 / 53% / +3.3% / -3.8% | 206 / 49% / +5.8% / -11.5% |
| Castings, Forgings & Fasteners | 39 / 54% / +2.2% / +2.5% | 37 / 57% / +11.3% / +6.5% | 30 / 67% / +35.5% / +21.6% |
| Chemicals | 355 / 41% / -0.1% / -1.0% | 329 / 41% / +1.3% / -5.5% | 316 / 48% / +11.0% / -1.9% |
| Consumer Discretionary | 259 / 51% / +1.8% / +0.2% | 232 / 46% / +5.4% / -0.7% | 221 / 54% / +12.7% / -1.8% |
| Energy | 155 / 51% / +1.0% / +0.5% | 143 / 57% / +4.9% / +0.1% | 125 / 46% / +10.3% / +0.5% |
| FMCG | 340 / 55% / +2.7% / +1.3% | 318 / 63% / +13.0% / +5.3% | 298 / 61% / +17.6% / +3.5% |
| Financials | 503 / 50% / +1.7% / +0.8% | 449 / 60% / +7.2% / +2.6% | 412 / 62% / +18.7% / +6.5% |
| Healthcare | 424 / 55% / +2.0% / +0.5% | 364 / 68% / +12.0% / +6.5% | 322 / 63% / +21.3% / +7.7% |
| I.T | 256 / 46% / +1.0% / +0.1% | 222 / 61% / +10.0% / +5.6% | 203 / 55% / +20.0% / +7.2% |
| Industrials | 240 / 62% / +4.1% / +2.7% | 217 / 59% / +15.8% / +9.3% | 200 / 60% / +36.6% / +24.0% |
| Media | 79 / 47% / +0.1% / +0.4% | 74 / 34% / -1.7% / -5.4% | 69 / 42% / +3.5% / -10.7% |
| Metals & Mining | 233 / 51% / +2.4% / +1.8% | 203 / 62% / +18.7% / +12.8% | 184 / 73% / +43.2% / +28.7% |
| Miscellaneous | 133 / 54% / +1.4% / -0.6% | 125 / 58% / +6.3% / -1.6% | 120 / 57% / +27.4% / +7.8% |
| Plastic products | 44 / 50% / +2.4% / +1.9% | 41 / 44% / +11.4% / +6.3% | 35 / 60% / +22.3% / +7.4% |
| Power & Utilities | 107 / 39% / -0.4% / -1.9% | 106 / 48% / +6.2% / +0.9% | 88 / 81% / +39.2% / +25.5% |
| Readymade Garments/Apparels | 42 / 45% / +4.6% / +2.6% | 37 / 70% / +30.7% / +22.0% | 34 / 68% / +35.2% / +14.3% |
| Realty | 278 / 55% / +2.4% / +1.6% | 254 / 58% / +15.0% / +9.1% | 245 / 62% / +51.1% / +36.4% |
| Services | 101 / 54% / +4.5% / +4.1% | 90 / 59% / +9.1% / +4.7% | 83 / 71% / +24.7% / +16.8% |
| Telecom-Service | 44 / 59% / +5.3% / +4.5% | 40 / 80% / +11.8% / +4.2% | 39 / 69% / +18.8% / +4.9% |
| Textiles | 107 / 46% / +0.7% / -0.3% | 99 / 45% / +1.2% / -4.5% | 91 / 62% / +13.3% / -2.3% |
| Transportation | 117 / 53% / +2.4% / +1.0% | 110 / 63% / +10.0% / +2.6% | 108 / 50% / +15.2% / +1.5% |

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| PURVA | Realty | Smallcap | 7 | +1.1% | +65.1% | +298.0% | 71% |
| ZENTEC | Aerospace & Defence | Midcap | 4 | +17.4% | +159.5% | +273.3% | 100% |
| IRFC | Financials | Largecap | 4 | -6.4% | +20.4% | +247.8% | 100% |
| JINDALSAW | Industrials | Midcap | 4 | -2.0% | +93.0% | +241.2% | 75% |
| RVNL | Realty | Largecap | 5 | +4.8% | +59.5% | +240.7% | 60% |
| ACE | Industrials | Midcap | 5 | +4.4% | +41.4% | +215.4% | 40% |
| TIMETECHNO | Plastic products | Midcap | 3 | +2.5% | +96.6% | +214.4% | 33% |
| GANESHHOU | Realty | Midcap | 3 | +41.8% | +108.8% | +207.8% | 67% |
| SCHNEIDER | Industrials | Largecap | 5 | +24.9% | +34.0% | +200.0% | 80% |
| INOXGREEN | Miscellaneous | Smallcap | 4 | +6.2% | +72.5% | +196.0% | 100% |

**Worst repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| FUSION | Financials | Smallcap | 6 | -11.4% | -12.4% | -73.3% | 0% |
| SADBHAV | Realty | Smallcap | 3 | +4.4% | -40.6% | -72.4% | 0% |
| VISHWARAJ | FMCG | Smallcap | 3 | -10.1% | -41.2% | -50.6% | 0% |
| GRAPHITE | Industrials | Midcap | 3 | -1.8% | -36.9% | -50.5% | 0% |
| PRINCEPIPE | Plastic products | Smallcap | 4 | +1.1% | -36.0% | -50.3% | 0% |
| DELTACORP | Miscellaneous | Smallcap | 5 | +2.6% | -36.2% | -49.0% | 0% |
| JYOTICNC | Industrials | Largecap | 3 | -1.3% | -22.9% | -47.5% | 0% |
| RAJESHEXPO | Consumer Discretionary | Smallcap | 3 | -6.9% | -30.3% | -45.0% | 0% |
| SDBL | FMCG | Smallcap | 4 | +2.4% | +5.0% | -45.0% | 0% |
| RKSWAMY | Media | Smallcap | 4 | -12.3% | -17.3% | -44.3% | 0% |

**Biggest single winners after 1 year**

| Stock | Bought | Price | Return | Nifty 500 |
|---|---|---|---|---|
| MAZDOCK | 2022-08-18 | 162.32 | +472.5% | +10.1% |
| PURVA | 2023-06-21 | 97.95 | +461.2% | +41.1% |
| PURVA | 2023-06-23 | 98.00 | +438.4% | +42.4% |
| PURVA | 2023-06-13 | 88.75 | +437.0% | +40.4% |
| CUPID | 2023-08-21 | 3.32 | +416.4% | +41.8% |
| RVNL | 2022-09-07 | 33.40 | +408.5% | +14.0% |
| RVNL | 2022-09-09 | 34.00 | +402.8% | +14.0% |
| RVNL | 2022-09-09 | 34.00 | +402.8% | +14.0% |
| PURVA | 2023-06-06 | 87.55 | +392.9% | +40.8% |
| JINDALSAW | 2022-11-29 | 47.10 | +384.4% | +18.3% |

## Bullish_Scanner

5084 signals (31 Dec 2020 to 22 Oct 2026): 4204 bought, 858 never crossed the trigger, 18 without Yahoo prices, 4 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 4197 | 55% | +2.1% | +0.8% | +6.0% / -3.4% | +0.7% | 50% | +1.4% |
| Short | 1 month | 4184 | 59% | +3.7% | +2.0% | +9.6% / -5.1% | +1.6% | 51% | +2.1% |
| Medium | 3 months | 4113 | 63% | +8.7% | +5.7% | +19.8% / -8.5% | +4.3% | 53% | +4.4% |
| Medium | 6 months | 3973 | 65% | +15.4% | +9.2% | +31.8% / -11.4% | +8.0% | 52% | +7.4% |
| Long | 1 year | 3739 | 64% | +27.4% | +13.5% | +53.7% / -15.3% | +14.4% | 52% | +13.0% |
| Long | 2 years | 3400 | 69% | +48.3% | +26.9% | +90.1% / -19.6% | +26.6% | 51% | +21.7% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Largecap | 2019 / 59% / +2.7% / +1.2% | 1944 / 68% / +14.5% / +7.3% | 1771 / 71% / +29.4% / +15.2% |
| Midcap | 1133 / 60% / +4.7% / +3.1% | 1061 / 66% / +19.1% / +10.8% | 1013 / 62% / +32.5% / +18.6% |
| Smallcap | 1032 / 57% / +4.5% / +2.7% | 968 / 58% / +13.0% / +3.7% | 955 / 53% / +18.4% / +3.1% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2021 | 854 / 56% / +4.2% / +2.0% | 854 / 59% / +13.2% / +5.8% | 854 / 54% / +15.9% / +10.3% |
| 2022 | 403 / 48% / +1.4% / +3.3% | 403 / 51% / +4.4% / +6.2% | 403 / 69% / +25.7% / +18.0% |
| 2023 | 1235 / 68% / +5.5% / +2.2% | 1235 / 85% / +30.1% / +12.9% | 1235 / 84% / +58.6% / +24.8% |
| 2024 | 1007 / 55% / +2.8% / +1.3% | 1007 / 59% / +8.2% / +3.4% | 1007 / 50% / +4.4% / +0.3% |
| 2025 | 373 / 57% / +2.6% / +1.9% | 373 / 48% / +2.8% / +2.1% | 240 / 48% / +7.8% / +7.0% |
| 2026 | 312 / 54% / +1.9% / +3.3% | 101 / 50% / +15.4% / +15.8% | 0 / – / – / – |

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
| Financials | 437 / 53% / +1.9% / +0.5% | 420 / 58% / +11.2% / +3.6% | 385 / 57% / +28.3% / +14.6% |
| Healthcare | 458 / 64% / +4.9% / +2.6% | 416 / 71% / +13.1% / +4.1% | 411 / 68% / +24.3% / +8.8% |
| I.T | 218 / 60% / +3.1% / +1.4% | 209 / 61% / +11.4% / +5.2% | 204 / 48% / +10.8% / +0.3% |
| Industrials | 325 / 64% / +4.7% / +3.0% | 311 / 76% / +23.4% / +15.7% | 294 / 80% / +55.0% / +38.8% |
| Media | 34 / 38% / -1.6% / -2.1% | 34 / 24% / -1.9% / -8.0% | 34 / 21% / -10.3% / -19.0% |
| Metals & Mining | 169 / 57% / +3.4% / +3.1% | 162 / 61% / +15.7% / +9.4% | 137 / 72% / +27.7% / +13.9% |
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
| Medium | 6 months | 695 | 52% | +16.0% | +1.4% | +42.1% / -17.3% | +5.7% | 46% | +10.3% |
| Long | 1 year | 664 | 56% | +30.3% | +7.1% | +70.9% / -23.6% | +11.4% | 47% | +18.9% |
| Long | 2 years | 616 | 60% | +52.6% | +15.7% | +120.6% / -29.5% | +26.3% | 43% | +26.3% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Unknown | 0 / – / – / – | 0 / – / – / – | 0 / – / – / – |
| Largecap | 212 / 57% / +2.6% / +1.3% | 195 / 59% / +14.0% / +9.1% | 189 / 66% / +26.3% / +14.9% |
| Midcap | 180 / 54% / +3.1% / +2.0% | 174 / 51% / +15.8% / +11.7% | 158 / 55% / +48.7% / +38.6% |
| Smallcap | 350 / 50% / +2.7% / +1.5% | 326 / 48% / +17.2% / +10.2% | 317 / 51% / +23.4% / +11.5% |

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
| 2025 | 43 / 51% / +0.2% / -0.9% | 43 / 28% / -8.3% / -8.6% | 32 / 38% / -5.9% / -6.2% |
| 2026 | 66 / 41% / -0.4% / +0.5% | 19 / 53% / +18.8% / +21.2% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Auto | 36 / 72% / +7.4% / +5.3% | 34 / 65% / +45.3% / +39.5% | 32 / 66% / +63.6% / +52.7% |
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
| Metals & Mining | 40 / 38% / -2.2% / -2.8% | 35 / 54% / +15.3% / +8.2% | 31 / 65% / +30.4% / +19.4% |
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
| 63_30_daily | 5952 | 5.5 | 20% | +18.6% | -5.8% | -21.7% | 217 | 1225 | +8.7% | +9.9% |
| Bullish_Scanner | 4948 | 5.5 | 22% | +22.5% | -5.8% | -23.0% | 250 | 1118 | +9.7% | +12.8% |
| Wkly_upswing | 1010 | 5.3 | 18% | +39.0% | -8.0% | -25.4% | 228 | 171 | +11.2% | +27.8% |
| **All** | 11910 | 5.5 | 21% | +22.0% | -6.0% | -22.7% | 232 | 2514 | +9.4% | +12.6% |

| Scanner | Cap | Signals | Profitable | Avg return | Median | Avg days invested |
|---|---|---|---|---|---|---|
| 63_30_daily | Largecap | 2144 | 27% | +39.1% | -4.5% | 272 |
| 63_30_daily | Midcap | 1741 | 21% | +17.8% | -5.8% | 225 |
| 63_30_daily | Smallcap | 2067 | 11% | -1.9% | -7.5% | 153 |
| Bullish_Scanner | Largecap | 2364 | 28% | +34.1% | -4.4% | 277 |
| Bullish_Scanner | Midcap | 1356 | 22% | +22.3% | -6.5% | 251 |
| Bullish_Scanner | Smallcap | 1228 | 13% | +0.5% | -7.7% | 196 |
| Wkly_upswing | Largecap | 272 | 25% | +52.4% | -5.7% | 301 |
| Wkly_upswing | Midcap | 241 | 20% | +78.4% | -7.5% | 258 |
| Wkly_upswing | Smallcap | 496 | 12% | +12.5% | -9.7% | 174 |

| Buys per signal | Signals | Profitable | Avg return |
|---|---|---|---|
| 1 | 1797 | 34% | +43.7% |
| 2 | 1558 | 26% | +32.7% |
| 3 | 1333 | 22% | +31.7% |
| 4 | 1185 | 20% | +28.3% |
| 5 | 1046 | 20% | +20.1% |
| 6+ | 4991 | 14% | +7.1% |

### Stop on any trade below the trigger

| Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | Worst 10% avg | Avg days invested | Still holding | Nifty 500 avg | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 5952 | 6.7 | 17% | +16.4% | -6.1% | -22.7% | 195 | 1095 | +8.1% | +8.3% |
| Bullish_Scanner | 4948 | 6.9 | 19% | +18.9% | -6.2% | -23.8% | 225 | 996 | +9.2% | +9.7% |
| Wkly_upswing | 1010 | 6.5 | 15% | +29.5% | -7.6% | -28.7% | 204 | 152 | +10.6% | +18.9% |
| **All** | 11910 | 6.8 | 18% | +18.5% | -6.2% | -23.8% | 208 | 2243 | +8.7% | +9.8% |

| Scanner | Cap | Signals | Profitable | Avg return | Median | Avg days invested |
|---|---|---|---|---|---|---|
| 63_30_daily | Largecap | 2144 | 23% | +35.9% | -4.8% | 246 |
| 63_30_daily | Midcap | 1741 | 19% | +15.1% | -6.2% | 202 |
| 63_30_daily | Smallcap | 2067 | 9% | -2.8% | -7.4% | 136 |
| Bullish_Scanner | Largecap | 2364 | 23% | +29.4% | -5.0% | 247 |
| Bullish_Scanner | Midcap | 1356 | 19% | +18.1% | -6.5% | 229 |
| Bullish_Scanner | Smallcap | 1228 | 11% | -0.8% | -8.4% | 176 |
| Wkly_upswing | Largecap | 272 | 21% | +47.9% | -5.3% | 268 |
| Wkly_upswing | Midcap | 241 | 18% | +62.5% | -8.1% | 231 |
| Wkly_upswing | Smallcap | 496 | 9% | +3.4% | -8.9% | 157 |

| Buys per signal | Signals | Profitable | Avg return |
|---|---|---|---|
| 1 | 1240 | 23% | +37.4% |
| 2 | 1340 | 26% | +37.0% |
| 3 | 1125 | 24% | +47.0% |
| 4 | 1056 | 21% | +24.9% |
| 5 | 923 | 17% | +12.5% |
| 6+ | 6226 | 13% | +5.4% |


## The pullback after the breakout

For every signal that crossed its trigger, the 20 sessions after the first crossing. **Back at the trigger** = the low came within 2% of the trigger (or below).

| Scanner | Breakouts | Back at the trigger | Median days to get there | Closed below the trigger | Closed 5%+ below | Median dip from the high | 3 months later: retested / not |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 5926 | 97% | 1 | 84% | 47% | -11.5% | +6.1% / +28.2% |
| Bullish_Scanner | 4927 | 96% | 1 | 80% | 41% | -11.4% | +7.7% / +30.0% |
| Wkly_upswing | 999 | 93% | 1 | 82% | 55% | -15.1% | +5.9% / +46.0% |
| **All** | 11852 | 96% | 1 | 82% | 45% | -11.7% | +6.7% / +31.5% |

## Why a stop at the buy price still loses

Every round trip of the *breakout* rule (buy above the trigger, sell after a close below it). Entry and exit are shown against the trigger price.

| Scanner | Stopped round trips | Avg bought above trigger | Avg sold below trigger | Costs | Avg loss per stop | Bought on a gap-up | Sold 3%+ below trigger | Avg days held |
|---|---|---|---|---|---|---|---|---|
| 63_30_daily | 31489 | +0.1% | -1.2% | -0.25% | -1.6% | 8% | 11% | 15 |
| Bullish_Scanner | 26139 | +0.2% | -1.2% | -0.25% | -1.6% | 9% | 11% | 16 |
| Wkly_upswing | 5192 | +0.3% | -1.6% | -0.25% | -2.1% | 14% | 19% | 14 |
| **All** | 62820 | +0.2% | -1.3% | -0.25% | -1.7% | 9% | 12% | 15 |

Signals are bought 5.5 times on average under this rule, so the small loss per stop (-1.7%) repeats: 5 stops in a row is about -8.1%.


## Buying the pullback: rules compared

Same signals, every market cap, no target, no time limit, new buys for 3 months after the signal, 0.25% costs per round trip, open positions valued at the latest close.

- **breakout**: Buy above the trigger, sell on a close below it, buy again above it
- **breakout5**: Same, stop on a close 5% below the trigger
- **retest**: Buy the dip back to the trigger (within 2%) that closes above it; stop 5% below
- **dip5**: Buy a 5% dip from the post-breakout high; stop 5% below the trigger
- **ema20**: Buy the dip to the 20-day average that closes above it; stop 5% below the trigger

| Rule | Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | Worst 10% avg | Avg days invested |
|---|---|---|---|---|---|---|---|---|
| breakout | 63_30_daily | 5951 | 5.5 | 20% | +18.6% | -5.8% | -21.8% | 217 |
| breakout | Bullish_Scanner | 4948 | 5.5 | 22% | +22.5% | -5.8% | -23.0% | 250 |
| breakout | Wkly_upswing | 1010 | 5.3 | 18% | +39.0% | -8.0% | -25.4% | 228 |
| breakout | **All** | 11909 | 5.5 | 21% | +22.0% | -6.0% | -22.7% | 232 |
| breakout5 | 63_30_daily | 5951 | 1.6 | 24% | +23.7% | -6.6% | -22.3% | 264 |
| breakout5 | Bullish_Scanner | 4948 | 1.5 | 28% | +29.7% | -6.4% | -23.5% | 312 |
| breakout5 | Wkly_upswing | 1010 | 1.7 | 20% | +46.0% | -8.5% | -26.6% | 267 |
| breakout5 | **All** | 11909 | 1.6 | 25% | +28.1% | -6.6% | -23.2% | 284 |
| retest | 63_30_daily | 5188 | 1.3 | 26% | +24.7% | -7.7% | -23.0% | 280 |
| retest | Bullish_Scanner | 4465 | 1.3 | 29% | +28.3% | -7.8% | -24.6% | 316 |
| retest | Wkly_upswing | 847 | 1.4 | 21% | +47.7% | -9.2% | -28.4% | 276 |
| retest | **All** | 10500 | 1.3 | 27% | +28.1% | -7.9% | -24.3% | 295 |
| dip5 | 63_30_daily | 4958 | 1.7 | 26% | +23.3% | -6.5% | -25.9% | 269 |
| dip5 | Bullish_Scanner | 4296 | 1.8 | 28% | +26.6% | -6.7% | -27.6% | 310 |
| dip5 | Wkly_upswing | 867 | 1.8 | 22% | +50.2% | -8.7% | -31.3% | 287 |
| dip5 | **All** | 10121 | 1.8 | 26% | +27.0% | -6.8% | -27.1% | 288 |
| ema20 | 63_30_daily | 5559 | 1.6 | 25% | +23.0% | -7.0% | -23.3% | 264 |
| ema20 | Bullish_Scanner | 4729 | 1.6 | 29% | +28.0% | -7.4% | -25.5% | 313 |
| ema20 | Wkly_upswing | 885 | 1.6 | 21% | +49.5% | -8.3% | -29.3% | 281 |
| ema20 | **All** | 11173 | 1.6 | 26% | +27.2% | -7.3% | -24.8% | 286 |

| Rule | Cap | Signals bought | Profitable | Avg return | Median |
|---|---|---|---|---|---|
| breakout | Largecap | 4779 | 27% | +37.4% | -4.5% |
| breakout | Midcap | 3338 | 21% | +24.0% | -6.2% |
| breakout | Smallcap | 3791 | 12% | +0.8% | -7.9% |
| breakout5 | Largecap | 4779 | 35% | +48.2% | -5.7% |
| breakout5 | Midcap | 3338 | 25% | +28.9% | -6.6% |
| breakout5 | Smallcap | 3791 | 14% | +2.0% | -9.0% |
| dip5 | Largecap | 4033 | 36% | +46.7% | -4.5% |
| dip5 | Midcap | 2837 | 26% | +29.2% | -7.1% |
| dip5 | Smallcap | 3250 | 15% | +0.6% | -9.7% |
| ema20 | Largecap | 4557 | 35% | +47.2% | -5.8% |
| ema20 | Midcap | 3162 | 26% | +26.9% | -7.2% |
| ema20 | Smallcap | 3453 | 15% | +1.0% | -9.5% |
| retest | Largecap | 4372 | 36% | +48.6% | -6.7% |
| retest | Midcap | 2918 | 26% | +27.7% | -7.8% |
| retest | Smallcap | 3209 | 14% | +0.6% | -10.0% |

## Buy-the-dip rule (the live alert rule)

After the breakout, buy at the next open once a close is 3% below the highest close since the breakout (5% for Wkly_upswing), within 20 sessions and no more than 5% below the trigger. Exit at +8%, a 12% stop, or after 40 sessions. 0.25% costs.

| Group | Trades | Win rate | Avg | Avg win / loss | Target / stop / time | Avg days | ₹ on ₹1L a trade |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 3933 | 67% | +1.71% | +7.5% / -10.3% | 63% / 23% / 14% | 19 | 6,709,670 |
| Bullish_Scanner | 3614 | 68% | +1.86% | +7.6% / -10.3% | 65% / 23% / 12% | 18 | 6,721,750 |
| Wkly_upswing | 473 | 62% | +0.36% | +7.9% / -12.0% | 60% / 35% / 5% | 13 | 172,050 |
| Largecap | 3205 | 68% | +1.90% | +7.3% / -9.7% | 61% / 20% / 18% | 22 | 6,098,330 |
| Midcap | 2289 | 69% | +1.95% | +7.7% / -10.6% | 67% / 23% / 11% | 17 | 4,472,550 |
| Smallcap | 2525 | 65% | +1.21% | +7.8% / -11.2% | 64% / 29% / 7% | 15 | 3,044,840 |
| **All** | 8020 | 67% | +1.70% | +7.6% / -10.4% | 64% / 24% / 13% | 18 | 13,603,470 |

## Reading this

- Average vs median: a high average with a low median means a few big winners carry the result; most buys did worse than the average.
- Compare with the Nifty 500 column: a scanner adds value only when its picks beat the index.
- Stocks Yahoo no longer lists (delisted, renamed) are missing, which flatters long-term results a little (survivorship bias).
- No costs, taxes or stop-loss are included; real results will be lower, and holding with no stop means sitting through every drawdown shown in 'Avg best / worst'.
