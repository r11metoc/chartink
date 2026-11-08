"""
valuepick_score.py: score a Screener.in export against the Valuepick thesis.

Same logic as the 'Highs Scan' / 'Screener Import' sheets in
Valuepick_Thesis_Scoring_Model.xlsx, so results match the workbook.

Usage:
    python scripts/valuepick_score.py data/fundamentals/latest.csv \
        --out reports/valuepick_watchlist.csv --telegram reports/valuepick_msg.txt

Input: any Screener export with (some of) the columns in COLS below.
Works with both the 'hitting highs' export and the 14-column import format.
Percent columns are expected as Screener gives them (25.3 = 25.3%).
Information only: this does not change any live buy/sell rule.
"""
import argparse
import csv
import math
import sys

# ---------------------------------------------------------------- CONFIG
CONFIG = {
    # factor: (weight, direction, [T1..T5]); score = number of thresholds cleared (0-5)
    "factors": {
        "sales_growth":  (0.15, "higher", [5, 10, 15, 25, 40]),       # % (3Y CAGR, else 1Y)
        "cap_eff":       (0.15, "higher", [8, 12, 16, 20, 30]),       # % ROCE, else ROE
        "valuation":     (0.10, "lower",  [3.0, 2.0, 1.5, 1.0, 0.7]), # PEG = P/E / growth%
        "balance_de":    (0.10, "lower",  [2.0, 1.0, 0.5, 0.25, 0.10]),  # Debt/Equity if present
        "balance_dpat":  (0.10, "lower",  [5, 3, 2, 1, 0.5]),         # else Debt / PAT (years)
        "promoter":      (0.10, "higher", [30, 40, 50, 60, 70]),      # %
        "size":          (0.10, "lower",  [50000, 10000, 3000, 1000, 500]),  # mcap Rs Cr
        "momentum":      (0.05, "higher", [0, 10, 20, 35, 50]),       # % profit growth (3Y, else 1Y)
    },
    # optional judgement scores (0-5), weights 0.15 / 0.10 in the workbook; keyed by NSE or BSE code
    "theme_weight": 0.15,
    "niche_weight": 0.10,
    "manual": {
        # "GENXAI": {"theme": 4, "niche": 2},
    },
    "shortlist_min": 65,
    "maybe_min": 50,
    "low_data_coverage": 0.70,
    "reject_promoter_below": 30,
    "flag_cfo_pat_below": 0.5,
    "flag_debtor_days_above": 120,
    "flag_debtor_days_rise_above": 20,
    "flag_debt_jump_ratio": 0.5,      # debt change > 50% of debt
    "flag_profit_spike_above": 500,   # % profit growth: likely one-off
    "dip_zone_from_high": -20,        # % below 52w high = his preferred entry zone
}

# Screener column names (first match wins)
COLS = {
    "name": ["Name"],
    "nse": ["NSE Code"], "bse": ["BSE Code"],
    "industry": ["Industry", "Industry Group"],
    "price": ["Current Price", "Current price"],
    "mcap": ["Market Capitalization"],
    "pe": ["Price to Earning"],
    "roce": ["Return on capital employed"],
    "roe": ["Return on equity"],
    "de": ["Debt to equity"],
    "promoter": ["Promoter holding"],
    "sales3y": ["Sales growth 3Years"],
    "profit3y": ["Profit growth 3Years"],
    "sales1y": ["Sales growth"],
    "profit1y": ["Profit growth"],
    "pat": ["Profit after tax"],
    "cfo": ["CFO"],
    "debt": ["Debt"],
    "debt_change": ["Debt Change"],
    "debtor_days": ["Debtor days"],
    "debtor_days_ch": ["Debtor Days Ch"],
    "high": ["High price"],
}


# ---------------------------------------------------------------- helpers
def num(x):
    try:
        v = float(str(x).replace(",", "").strip())
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def get(row, key):
    for c in COLS[key]:
        if c in row and str(row[c]).strip() != "":
            return row[c] if key in ("name", "nse", "bse", "industry") else num(row[c])
    return None


def first(*vals):
    for v in vals:
        if v is not None:
            return v
    return None


def band(x, direction, t):
    """0-5: how many thresholds x clears (inclusive)."""
    if x is None:
        return None
    if direction == "higher":
        return sum(x >= ti for ti in t)
    return sum(x <= ti for ti in t)


# ---------------------------------------------------------------- core
def score_row(row, cfg=CONFIG):
    f = cfg["factors"]
    d = {k: get(row, k) for k in COLS}

    # derived metrics
    pe = d["pe"]
    if pe is None and d["mcap"] is not None and d["pat"] is not None:
        pe = d["mcap"] / d["pat"] if d["pat"] > 0 else None
    loss_making = (d["pat"] is not None and d["pat"] <= 0) or (d["pe"] is not None and d["pe"] <= 0)
    growth = first(d["sales3y"], d["sales1y"])
    peg = pe / growth if (pe and pe > 0 and growth and growth > 0) else None
    debt_pat = None
    if d["debt"] is not None and d["pat"] is not None:
        debt_pat = d["debt"] / d["pat"] if d["pat"] > 0 else 99
    cfo_pat = d["cfo"] / d["pat"] if (d["cfo"] is not None and d["pat"] and d["pat"] > 0) else None
    from_high = (d["price"] / d["high"] - 1) * 100 if (d["price"] and d["high"]) else None

    # factor scores (None = no data -> excluded, remaining weights rescaled)
    s, w = {}, {}
    s["sales_growth"] = band(growth, *f["sales_growth"][1:])
    s["cap_eff"] = band(first(d["roce"], d["roe"]), *f["cap_eff"][1:])
    s["valuation"] = 0 if loss_making else band(peg, *f["valuation"][1:])
    if d["de"] is not None:
        s["balance"] = band(d["de"], *f["balance_de"][1:]); w["balance"] = f["balance_de"][0]
    else:
        s["balance"] = band(debt_pat, *f["balance_dpat"][1:]); w["balance"] = f["balance_dpat"][0]
    s["promoter"] = band(d["promoter"], *f["promoter"][1:])
    s["size"] = band(d["mcap"], *f["size"][1:])
    s["momentum"] = band(first(d["profit3y"], d["profit1y"]), *f["momentum"][1:])
    for k in ("sales_growth", "cap_eff", "valuation", "promoter", "size", "momentum"):
        w[k] = f[k][0]

    code = d["nse"] or d["bse"] or ""
    man = cfg["manual"].get(str(code).strip(), {})
    if "theme" in man:
        s["theme"], w["theme"] = man["theme"], cfg["theme_weight"]
    if "niche" in man:
        s["niche"], w["niche"] = man["niche"], cfg["niche_weight"]

    have = {k: v for k, v in s.items() if v is not None}
    wsum = sum(w[k] for k in have)
    total_w = sum(w.values())
    score = sum(have[k] * w[k] for k in have) / wsum * 20 if wsum else None
    coverage = wsum / total_w if total_w else 0

    # flags
    flags = []
    if cfo_pat is not None and cfo_pat < cfg["flag_cfo_pat_below"]:
        flags.append("weak cash conversion")
    if d["cfo"] is not None and d["cfo"] < 0:
        flags.append("negative CFO")
    if d["debtor_days"] is not None and d["debtor_days"] > cfg["flag_debtor_days_above"]:
        flags.append("high debtor days")
    if d["debtor_days_ch"] is not None and d["debtor_days_ch"] > cfg["flag_debtor_days_rise_above"]:
        flags.append("debtor days rising")
    if d["debt"] and d["debt"] > 0 and d["debt_change"] is not None and d["debt_change"] > d["debt"] * cfg["flag_debt_jump_ratio"]:
        flags.append("debt jumped")
    if d["profit1y"] is not None and d["profit1y"] > cfg["flag_profit_spike_above"]:
        flags.append("one-off profit spike?")

    # verdict
    if score is None:
        verdict = ""
    elif d["promoter"] is not None and d["promoter"] < cfg["reject_promoter_below"]:
        verdict = "Reject: low promoter"
    elif score >= cfg["shortlist_min"]:
        verdict = "Shortlist" if not flags else "Shortlist - check flags"
    elif score >= cfg["maybe_min"]:
        verdict = "Maybe"
    else:
        verdict = "Skip"
    if verdict and coverage < cfg["low_data_coverage"]:
        verdict += " (low data)"

    entry = ""
    if from_high is not None:
        entry = "dip zone" if from_high <= cfg["dip_zone_from_high"] else "near high: wait for dip/results"

    return {
        "name": d["name"], "code": code, "industry": d["industry"],
        "score": round(score, 1) if score is not None else None,
        "coverage": round(coverage, 2), "verdict": verdict, "flags": "; ".join(flags),
        "entry": entry,
        "pe": round(pe, 1) if pe else None, "peg": round(peg, 2) if peg else None,
        "cfo_pat": round(cfo_pat, 2) if cfo_pat is not None else None,
        "from_high_pct": round(from_high, 1) if from_high is not None else None,
        "mcap": d["mcap"], "roce": d["roce"], "promoter": d["promoter"],
        **{f"s_{k}": v for k, v in s.items()},
    }


def score_file(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = [r for r in csv.DictReader(fh) if (r.get("Name") or "").strip()]
    out = [score_row(r) for r in rows]
    out = [o for o in out if o["score"] is not None]
    out.sort(key=lambda o: -o["score"])
    for i, o in enumerate(out, 1):
        o["rank"] = i
    return out


def telegram_text(results, top=8):
    clean = [r for r in results if r["verdict"] == "Shortlist"][:top]
    flagged = [r for r in results if r["verdict"].startswith("Shortlist - check")][:5]
    lines = ["VALUEPICK WATCHLIST (fundamentals, info only)", ""]
    lines.append("Clean shortlist:")
    for r in clean:
        lines.append(f"  {r['name']} ({r['code']}) {r['score']:.0f} | P/E {r['pe']} | ROCE {r['roce']}% | {r['entry']}")
    if flagged:
        lines += ["", "High score, check first:"]
        for r in flagged:
            lines.append(f"  {r['name']} {r['score']:.0f}: {r['flags']}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--out", default="valuepick_watchlist.csv")
    ap.add_argument("--telegram", default=None)
    a = ap.parse_args(argv)
    res = score_file(a.csv)
    if not res:
        sys.exit("No scorable rows found.")
    keys = list(dict.fromkeys(k for r in res for k in r))
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=keys)
        wr.writeheader(); wr.writerows(res)
    msg = telegram_text(res)
    if a.telegram:
        with open(a.telegram, "w", encoding="utf-8") as fh:
            fh.write(msg)
    print(msg)


if __name__ == "__main__":
    main()
