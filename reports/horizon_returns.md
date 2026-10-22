# Price after the trigger: 2 to 12 weeks

Generated 2026-10-22 18:48 UTC by `scripts/horizon_returns.py`.

Buy when price crosses the trigger (the signal candle's high; the completed week's candle for `Wkly_upswing`) within 3 sessions (5 for weekly), then just hold. No stop-loss, no target, no costs deducted. **Up** = share of trades above the entry price at that point. **Best / worst close** = the highest and lowest close reached at any time up to that point, averaged across trades. **Beat Nifty 500** = share of trades that did better than the index over the same days. Recent signals only count for horizons that have fully passed, so longer horizons have fewer trades and lean towards older signals.

Per-trade prices: `data/model/horizon_returns.csv`.

## 63_30_daily

1832 signals, 1439 crossed the trigger (31 Dec 2020 to 14 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 1437 | 52% | +1.6% | +0.2% | +5.4% / -3.7% | +0.7% | 47% |
| 4 weeks | 1435 | 57% | +3.1% | +1.6% | +8.8% / -5.3% | +1.4% | 48% |
| 6 weeks | 1431 | 60% | +4.4% | +3.0% | +11.5% / -6.6% | +2.1% | 51% |
| 8 weeks | 1425 | 60% | +5.3% | +4.1% | +14.1% / -7.5% | +2.8% | 52% |
| 12 weeks | 1416 | 60% | +7.9% | +4.9% | +19.1% / -9.0% | +4.3% | 51% |

## Bullish_Scanner

5084 signals, 4204 crossed the trigger (31 Dec 2020 to 19 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 4196 | 55% | +2.1% | +0.7% | +6.0% / -3.4% | +0.7% | 50% |
| 4 weeks | 4184 | 59% | +3.5% | +2.1% | +9.3% / -4.9% | +1.5% | 51% |
| 6 weeks | 4170 | 60% | +4.6% | +2.8% | +11.9% / -6.0% | +2.0% | 53% |
| 8 weeks | 4152 | 60% | +5.6% | +3.7% | +14.5% / -7.0% | +2.8% | 52% |
| 12 weeks | 4113 | 63% | +8.5% | +5.4% | +19.2% / -8.3% | +4.1% | 53% |

## Wkly_upswing

1119 signals, 750 crossed the trigger (18 Aug 2017 to 16 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 747 | 47% | +1.1% | -0.7% | +6.9% / -5.7% | +0.7% | 42% |
| 4 weeks | 742 | 51% | +2.6% | +0.5% | +11.2% / -8.0% | +1.1% | 46% |
| 6 weeks | 738 | 54% | +4.0% | +1.2% | +14.9% / -9.5% | +1.3% | 49% |
| 8 weeks | 733 | 55% | +5.3% | +2.0% | +18.3% / -11.0% | +1.7% | 49% |
| 12 weeks | 721 | 53% | +8.9% | +1.9% | +25.0% / -12.8% | +3.1% | 47% |

## Side by side, signals since 31 Dec 2020

Average return / share of trades up, over the same period for every scanner.

| Horizon | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| 2 weeks | +1.6% / 52% (n=1437) | +2.1% / 55% (n=4196) | +1.2% / 47% (n=573) |
| 4 weeks | +3.1% / 57% (n=1435) | +3.5% / 59% (n=4184) | +2.7% / 53% (n=568) |
| 6 weeks | +4.4% / 60% (n=1431) | +4.6% / 60% (n=4170) | +4.3% / 54% (n=564) |
| 8 weeks | +5.3% / 60% (n=1425) | +5.6% / 60% (n=4152) | +6.1% / 57% (n=559) |
| 12 weeks | +7.9% / 60% (n=1416) | +8.5% / 63% (n=4113) | +9.8% / 52% (n=547) |

## Trailing stop vs just holding (up to 12 weeks)

Same entries as above. Each trailing stop starts that % below the entry and, after every close, moves up to that % below the highest close so far (it never moves down). It exits when a low touches it (at the open on a gap-down), or after 12 weeks at the close. The last row starts with the tight signal-candle-low stop instead. After 0.25% round-trip costs. Only signals with a full 12 weeks of prices are used, so every rule is judged on the same trades.

### 63_30_daily

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 1416 | 60% | +7.6% | +4.6% | +20.7% / -12.0% | 60 | +3.4% (+5.8) |
| Trailing stop 10% | 1416 | 47% | +4.4% | -1.0% | +17.4% / -7.2% | 31 | +2.2% (+5.6) |
| Trailing stop 15% | 1416 | 54% | +6.1% | +2.0% | +19.7% / -9.7% | 45 | +3.2% (+6.3) |
| Trailing stop 20% | 1416 | 57% | +6.7% | +3.5% | +20.6% / -11.5% | 53 | +3.2% (+5.8) |
| Candle-low stop (2-8%), then trail 15% | 1416 | 21% | +2.2% | -2.9% | +25.0% / -3.7% | 17 | +1.0% (+2.6) |

### Bullish_Scanner

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 4113 | 62% | +8.2% | +5.2% | +19.7% / -10.6% | 60 | +4.1% (+12.6) |
| Trailing stop 10% | 4113 | 48% | +3.5% | -0.8% | +15.0% / -6.9% | 30 | +1.5% (+7.2) |
| Trailing stop 15% | 4113 | 55% | +5.7% | +2.1% | +18.2% / -9.4% | 45 | +3.0% (+10.5) |
| Trailing stop 20% | 4113 | 59% | +7.0% | +3.8% | +19.4% / -10.9% | 53 | +3.6% (+11.2) |
| Candle-low stop (2-8%), then trail 15% | 4113 | 29% | +2.7% | -3.1% | +20.4% / -4.5% | 22 | +1.3% (+6.0) |

### Wkly_upswing

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 721 | 52% | +8.7% | +1.6% | +29.3% / -14.0% | 60 | +5.6% (+3.1) |
| Trailing stop 10% | 721 | 36% | +1.4% | -4.8% | +16.9% / -7.5% | 19 | +0.4% (+0.7) |
| Trailing stop 15% | 721 | 42% | +3.4% | -3.8% | +22.6% / -10.6% | 33 | +1.8% (+2.1) |
| Trailing stop 20% | 721 | 48% | +6.6% | -0.7% | +27.6% / -12.9% | 44 | +4.3% (+2.7) |
| Candle-low stop (2-8%), then trail 15% | 721 | 30% | +1.9% | -8.2% | +24.2% / -7.5% | 22 | +0.7% (+0.9) |


## Reading this

- A positive average with a much lower median means a few big winners carry the result; most individual trades did worse than the average.
- Compare every number with the Nifty 500 column. When the market rises, most stocks rise; the scanner adds value only if its picks beat the index.
- The gap between the average best close and the final return shows how much of the gain is given back by holding to a fixed date. That is what a trailing stop or target tries to keep.
- Yahoo prices; symbols it doesn't carry are missing (survivorship bias). Corporate actions Yahoo hasn't adjusted can show up as false big moves (e.g. TRIVENI, Jul 2026).