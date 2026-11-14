"""Look for deal characteristics that decide winnability. Found on the discovery sample, checked on the confirmation one.

1. Each characteristic alone: winnable share at each value, and information gain (how much knowing it reduces
   uncertainty about W/L, in bits; 0 = useless, the full uncertainty of a 50/50 outcome is 1 bit).
2. Pure rules: combinations of up to two characteristic values with at least 50 shuffles that are always (or never)
   winnable in the discovery sample, and how they fare in the confirmation sample.
3. A small decision tree (depth 3) built on discovery, with its accuracy on confirmation.

Usage: python3 patterns.py <discovery.csv> <confirmation.csv>
"""
import itertools, math, sys
from collections import defaultdict
from summarize import load
import features as F
import sampling as SM

BASE = ["D1_blockers", "D1_columns", "D1_waste", "D1_stock", "D2_first_col_ace", "D3_rank", "D4_aces_exposed"]

def enrich(rows, code):
    for r in rows:
        r["D3_rank"] = SM.S.RANKS.index(r["D3_waste_top"][0]) + 1
        r.update(F.features(code, r["order"].split()))
    return rows

def H(k, n):
    if n == 0 or k in (0, n): return 0.0
    p = k / n; return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))

def gain(rows, key):
    n = len(rows); k = sum(r["winnable"] for r in rows)
    g = defaultdict(lambda: [0, 0])
    for r in rows: g[r[key]][0] += r["winnable"]; g[r[key]][1] += 1
    return H(k, n) - sum(m / n * H(w, m) for w, m in g.values())

def single(A, B, keys):
    print("\n1. Each characteristic alone (information gain in bits: discovery / confirmation)")
    for key in sorted(keys, key=lambda k: -gain(A, k)):
        lv = sorted({r[key] for r in A} | {r[key] for r in B})
        cells = []
        for v in lv:
            a = [r["winnable"] for r in A if r[key] == v]; b = [r["winnable"] for r in B if r[key] == v]
            if len(a) >= 30: cells.append(f"{v}: {100 * sum(a) / len(a):.0f}/{100 * sum(b) / max(1, len(b)):.0f}% (n {len(a)})")
        print(f"  {key:34s} {gain(A, key):.3f} / {gain(B, key):.3f}   " + "   ".join(cells))

def pure(A, B, keys, nmin=50):
    print(f"\n2. Pure rules (discovery n >= {nmin}; winnable 0% or 100%), with the confirmation result")
    found = []
    conds = [(k,) for k in keys] + list(itertools.combinations(keys, 2))
    for ks in conds:
        g = defaultdict(list)
        for r in A: g[tuple(r[k] for k in ks)].append(r["winnable"])
        for vals, ws in g.items():
            if len(ws) >= nmin and sum(ws) in (0, len(ws)):
                found.append((ks, vals, len(ws), sum(ws) == len(ws)))
    # keep only rules not implied by a simpler rule already found (same direction)
    simple = {(ks, vals) for ks, vals, n, w in found if len(ks) == 1}
    seen = set()
    for ks, vals, n, win in sorted(found, key=lambda x: (len(x[0]), -x[2])):
        if len(ks) == 2 and any(((k,), (v,)) in simple for k, v in zip(ks, vals)): continue
        cond = " & ".join(f"{k} = {v}" for k, v in zip(ks, vals))
        bs = [r["winnable"] for r in B if all(r[k] == v for k, v in zip(ks, vals))]
        held = sum(bs) if win else len(bs) - sum(bs)
        print(f"  {'ALWAYS' if win else 'NEVER '} winnable: {cond:70s} discovery {n:5d}   confirmation {held}/{len(bs)} hold")

def best_split(rows, keys, nmin):
    n = len(rows); k = sum(r["winnable"] for r in rows); base = H(k, n); best = None
    for key in keys:
        for t in sorted({r[key] for r in rows})[:-1]:
            le = [r for r in rows if r[key] <= t]
            if len(le) < nmin or n - len(le) < nmin: continue
            kl = sum(r["winnable"] for r in le)
            g = base - len(le) / n * H(kl, len(le)) - (n - len(le)) / n * H(k - kl, n - len(le))
            if best is None or g > best[0]: best = (g, key, t)
    return best

def tree(rows, keys, depth, nmin=200):
    if depth == 0: return None
    b = best_split(rows, keys, nmin)
    if b is None or b[0] < 0.005: return None
    _, key, t = b
    return (key, t, tree([r for r in rows if r[key] <= t], keys, depth - 1, nmin),
            tree([r for r in rows if r[key] > t], keys, depth - 1, nmin))

def show(node, A, B, ind="  "):
    pa = 100 * sum(r["winnable"] for r in A) / len(A); pb = 100 * sum(r["winnable"] for r in B) / max(1, len(B))
    if node is None:
        print(f"{ind}-> winnable {pa:.0f}% (n {len(A)}) | confirmation {pb:.0f}% (n {len(B)})"); return
    key, t, lo, hi = node
    print(f"{ind}{key} <= {t}:"); show(lo, [r for r in A if r[key] <= t], [r for r in B if r[key] <= t], ind + "    ")
    print(f"{ind}{key} > {t}:"); show(hi, [r for r in A if r[key] > t], [r for r in B if r[key] > t], ind + "    ")

def predict(node, r, A):
    while node is not None:
        key, t, lo, hi = node
        A = [x for x in A if (x[key] <= t) == (r[key] <= t)]; node = lo if r[key] <= t else hi
    return sum(x["winnable"] for x in A) * 2 >= len(A)

def main(pa, pb):
    code = pa.split("sample-")[1][:4]
    A, B = enrich(load(pa), code), enrich(load(pb), code)
    keys = BASE + sorted(k for k in A[0] if k.startswith("D") and k not in BASE and k[1].isdigit() and k != "D3_waste_top")
    print(f"=== {code}: discovery {len(A)}, confirmation {len(B)}; winnable {100*sum(r['winnable'] for r in A)/len(A):.1f}%")
    single(A, B, keys)
    pure(A, B, keys)
    print("\n3. Decision tree (depth 3, built on discovery)")
    t = tree(A, keys, 3); show(t, A, B)
    acc = sum(predict(t, r, A) == bool(r["winnable"]) for r in B) / len(B)
    base = max(sum(r["winnable"] for r in B), len(B) - sum(r["winnable"] for r in B)) / len(B)
    print(f"  accuracy on confirmation {100*acc:.1f}% (always guessing the majority: {100*base:.1f}%)")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
