"""Random-shuffle sampling and estimators (standard library only).

A sample is drawn by shuffling the full deck uniformly at random and keeping the first instance of its mirror class
(every mirror class has the same size, so this samples the mirror-removed shuffles uniformly). Sampling is with
replacement, which is what a 10,000 sample of a large setup amounts to.

Each sampled shuffle becomes one row: its order, deal characteristics (D1-D4, see shuffle-type-catalog.md) and
outcome characteristics from the solver's counting mode.

Usage: python3 sampling.py <code> <n> <seed> <out.csv>
"""
import csv, importlib.util, math, os, random, sys

_spec = importlib.util.spec_from_file_location("solver3", os.path.join(os.path.dirname(__file__), "solitaire-solver3.py"))
S = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S)

def parse(code):
    return code[0], int(code[1]), int(code[2]), int(code[3])

def deck_of(code):
    high, nsuits, _, _ = parse(code)
    return [r + s for r in S.RANKS[: S.RANKS.index(high) + 1] for s in S.SUITS[:nsuits]]

def first_instance(perm, deck, nsuits):
    """The first instance (in standard order) of the mirror class of this shuffle order."""
    best = list(perm); key = [deck.index(c) for c in perm]
    for m in S.MIRRORS[nsuits]:
        alt = [c[0] + m[c[1]] for c in perm]
        k = [deck.index(c) for c in alt]
        if k < key: best, key = alt, k
    return tuple(best)

def random_shuffle(code, rng):
    deck = deck_of(code); perm = deck[:]; rng.shuffle(perm)
    return first_instance(perm, deck, parse(code)[1])

def row(code, perm):
    """Deal and outcome characteristics of one shuffle order."""
    high, nsuits, ncols, draw = parse(code)
    cols, w, stock = S.deal(list(perm), ncols, draw)
    state = (cols, w, tuple([0] * nsuits))
    g, wn, ls, few, most = S.stats(state, stock, high, nsuits, len(perm), draw)
    piles = [list(w)] + [list(h) + list(u) for h, u in cols]
    rk = S.RANKS.index
    d1 = sum(1 for p in piles for i, c in enumerate(p) if any(d[1] == c[1] and rk(d[0]) < rk(c[0]) for d in p[:i]))
    tops = [w[-1]] if w else []
    tops += [u[-1] for h, u in cols if u]
    return {"order": " ".join(perm),
            "D1_blockers": d1,
            "D2_first_col_ace": int(bool(cols[0][1]) and cols[0][1][0][0] == "A"),
            "D3_waste_top": w[-1] if w else "",
            "D4_aces_exposed": sum(1 for c in tops if c[0] == "A"),
            "stock": len(stock),
            "games": g, "wins": wn, "losses": ls,
            "winnable": int(wn > 0),
            "fewest": "" if few is None else few,
            "most": most}

def sample(code, n, seed):
    rng = random.Random(seed)
    return [row(code, random_shuffle(code, rng)) for _ in range(n)]

def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)

# ---------- estimators (95% intervals) ----------
Z = 1.959964

def wilson(k, n, z=Z):
    """Proportion k/n with its Wilson score interval."""
    if n == 0: return (None, None, None)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, 0.0 if k == 0 else max(0.0, c - h), 1.0 if k == n else min(1.0, c + h))

def mean_ci(xs, z=Z):
    """Mean with a normal-approximation interval."""
    n = len(xs); m = sum(xs) / n
    if n < 2: return (m, None, None)
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    return (m, m - z * sd / math.sqrt(n), m + z * sd / math.sqrt(n))

def _binom_cdfs(n, q):
    """cdf[k] = P(B <= k) for B ~ Binomial(n, q)."""
    lq, l1, lg = math.log(q), math.log1p(-q), math.lgamma(n + 1)
    out, t = [], 0.0
    for i in range(n + 1):
        t += math.exp(lg - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lq + (n - i) * l1)
        out.append(t)
    return out

def quantile_ci(xs, q, alpha=0.05):
    """Sample quantile q with a distribution-free interval [x(l), x(u)] from order statistics: with B the number of
    observations below the true quantile, l is the largest rank with P(B <= l-1) <= alpha/2 and u the smallest with
    P(B <= u-1) >= 1 - alpha/2. Ties (whole-number counts) make it conservative."""
    s = sorted(xs); n = len(s); cdf = _binom_cdfs(n, q)
    est = s[min(n - 1, max(0, math.ceil(q * n) - 1))]
    l = 1
    while l + 1 <= n and cdf[l] <= alpha / 2: l += 1     # cdf[l] = P(B <= (l+1)-1)
    u = 1
    while u < n and cdf[u - 1] < 1 - alpha / 2: u += 1
    return (est, s[l - 1], s[u - 1])

def true_quantile(xs, q):
    s = sorted(xs); n = len(s)
    return s[min(n - 1, max(0, math.ceil(q * n) - 1))]

if __name__ == "__main__":
    code, n, seed, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    write_csv(sample(code, n, seed), out)
