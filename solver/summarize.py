"""Summarize a sample table (from sampling.py) with 95% intervals, and test the catalog hypotheses H1, H3, H4, H5.

Usage: python3 summarize.py <sample.csv> [<sample.csv> ...]
"""
import csv, sys
from collections import Counter
import sampling as SM

INT = ("D1_blockers", "D1_columns", "D1_waste", "D1_stock", "D2_first_col_ace", "D4_aces_exposed", "stock", "games", "wins", "losses", "winnable", "most")

def load(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    for r in rows:
        for k in INT: r[k] = int(r[k])
        r["fewest"] = int(r["fewest"]) if r["fewest"] else None
    return rows

def pct(e): return f"{100 * e[0]:5.1f}% ({100 * e[1]:.1f}–{100 * e[2]:.1f})"
def num(e, d=1): return f"{e[0]:.{d}f} ({e[1]:.{d}f}–{e[2]:.{d}f})"

def by(rows, key, label):
    print(f"  by {label}:")
    for v in sorted({r[key] for r in rows}, key=str):
        g = [r for r in rows if r[key] == v]
        w = SM.wilson(sum(r["winnable"] for r in g), len(g))
        med = SM.quantile_ci([r["games"] for r in g], 0.5)
        print(f"    {str(v):>3s}  n = {len(g):5d}   winnable {pct(w)}   median games {med[0]} ({med[1]}–{med[2]})"
              f"   mean games {sum(r['games'] for r in g) / len(g):.1f}")

def summarize(path):
    rows = load(path); n = len(rows); ncards = len(rows[0]["order"].split())
    dup = sum(c - 1 for c in Counter(r["order"] for r in rows).values() if c > 1)
    win = [r for r in rows if r["winnable"]]
    games = [r["games"] for r in rows]
    print(f"\n=== {path}: {n} shuffles ({dup} repeats), stock after the deal {sorted(set(r['stock'] for r in rows))}")
    print(f"  winnable shuffles          {pct(SM.wilson(len(win), n))}")
    print(f"  shuffles with a losing game {pct(SM.wilson(sum(r['losses'] > 0 for r in rows), n))}")
    print(f"  all games won              {pct(SM.wilson(sum(r['losses'] == 0 for r in rows), n))}")
    print(f"  games per shuffle: mean {num(SM.mean_ci(games))}, median {SM.quantile_ci(games, .5)[0]} "
          f"{SM.quantile_ci(games, .5)[1:]}, 90th pct {SM.quantile_ci(games, .9)[0]} {SM.quantile_ci(games, .9)[1:]}, "
          f"99th pct {SM.quantile_ci(games, .99)[0]}, max {max(games)}")
    print(f"  share of all games won     {100 * sum(r['wins'] for r in rows) / sum(games):.1f}%")
    print(f"  fewest plays (winnable): mean {num(SM.mean_ci([r['fewest'] for r in win]), 2)}, "
          f"distribution {dict(sorted(Counter(r['fewest'] for r in win).items()))}")
    print(f"  longest game: distribution {dict(sorted(Counter(r['most'] for r in rows).items()))}")
    ok = sum(r["fewest"] >= ncards + r["D1_blockers"] for r in win)
    eq = sum(r["fewest"] == ncards + r["D1_blockers"] for r in win)
    print(f"  H1 fewest >= cards + D1: holds {ok}/{len(win)}; equality {pct(SM.wilson(eq, len(win)))}")
    by(rows, "D2_first_col_ace", "D2 (column a starts with an A)  [H3]")
    by(rows, "D3_waste_top", "D3 (top waste card)  [H3]")
    by(rows, "D4_aces_exposed", "D4 (aces exposed)  [H4]")
    by(rows, "D1_blockers", "D1 (blocking cards: columns + waste + stock)  [H5]")
    for k in ("D1_columns", "D1_waste", "D1_stock"): by(rows, k, k)

if __name__ == "__main__":
    for p in sys.argv[1:]: summarize(p)
