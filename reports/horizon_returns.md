# Price after the trigger: 2 to 12 weeks

Generated 2026-10-23 04:53 UTC by `scripts/horizon_returns.py`.

Buy when price crosses the trigger (the signal candle's high; the completed week's candle for `Wkly_upswing`) within 3 sessions (5 for weekly), then just hold. No stop-loss, no target, no costs deducted. **Up** = share of trades above the entry price at that point. **Best / worst close** = the highest and lowest close reached at any time up to that point, averaged across trades. **Beat Nifty 500** = share of trades that did better than the index over the same days. Recent signals only count for horizons that have fully passed, so longer horizons have fewer trades and lean towards older signals.

Per-trade prices: `data/model/horizon_returns.csv`.

## 63_30_daily

1831 signals, 1439 crossed the trigger (01 Jan 2021 to 21 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 1436 | 52% | +1.6% | +0.3% | +5.4% / -3.7% | +0.7% | 47% |
| 4 weeks | 1434 | 57% | +3.1% | +1.6% | +8.8% / -5.3% | +1.4% | 48% |
| 6 weeks | 1433 | 60% | +4.3% | +3.0% | +11.5% / -6.6% | +2.0% | 51% |
| 8 weeks | 1424 | 60% | +5.3% | +4.0% | +14.0% / -7.5% | +2.8% | 52% |
| 12 weeks | 1416 | 60% | +7.9% | +4.8% | +19.1% / -9.0% | +4.2% | 51% |

## Bullish_Scanner

5083 signals, 4203 crossed the trigger (01 Jan 2021 to 19 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 4196 | 55% | +2.1% | +0.7% | +6.0% / -3.4% | +0.7% | 50% |
| 4 weeks | 4183 | 59% | +3.5% | +2.1% | +9.3% / -4.9% | +1.5% | 51% |
| 6 weeks | 4171 | 60% | +4.6% | +2.8% | +11.9% / -6.0% | +2.0% | 53% |
| 8 weeks | 4153 | 60% | +5.6% | +3.7% | +14.5% / -7.0% | +2.8% | 52% |
| 12 weeks | 4114 | 63% | +8.5% | +5.4% | +19.1% / -8.3% | +4.1% | 53% |

## Wkly_upswing

615 signals, 415 crossed the trigger (01 Sep 2017 to 16 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 411 | 48% | +1.0% | -0.4% | +6.2% / -5.1% | +0.5% | 43% |
| 4 weeks | 406 | 52% | +2.1% | +0.3% | +9.7% / -7.1% | +0.8% | 48% |
| 6 weeks | 406 | 52% | +2.8% | +0.6% | +12.7% / -8.7% | +0.9% | 49% |
| 8 weeks | 403 | 50% | +3.1% | +0.1% | +15.2% / -10.2% | +1.1% | 49% |
| 12 weeks | 391 | 54% | +6.1% | +1.3% | +19.9% / -12.1% | +2.6% | 49% |

## Side by side, signals since 01 Jan 2021

Average return / share of trades up, over the same period for every scanner.

| Horizon | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| 2 weeks | +1.6% / 52% (n=1436) | +2.1% / 55% (n=4196) | +1.5% / 46% (n=315) |
| 4 weeks | +3.1% / 57% (n=1434) | +3.5% / 59% (n=4183) | +2.5% / 52% (n=310) |
| 6 weeks | +4.3% / 60% (n=1433) | +4.6% / 60% (n=4171) | +3.7% / 52% (n=310) |
| 8 weeks | +5.3% / 60% (n=1424) | +5.6% / 60% (n=4153) | +4.2% / 53% (n=307) |
| 12 weeks | +7.9% / 60% (n=1416) | +8.5% / 63% (n=4114) | +7.3% / 55% (n=295) |

## Trailing stop vs just holding (up to 12 weeks)

Same entries as above. Each trailing stop starts that % below the entry and, after every close, moves up to that % below the highest close so far (it never moves down). It exits when a low touches it (at the open on a gap-down), or after 12 weeks at the close. The last row starts with the tight signal-candle-low stop instead. After 0.25% round-trip costs. Only signals with a full 12 weeks of prices are used, so every rule is judged on the same trades.

### 63_30_daily

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 1415 | 60% | +7.6% | +4.6% | +20.7% / -12.0% | 60 | +3.4% (+5.8) |
| Trailing stop 10% | 1415 | 47% | +4.4% | -1.1% | +17.4% / -7.2% | 31 | +2.2% (+5.6) |
| Trailing stop 15% | 1415 | 54% | +6.1% | +2.0% | +19.7% / -9.7% | 45 | +3.2% (+6.3) |
| Trailing stop 20% | 1415 | 57% | +6.7% | +3.5% | +20.6% / -11.5% | 53 | +3.2% (+5.8) |
| Candle-low stop (2-8%), then trail 15% | 1415 | 21% | +2.2% | -2.9% | +25.0% / -3.7% | 17 | +1.0% (+2.6) |

### Bullish_Scanner

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 4112 | 62% | +8.2% | +5.2% | +19.7% / -10.6% | 60 | +4.1% (+12.6) |
| Trailing stop 10% | 4112 | 48% | +3.5% | -0.8% | +15.0% / -6.9% | 30 | +1.6% (+7.2) |
| Trailing stop 15% | 4112 | 55% | +5.7% | +2.1% | +18.2% / -9.4% | 45 | +3.0% (+10.5) |
| Trailing stop 20% | 4112 | 59% | +7.0% | +3.8% | +19.4% / -10.9% | 53 | +3.6% (+11.3) |
| Candle-low stop (2-8%), then trail 15% | 4112 | 29% | +2.7% | -3.1% | +20.4% / -4.5% | 22 | +1.3% (+6.0) |

### Wkly_upswing

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 391 | 52% | +5.9% | +1.1% | +23.7% / -13.8% | 60 | +3.2% (+2.4) |
| Trailing stop 10% | 391 | 36% | +1.4% | -4.3% | +16.8% / -7.2% | 22 | +0.8% (+0.9) |
| Trailing stop 15% | 391 | 42% | +3.3% | -3.3% | +22.1% / -10.3% | 37 | +1.9% (+1.6) |
| Trailing stop 20% | 391 | 48% | +4.3% | -0.7% | +22.9% / -12.6% | 47 | +2.2% (+1.7) |
| Candle-low stop (2-8%), then trail 15% | 391 | 32% | +2.6% | -7.9% | +24.1% / -7.4% | 25 | +1.7% (+1.6) |


## Reading this

- A positive average with a much lower median means a few big winners carry the result; most individual trades did worse than the average.
- Compare every number with the Nifty 500 column. When the market rises, most stocks rise; the scanner adds value only if its picks beat the index.
- The gap between the average best close and the final return shows how much of the gain is given back by holding to a fixed date. That is what a trailing stop or target tries to keep.
- Yahoo prices; symbols it doesn't carry are missing (survivorship bias). Corporate actions Yahoo hasn't adjusted can show up as false big moves (e.g. TRIVENI, Jul 2026).