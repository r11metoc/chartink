# Fundamentals (information only)

Two separate uses, neither changes a buy or sell:

1. **Scanner stocks** (tags on Today, details in Telegram): each stock's
   Screener.in company page is read monthly (`scripts/screener_company.py`;
   figures kept in the git-ignored `data/screener_cache.json`, carried in the
   private Actions cache), with Yahoo (`scripts/yahoo_fundamentals.py`) as the
   fallback. Checked against the main screen (`scripts/main_screen.py`) and the
   Valuepick score (`scripts/valuepick_score.py`).
2. **More → Fundamentals**: every stock in your latest Screener export, ranked
   by Valuepick (`scripts/fundamental_scan.py`).

## Uploads

Upload a Screener export from the app (More → Upload, Excel or CSV). It lands in
`uploads/<UTC time>.csv` and replaces the previous one: only the newest file is
used and the app deletes the older ones. For scanner stocks in the export, its
numbers take priority; columns it lacks come from the automatic source.

Columns used (any subset works; more columns = more checks):
Name, NSE Code, BSE Code, Industry, Current Price, High price, Market
Capitalization, Price to Earning, Return on capital employed, Return on equity,
OPM, Debt to equity, Pledged percentage, Promoter holding, Sales growth 3Years,
Profit growth 3Years, Sales growth, Profit growth, YOY Quarterly profit growth,
Profit after tax, CFO, Debt, Debt Change, Debtor days, Debtor Days Ch.

Adding Price to Earning, Debt to equity, Pledged percentage and YOY Quarterly
profit growth to your Screener screen lets all ten main-screen checks run.
