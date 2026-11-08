# Fundamentals (Valuepick check, information only)

Every stock the Chartink scanners pick gets its fundamentals fetched from Yahoo
Finance automatically (scripts/update_fundamentals.py, each scan, cached 30 days)
and scored with the Valuepick logic: score 0-100, verdict and red flags on every
buy-stop alert, recent buy and holding. It never changes a buy or sell.

Optional: Screener.in exports uploaded from the app (More -> Upload, Excel or CSV) land in `uploads/`, one file per upload (a hand-placed `latest.csv` also works). For a stock in several exports the newest wins; uploads older than 180 days are ignored; columns an export lacks come from Yahoo takes priority for the
stocks it covers (Screener has ROCE and promoter holding directly).

Screener columns used (any subset works; more columns = better coverage):
Name, NSE Code, BSE Code, Industry, Current Price, Market Capitalization,
Price to Earning, Return on capital employed, Return on equity, Debt to equity,
Promoter holding, Sales growth 3Years, Profit growth 3Years, Sales growth,
Profit growth, Profit after tax, CFO, Debt, Debt Change, Debtor days,
Debtor Days Ch, High price.

Refresh it monthly or after results season.
