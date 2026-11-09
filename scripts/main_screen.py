"""The user's main fundamental screen (Screener-style query), checked on every
scanner stock. Information only: it never changes a buy or sell.

    Current price > High price * 0.8 AND
    Market Capitalization > 100 AND Market Capitalization < 5000 AND
    Return on capital employed > 15 AND OPM > 5 AND
    Debt to equity < 1.1 AND Pledged percentage = 0 AND Promoter holding > 55 AND
    (Profit growth > 40 OR YOY Quarterly profit growth > 100) AND
    Debtor Days < 150 AND Price to Earning < 20

A condition whose data is missing is reported as 'not checked' (Yahoo, the
automatic source, has no pledge data); it is not counted as a fail.
"""

from __future__ import annotations

MIN_CHECKED = 7  # a pass needs at least this many of the 10 checks to have data


def _n(row: dict, col: str):
    try:
        v = float(str(row.get(col, "")).replace(",", "").strip())
        return v
    except (TypeError, ValueError):
        return None


def _fmt(v) -> str:
    return f"{v:,.0f}" if abs(v) >= 1000 else f"{v:g}" if v == int(v) else f"{v:.1f}"


# (label, value function, test, condition text)
RULES = [
    ("Near 52w high", lambda r: (_n(r, "Current Price") / _n(r, "High price") * 100)
     if _n(r, "Current Price") and _n(r, "High price") else None, lambda v: v > 80, "price > 80% of 52w high"),
    ("Market cap", lambda r: _n(r, "Market Capitalization"), lambda v: 100 < v < 5000, "₹100–5,000 Cr"),
    ("ROCE", lambda r: _n(r, "Return on capital employed"), lambda v: v > 15, "> 15%"),
    ("OPM", lambda r: _n(r, "OPM"), lambda v: v > 5, "> 5%"),
    ("Debt/equity", lambda r: _n(r, "Debt to equity"), lambda v: v < 1.1, "< 1.1"),
    ("Pledge", lambda r: _n(r, "Pledged percentage"), lambda v: v == 0, "= 0%"),
    ("Promoter", lambda r: _n(r, "Promoter holding"), lambda v: v > 55, "> 55%"),
    ("Profit growth", None, None, "profit growth > 40% or YoY quarterly profit growth > 100%"),
    ("Debtor days", lambda r: _n(r, "Debtor days"), lambda v: v < 150, "< 150"),
    ("P/E", lambda r: _n(r, "Price to Earning"), lambda v: 0 < v < 20, "< 20"),
]


def evaluate(row: dict) -> dict:
    """{'passed', 'checked', 'total', 'fails': [text], 'unknown': [label], 'ok'}."""
    fails, labels, unknown, passed = [], [], [], 0
    for label, val, test, text in RULES:
        if label == "Profit growth":
            g, q = _n(row, "Profit growth"), _n(row, "YOY Quarterly profit growth")
            if g is None and q is None:
                unknown.append(label)
            elif (g is not None and g > 40) or (q is not None and q > 100):
                passed += 1
            else:
                shown = ", ".join(f"{n} {_fmt(v)}%" for n, v in (("1y", g), ("qtr YoY", q)) if v is not None)
                fails.append(f"Profit growth {shown} (needs {text.replace('profit growth ', '')})")
                labels.append(label)
            continue
        v = val(row)
        if v is None:
            unknown.append(label)
        elif test(v):
            passed += 1
        else:
            unit = "%" if label in ("ROCE", "OPM", "Promoter", "Pledge", "Near 52w high") else " Cr" if label == "Market cap" else ""
            fails.append(f"{label} {_fmt(v)}{unit} (needs {text})")
            labels.append(label)
    checked = passed + len(fails)
    return {"passed": passed, "checked": checked, "total": len(RULES), "fails": fails,
            "fail_labels": labels,
            "unknown": unknown, "ok": not fails and checked >= MIN_CHECKED}


def label(res: dict | None) -> str:
    if not res or not res["checked"]:
        return ""
    if not res["fails"] and not res["ok"]:
        return f"Your screen ? only {res['checked']}/{res['total']} checks had data"
    if res["ok"]:
        note = f" ({', '.join(res['unknown']).lower()} not checked)" if res["unknown"] else ""
        return f"Your screen ✓ {res['passed']}/{res['checked']}{note}"
    return f"Your screen ✗ {len(res['fails'])} fail: " + "; ".join(res["fails"])
