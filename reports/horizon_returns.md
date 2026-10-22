# Price after the trigger: 2 to 12 weeks

Generated 2026-10-22 18:10 UTC by `scripts/horizon_returns.py`.

Buy when price crosses the trigger (the signal candle's high; the completed week's candle for `Wkly_upswing`) within 3 sessions (5 for weekly), then just hold. No stop-loss, no target, no costs deducted. **Up** = share of trades above the entry price at that point. **Best / worst close** = the highest and lowest close reached at any time up to that point, averaged across trades. **Beat Nifty 500** = share of trades that did better than the index over the same days. Recent signals only count for horizons that have fully passed, so longer horizons have fewer trades and lean towards older signals.

Per-trade prices: `data/model/horizon_returns.csv`.

## 63_30_daily

6300 signals, 4740 crossed the trigger (31 Dec 2020 to 21 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 4732 | 48% | +0.8% | -0.2% | +4.9% / -4.1% | +0.6% | 44% |
| 4 weeks | 4724 | 52% | +2.0% | +0.4% | +8.0% / -5.8% | +1.1% | 44% |
| 6 weeks | 4717 | 54% | +3.0% | +1.1% | +10.5% / -7.1% | +1.6% | 47% |
| 8 weeks | 4682 | 56% | +4.1% | +2.0% | +13.0% / -8.0% | +2.2% | 49% |
| 12 weeks | 4619 | 58% | +6.3% | +3.3% | +17.7% / -9.5% | +3.3% | 49% |

## Bullish_Scanner

5084 signals, 4204 crossed the trigger (31 Dec 2020 to 19 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 4197 | 55% | +2.1% | +0.7% | +6.0% / -3.4% | +0.7% | 50% |
| 4 weeks | 4184 | 59% | +3.5% | +2.1% | +9.3% / -4.9% | +1.5% | 51% |
| 6 weeks | 4172 | 60% | +4.6% | +2.8% | +11.9% / -6.0% | +2.0% | 53% |
| 8 weeks | 4153 | 60% | +5.6% | +3.7% | +14.5% / -7.0% | +2.8% | 52% |
| 12 weeks | 4115 | 63% | +8.5% | +5.4% | +19.1% / -8.3% | +4.1% | 53% |

## Wkly_upswing

1119 signals, 750 crossed the trigger (18 Aug 2017 to 16 Oct 2026).

| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |
|---|---|---|---|---|---|---|---|
| 2 weeks | 747 | 47% | +1.1% | -0.7% | +6.9% / -5.7% | +0.7% | 42% |
| 4 weeks | 742 | 51% | +2.6% | +0.5% | +11.2% / -8.0% | +1.1% | 46% |
| 6 weeks | 739 | 54% | +3.9% | +1.2% | +14.9% / -9.5% | +1.3% | 49% |
| 8 weeks | 735 | 55% | +5.3% | +2.0% | +18.3% / -11.0% | +1.7% | 49% |
| 12 weeks | 721 | 53% | +8.9% | +1.9% | +25.0% / -12.8% | +3.1% | 47% |

## Side by side, signals since 31 Dec 2020

Average return / share of trades up, over the same period for every scanner.

| Horizon | 63_30_daily | Bullish_Scanner | Wkly_upswing |
|---|---|---|---|
| 2 weeks | +0.8% / 48% (n=4732) | +2.1% / 55% (n=4197) | +1.2% / 47% (n=573) |
| 4 weeks | +2.0% / 52% (n=4724) | +3.5% / 59% (n=4184) | +2.7% / 53% (n=568) |
| 6 weeks | +3.0% / 54% (n=4717) | +4.6% / 60% (n=4172) | +4.2% / 54% (n=565) |
| 8 weeks | +4.1% / 56% (n=4682) | +5.6% / 60% (n=4153) | +6.1% / 57% (n=561) |
| 12 weeks | +6.3% / 58% (n=4619) | +8.5% / 63% (n=4115) | +9.8% / 52% (n=547) |

## Trailing stop vs just holding (up to 12 weeks)

Same entries as above. Each trailing stop starts that % below the entry and, after every close, moves up to that % below the highest close so far (it never moves down). It exits when a low touches it (at the open on a gap-down), or after 12 weeks at the close. The last row starts with the tight signal-candle-low stop instead. After 0.25% round-trip costs. Only signals with a full 12 weeks of prices are used, so every rule is judged on the same trades.

### 63_30_daily

| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |
|---|---|---|---|---|---|---|---|
| Hold 12 weeks, no stop | 4615 | 57% | +6.0% | +3.1% | +19.3% / -11.7% | 60 | +2.8% (+8.8) |
| Trailing stop 10% | 4615 | 42% | +2.5% | -3.0% | +16.1% / -7.4% | 30 | +1.0% (+4.7) |
| Trailing stop 15% | 4615 | 51% | +4.4% | +0.3% | +18.6% / -10.0% | 45 | +2.3% (+8.3) |
| Trailing stop 20% | 4615 | 54% | +5.2% | +1.9% | +19.3% / -11.3% | 53 | +2.5% (+8.5) |
| Candle-low stop (2-8%), then trail 15% | 4615 | 20% | +1.3% | -3.1% | +22.1% / -3.9% | 16 | +0.3% (+1.7) |

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