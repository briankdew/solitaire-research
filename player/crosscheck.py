"""Checks the player engine against the solver: deals, legal plays (same set and order) and draws."""
import importlib.util, json, os, sys
spec = importlib.util.spec_from_file_location("s3", os.path.join(os.path.dirname(__file__), "..", "solver", "solitaire-solver3.py"))
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
data = json.load(sys.stdin)
cols_t = lambda cols: tuple((tuple(c["down"]), tuple(c["up"])) for c in cols)
nd = npos = ndr = bad = 0
for x in data:
    code = x["code"]; high, nsuits, ncols, draw = code[0], int(code[1]), int(code[2]), int(code[3])
    if "deal" in x:
        cols, w, stock = S.deal(x["order"], ncols, draw); nd += 1
        if (cols, w, stock) != (cols_t(x["deal"]["cols"]), tuple(x["deal"]["waste"]), tuple(x["deal"]["stock"])): bad += 1; print("deal", x)
    elif x.get("drew"):
        b = x["before"]; ndr += 1
        st, w = S.draw_once(tuple(b["stock"]), tuple(b["waste"]), draw)
        if (st, w) != (tuple(x["stock"]), tuple(x["waste"])): bad += 1; print("draw", x)
    else:
        npos += 1
        st = (cols_t(x["cols"]), tuple(x["waste"]), tuple(x["home"]))
        exp = [f"{a} {b} {n}" for a, b, n in S.gen_plays(st, high, nsuits)]
        if exp != x["plays"]: bad += 1; print("plays", code, exp, x["plays"])
print(f"deals {nd}, positions {npos}, draws {ndr}; mismatches {bad}")
