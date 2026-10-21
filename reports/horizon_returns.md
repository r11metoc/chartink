# Price after the trigger: 2 to 12 weeks

Generated 2026-10-21 08:59 UTC by `scripts/horizon_returns.py`.

Buy when price crosses the trigger (the signal candle's high; the completed week's candle for `Wkly_upswing`) within 3 sessions (5 for weekly), then just hold. No stop-loss, no target, no costs deducted. **Up** = share of trades above the entry price at that point. **Best / worst close** = the highest and lowest close reached at any time up to that point, averaged across trades. **Beat Nifty 500** = share of trades that did better than the index over the same days. Recent signals only count for horizons that have fully passed, so longer horizons have fewer trades and lean towards older signals.

Per-trade prices: `data/model/horizon_returns.csv`.

## 63_30_daily

5953 signals, 4241 crossed the trigger (31 Dec 2020 to 16 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 4232 | 48% | +0.8% | -0.3% | +5.0% / -4.4% | +0.6% | 43% |
| 4 weeks | 4222 | 52% | +2.0% | +0.5% | +8.2% / -6.0% | +1.1% | 46% |
| 6 weeks | 4209 | 54% | +3.3% | +1.1% | +10.9% / -7.3% | +1.7% | 48% |
| 8 weeks | 4185 | 55% | +4.1% | +1.6% | +13.5% / -8.3% | +2.2% | 48% |
| 12 weeks | 4136 | 56% | +6.0% | +2.8% | +18.0% / -9.9% | +3.4% | 48% |

## Bullish_Scanner

1701 signals, 1333 crossed the trigger (11 Jun 2021 to 19 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 1323 | 48% | +0.5% | -0.4% | +4.9% / -4.6% | +0.5% | 45% |
| 4 weeks | 1308 | 51% | +1.4% | +0.2% | +7.8% / -6.3% | +1.2% | 46% |
| 6 weeks | 1300 | 53% | +2.1% | +1.0% | +10.2% / -7.8% | +1.5% | 48% |
| 8 weeks | 1285 | 54% | +3.3% | +1.3% | +12.7% / -8.9% | +2.3% | 47% |
| 12 weeks | 1251 | 57% | +5.1% | +3.2% | +17.2% / -10.6% | +3.8% | 48% |

## Wkly_upswing

1838 signals, 1220 crossed the trigger (18 Aug 2017 to 16 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 1216 | 46% | +0.8% | -0.8% | +7.1% / -6.1% | +0.7% | 42% |
| 4 weeks | 1211 | 51% | +2.2% | +0.2% | +11.6% / -8.6% | +1.1% | 45% |
| 6 weeks | 1206 | 51% | +3.5% | +0.5% | +15.3% / -10.3% | +1.3% | 47% |
| 8 weeks | 1201 | 52% | +4.6% | +1.1% | +18.7% / -11.8% | +1.7% | 48% |
| 12 weeks | 1186 | 52% | +7.7% | +0.9% | +24.9% / -13.8% | +3.1% | 46% |

## Side by side, signals since 31 Dec 2020

Average return / share of trades up, over the same period for every scanner.

| Horizon | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| 2 weeks | +0.8% / 48% (n=4232) | +0.5% / 48% (n=1323) | +1.0% / 46% (n=959) |
| 4 weeks | +2.0% / 52% (n=4222) | +1.4% / 51% (n=1308) | +2.5% / 51% (n=954) |
| 6 weeks | +3.3% / 54% (n=4209) | +2.1% / 53% (n=1300) | +4.0% / 52% (n=949) |
| 8 weeks | +4.1% / 55% (n=4185) | +3.3% / 54% (n=1285) | +5.4% / 54% (n=944) |
| 12 weeks | +6.0% / 56% (n=4136) | +5.1% / 57% (n=1251) | +8.4% / 51% (n=929) |

## Trailing stop vs just holding (up to 12 weeks)

Same entries as above. Each trailing stop starts that % below the entry and, after every close, moves up to that % below the highest close so far (it never moves down). It exits when a low touches it (at the open on a gap-down), or after 12 weeks at the close. The last row starts with the tight signal-candle-low stop instead. After 0.25% round-trip costs. Only signals with a full 12 weeks of prices are used, so every rule is judged on the same trades.

### 63_30_daily

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 4133 | 56% | +5.7% | +2.6% | +19.8% / -11.9% | 60 | +2.4% (+6.9) |
| Trailing stop 10% | 4133 | 40% | +2.1% | -3.1% | +15.9% / -7.3% | 28 | +0.6% (+2.9) |
| Trailing stop 15% | 4133 | 48% | +3.8% | -0.9% | +18.8% / -10.0% | 43 | +1.8% (+6.1) |
| Trailing stop 20% | 4133 | 52% | +4.8% | +0.9% | +19.9% / -11.5% | 52 | +2.1% (+6.5) |
| Candle-low stop (2-8%), then trail 15% | 4133 | 24% | +1.5% | -3.7% | +22.2% / -4.9% | 20 | +0.4% (+2.0) |

### Bullish_Scanner

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 1249 | 57% | +4.9% | +2.9% | +18.4% / -12.7% | 60 | +1.0% (+1.9) |
| Trailing stop 10% | 1249 | 38% | +0.8% | -4.2% | +14.2% / -7.5% | 26 | -0.6% (-1.6) |
| Trailing stop 15% | 1249 | 46% | +2.2% | -2.3% | +17.3% / -10.4% | 41 | +0.1% (+0.2) |
| Trailing stop 20% | 1249 | 52% | +3.7% | +1.0% | +18.5% / -12.3% | 51 | +0.7% (+1.3) |
| Candle-low stop (2-8%), then trail 15% | 1249 | 28% | +0.7% | -4.8% | +18.9% / -6.3% | 23 | -0.6% (-1.5) |

### Wkly_upswing

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 1186 | 51% | +7.4% | +0.7% | +29.0% / -15.1% | 60 | +4.3% (+3.6) |
| Trailing stop 10% | 1186 | 35% | +1.0% | -5.2% | +17.0% / -7.8% | 17 | +0.1% (+0.3) |
| Trailing stop 15% | 1186 | 39% | +2.8% | -4.5% | +23.6% / -10.6% | 31 | +1.3% (+2.0) |
| Trailing stop 20% | 1186 | 46% | +5.4% | -2.0% | +27.8% / -13.3% | 42 | +3.2% (+3.0) |
| Candle-low stop (2-8%), then trail 15% | 1186 | 28% | +1.7% | -8.2% | +25.3% / -7.5% | 20 | +0.7% (+1.2) |


## Reading this

- A positive average with a much lower median means a few big winners carry the result; most individual trades did worse than the average.
- Compare every number with the Nifty 500 column. When the market rises, most stocks rise; the scanner adds value only if its picks beat the index.
- The gap between the average best close and the final return shows how much of the gain is given back by holding to a fixed date. That is what a trailing stop or target tries to keep.
- Yahoo prices; symbols it doesn't carry are missing (survivorship bias). Corporate actions Yahoo hasn't adjusted can show up as false big moves (e.g. TRIVENI, Jul 2026).