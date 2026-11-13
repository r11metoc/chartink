# Chartink scanner tracker

A bot that runs entirely on GitHub. It reads the three scanners on the
Chartink dashboard [Atlas NG Scanners](https://chartink.com/dashboard/45863)
(`63_30_daily`, `Bullish_Scanner`, `Wkly_upswing`), applies one fixed
breakout rule to every signal, keeps a paper portfolio, and shows it all on a
phone app and in Telegram.

- App: <https://r11metoc.github.io/chartink/> (install: Chrome ⋮ → Add to Home
  screen, or Safari Share → Add to Home Screen)
- Paper trades and information only. Not advice.

## The rule

- **Trigger** = high of the signal candle (the day's high; the week's high for
  `Wkly_upswing`).
- **Buy**: buy-stop at the trigger for 3 sessions after the signal (5 for
  weekly); cancelled if the price hasn't crossed by then. Filled at the
  trigger, or at the open on a gap-up.
- **Sell**: at the next open after a close below the 30-day EMA; 15% stop-loss
  for every scanner; at most 250 sessions.
- **Slots**: 15 positions, one per stock. When short of slots: mid caps first,
  then large, then small.
- **Filters**: `Wkly_upswing` only when ATR(14) < 4% of price; `63_30_daily`
  only within 10% of the 52-week high.
- Changed on 13 Nov 2026 from a 50-day simple average exit and a 12% stop (15%
  weekly): better in both 2019-22 and 2023-26 with a smaller worst fall
  (`reports/rule_compare.md`). Longer buy-stop windows and
  dropping the volatility filter were tested and did worse.
- Returns are after 0.25% round-trip costs.

Backtest Feb 2019 to Nov 2026 (`reports/stock_outcomes.md`, the app's Backtest
page; refreshed every Saturday): 6,487 trades, +4.2% a trade, 43% wins, held
about 31 days; ₹10L in 15 slots became about ₹62L, 26.6% a year, worst fall
−9.2%, against the Nifty 500's 13.2% a year and −38%. Tested and rejected: Nifty trend filter, skipping small caps, volume or
sector ranking, buying pullbacks, +8% targets, trailing stops, a 20-day exit,
longer buy-stop windows (`reports/entry_window_test.md`).

## The app

**Today**: the holding count and P&L, **To do** (sells at the next open and the
buy-stops to place; tap a buy-stop for its fundamentals) and **On the scanners
now** (every stock in the latest scan and what the rule did with it).

**More** (swipe left/right between pages on a phone):
- **Breakouts**: every signal of the last 90 days, its price vs its own trigger,
  and what the paper book did with it (holding, sold, no free slot, skipped…).
- **Holdings**: done this week, open positions, sold trades.
- **Market**: Nifty 50 / Nifty 500 vs their 50- and 200-day averages, India
  VIX, breadth, sectors gaining or losing picks (context only), results coming
  for holdings and buy-stops, and the **Data check** (scan freshness, prices,
  every paper trade against the daily prices, fundamentals coverage).
- Sectors, Backtest, Fundamentals, Upload, How it works.

## Fundamentals (information only)

- **Your main screen** (`scripts/main_screen.py`): price > 80% of the 52-week
  high, market cap ₹100–5,000 Cr, ROCE > 15, OPM > 5, debt/equity < 1.1,
  pledge = 0, promoter > 55, profit growth > 40 or quarterly YoY > 100, debtor
  days < 150, P/E < 20. Plus your Valuepick score (`scripts/valuepick_score.py`).
  Banks: ROE in place of ROCE; OPM, debt/equity and debtor days don't apply.
- **Scanner stocks**: figures from each stock's Screener.in company page
  (`scripts/screener_company.py`, monthly, a few seconds apart), Yahoo as the
  fallback. Screener allows personal viewing only, so the figures live in a
  git-ignored cache carried in GitHub's private Actions cache; the public app
  shows pass/fail and which conditions fail, Telegram shows the figures.
  Pledge isn't on Screener's public pages.
- **More → Fundamentals** (`scripts/fundamental_scan.py`): every stock in
  your latest uploaded Screener export, ranked by Valuepick (Shortlist,
  Check flags, Maybe, Your screen). A new upload replaces the old list.
- **Results dates** (`scripts/market.py`): board-meeting dates from each
  stock's Screener announcements, read daily for held, buy-stop and scanner
  stocks (BSE's calendar is blocked from GitHub; Yahoo is used for large caps).

## Telegram

The bot pushes only **Today's actions** (set a buy-stop, bought, sell, closed).
Everything else on request, answered within about 15 minutes
(`scripts/telegram_commands.py`, only from your chat):
`/today`, `/holdings`, `/scanners`, `/breakouts`, `/fundamentals`, `/help`.

## Uploads (More → Upload)

Uses your own fine-grained GitHub token (only this repo; Contents and Actions:
read and write), saved in your browser only.
- **Chartink backtest export** → replaces `data/backtest/<scanner>.csv`, then
  starts the retrain and a scan.
- **Screener export** (Excel or CSV) → `data/fundamentals/uploads/`, replacing
  the previous one, then starts a scan.

## Schedule and workflows

- **Timer** (`keeper.yml`): GitHub runs short-interval schedules only every few
  hours, so this job stays up ~5.5 hours, starts `scan.yml` in auto mode every
  15 minutes, then restarts itself (its own 3-hourly schedule only revives it).
- **Scan** (`scan.yml`): the gate (`scripts/slot_gate.py`) scans once per slot,
  10:00, 13:00 and 15:00 IST, Mon–Fri (each slot open until the next, the last
  until 20:00). A scan reads the dashboard (`scrape_dashboard.py`, waits until
  every widget's rows stop changing), repairs half-read scans
  (`db.repair_partial_reads`), refreshes prices (Yahoo), the results calendar
  and fundamentals, sends Telegram alerts, rebuilds `site/data.json`, commits
  `data/chartink.db` and publishes the app. Manual runs: Actions → "Chartink
  breakout scan" → Run workflow.
- **Signal model** (`signal_model.yml`): Saturday 08:47 IST, or manually with
  `mode=train`, rebuilds the dataset from the backtest exports plus the live
  triggers and re-runs the backtests. `mode=window_test` runs the entry-window
  test.

## Setup (one time)

1. Telegram: create a bot with @BotFather, add repo secrets
   `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
2. Settings → Pages → Source: **GitHub Actions**.
3. Actions → "Timer" → Run workflow (once; it keeps itself running).

## Updating from a PC

Updates arrive as a git bundle. In the repo folder, paste one block like this
(it stops at the first error and deletes the bundle only after a successful
push):

```
git fetch origin claude/scanner-github-breakout-tracking-p7spin
if ($LASTEXITCODE -eq 0) { git reset --hard FETCH_HEAD }
if ($LASTEXITCODE -eq 0) { git fetch <bundle> HEAD }
if ($LASTEXITCODE -eq 0) { git cherry-pick <base>..FETCH_HEAD }
if ($LASTEXITCODE -eq 0) { git push }
if ($LASTEXITCODE -eq 0) { Remove-Item <bundle>; "UPDATE DONE" }
```

## Data

`data/chartink.db` (SQLite): `runs`, `results` (every stock in every scan),
`breakouts` (stocks new to a scanner vs its previous scan), `daily_prices`,
`backtest_hits`, `slots`, `fundamentals` (Yahoo), `results_calendar`,
`yahoo_events`, `dip_alerts`.

```bash
sqlite3 data/chartink.db "select * from breakouts order by detected_at desc limit 20;"
```

Backtest exports: `data/backtest/<scanner>.csv` (Chartink's Date, Symbol,
Marketcapname, Sector). Scanner names come from each widget's title on the
dashboard (`scrape_dashboard.py`); `CHARTINK_SCANNER_NAMES` overrides them.
