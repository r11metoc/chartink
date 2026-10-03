# Price after the trigger: 2 to 12 weeks

Generated 2026-10-03 09:17 UTC by `scripts/horizon_returns.py`.

Buy when price crosses the trigger (the signal candle's high; the completed week's candle for `Wkly_upswing`) within 3 sessions (5 for weekly), then just hold. No stop-loss, no target, no costs deducted. **Up** = share of trades above the entry price at that point. **Best / worst close** = the highest and lowest close reached at any time up to that point, averaged across trades. **Beat Nifty 500** = share of trades that did better than the index over the same days. Recent signals only count for horizons that have fully passed, so longer horizons have fewer trades and lean towards older signals.

Per-trade prices: `data/model/horizon_returns.csv`.

## 63_30_daily

426 signals, 281 crossed the trigger (03 Feb 2026 to 24 Sep 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 273 | 48% | -0.3% | -0.8% | +5.7% / -6.0% | -0.4% | 50% |
| 4 weeks | 264 | 50% | +1.7% | +0.3% | +9.6% / -7.8% | -0.1% | 51% |
| 6 weeks | 253 | 52% | +2.7% | +0.5% | +12.1% / -8.9% | +0.6% | 50% |
| 8 weeks | 244 | 55% | +4.3% | +2.2% | +15.0% / -9.8% | +1.2% | 55% |
| 12 weeks | 219 | 62% | +7.8% | +4.0% | +21.2% / -10.5% | +1.5% | 58% |

## Bullish_Scanner

245 signals, 183 crossed the trigger (04 Feb 2026 to 30 Sep 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 167 | 54% | +1.6% | +0.7% | +5.5% / -3.8% | -0.5% | 53% |
| 4 weeks | 160 | 50% | +0.1% | -0.1% | +7.2% / -6.1% | -1.3% | 56% |
| 6 weeks | 146 | 56% | +1.3% | +1.6% | +9.1% / -7.7% | -1.1% | 56% |
| 8 weeks | 127 | 60% | +4.7% | +3.0% | +12.2% / -8.1% | -0.2% | 61% |
| 12 weeks | 105 | 64% | +6.1% | +6.7% | +15.7% / -9.6% | +0.6% | 60% |

## Wkly_upswing

766 signals, 521 crossed the trigger (08 Sep 2023 to 25 Sep 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 517 | 47% | +0.9% | -0.6% | +6.5% / -5.9% | +0.7% | 44% |
| 4 weeks | 512 | 51% | +2.2% | +0.5% | +10.5% / -8.2% | +1.4% | 45% |
| 6 weeks | 507 | 51% | +3.2% | +0.7% | +14.0% / -9.9% | +2.1% | 46% |
| 8 weeks | 497 | 52% | +3.8% | +1.1% | +16.9% / -11.3% | +2.9% | 46% |
| 12 weeks | 490 | 50% | +4.3% | -0.3% | +21.4% / -13.4% | +3.8% | 42% |

## Side by side, signals since 03 Feb 2026

Average return / share of trades up, over the same period for every scanner.

| Horizon | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| 2 weeks | -0.3% / 48% (n=273) | +1.6% / 54% (n=167) | +2.1% / 54% (n=76) |
| 4 weeks | +1.7% / 50% (n=264) | +0.1% / 50% (n=160) | +1.7% / 45% (n=71) |
| 6 weeks | +2.7% / 52% (n=253) | +1.3% / 56% (n=146) | +3.2% / 50% (n=66) |
| 8 weeks | +4.3% / 55% (n=244) | +4.7% / 60% (n=127) | +4.8% / 52% (n=56) |
| 12 weeks | +7.8% / 62% (n=219) | +6.1% / 64% (n=105) | +8.2% / 51% (n=49) |

## Trailing stop vs just holding (up to 12 weeks)

Same entries as above. Each trailing stop starts that % below the entry and, after every close, moves up to that % below the highest close so far (it never moves down). It exits when a low touches it (at the open on a gap-down), or after 12 weeks at the close. The last row starts with the tight signal-candle-low stop instead. After 0.25% round-trip costs. Only signals with a full 12 weeks of prices are used, so every rule is judged on the same trades.

### 63_30_daily

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 213 | 63% | +8.1% | +4.3% | +20.3% / -13.0% | 60 | +6.4% (+4.2) |
| Trailing stop 10% | 213 | 37% | +0.1% | -4.7% | +13.5% / -7.7% | 18 | +0.4% (+0.5) |
| Trailing stop 15% | 213 | 51% | +3.8% | +0.5% | +17.4% / -10.5% | 37 | +3.2% (+2.6) |
| Trailing stop 20% | 213 | 57% | +5.4% | +3.1% | +18.5% / -11.8% | 50 | +4.1% (+3.1) |
| Candle-low stop (2-8%), then trail 15% | 213 | 29% | +0.8% | -5.6% | +19.0% / -6.6% | 20 | +1.0% (+1.0) |

### Bullish_Scanner

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 105 | 64% | +5.9% | +6.5% | +17.0% / -13.7% | 60 | +5.3% (+2.9) |
| Trailing stop 10% | 105 | 40% | +1.0% | -3.6% | +14.2% / -7.8% | 29 | +1.5% (+1.3) |
| Trailing stop 15% | 105 | 50% | +3.2% | -0.6% | +18.2% / -11.5% | 43 | +3.7% (+2.1) |
| Trailing stop 20% | 105 | 61% | +4.9% | +5.4% | +16.9% / -13.8% | 54 | +4.5% (+2.5) |
| Candle-low stop (2-8%), then trail 15% | 105 | 30% | +2.0% | -4.2% | +20.6% / -6.2% | 24 | +2.2% (+1.6) |

### Wkly_upswing

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 486 | 48% | +4.0% | -0.6% | +23.3% / -14.1% | 60 | +0.1% (+0.1) |
| Trailing stop 10% | 486 | 33% | +0.1% | -5.5% | +15.8% / -7.8% | 18 | -0.7% (-1.1) |
| Trailing stop 15% | 486 | 38% | +1.5% | -4.5% | +20.6% / -10.5% | 32 | -0.2% (-0.2) |
| Trailing stop 20% | 486 | 44% | +2.8% | -3.3% | +22.8% / -13.2% | 44 | +0.2% (+0.2) |
| Candle-low stop (2-8%), then trail 15% | 486 | 27% | +0.6% | -8.2% | +22.5% / -7.6% | 20 | -0.4% (-0.5) |


## Reading this

- A positive average with a much lower median means a few big winners carry the result; most individual trades did worse than the average.
- Compare every number with the Nifty 500 column. When the market rises, most stocks rise; the scanner adds value only if its picks beat the index.
- The gap between the average best close and the final return shows how much of the gain is given back by holding to a fixed date. That is what a trailing stop or target tries to keep.
- Yahoo prices; symbols it doesn't carry are missing (survivorship bias). Corporate actions Yahoo hasn't adjusted can show up as false big moves (e.g. TRIVENI, Jul 2026).