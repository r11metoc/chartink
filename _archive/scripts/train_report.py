"""Build win-rate tables and a per-scanner logistic regression from the
labeled backtest outcomes (fetch_price_outcomes.py must run first), then
write a report to the repo and a compact summary to Telegram.

Each scanner gets its own model/statistics rather than a single pooled
one, since they're different strategies with different behavior. This is
descriptive + a simple model over categorical features (sector, market-cap
tier) - not a technical/price-pattern model, and the sample sizes here are
small enough that the win-rate tables are probably more trustworthy than
the logistic regression's coefficients. Both are reported with sample
sizes and rough confidence intervals so the numbers aren't over-trusted.
"""

from __future__ import annotations

import html
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score

import db
from fetch_price_outcomes import HORIZON_DAYS, SUCCESS_THRESHOLD_PCT
from notify import send_telegram_message

REPORT_PATH = Path(__file__).resolve().parent.parent / "reports" / "model_report.md"
MIN_GROUP_N = 5   # don't report a sector/marketcap win rate below this sample size
MIN_TRAIN_N = 30  # don't attempt a holdout-validated model below this sample size


def _wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for a binomial proportion - more honest
    than a plain normal approximation at small n."""
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def _win_rate_table(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    rows = []
    for group, sub in df.groupby(group_col):
        n = len(sub)
        if n < MIN_GROUP_N:
            continue
        wins = int(sub["label"].sum())
        rate = wins / n
        lo, hi = _wilson_ci(wins, n)
        rows.append({group_col: group, "n": n, "win_rate": rate, "ci_low": lo, "ci_high": hi})
    return pd.DataFrame(rows).sort_values("win_rate", ascending=False)


def _train_model(df: pd.DataFrame) -> dict | None:
    """Time-ordered train/test split (train = earlier 80%, test = most
    recent 20%) to avoid lookahead bias. Returns None if there isn't enough
    data to validate honestly."""
    df = df.sort_values("hit_date")
    n = len(df)
    if n < MIN_TRAIN_N:
        return None

    split = int(n * 0.8)
    train, test = df.iloc[:split], df.iloc[split:]
    if train["label"].nunique() < 2 or len(test) < 5:
        return None

    features = pd.get_dummies(df[["sector", "marketcap"]], dummy_na=True)
    X_train, X_test = features.loc[train.index], features.loc[test.index]
    y_train, y_test = train["label"], test["label"]

    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "train_n": len(train),
        "test_n": len(test),
        "accuracy": accuracy_score(y_test, pred),
        "precision": precision_score(y_test, pred, zero_division=0),
        "recall": recall_score(y_test, pred, zero_division=0),
    }
    if y_test.nunique() == 2:
        metrics["auc"] = roc_auc_score(y_test, proba)

    coefs = sorted(zip(features.columns, model.coef_[0]), key=lambda kv: kv[1], reverse=True)
    metrics["top_positive"] = coefs[:5]
    metrics["top_negative"] = coefs[-5:]
    return metrics


def build_report(outcomes: list[dict]) -> tuple[str, dict[str, dict]]:
    """Returns (markdown_report, per_scanner_summary_for_telegram)."""
    df = pd.DataFrame(outcomes)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Chartink backtest outcome report",
        "",
        f"Generated {generated_at}.",
        "",
        "## Methodology",
        "",
        f"- **Success rule**: a historical scan trigger is labeled a *real breakout* "
        f"if price closed at least **+{SUCCESS_THRESHOLD_PCT}%** above the trigger-day "
        f"close within **{HORIZON_DAYS} trading days**; otherwise it's a *fake trigger* (hold).",
        "- **Price source**: Yahoo Finance (NSE, `.NS` suffix). Symbols that don't resolve "
        "(delisted, renamed, or a ticker format Yahoo doesn't recognize) are skipped entirely, "
        "which introduces some survivorship bias - stocks that got delisted after a bad "
        "move are underrepresented.",
        "- **Each scanner is modeled and reported separately** - they're different "
        "strategies with different behavior, so pooling them would blur real differences.",
        "- Win rates below are shown with a 95% confidence interval (Wilson score) - "
        "treat any group with a wide interval as noisy, not a reliable edge.",
        "- The model (where trained) uses only sector and market-cap tier as features - "
        "no price/volume/technical features - and is validated on a time-ordered holdout "
        "(most recent 20% of each scanner's data), not random k-fold, to avoid lookahead bias.",
        "- Sample sizes here are small (hundreds of rows per scanner at most). Take the "
        "logistic regression's coefficients as suggestive, not proven; the win-rate tables "
        "are the more defensible output.",
    ]

    telegram_summary: dict[str, dict] = {}

    for scanner_name, sub in df.groupby("scanner_name"):
        n = len(sub)
        wins = int(sub["label"].sum())
        rate = wins / n if n else 0.0
        lo, hi = _wilson_ci(wins, n)

        lines += [
            "",
            f"## {scanner_name}",
            "",
            f"**Overall**: {wins}/{n} triggers were real breakouts "
            f"({rate:.0%}, 95% CI {lo:.0%}-{hi:.0%})",
            "",
        ]

        sector_table = _win_rate_table(sub, "sector")
        lines.append(f"### Win rate by sector (n ≥ {MIN_GROUP_N})")
        lines.append("")
        if sector_table.empty:
            lines.append("Not enough data per sector yet.")
        else:
            lines.append("| Sector | n | Win rate | 95% CI |")
            lines.append("|---|---|---|---|")
            for _, r in sector_table.iterrows():
                lines.append(f"| {r['sector']} | {r['n']} | {r['win_rate']:.0%} | {r['ci_low']:.0%}-{r['ci_high']:.0%} |")

        mcap_table = _win_rate_table(sub, "marketcap")
        lines += ["", f"### Win rate by market-cap tier (n ≥ {MIN_GROUP_N})", ""]
        if mcap_table.empty:
            lines.append("Not enough data per tier yet.")
        else:
            lines.append("| Tier | n | Win rate | 95% CI |")
            lines.append("|---|---|---|---|")
            for _, r in mcap_table.iterrows():
                lines.append(f"| {r['marketcap']} | {r['n']} | {r['win_rate']:.0%} | {r['ci_low']:.0%}-{r['ci_high']:.0%} |")

        model_metrics = _train_model(sub)
        lines += ["", "### Model (logistic regression, sector + market-cap tier)", ""]
        if model_metrics is None:
            lines.append(f"Not enough data to train and validate a model honestly (need ≥{MIN_TRAIN_N} rows "
                          "with both outcomes present in the training split).")
        else:
            lines.append(f"Trained on {model_metrics['train_n']} rows, tested on the most recent "
                          f"{model_metrics['test_n']} (time-ordered holdout):")
            lines.append("")
            lines.append(f"- Accuracy: {model_metrics['accuracy']:.0%}")
            lines.append(f"- Precision (of predicted breakouts, how many were real): {model_metrics['precision']:.0%}")
            lines.append(f"- Recall (of real breakouts, how many were caught): {model_metrics['recall']:.0%}")
            if "auc" in model_metrics:
                lines.append(f"- ROC-AUC: {model_metrics['auc']:.2f}")
            lines.append("")
            pos = ", ".join(f"{name} ({coef:+.2f})" for name, coef in model_metrics["top_positive"])
            neg = ", ".join(f"{name} ({coef:+.2f})" for name, coef in model_metrics["top_negative"])
            lines.append(f"- Features pushing toward 'real breakout': {pos}")
            lines.append(f"- Features pushing toward 'fake trigger': {neg}")

        telegram_summary[scanner_name] = {
            "n": n, "wins": wins, "rate": rate, "ci": (lo, hi),
            "top_sector": sector_table.iloc[0].to_dict() if not sector_table.empty else None,
            "model": model_metrics,
        }

    return "\n".join(lines), telegram_summary


def format_telegram_summary(summary: dict[str, dict]) -> str:
    lines = [f"<b>📈 Backtest model report</b> (+{SUCCESS_THRESHOLD_PCT}% in {HORIZON_DAYS}d = real breakout)"]
    for scanner_name, s in summary.items():
        lo, hi = s["ci"]
        lines.append(f"\n<b>{scanner_name}</b>")
        lines.append(f"  Win rate: {s['wins']}/{s['n']} ({s['rate']:.0%}, CI {lo:.0%}-{hi:.0%})")
        if s["top_sector"] is not None:
            ts = s["top_sector"]
            lines.append(f"  Best sector: {html.escape(ts['sector'])} ({ts['win_rate']:.0%}, n={ts['n']})")
        if s["model"] and "auc" in s["model"]:
            lines.append(f"  Model AUC: {s['model']['auc']:.2f} (n={s['model']['train_n']}+{s['model']['test_n']})")
    lines.append("\nFull tables + methodology: reports/model_report.md in the repo.")
    return "\n".join(lines)


def main() -> int:
    conn = db.connect()
    outcomes = db.outcomes_with_context(conn, HORIZON_DAYS, SUCCESS_THRESHOLD_PCT)
    conn.close()

    if not outcomes:
        print("No backtest outcomes found. Run fetch_price_outcomes.py first.")
        return 1

    report_md, summary = build_report(outcomes)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report_md, encoding="utf-8")
    print(f"Wrote {REPORT_PATH} ({len(outcomes)} outcomes across {len(summary)} scanners)")

    send_telegram_message(format_telegram_summary(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
