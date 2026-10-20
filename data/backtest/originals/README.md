# Original Chartink backtest exports

Unedited copies of the exports uploaded on 20 Oct 2026, kept as a backup.
The bot does not read this folder; it reads the merged files one level up
(`data/backtest/<scanner>.csv`), which combine these exports with the
earlier, shorter ones.

| File | Scanner | Signals | Period |
|---|---|---|---|
| 63_30_daily_2020-12-29_to_2026-10-16.csv | 63_30_daily | 2,995 | 29 Dec 2020 to 16 Oct 2026 |
| Bullish_Scanner_2021-06-11_to_2026-10-19.csv | Bullish_Scanner | 1,688 | 11 Jun 2021 to 19 Oct 2026 |
| Wkly_upswing_2017-08-14_to_2026-10-12.csv | Wkly_upswing | 1,828 | 14 Aug 2017 to 12 Oct 2026 |

To add a newer export: drop it here under a dated name, and merge it into
`data/backtest/<scanner>.csv` (same columns: Date, Symbol, Marketcapname,
Sector). Duplicate rows are ignored by the bot.
