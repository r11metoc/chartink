# Archive

Not run by any workflow. Kept for reference only.

- `workflows/train_model.yml`, `scripts/fetch_price_outcomes.py`,
  `scripts/train_report.py`, `reports/model_report.md`: the old manual
  "real vs fake breakout" model (last run 24 Sep 2026). Superseded by
  `signal_model.yml` / `scripts/signal_model.py` and `scripts/learn.py`.
- `workflows/query.yml`, `scripts/run_query.py`: manual SQL-to-Telegram
  query. Run `sqlite3 data/chartink.db` locally instead.

To restore anything, `git mv` it back to its old folder.
