# Chartink breakout tracker

Scrapes the three scanner widgets on the public dashboard
[chartink.com/dashboard/45863](https://chartink.com/dashboard/45863) on a
schedule, stores every result in a SQLite database committed to this repo,
and sends a Telegram alert whenever a symbol newly appears in one of the
scanners (i.e. a fresh breakout).

## How it works

- `.github/workflows/scan.yml` runs on a cron schedule (daily at 09:30,
  12:30 and 15:30 IST, Mon–Fri) and can also be triggered manually from
  the Actions tab.
- `scripts/scrape_dashboard.py` opens the dashboard in a headless Chromium
  browser (via Playwright — the page is JS-rendered, so a plain HTTP request
  won't show the tables), and extracts each widget's table generically: it
  looks for a heading near each `<table>` to use as the scanner name, and
  picks the column that looks like the stock symbol.
- `scripts/db.py` stores every run in `data/chartink.db` (SQLite):
  - `runs` — one row per scrape
  - `results` — every symbol seen in every run, per scanner
  - `breakouts` — symbols that were *not* present in a scanner's previous
    run but *are* present now, tagged `kind`:
    - `fresh` — never seen on this scanner before
    - `retest` — seen before, dropped out for at least one run, and back
      again (the scan's own condition re-triggering at the same level)
- `scripts/notify.py` sends a Telegram message listing new breakouts,
  grouped by scanner, with a 🚀 (fresh) or 🔁 (retest) marker per symbol.
- The workflow commits `data/chartink.db` back to the repo after each run,
  so you get full git history of every scan.

The first run for each scanner just seeds the baseline (nothing to compare
against yet), so no breakout alert fires until the second run onward.

To get the current scan results in Telegram on demand (not just new
breakouts), go to the Actions tab → "Chartink breakout scan" → Run workflow
→ set `snap` to `true`. This sends two messages: the raw current results
for every scanner, and a **🎯 Buy / Hold list** that splits every symbol
currently on each scanner into:

- **BUY** — current price is above the price it had the first time it
  ever triggered that scanner (or, if it triggered again after dropping
  out, above that retest's price)
- **HOLD** — at or below that trigger price

This works even for symbols that have been sitting on a scanner
continuously since before formal breakout tracking started, since the
trigger price falls back to the earliest known price for that symbol on
that scanner. A symbol showing up for the very first time this run will
always start in HOLD (nothing to compare against yet but itself).

To get a digest of recent activity (top recurring symbols across scanners,
retest candidates, fresh breakouts), run the same workflow with `digest`
set to `true` and optionally `days` (default `7`) for the lookback
window. There's no fixed schedule for this — it's on-demand only, run it
whenever you want a report.

Every digest entry also shows a **BUY**/**HOLD** label per this fixed rule,
evaluated separately for each scanner: BUY only if the current known price
is above the price recorded when that breakout triggered, HOLD otherwise
(covers both "unchanged" and "below"). This is a mechanical comparison of
two stored numbers per the user's own stated rule, not an independent
recommendation, and it's only as fresh as the last time the symbol actually
appeared in that scanner's results — if it's since dropped out entirely,
the "current" price shown is stale.

The digest also always includes a **🏭 Sectors in focus** section, broken
out per scanner: the top 5 sectors by backtest-hit count in the last 7 days
and the last 30 days. This comes from `data/backtest/*.csv`
(`backtest_hits` table) and shows up even when there's been no live
breakout activity in the `days` window, since it's independent of
that lookback.

## Backtest model: is a trigger a real breakout or a fake one?

The descriptive backtest context above (seen-before counts, sector share)
doesn't say whether a scanner's trigger actually led anywhere - it has no
price data. `.github/workflows/train_model.yml` (manual only, Actions tab →
"Chartink backtest model training" → Run workflow) fills that gap:

1. `scripts/fetch_price_outcomes.py` fetches historical NSE prices from
   Yahoo Finance for every symbol in `backtest_hits`, and labels each
   historical trigger a **real breakout** if price closed at least **+3%**
   above the trigger-day close within **5 trading days**, otherwise a
   **fake trigger** (hold). Stored in a `backtest_outcomes` table.
2. `scripts/train_report.py` builds, **separately per scanner** (they're
   different strategies, not pooled):
   - overall win rate, with a 95% confidence interval
   - win rate by sector and by market-cap tier (min sample size enforced)
   - a logistic regression (sector + market-cap tier → probability of a
     real breakout), validated on a time-ordered holdout to avoid
     lookahead bias
   - writes the full tables to `reports/model_report.md` and a compact
     summary to Telegram

Read the "Methodology" section at the top of `reports/model_report.md`
before trusting any number in it — small sample sizes, survivorship bias
(delisted symbols just get skipped), and categorical-only features (no
price/volume patterns) all limit how much weight these results should
carry. The win-rate tables are more defensible than the logistic
regression's coefficients given how little data each scanner has.

This only needs re-running when you get a fresh backtest export from
Chartink (re-import it first per the section above) or want updated price
outcomes for symbols that have had more time to play out since the last
run.

## Setup

1. **Create a Telegram bot** (skip if you chose "no notifications" — you can
   still query the database directly):
   - Message [@BotFather](https://t.me/BotFather) on Telegram, run `/newbot`,
     and copy the token it gives you.
   - Send your new bot any message, then visit
     `https://api.telegram.org/bot<TOKEN>/getUpdates` in a browser to find
     your `chat.id`.
2. **Add repo secrets** (Settings → Secrets and variables → Actions):
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. Push this repo to GitHub (branch already set up if you're reading this
   from the PR). No other secrets are needed — the dashboard is public.
4. **Run it once manually** with debug on: Actions tab → "Chartink breakout
   scan" → "Run workflow" → set `debug` to `true`. This uploads a
   `chartink-debug-dump` artifact with the full page HTML and a screenshot,
   so you can confirm the three scanners were detected and split correctly.

## Scanner names

The dashboard doesn't expose a heading/title next to each widget's table
that can be detected generically, so the three scanners are matched by
**position**: the 1st, 2nd and 3rd non-empty table found on the page are
named, in order:

1. `Wkly_upswing`
2. `63_30_daily`
3. `Bullish_Scanner`

This order was verified against Chartink's own backtest CSV exports
(`data/backtest/`) by cross-checking the live scrape's results for today
against each scanner's most recent backtest entry — the original order
(guessed from the order the scanners were listed in) turned out to be
completely scrambled, so every symbol/price was always correct but was
attributed to the wrong scanner name until this was caught and the
existing database's `scanner_name` values were corrected retroactively.

This is set in `DEFAULT_SCANNER_NAMES` in `scripts/scrape_dashboard.py`, or
can be overridden per-run with a `CHARTINK_SCANNER_NAMES` env var
(comma-separated, no spaces needed). If the dashboard's scanners are ever
reordered, renamed, or a fourth one is added, update that list — a mismatch
between the number of tables found and the number of configured names logs
a warning and falls back to generic `Scanner N` labels rather than silently
mislabeling data.

Renaming a scanner effectively starts its breakout tracking over (the new
name has no prior run to diff against), so expect one baseline-seeding run
with no alert right after a name change.

## If the scraper doesn't split your three scanners correctly

The table/column detection in `scripts/scrape_dashboard.py` was written
without being able to load the live page directly (this environment's
network policy blocks chartink.com), so it uses generic heuristics rather
than Chartink-specific CSS selectors. If a debug run shows it merging
scanners, missing one, or picking the wrong column as the symbol, share the
`chartink-debug-dump` artifact contents and the selectors can be tightened
in `_EXTRACT_JS` and `_pick_symbol_index`.

## Backtest-based descriptive context

`data/backtest/*.csv` holds Chartink's own backtest exports (one per
scanner: Date, Symbol, Marketcapname, Sector — no price or return data).
`scripts/import_backtest.py` loads them into a `backtest_hits` table:

```bash
python scripts/import_backtest.py            # imports data/backtest/*.csv
python scripts/import_backtest.py some/dir    # or a custom directory
```

It's safe to re-run — duplicate (scanner, date, symbol) rows are skipped.
To refresh, export a new backtest CSV from Chartink, drop it into
`data/backtest/<scanner_name>.csv` (filename must match the scanner name),
and re-run the import.

Every breakout and digest entry now shows, when available:
- **📚 seen Nx before, last DATE** — how many times this exact symbol has
  triggered this scanner historically (exact match, high confidence)
- **sector ~X% of history** — how common this symbol's sector is among the
  scanner's historical hits (approximate — matched by loose substring
  comparison since the live scan's "Industry" labels don't exactly match
  the backtest's "Sector" labels)

This is **descriptive pattern-counting, not a return prediction** — the
backtest data has no outcome (win/loss, % gain) attached to any historical
hit, so there's nothing here that estimates whether a breakout will be
profitable. It only tells you how often this scanner has liked this
symbol/sector before.

## Querying the data yourself

```bash
sqlite3 data/chartink.db "select * from breakouts order by detected_at desc limit 20;"
sqlite3 data/chartink.db "select scanner_name, count(*) from results where run_id = (select max(id) from runs) group by scanner_name;"
```

## Changing the schedule

Edit the `cron` entries in `.github/workflows/scan.yml`. They're in UTC;
the defaults fire at 09:30, 12:30 and 15:30 IST on weekdays.
