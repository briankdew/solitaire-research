"""Compare a discovery sample with an independent confirmation sample.

For each finding: both estimates with 95% intervals, and whether they agree (the difference is within its own
95% margin: two-proportion z test for proportions; overlap of the distribution-free intervals for medians).
Rules (H1) are checked for exceptions.

Usage: python3 compare.py <discovery.csv> <confirmation.csv>
"""
import math, sys
from summarize import load
import sampling as SM

def prop_row(name, a, b):
    ka, na = sum(a), len(a); kb, nb = sum(b), len(b)
    if not na or not nb: return
    ea, eb = SM.wilson(ka, na), SM.wilson(kb, nb)
    p = (ka + kb) / (na + nb); se = math.sqrt(p * (1 - p) * (1 / na + 1 / nb)) if 0 < p < 1 else 0
    z = abs(ea[0] - eb[0]) / se if se else 0.0
    ok = "agree" if z <= SM.Z else f"DIFFER (z = {z:.1f})"
    print(f"  {name:44s} {100*ea[0]:5.1f}% ({100*ea[1]:.1f}–{100*ea[2]:.1f}) n={na:<5d}  "
          f"{100*eb[0]:5.1f}% ({100*eb[1]:.1f}–{100*eb[2]:.1f}) n={nb:<5d}  {ok}")

def median_row(name, a, b):
    if not a or not b: return
    ea, eb = SM.quantile_ci(a, .5), SM.quantile_ci(b, .5)
    ok = "agree" if ea[1] <= eb[2] and eb[1] <= ea[2] else "DIFFER"
    print(f"  {name:44s} {ea[0]:>8} ({ea[1]}–{ea[2]}){'':8s} {eb[0]:>8} ({eb[1]}–{eb[2]}){'':8s} {ok}")

def compare(pa, pb):
    A, B = load(pa), load(pb); ncards = len(A[0]["order"].split())
    print(f"\n=== {pa}  vs  {pb}")
    print("  proportions (winnable unless stated):     discovery                          confirmation")
    prop_row("winnable shuffles", [r["winnable"] for r in A], [r["winnable"] for r in B])
    prop_row("shuffles with a losing game", [int(r["losses"] > 0) for r in A], [int(r["losses"] > 0) for r in B])
    prop_row("no play possible after the deal", [int(r["most"] == 0) for r in A], [int(r["most"] == 0) for r in B])
    wa, wb = [r for r in A if r["winnable"]], [r for r in B if r["winnable"]]
    fx = lambda r: ncards + r["D1_columns"] + r["D1_waste"]
    prop_row("H1 equality, fixed blockers (of winnable)", [int(r["fewest"] == fx(r)) for r in wa], [int(r["fewest"] == fx(r)) for r in wb])
    for key, label in (("D2_first_col_ace", "D2"), ("D4_aces_exposed", "D4"), ("D1_blockers", "D1"),
                       ("D1_columns", "D1 columns"), ("D1_waste", "D1 waste"), ("D1_stock", "D1 stock")):
        for v in sorted({r[key] for r in A} | {r[key] for r in B}):
            a = [r["winnable"] for r in A if r[key] == v]; b = [r["winnable"] for r in B if r[key] == v]
            if min(len(a), len(b)) >= 30: prop_row(f"winnable | {label} = {v}", a, b)
    for v in sorted({r["D3_waste_top"][0] for r in A}, key=SM.S.RANKS.index):
        a = [r["winnable"] for r in A if r["D3_waste_top"][0] == v]; b = [r["winnable"] for r in B if r["D3_waste_top"][0] == v]
        prop_row(f"winnable | D3 rank = {v}", a, b)
    print("  medians of games per shuffle:")
    median_row("all shuffles", [r["games"] for r in A], [r["games"] for r in B])
    for key, label in (("D2_first_col_ace", "D2"), ("D4_aces_exposed", "D4"), ("D1_blockers", "D1")):
        for v in sorted({r[key] for r in A} | {r[key] for r in B}):
            a = [r["games"] for r in A if r[key] == v]; b = [r["games"] for r in B if r[key] == v]
            if min(len(a), len(b)) >= 30: median_row(f"{label} = {v}", a, b)
    for v in sorted({r["D3_waste_top"][0] for r in A}, key=SM.S.RANKS.index):
        median_row(f"D3 rank = {v}", [r["games"] for r in A if r["D3_waste_top"][0] == v],
                   [r["games"] for r in B if r["D3_waste_top"][0] == v])
    print("  rules:")
    for name, rows in (("discovery", wa), ("confirmation", wb)):
        bad = sum(r["fewest"] < fx(r) for r in rows)
        print(f"    H1 fewest >= cards + fixed D1, {name}: {len(rows) - bad}/{len(rows)} hold")

if __name__ == "__main__":
    compare(sys.argv[1], sys.argv[2])
