"""Drop rows from a Chartink backtest export by sector and/or market-cap tier.

Usage: python filter_hits.py <in.csv> <out.csv> [--drop-sector Bank,Media] [--drop-cap Smallcap]
"""

from __future__ import annotations

import csv
import sys


def main() -> int:
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        return 1
    src, dst, rest = args[0], args[1], args[2:]
    sectors, caps = set(), set()
    for flag, val in zip(rest[::2], rest[1::2]):
        items = {v.strip().lower() for v in val.split(",") if v.strip()}
        if flag == "--drop-sector":
            sectors |= items
        elif flag == "--drop-cap":
            caps |= items
    with open(src, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    keep = [r for r in rows if (r.get("Sector", "").strip().lower() not in sectors
                                and r.get("Marketcapname", "").strip().lower() not in caps)]
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(keep)
    print(f"{src}: kept {len(keep)} of {len(rows)} (dropped sectors {sorted(sectors) or '-'}, caps {sorted(caps) or '-'}) -> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
