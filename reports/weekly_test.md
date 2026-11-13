# Wkly_upswing: buy at once or wait for the trigger?

608 weekly signals in the backtest exports. Live exit for all (30-day EMA, 15% stop, 250 sessions), after 0.25% costs. Trades still open are left out.

## With the 4% volatility filter

| Entry | Weekly trades | Win | Avg | Avg win / loss | Days | 2019-22 avg | 2023-26 avg | Portfolio per year | Worst fall |
|---|---|---|---|---|---|---|---|---|---|
| Buy-stop 5 sessions (live) | 239 | 42% | +3.01% | +15.5% / -6.0% | 29 | +4.26% | +1.99% | 26.9% | -9.2% |
| Buy-stop 10 sessions | 261 | 42% | +2.95% | +15.5% / -6.1% | 29 | +4.15% | +2.05% | 26.8% | -9.2% |
| Buy-stop 20 sessions | 280 | 41% | +2.62% | +15.4% / -6.2% | 29 | +3.49% | +1.95% | 26.9% | -9.3% |
| Buy at next open (no trigger) | 325 | 40% | +2.81% | +15.3% / -5.6% | 28 | +3.45% | +2.31% | 25.8% | -9.4% |

## Without the 4% volatility filter

| Entry | Weekly trades | Win | Avg | Avg win / loss | Days | 2019-22 avg | 2023-26 avg | Portfolio per year | Worst fall |
|---|---|---|---|---|---|---|---|---|---|
| Buy-stop 5 sessions (live) | 406 | 39% | +3.65% | +22.2% / -8.1% | 28 | +2.90% | +4.24% | 25.2% | -11.0% |
| Buy-stop 10 sessions | 459 | 38% | +3.21% | +21.5% / -7.9% | 28 | +2.45% | +3.79% | 25.4% | -11.0% |
| Buy-stop 20 sessions | 501 | 37% | +3.04% | +21.4% / -7.9% | 28 | +2.57% | +3.40% | 25.9% | -10.5% |
| Buy at next open (no trigger) | 606 | 38% | +3.24% | +20.1% / -7.3% | 27 | +2.72% | +3.67% | 24.8% | -10.4% |

