"""Enumerate every full game for a single-suit, one-column, draw-3 setup (e.g. 4113) and emit diagram data.

State: column a (list, bottom->top), waste (list, bottom->top; only the top is playable, and with <=3 waste
cards a draw-3 recycle never changes the order), home (list A..).
Plays (per the study's definition): w-h, w-a, a-h. One column, one suit: a card can only enter column a
when it is empty and the card is the high card.
"""
import itertools, json, sys

RANKS = "A23456789XJQK"
S = "♠"

def card(r): return r + S

def plays(state, high):
    a, w, h = state
    nxt = RANKS[len(h)]  # next rank needed at home
    out = []
    if w and w[-1][0] == nxt: out.append(("w", "h"))
    if a and a[-1][0] == nxt: out.append(("a", "h"))
    if w and not a and w[-1][0] == high: out.append(("w", "a"))
    return out

def apply(state, mv):
    a, w, h = [list(x) for x in state]
    src = w if mv[0] == "w" else a
    c = src.pop()
    (h if mv[1] == "h" else a).append(c)
    return (tuple(a), tuple(w), tuple(h)), c

def degree(mv, card, avail):
    """Degree of a play, judged ONLY from the plays available at this moment (no look-ahead).
    p1: direct. p2: the same card had a direct home play available right now, but this play takes it elsewhere."""
    if mv[1] != "h" and any(m[1] == "h" and c == card for (m, c) in avail):
        return "p2"
    return "p1"

def build(state, high, total):
    a, w, h = state
    node = {"s": 0, "w": list(w), "cols": {"a": list(a)}, "h": ({S: list(h)} if h else {})}
    avail = []
    for mv in plays(state, high):
        src = w if mv[0] == "w" else a
        avail.append((mv, src[-1]))
    if not avail:
        return node
    # order: lower degree first, then home plays before column plays, waste source before column source
    kids = sorted(avail, key=lambda mc: (degree(mc[0], mc[1], avail), mc[0][1] != "h", mc[0][0] != "w"))
    node["children"] = []
    for mv, c in kids:
        nstate, _ = apply(state, mv)
        node["children"].append({"play": f"{c}{mv[0]}-{mv[1]}", "type": degree(mv, c, avail), "node": build(nstate, high, total)})
    return node

def finish(node, plays_so_far=0):
    """Fill in leaf results (W/L + plays from the deal)."""
    if not node.get("children"):
        total_home = len(node["h"].get(S, []))
        node["result"] = ("W" if not node["w"] and not node["cols"]["a"] else "L") + str(plays_so_far)
        return
    for c in node["children"]:
        finish(c["node"], plays_so_far + 1)

def games(node, path, out):
    if not node.get("children"):
        out.append((path, node["result"])); return
    for c in node["children"]:
        games(c["node"], path + [f'{c["play"]} {c["type"]}'], out)

def main(code):
    high, nsuits, ncols, draw = code[0], int(code[1]), int(code[2]), int(code[3])
    deck = RANKS[: RANKS.index(high) + 1]
    shuffles = []
    for i, perm in enumerate(itertools.permutations(deck), 1):
        cards = [card(r) for r in perm]
        a, rest = [cards[0]], cards[1:]
        w = rest[:draw]  # first draw is part of the deal; drawn in order, last drawn on top
        state = (tuple(a), tuple(w), tuple())
        root = build(state, high, len(deck))
        finish(root)
        gl = []
        games(root, [], gl)
        shuffles.append({"id": f"{code}-{i}", "order": " ".join(cards), "root": root, "games": gl})
    return shuffles

if __name__ == "__main__":
    code = sys.argv[1]
    sh = main(code)
    json.dump([{"id": s["id"], "root": s["root"]} for s in sh], open(sys.argv[2], "w"), ensure_ascii=False)
    for s in sh:
        print(s["id"], s["order"], "| setup a:", s["root"]["cols"]["a"], "w:", s["root"]["w"])
        for n, (path, res) in enumerate(s["games"], 1):
            print(f"   {s['id']}.{n}-{res}: " + ", ".join(path))
