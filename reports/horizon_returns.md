# Price after the trigger: 2 to 12 weeks

Generated 2026-10-17 07:55 UTC by `scripts/horizon_returns.py`.

Buy when price crosses the trigger (the signal candle's high; the completed week's candle for `Wkly_upswing`) within 3 sessions (5 for weekly), then just hold. No stop-loss, no target, no costs deducted. **Up** = share of trades above the entry price at that point. **Best / worst close** = the highest and lowest close reached at any time up to that point, averaged across trades. **Beat Nifty 500** = share of trades that did better than the index over the same days. Recent signals only count for horizons that have fully passed, so longer horizons have fewer trades and lean towards older signals.

Per-trade prices: `data/model/horizon_returns.csv`.

## 63_30_daily

427 signals, 284 crossed the trigger (03 Feb 2026 to 07 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 283 | 47% | -0.6% | -1.4% | +5.7% / -6.2% | -0.5% | 49% |
| 4 weeks | 275 | 49% | +1.1% | -0.3% | +9.6% / -8.0% | -0.4% | 50% |
| 6 weeks | 266 | 51% | +2.6% | +0.4% | +12.2% / -9.2% | +0.4% | 51% |
| 8 weeks | 254 | 55% | +4.3% | +2.6% | +15.3% / -9.9% | +1.0% | 53% |
| 12 weeks | 236 | 58% | +7.0% | +3.7% | +20.9% / -11.0% | +1.2% | 54% |

## Bullish_Scanner

251 signals, 191 crossed the trigger (04 Feb 2026 to 15 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 185 | 54% | +1.7% | +0.7% | +5.8% / -3.9% | -0.8% | 54% |
| 4 weeks | 170 | 49% | +0.9% | -0.3% | +8.4% / -6.0% | -1.6% | 55% |
| 6 weeks | 161 | 57% | +1.9% | +1.8% | +10.0% / -7.8% | -1.6% | 58% |
| 8 weeks | 144 | 58% | +4.8% | +1.9% | +13.0% / -8.2% | -0.9% | 58% |
| 12 weeks | 113 | 61% | +6.3% | +6.5% | +16.7% / -9.6% | +0.2% | 61% |

## Wkly_upswing

770 signals, 524 crossed the trigger (08 Sep 2023 to 09 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 521 | 47% | +0.7% | -0.7% | +6.5% / -5.9% | +0.7% | 44% |
| 4 weeks | 517 | 52% | +2.2% | +0.5% | +10.6% / -8.2% | +1.4% | 45% |
| 6 weeks | 511 | 52% | +3.2% | +0.6% | +14.1% / -9.9% | +2.0% | 46% |
| 8 weeks | 507 | 52% | +3.6% | +1.1% | +16.9% / -11.4% | +2.7% | 46% |
| 12 weeks | 492 | 49% | +4.1% | -0.4% | +21.3% / -13.5% | +3.8% | 43% |

## Side by side, signals since 03 Feb 2026

Average return / share of trades up, over the same period for every scanner.

| Horizon | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| 2 weeks | -0.6% / 47% (n=283) | +1.7% / 54% (n=185) | +1.1% / 52% (n=80) |
| 4 weeks | +1.1% / 49% (n=275) | +0.9% / 49% (n=170) | +1.2% / 47% (n=76) |
| 6 weeks | +2.6% / 51% (n=266) | +1.9% / 57% (n=161) | +3.4% / 53% (n=70) |
| 8 weeks | +4.3% / 55% (n=254) | +4.8% / 58% (n=144) | +3.5% / 52% (n=66) |
| 12 weeks | +7.0% / 58% (n=236) | +6.3% / 61% (n=113) | +6.5% / 49% (n=51) |

## Trailing stop vs just holding (up to 12 weeks)

Same entries as above. Each trailing stop starts that % below the entry and, after every close, moves up to that % below the highest close so far (it never moves down). It exits when a low touches it (at the open on a gap-down), or after 12 weeks at the close. The last row starts with the tight signal-candle-low stop instead. After 0.25% round-trip costs. Only signals with a full 12 weeks of prices are used, so every rule is judged on the same trades.

### 63_30_daily

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 234 | 59% | +7.0% | +3.6% | +21.3% / -13.6% | 60 | +5.7% (+3.8) |
| Trailing stop 10% | 234 | 35% | -0.4% | -5.6% | +14.0% / -7.9% | 18 | -0.0% (-0.0) |
| Trailing stop 15% | 234 | 47% | +2.9% | -0.7% | +18.1% / -10.8% | 36 | +2.4% (+2.0) |
| Trailing stop 20% | 234 | 54% | +4.3% | +2.0% | +18.8% / -12.6% | 49 | +3.3% (+2.6) |
| Candle-low stop (2-8%), then trail 15% | 234 | 27% | +0.3% | -5.7% | +18.9% / -6.6% | 19 | +0.4% (+0.5) |

### Bullish_Scanner

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 111 | 61% | +6.0% | +6.2% | +18.4% / -13.5% | 60 | +5.8% (+3.1) |
| Trailing stop 10% | 111 | 41% | +1.6% | -3.3% | +15.0% / -7.9% | 29 | +2.2% (+1.8) |
| Trailing stop 15% | 111 | 50% | +3.6% | +1.4% | +18.8% / -11.8% | 43 | +4.2% (+2.4) |
| Trailing stop 20% | 111 | 59% | +5.2% | +4.9% | +18.2% / -13.9% | 53 | +5.0% (+2.7) |
| Candle-low stop (2-8%), then trail 15% | 111 | 32% | +2.5% | -4.2% | +20.8% / -6.3% | 25 | +2.8% (+2.0) |

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