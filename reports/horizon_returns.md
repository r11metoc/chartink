# Price after the trigger: 2 to 12 weeks

Generated 2026-10-10 09:59 UTC by `scripts/horizon_returns.py`.

Buy when price crosses the trigger (the signal candle's high; the completed week's candle for `Wkly_upswing`) within 3 sessions (5 for weekly), then just hold. No stop-loss, no target, no costs deducted. **Up** = share of trades above the entry price at that point. **Best / worst close** = the highest and lowest close reached at any time up to that point, averaged across trades. **Beat Nifty 500** = share of trades that did better than the index over the same days. Recent signals only count for horizons that have fully passed, so longer horizons have fewer trades and lean towards older signals.

Per-trade prices: `data/model/horizon_returns.csv`.

## 63_30_daily

427 signals, 284 crossed the trigger (03 Feb 2026 to 07 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 281 | 47% | -0.5% | -1.4% | +5.7% / -6.2% | -0.5% | 49% |
| 4 weeks | 272 | 50% | +1.2% | -0.1% | +9.7% / -8.0% | -0.4% | 50% |
| 6 weeks | 260 | 52% | +3.1% | +0.6% | +12.5% / -8.9% | +0.5% | 51% |
| 8 weeks | 249 | 55% | +4.5% | +2.8% | +15.5% / -9.9% | +1.2% | 53% |
| 12 weeks | 231 | 60% | +7.4% | +3.9% | +21.1% / -10.9% | +1.4% | 55% |

## Bullish_Scanner

247 signals, 189 crossed the trigger (04 Feb 2026 to 07 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 179 | 54% | +1.7% | +0.9% | +5.8% / -3.9% | -0.8% | 54% |
| 4 weeks | 166 | 49% | +0.7% | -0.2% | +7.9% / -6.0% | -1.5% | 55% |
| 6 weeks | 157 | 57% | +2.1% | +1.8% | +10.1% / -7.7% | -1.5% | 59% |
| 8 weeks | 136 | 60% | +4.7% | +2.5% | +12.9% / -8.2% | -0.5% | 57% |
| 12 weeks | 111 | 61% | +6.3% | +6.5% | +16.6% / -9.7% | +0.3% | 60% |

## Wkly_upswing

768 signals, 522 crossed the trigger (08 Sep 2023 to 25 Sep 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 517 | 47% | +0.8% | -0.6% | +6.5% / -5.9% | +0.7% | 44% |
| 4 weeks | 515 | 52% | +2.2% | +0.5% | +10.6% / -8.2% | +1.4% | 45% |
| 6 weeks | 509 | 52% | +3.3% | +0.7% | +14.1% / -9.9% | +2.0% | 46% |
| 8 weeks | 502 | 52% | +3.7% | +1.1% | +17.0% / -11.4% | +2.8% | 46% |
| 12 weeks | 490 | 49% | +4.3% | -0.4% | +21.4% / -13.4% | +3.8% | 43% |

## Side by side, signals since 03 Feb 2026

Average return / share of trades up, over the same period for every scanner.

| Horizon | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| 2 weeks | -0.5% / 47% (n=281) | +1.7% / 54% (n=179) | +1.6% / 55% (n=76) |
| 4 weeks | +1.2% / 50% (n=272) | +0.7% / 49% (n=166) | +1.7% / 49% (n=74) |
| 6 weeks | +3.1% / 52% (n=260) | +2.1% / 57% (n=157) | +3.6% / 54% (n=68) |
| 8 weeks | +4.5% / 55% (n=249) | +4.7% / 60% (n=136) | +4.3% / 52% (n=61) |
| 12 weeks | +7.4% / 60% (n=231) | +6.3% / 61% (n=111) | +8.1% / 49% (n=49) |

## Trailing stop vs just holding (up to 12 weeks)

Same entries as above. Each trailing stop starts that % below the entry and, after every close, moves up to that % below the highest close so far (it never moves down). It exits when a low touches it (at the open on a gap-down), or after 12 weeks at the close. The last row starts with the tight signal-candle-low stop instead. After 0.25% round-trip costs. Only signals with a full 12 weeks of prices are used, so every rule is judged on the same trades.

### 63_30_daily

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 226 | 60% | +7.5% | +4.1% | +21.4% / -13.3% | 60 | +6.0% (+3.9) |
| Trailing stop 10% | 226 | 35% | -0.3% | -5.6% | +13.7% / -7.8% | 18 | +0.0% (+0.0) |
| Trailing stop 15% | 226 | 48% | +3.2% | -0.6% | +18.1% / -10.6% | 36 | +2.6% (+2.2) |
| Trailing stop 20% | 226 | 54% | +4.7% | +2.5% | +19.0% / -12.3% | 49 | +3.5% (+2.7) |
| Candle-low stop (2-8%), then trail 15% | 226 | 27% | +0.3% | -5.7% | +18.7% / -6.6% | 19 | +0.5% (+0.5) |

### Bullish_Scanner

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 108 | 62% | +6.4% | +7.2% | +18.6% / -13.5% | 60 | +5.9% (+3.1) |
| Trailing stop 10% | 108 | 42% | +1.7% | -3.5% | +15.2% / -8.0% | 29 | +2.3% (+1.8) |
| Trailing stop 15% | 108 | 51% | +3.9% | +1.9% | +19.1% / -11.9% | 43 | +4.3% (+2.4) |
| Trailing stop 20% | 108 | 60% | +5.6% | +5.5% | +18.4% / -13.9% | 54 | +5.2% (+2.8) |
| Candle-low stop (2-8%), then trail 15% | 108 | 32% | +2.7% | -4.0% | +21.3% / -6.3% | 24 | +2.9% (+2.0) |

### Wkly_upswing

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 490 | 48% | +4.0% | -0.6% | +23.6% / -14.0% | 60 | +0.2% (+0.2) |
| Trailing stop 10% | 490 | 33% | +0.1% | -5.6% | +16.0% / -7.8% | 18 | -0.7% (-1.1) |
| Trailing stop 15% | 490 | 38% | +1.4% | -4.5% | +20.8% / -10.4% | 32 | -0.2% (-0.2) |
| Trailing stop 20% | 490 | 44% | +2.9% | -3.3% | +23.1% / -13.1% | 44 | +0.3% (+0.3) |
| Candle-low stop (2-8%), then trail 15% | 490 | 27% | +0.6% | -8.2% | +22.7% / -7.6% | 20 | -0.4% (-0.5) |


## Reading this

- A positive average with a much lower median means a few big winners carry the result; most individual trades did worse than the average.
- Compare every number with the Nifty 500 column. When the market rises, most stocks rise; the scanner adds value only if its picks beat the index.
- The gap between the average best close and the final return shows how much of the gain is given back by holding to a fixed date. That is what a trailing stop or target tries to keep.
- Yahoo prices; symbols it doesn't carry are missing (survivorship bias). Corporate actions Yahoo hasn't adjusted can show up as false big moves (e.g. TRIVENI, Jul 2026).