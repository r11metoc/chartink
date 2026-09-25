# Chartink breakout tracker

Scrapes the three scanner widgets on the public dashboard
[chartink.com/dashboard/45863](https://chartink.com/dashboard/45863) on a
schedule, stores every result in a SQLite database committed to this repo,
and sends a Telegram alert whenever a symbol newly appears in one of the
scanners (i.e. a fresh breakout).

## How it works

- `.github/workflows/scan.yml` runs on a cron schedule (daily at 09:23,
  12:23 and 15:23 IST, Mon–Fri) and can also be triggered manually from
  the Actions tab. Every scheduled run automatically sends the breakout
  alert (if any), the snapshot, sectors, digest and scanner track record,
  all together — no manual inputs needed for that. Manual runs still only
  send the extras you explicitly opt into via the `snap`/`digest` inputs,
  so you can trigger a quick breakout-only check without the noise.
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

Every scheduled run sends the current scan results too (not just new
breakouts) — you don't need to do anything for this. To get the same thing
on demand between scheduled runs, go to the Actions tab → "Chartink
breakout scan" → Run workflow → set `snap` to `true`.

Each scheduled run sends these messages (the digest ones with `digest`):

| Message | Answers | Contents |
|---|---|---|
| **📋 Snapshot** | What's on my scanners right now? | Every stock on each scanner, in a 🟢 BUY table and a ⏸ HOLD table |
| **🏭 Sectors in focus** | Which sectors are the scanners picking? | Top 5 sectors per scanner by backtest picks, last 7 and 30 days |
| **📊 Digest** | How are this month's new triggers doing? | Stocks that triggered in the last `days` (default 30), in BUY / HOLD tables per scanner |
| **📜 Scanner track record** | How often did past triggers work? | Per scanner: past triggers that rose 3%+ within 5 trading days, and the winners that gained 1–15% |

**BUY / HOLD rule** (snapshot and digest): BUY if the price now is above
the trigger price, HOLD otherwise. The trigger price is the price when the
stock last broke out on that scanner, or, if no breakout was recorded,
the earliest price seen for it there — so a stock that appeared this run
starts in HOLD at +0.0%. Each table shows Symbol, Trig, Now and Chg (% move
since the trigger), best move first. In the digest, `*` marks a stock that
has since dropped off the scanner (its "Now" is the last price seen). This
is a mechanical comparison of two stored prices, not a recommendation.

**Sectors in focus** comes from `data/backtest/*.csv` (`backtest_hits`),
so it's independent of the live scans.

**Scanner track record** needs `train_model.yml` to have run at least
once. It's history from the backtest file with real prices, not today's
picks — those moves already happened. It looks back 30 days (or `days` if
longer), since outcomes need 5 trading days to settle. The 1–15% filter
leaves out near-flat moves and extreme outliers, which are often corporate
actions like splits rather than genuine moves.

For a custom lookback, trigger the workflow manually with `digest` set to
`true` and `days` set to whatever window you want. Any message longer than
Telegram's 4096-character limit is split at section boundaries, and a
message Telegram rejects is resent as plain text rather than dropped.

## Backtest model: is a trigger a real breakout or a fake one?

The descriptive backtest context above (seen-before counts, sector focus)
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

Breakout alerts and the scan snapshot show **📚 Nx before** when available:
how many times this exact symbol has triggered this scanner in the backtest.

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

Or without touching git/sqlite at all: Actions tab → **"Chartink database query"** →
Run workflow → paste a `SELECT` statement into the `sql` field → the result
comes back as a message in Telegram (you still trigger it from GitHub, not
by typing into Telegram itself — this bot can only send messages, not
receive them). The connection is opened read-only at the SQLite level, so
`INSERT`/`UPDATE`/`DELETE`/`DROP`/etc. fail outright rather than risk
corrupting your tracked history. Results are capped at 50 rows and ~3800
characters to fit in a single Telegram message; narrow your query
(`LIMIT`, fewer columns) if it gets truncated.

## Changing the schedule

Edit the `cron` entries in `.github/workflows/scan.yml`. They're in UTC;
the defaults fire at 09:23, 12:23 and 15:23 IST on weekdays. They're kept
off the top of the hour on purpose: GitHub queues scheduled runs and is
busiest on the hour, so on-the-hour schedules tend to start later.
Scheduled runs can still be late (sometimes by hours), and they only run
from the repository's default branch.
