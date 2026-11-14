"""Calibrate the sampling method on a setup whose shuffles are all known (default 3223).

1. Solves every shuffle exactly (counting mode) and writes the exact table.
2. Checks that random sampling reaches the shuffles uniformly.
3. For several sample sizes, draws many independent samples and records how often each 95% interval contains the
   exact value (coverage), the typical error and the typical interval half-width.

Usage: python3 calibrate.py [code] [exact.csv] [reps] [seed]
"""
import itertools, random, sys
from collections import Counter
import sampling as SM

def exact_table(code):
    deck = SM.deck_of(code); nsuits = SM.parse(code)[1]
    perms = [p for p in itertools.permutations(deck) if SM.S.is_first_instance(p, deck, nsuits)]
    rows = []
    for i, p in enumerate(perms, 1):
        r = {"id": f"{code}-{i}"}; r.update(SM.row(code, p)); rows.append(r)
    return rows

def quantities(rows, ncards):
    """name -> (kind, values) where kind 'p' = proportion (list of 0/1), 'm' = mean, ('q', q) = quantile."""
    win = [r for r in rows if r["winnable"]]
    out = {
        "winnable shuffles": ("p", [r["winnable"] for r in rows]),
        "shuffles with a losing game": ("p", [int(r["losses"] > 0) for r in rows]),
        "games per shuffle: mean": ("m", [r["games"] for r in rows]),
        "games per shuffle: median": (("q", 0.5), [r["games"] for r in rows]),
        "games per shuffle: 90th percentile": (("q", 0.9), [r["games"] for r in rows]),
        "fewest plays (winnable): mean": ("m", [r["fewest"] for r in win]),
        "H1 equality (winnable)": ("p", [int(r["fewest"] == ncards + r["D1_blockers"]) for r in win]),
    }
    for k in (0, 1, 2):
        out[f"winnable | D4 = {k}"] = ("p", [r["winnable"] for r in rows if r["D4_aces_exposed"] == k])
    for k in (0, 1, 2):
        out[f"winnable | D1 = {k}"] = ("p", [r["winnable"] for r in rows if r["D1_blockers"] == k])
    return out

def estimate(kind, xs):
    if not xs: return None
    if kind == "p": return SM.wilson(sum(xs), len(xs))
    if kind == "m": return SM.mean_ci(xs)
    return SM.quantile_ci(xs, kind[1])

def truth(kind, xs):
    if kind == "p" or kind == "m": return sum(xs) / len(xs)
    return SM.true_quantile(xs, kind[1])

def main():
    code = sys.argv[1] if len(sys.argv) > 1 else "3223"
    out = sys.argv[2] if len(sys.argv) > 2 else None
    reps = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 20261114
    ncards = len(SM.deck_of(code))

    rows = exact_table(code)
    if out: SM.write_csv(rows, out)
    by_order = {r["order"]: r for r in rows}
    tot = [sum(r[k] for r in rows) for k in ("games", "wins", "losses", "winnable")]
    print(f"{code}: {len(rows)} shuffles; games {tot[0]}, wins {tot[1]}, losses {tot[2]}, winnable {tot[3]}")

    # 2. uniformity of the sampler
    rng = random.Random(seed)
    draws = 1000 * len(rows)
    cnt = Counter(" ".join(SM.random_shuffle(code, rng)) for _ in range(draws))
    assert set(cnt) == set(by_order)
    chi2 = sum((c - 1000) ** 2 / 1000 for c in cnt.values())
    print(f"sampler: {draws} draws, every shuffle reached; per-shuffle count min {min(cnt.values())}, "
          f"max {max(cnt.values())} (expected 1000); chi-square {chi2:.0f} on {len(rows) - 1} df")

    # 3. coverage
    exact = quantities(rows, ncards)
    print("\nexact values")
    for name, (kind, xs) in exact.items():
        print(f"  {name:38s} {truth(kind, xs):.4f}   (n = {len(xs)})")
    orders = list(by_order)
    for n in (50, 100, 200, 500, 1000):
        res = {name: [0, 0, 0.0, 0.0] for name in exact}   # [samples with an estimate, covered, sum |err|, sum half-width]
        for _ in range(reps):
            smp = [by_order[" ".join(SM.random_shuffle(code, rng))] for _ in range(n)]
            for name, (kind, xs) in quantities(smp, ncards).items():
                e = estimate(kind, xs)
                if e is None or e[1] is None: continue
                t = truth(*exact[name]); r = res[name]
                r[0] += 1; r[1] += e[1] <= t <= e[2]; r[2] += abs(e[0] - t); r[3] += (e[2] - e[1]) / 2
        print(f"\nn = {n} ({reps} samples)")
        print(f"  {'quantity':38s} {'coverage':>9s} {'mean |error|':>13s} {'mean ±':>9s}")
        for name, (m, cov, err, hw) in res.items():
            print(f"  {name:38s} {100 * cov / m:8.1f}% {err / m:13.4f} {hw / m:9.4f}")

if __name__ == "__main__":
    main()
