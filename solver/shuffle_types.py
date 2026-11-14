"""Shuffle-type analysis for solver output (see shuffle-type-catalog.md).

Usage: python3 shuffle_types.py <solver-output.json>
The JSON is the list written by solitaire-solver2.py: [{"id": ..., "root": {...}}, ...].

Prints, per shuffle: deal characteristics (D*), outcome characteristics (O*), and the shuffle type (T3),
then groups shuffles by type.
"""
import json, sys
from collections import Counter, defaultdict

RANKS = "A23456789XJQK"

def games(n, path, out):
    if "children" not in n:
        out.append((tuple(path), n["result"])); return
    for c in n["children"]:
        games(c["node"], path + [(c["play"], c["type"])], out)

def abstract(play, degree):
    """T2: a play with card identities removed: source kind > destination kind : degree."""
    frm, to = play[2], play.split("-")[1]
    return ("w" if frm == "w" else "c") + ">" + ("h" if to == "h" else "c") + ":" + degree

def shuffle_type(root):
    """T3: multiset of (result, abstract line), where a line is the order-free set of plays (T1)."""
    gl = []; games(root, [], gl)
    lines = {}
    for path, res in gl:
        lines.setdefault(frozenset(path), res)
    prof = Counter((res, tuple(sorted(abstract(p, t) for p, t in ps))) for ps, res in lines.items())
    return tuple(sorted(prof.items())), gl, lines

def deal_features(root, hidden_cards=None):
    """Deal characteristics from the root node. Face-down identities are not in the diagram data,
    so D1 here counts only visible piles (waste); pass hidden_cards {col: [cards bottom->top]} to include them."""
    f = {}
    piles = {"w": root["w"]}
    for c, up in root["cols"].items():
        piles[c] = (hidden_cards or {}).get(c, []) + up
    # D1: blocking cards = cards with a lower card of the same suit somewhere beneath them in the same pile
    f["D1_blockers"] = sum(1 for p in piles.values() for i, c in enumerate(p)
                           if any(d[1] == c[1] and RANKS.index(d[0]) < RANKS.index(c[0]) for d in p[:i]))
    f["D2_first_col_ace"] = bool(root["cols"].get("a")) and root["cols"]["a"][0][0] == "A"
    f["D3_waste_top"] = root["w"][-1] if root["w"] else None
    f["D4_aces_exposed"] = sum(1 for p in [root["w"][-1:]] + [u[-1:] for u in root["cols"].values()] for c in p if c[0] == "A")
    return f

if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    groups = defaultdict(list)
    for g in data:
        t, gl, lines = shuffle_type(g["root"])
        fewest = min(int(r[1:]) for _, r in gl if r[0] == "W") if any(r[0] == "W" for _, r in gl) else None
        print(g["id"], deal_features(g["root"]),
              {"O1_fewest": fewest, "O2_GM": len(gl), "O3_lines": len(lines)})
        groups[t].append(g["id"])
    print(f"\n{len(groups)} shuffle types from {len(data)} shuffles")
    for i, (t, ids) in enumerate(groups.items(), 1):
        print(f"  type {i}: {', '.join(ids)}")
