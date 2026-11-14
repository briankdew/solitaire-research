"""Builds pages/solitaire-player.html from player/page.html, player/engine.js and the solver results.

Solver results embedded (for scoring only; the player never sees them): every shuffle of A113-3223, and the
6223/6233 discovery and confirmation samples. Each row: order (no spaces), winnable 0/1, fewest plays (0 if none), games.
"""
import csv, itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "solver"))
import sampling as SM

def rows_of(code, perms):
    out = []
    for p in perms:
        r = SM.row(code, p); out.append(["".join(p), r["winnable"], r["fewest"] or 0, r["games"]])
    return out

data = {}
for code in ("A113", "2113", "3113", "4113", "2223"):
    deck = SM.deck_of(code); ns = SM.parse(code)[1]
    data[code] = {"all": rows_of(code, [p for p in itertools.permutations(deck) if SM.S.is_first_instance(p, deck, ns)])}
def from_csv(path):
    return [[r["order"].replace(" ", ""), int(r["winnable"]), int(r["fewest"] or 0), int(r["games"])]
            for r in csv.DictReader(open(path, encoding="utf-8"))]
data["3223"] = {"all": from_csv(os.path.join(ROOT, "data", "exact-3223.csv"))}
for code in ("6223", "6233"):
    data[code] = {s: from_csv(os.path.join(ROOT, "data", f"sample-{code}-{s}.csv")) for s in ("discovery", "confirmation")}

page = open(os.path.join(HERE, "page.html"), encoding="utf-8").read()
page = page.replace("/*__ENGINE__*/", open(os.path.join(HERE, "engine.js"), encoding="utf-8").read())
page = page.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
out = os.path.join(ROOT, "pages", "solitaire-player.html")
open(out, "w", encoding="utf-8").write(page)
print(out, f"{os.path.getsize(out) / 1e6:.2f} MB")
