# If I had bought every scanner stock

Generated 2026-11-26 22:03 UTC by `scripts/stock_outcomes.py` from `data/backtest/*.csv` plus the bot's live triggers.

**Rule:** buy when price crosses the signal candle's high within 3 sessions (5 for `Wkly_upswing`), filled at the trigger or at the open on a gap-up; then hold. No stop, no target, no costs. **Short** = 2 weeks / 1 month, **Medium** = 3 / 6 months, **Long** = 1 / 2 years. **Beat Nifty 500** = share of buys that did better than the index over the same days. Recent buys only count for horizons that have fully passed.

Per-trade data: `data/model/stock_outcomes.csv`; per-stock: `data/model/stock_summary.csv`.

## All scanners at a glance

| Scanner | Signals | Bought | 1 month avg | 6 months avg | 1 year avg | 2 years avg | 1 year vs Nifty 500 |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 237 | 199 | +5.8% | +13.4% | +18.3% | +29.6% | +7.3% |
| Bullish_Scanner | 2146 | 1755 | +4.0% | +14.9% | +26.8% | +42.8% | +14.6% |
| Wkly_upswing | 624 | 420 | +1.8% | +14.0% | +35.7% | +53.6% | +22.7% |

## 63_30_daily

237 signals (14 Mar 2019 to 26 Nov 2026): 199 bought, 33 never crossed the trigger, 3 without Yahoo prices, 2 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 172 | 64% | +4.7% | +2.9% | +8.5% / -2.6% | +1.2% | 57% | +3.5% |
| Short | 1 month | 171 | 67% | +5.8% | +4.9% | +13.1% / -4.4% | +1.5% | 57% | +4.3% |
| Medium | 3 months | 169 | 67% | +9.8% | +6.3% | +25.2% / -8.8% | +4.0% | 56% | +5.8% |
| Medium | 6 months | 164 | 59% | +13.4% | +7.1% | +35.9% / -13.4% | +6.0% | 51% | +7.4% |
| Long | 1 year | 153 | 54% | +18.3% | +4.1% | +52.4% / -19.6% | +11.0% | 47% | +7.3% |
| Long | 2 years | 129 | 63% | +29.6% | +13.7% | +82.8% / -25.3% | +24.6% | 45% | +5.0% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Unknown | 1 / – / – / – | 0 / – / – / – | 0 / – / – / – |
| Largecap | 53 / 70% / +3.2% / +0.6% | 50 / 64% / +9.4% / +1.4% | 47 / 62% / +18.0% / +5.1% |
| Midcap | 61 / 66% / +5.7% / +5.3% | 59 / 54% / +14.2% / +9.9% | 55 / 47% / +22.1% / +13.8% |
| Smallcap | 56 / 66% / +8.7% / +7.2% | 55 / 60% / +16.1% / +10.2% | 51 / 53% / +14.5% / +2.2% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2019 | 5 / – / – / – | 5 / – / – / – | 5 / – / – / – |
| 2020 | 10 / 40% / +0.5% / -6.8% | 10 / 70% / +18.1% / -9.3% | 10 / 60% / +67.8% / +13.8% |
| 2021 | 15 / 80% / +11.6% / +9.1% | 15 / 53% / +12.3% / +2.0% | 15 / 60% / +13.7% / +6.2% |
| 2022 | 18 / 56% / +0.8% / +2.4% | 18 / 61% / +6.8% / +6.0% | 18 / 61% / +8.9% / +3.9% |
| 2023 | 24 / 83% / +9.8% / +5.0% | 24 / 83% / +45.6% / +27.5% | 24 / 83% / +67.5% / +35.6% |
| 2024 | 65 / 68% / +6.4% / +5.5% | 65 / 54% / +7.2% / +5.2% | 65 / 43% / +1.4% / -1.9% |
| 2025 | 17 / 82% / +7.8% / +7.0% | 17 / 53% / +5.1% / +3.4% | 16 / 38% / +3.4% / +3.7% |
| 2026 | 17 / 41% / +0.4% / +1.9% | 10 / 50% / +10.5% / +12.4% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| EICHERMOT | Auto | Largecap | 3 | +3.4% | +9.7% | +35.0% | 33% |

**Worst repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| EICHERMOT | Auto | Largecap | 3 | +3.4% | +9.7% | +35.0% | 33% |

**Biggest single winners after 1 year**

| Stock | Bought | Price | Return | Nifty 500 |
|---|---|---|---|---|
| JWL | 2023-05-04 | 114.50 | +328.0% | +35.4% |
| VAIBHAVGBL | 2020-05-26 | 219.00 | +290.0% | +76.2% |
| DEEPAKNTR | 2020-05-08 | 557.80 | +222.2% | +68.1% |
| WABAG | 2023-11-09 | 535.00 | +218.3% | +26.4% |
| GANESHHOU | 2024-01-11 | 460.00 | +204.1% | +9.8% |
| VESUVIUS | 2023-05-08 | 180.40 | +187.5% | +37.0% |
| JSWHL | 2024-09-04 | 7666.00 | +145.0% | -3.5% |
| NIITLTD | 2021-06-04 | 199.70 | +117.0% | +4.5% |
| DLINKINDIA | 2023-07-18 | 288.50 | +109.6% | +38.9% |
| DEEPINDS | 2023-04-18 | 152.90 | +90.1% | +39.8% |

## Bullish_Scanner

2146 signals (05 Mar 2019 to 19 Nov 2026): 1755 bought, 385 never crossed the trigger, 6 without Yahoo prices, 0 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 1728 | 54% | +2.2% | +1.0% | +7.5% / -4.8% | +0.8% | 50% | +1.4% |
| Short | 1 month | 1713 | 57% | +4.0% | +2.1% | +12.1% / -6.8% | +1.5% | 51% | +2.5% |
| Medium | 3 months | 1670 | 58% | +8.3% | +3.9% | +24.2% / -11.9% | +3.8% | 51% | +4.5% |
| Medium | 6 months | 1645 | 60% | +14.9% | +7.9% | +37.8% / -15.9% | +7.5% | 51% | +7.4% |
| Long | 1 year | 1603 | 59% | +26.8% | +8.9% | +62.5% / -20.5% | +12.2% | 49% | +14.6% |
| Long | 2 years | 1485 | 61% | +42.8% | +16.4% | +100.9% / -25.7% | +24.0% | 46% | +18.8% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Unknown | 3 / – / – / – | 0 / – / – / – | 0 / – / – / – |
| Largecap | 506 / 62% / +3.3% / +1.8% | 482 / 67% / +17.4% / +9.6% | 469 / 69% / +31.0% / +18.0% |
| Midcap | 472 / 61% / +6.1% / +4.4% | 452 / 66% / +21.6% / +14.2% | 432 / 65% / +40.6% / +28.6% |
| Smallcap | 732 / 52% / +3.0% / +1.7% | 711 / 51% / +8.9% / +1.5% | 702 / 49% / +15.4% / +3.7% |

### By year bought

| Year | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| 2019 | 29 / 69% / +1.7% / +0.3% | 29 / 59% / +3.8% / +8.7% | 29 / 41% / -4.6% / +5.9% |
| 2020 | 64 / 56% / +2.9% / +2.2% | 64 / 69% / +25.9% / +9.2% | 64 / 81% / +69.1% / +27.5% |
| 2021 | 330 / 62% / +5.6% / +3.0% | 330 / 62% / +17.8% / +12.1% | 330 / 61% / +28.7% / +21.3% |
| 2022 | 170 / 44% / +0.2% / +1.1% | 170 / 48% / +3.5% / +3.3% | 170 / 60% / +27.9% / +21.2% |
| 2023 | 354 / 66% / +6.6% / +3.5% | 354 / 82% / +34.3% / +16.1% | 354 / 86% / +63.0% / +30.4% |
| 2024 | 576 / 55% / +3.1% / +1.9% | 576 / 50% / +6.1% / +0.9% | 576 / 43% / +2.5% / -1.0% |
| 2025 | 90 / 53% / +4.0% / +3.4% | 90 / 43% / +1.7% / +1.3% | 80 / 42% / +8.3% / +7.9% |
| 2026 | 100 / 52% / +1.6% / +2.5% | 32 / 69% / +12.3% / +12.3% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Aerospace & Defence | 54 / 56% / +4.9% / +3.2% | 51 / 61% / +24.6% / +15.0% | 50 / 72% / +38.7% / +28.6% |
| Auto | 115 / 56% / +3.5% / +2.3% | 110 / 62% / +10.1% / +2.8% | 104 / 64% / +17.9% / +4.7% |
| Bank | 47 / 66% / +2.2% / +0.6% | 39 / 62% / +11.8% / +4.6% | 32 / 53% / +7.4% / -7.9% |
| Building Materials | 62 / 66% / +4.1% / +2.6% | 62 / 52% / +2.2% / -3.5% | 61 / 57% / +8.8% / -1.8% |
| Chemicals | 124 / 60% / +4.3% / +2.3% | 117 / 66% / +19.3% / +11.7% | 115 / 59% / +26.2% / +14.4% |
| Consumer Discretionary | 76 / 62% / +5.2% / +3.4% | 75 / 56% / +18.5% / +13.1% | 74 / 51% / +29.8% / +20.3% |
| Energy | 37 / 49% / +3.5% / +2.2% | 36 / 53% / +9.6% / +2.7% | 36 / 50% / +15.4% / +5.3% |
| FMCG | 118 / 54% / +2.6% / +0.8% | 117 / 53% / +6.5% / -0.0% | 114 / 61% / +22.0% / +9.4% |
| Financials | 145 / 53% / +3.4% / +2.6% | 141 / 57% / +9.6% / +4.8% | 137 / 55% / +17.3% / +10.3% |
| Healthcare | 137 / 58% / +3.6% / +2.1% | 130 / 54% / +7.6% / -0.6% | 124 / 60% / +16.7% / +2.4% |
| I.T | 103 / 58% / +4.7% / +3.2% | 100 / 63% / +20.4% / +10.9% | 100 / 60% / +38.7% / +24.2% |
| Industrials | 210 / 58% / +5.1% / +3.7% | 203 / 76% / +30.1% / +21.8% | 202 / 80% / +69.9% / +54.5% |
| Media | 21 / 48% / +6.4% / +6.9% | 21 / 57% / +28.8% / +24.0% | 21 / 52% / +33.8% / +26.5% |
| Metals & Mining | 97 / 64% / +7.4% / +6.2% | 92 / 66% / +20.5% / +11.8% | 87 / 63% / +25.9% / +13.2% |
| Miscellaneous | 30 / 60% / +4.2% / +1.8% | 30 / 57% / +21.6% / +10.3% | 29 / 41% / +25.8% / +8.8% |
| Plastic products | 28 / 61% / +1.7% / +0.5% | 27 / 59% / +8.5% / -0.8% | 27 / 44% / +11.9% / +1.7% |
| Power & Utilities | 29 / 69% / +6.2% / +3.8% | 29 / 69% / +30.0% / +19.9% | 29 / 59% / +42.9% / +32.4% |
| Realty | 125 / 58% / +1.9% / -0.5% | 123 / 57% / +9.5% / +0.3% | 120 / 45% / +4.0% / -7.4% |
| Services | 36 / 47% / +2.7% / +1.1% | 35 / 49% / +3.6% / -6.0% | 34 / 50% / +13.2% / +1.2% |
| Textiles | 52 / 46% / +1.2% / +1.3% | 48 / 35% / +3.0% / -0.7% | 48 / 44% / +6.7% / -3.2% |

**Best repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| TARIL | Industrials | Midcap | 5 | +19.0% | +105.5% | +401.5% | 100% |
| TITAGARH | Industrials | Midcap | 3 | +11.8% | +144.9% | +351.8% | 100% |
| JWL | Industrials | Midcap | 4 | +0.1% | +39.3% | +274.2% | 100% |
| TATAELXSI | I.T | Largecap | 3 | +34.4% | +126.7% | +208.6% | 100% |
| V2RETAIL | Consumer Discretionary | Midcap | 3 | +19.9% | +134.5% | +197.3% | 67% |
| NAHARPOLY | Industrials | Smallcap | 4 | +7.4% | +60.1% | +192.1% | 75% |
| PCBL | Chemicals | Midcap | 3 | +4.8% | +53.2% | +171.5% | 100% |
| SHAKTIPUMP | Industrials | Smallcap | 3 | +5.2% | +96.0% | +169.6% | 67% |
| GRPLTD | FMCG | Smallcap | 3 | -1.0% | +37.6% | +143.6% | 100% |
| NDTV | Media | Smallcap | 4 | +17.1% | +94.7% | +134.7% | 75% |

**Worst repeat stocks by average 1 year return** (at least 3 buys)

| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |
|---|---|---|---|---|---|---|---|
| TARMAT | Realty | Smallcap | 3 | -11.6% | -27.3% | -43.3% | 0% |
| CAMLINFINE | Chemicals | Smallcap | 4 | +18.3% | -12.1% | -37.6% | 0% |
| GOLDIAM | Consumer Discretionary | Smallcap | 3 | -3.4% | -27.9% | -31.6% | 0% |
| PNB | Bank | Largecap | 4 | -8.9% | -24.0% | -29.9% | 0% |
| BSOFT | I.T | Midcap | 4 | -6.5% | -7.7% | -29.0% | 25% |
| GRANULES | Healthcare | Largecap | 3 | -11.3% | -25.3% | -28.3% | 0% |
| NITINSPIN | Textiles | Smallcap | 3 | +2.0% | -31.7% | -26.8% | 0% |
| PNCINFRA | Realty | Smallcap | 3 | -1.3% | -27.2% | -26.4% | 0% |
| ALPA | Healthcare | Smallcap | 3 | +5.5% | -17.7% | -24.7% | 0% |
| PATELENG | Realty | Smallcap | 3 | -0.7% | -8.7% | -24.5% | 0% |

**Biggest single winners after 1 year**

| Stock | Bought | Price | Return | Nifty 500 |
|---|---|---|---|---|
| TARIL | 2023-05-24 | 39.35 | +787.2% | +30.7% |
| TANLA | 2020-01-28 | 79.45 | +746.6% | +17.7% |
| SHAKTIPUMP | 2024-01-11 | 189.17 | +510.6% | +9.8% |
| TITAGARH | 2022-11-16 | 174.30 | +455.6% | +12.3% |
| TARIL | 2023-12-26 | 113.00 | +448.3% | +19.2% |
| NAHARPOLY | 2021-03-15 | 109.00 | +441.6% | +16.9% |
| TERASOFT | 2024-11-08 | 102.99 | +434.4% | +5.0% |
| JWL | 2022-08-29 | 76.50 | +394.8% | +13.4% |
| SIGMAADV | 2025-10-27 | 184.99 | +383.7% | -4.9% |
| JWL | 2022-08-25 | 71.90 | +377.5% | +11.8% |

## Wkly_upswing

624 signals (28 Aug 2017 to 26 Nov 2026): 420 bought, 203 never crossed the trigger, 1 without Yahoo prices, 0 still pending.

| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |
|---|---|---|---|---|---|---|---|---|---|
| Short | 2 weeks | 414 | 48% | +1.0% | -0.4% | +6.2% / -5.1% | +0.5% | 43% | +0.4% |
| Short | 1 month | 413 | 51% | +1.8% | +0.1% | +9.9% / -7.4% | +1.0% | 45% | +0.8% |
| Medium | 3 months | 400 | 52% | +6.1% | +1.7% | +20.5% / -12.5% | +2.7% | 48% | +3.3% |
| Medium | 6 months | 377 | 54% | +14.0% | +2.7% | +35.6% / -16.0% | +6.0% | 50% | +8.0% |
| Long | 1 year | 352 | 58% | +35.7% | +9.0% | +69.5% / -21.4% | +13.0% | 48% | +22.7% |
| Long | 2 years | 313 | 64% | +53.6% | +20.9% | +117.5% / -26.7% | +28.1% | 46% | +25.5% |

### By market cap

| Marketcap | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Unknown | 5 / – / – / – | 0 / – / – / – | 0 / – / – / – |
| Largecap | 163 / 59% / +2.5% / +1.4% | 151 / 62% / +16.1% / +10.8% | 138 / 72% / +39.1% / +25.2% |
| Midcap | 89 / 48% / +2.5% / +1.4% | 85 / 46% / +7.1% / +2.2% | 78 / 53% / +24.1% / +13.1% |
| Smallcap | 156 / 45% / +1.1% / +0.4% | 141 / 49% / +16.0% / +8.5% | 136 / 48% / +38.9% / +25.6% |

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
| 2025 | 32 / 59% / +6.5% / +5.5% | 32 / 38% / -1.4% / -1.4% | 28 / 39% / +1.8% / +1.7% |
| 2026 | 57 / 35% / -1.9% / -1.4% | 21 / 43% / +1.4% / +4.2% | 0 / – / – / – |

### By sector (20+ buys)

| Sector | 1 month: n / up / avg / vs index | 6 months: n / up / avg / vs index | 1 year: n / up / avg / vs index |
|---|---|---|---|
| Auto | 22 / 64% / +4.1% / +2.9% | 20 / 60% / +9.4% / +2.0% | 20 / 55% / +22.0% / +7.9% |
| Building Materials | 28 / 32% / -0.5% / -2.0% | 27 / 44% / -0.4% / -5.9% | 26 / 50% / +5.8% / -7.5% |
| Chemicals | 29 / 38% / -5.7% / -5.6% | 25 / 48% / +14.7% / +9.3% | 24 / 62% / +37.5% / +28.8% |
| Consumer Discretionary | 23 / 57% / +4.7% / +2.2% | 21 / 48% / +11.6% / +8.6% | 21 / 52% / +47.3% / +33.2% |
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

Every buy alert from 2019-03-15 (when all three scanners have backtest data) to 2026-11-25, starting with ₹10L: each buy is 1/15 of the portfolio's value at the time (profits reinvested), at most 15 open, first come first served, one position per stock, after costs.

| Scanner | Trades | Win rate | Avg | Avg win / loss | Avg days |
|---|---|---|---|---|---|
| 63_30_daily | 201 | 54% | +7.16% | +17.3% / -4.9% | 28 |
| Bullish_Scanner | 2080 | 45% | +3.43% | +16.2% / -7.1% | 26 |
| Wkly_upswing | 281 | 46% | +3.25% | +13.6% / -5.4% | 25 |
| All | 2562 | 46% | +3.70% | +16.0% / -6.8% | 26 |

| | Alerts portfolio | Nifty 500 |
|---|---|---|
| ₹10L became | ₹65.9L | ₹25.3L |
| Yearly growth (CAGR) | 27.8% | 12.8% |
| Worst fall from a peak | -10.2% | -38.3% |
| Trades taken / skipped (no free slot) | 876 / 1682 | |
| Win rate of trades taken | 46% | |

| Year | Alerts portfolio | Nifty 500 |
|---|---|---|
| 2019 | -0.0% | +3.9% |
| 2020 | +17.0% | +16.7% |
| 2021 | +74.7% | +30.2% |
| 2022 | +28.7% | +3.0% |
| 2023 | +59.3% | +25.8% |
| 2024 | +41.3% | +15.2% |
| 2025 | +15.9% | +6.7% |
| 2026 | -4.0% | +0.6% |

Open positions are counted at cost until sold. The current year is year-to-date.

## Breakout rule (the live alert rule)

Buy at the next open after the signal candle (Monday's open after a weekly signal). Sell at the next open after a close below the 30-day EMA, a 15% stop, at the next open if not +3% after 15 sessions, or after 250 sessions. Wkly_upswing only when daily ATR(14) is under 4% of the close. Filter: . 0.25% costs.

| Group | Trades | Win rate | Avg | Avg win / loss | Average / stop / time | Avg days | ₹ on ₹1L a trade |
|---|---|---|---|---|---|---|---|
| 63_30_daily | 201 | 54% | +7.16% | +17.3% / -4.9% | 81% / 0% / 0% | 28 | 1,439,500 |
| Bullish_Scanner | 2084 | 45% | +3.42% | +16.2% / -7.1% | 71% / 6% / 0% | 26 | 7,134,610 |
| Wkly_upswing | 326 | 45% | +2.70% | +12.4% / -5.2% | 70% / 1% / 0% | 25 | 881,280 |
| Largecap | 857 | 47% | +3.98% | +14.2% / -5.1% | 73% / 2% / 0% | 27 | 3,413,070 |
| Midcap | 743 | 50% | +5.13% | +17.0% / -6.5% | 73% / 3% / 0% | 26 | 3,808,940 |
| Smallcap | 1003 | 42% | +2.28% | +16.4% / -8.0% | 70% / 10% / 0% | 24 | 2,283,970 |
| **All** | 2611 | 46% | +3.62% | +15.8% / -6.7% | 72% / 5% / 0% | 26 | 9,455,390 |

## Reading this

- Average vs median: a high average with a low median means a few big winners carry the result; most buys did worse than the average.
- Compare with the Nifty 500 column: a scanner adds value only when its picks beat the index.
- Stocks Yahoo no longer lists (delisted, renamed) are missing, which flatters long-term results a little (survivorship bias).
- No costs, taxes or stop-loss are included; real results will be lower, and holding with no stop means sitting through every drawdown shown in 'Avg best / worst'.
