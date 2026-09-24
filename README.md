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
→ set `snapshot` to `true`. This sends every symbol currently in each
scanner as a single message, independent of what's changed since the last
run.

To get a digest of recent activity (top recurring symbols across scanners,
retest candidates, fresh breakouts), run the same workflow with `digest`
set to `true` and optionally `digest_days` (default `7`) for the lookback
window. There's no fixed schedule for this — it's on-demand only, run it
whenever you want a report.

Every digest entry also shows whether the current price is above, at, or
below the price recorded when that breakout triggered (✅ / ➖ / 🔻). This is
a mechanical comparison against the last known price for that symbol on
that scanner — not a recommendation — and it's only as fresh as the last
time the symbol actually appeared in the scan; if it's since dropped out
entirely, the "current" price shown is stale.

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
