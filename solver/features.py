"""Candidate deal characteristics (beyond D1-D4) computed from a shuffle order alone (no solving).

Piles at the deal: each column (face-down cards then face-up, bottom -> top), the waste, and each stock draw group
(last drawn on top). A card is *reachable* if it can be played without any play first: a column's face-up top,
the waste top, or the top card of a stock group (reached by drawing). Depth = cards above it in its pile.
"""
import sampling as SM
S = SM.S

def piles_of(code, perm):
    high, nsuits, ncols, draw = SM.parse(code)
    cols, w, stock = S.deal(list(perm), ncols, draw)
    piles = []                                    # (area, cards bottom->top, number face-down)
    for h, u in cols: piles.append(("col", list(h) + list(u), len(h)))
    piles.append(("waste", list(w), 0))
    for i in range(0, len(stock), draw): piles.append(("stock", list(stock[i:i + draw]), 0))
    return cols, w, stock, piles

def features(code, perm):
    high, nsuits, ncols, draw = SM.parse(code)
    cols, w, stock, piles = piles_of(code, perm)
    rk = S.RANKS.index
    loc = {}                                      # card -> (area, depth, face_down)
    for area, p, nd in piles:
        for i, c in enumerate(p): loc[c] = (area, len(p) - 1 - i, i < nd)
    reach = {c for c, (a, d, fd) in loc.items() if d == 0 and not fd}
    aces = [c for c in loc if c[0] == "A"]; twos = [c for c in loc if c[0] == "2"]
    highs = [c for c in loc if c[0] == high]
    f = {}
    f["D5_aces_reachable"] = sum(c in reach for c in aces)                       # incl. stock group tops
    f["D6_aces_face_down"] = sum(loc[c][2] for c in aces)
    f["D7_ace_depth_total"] = sum(loc[c][1] for c in aces)
    f["D8_twos_reachable"] = sum(c in reach for c in twos)
    f["D9_twos_face_down"] = sum(loc[c][2] for c in twos)
    f["D10_high_face_down"] = sum(loc[c][2] for c in highs)
    # D11: plays available at the deal (waste plays at every draw position, others at the current one)
    state = (cols, w, tuple([0] * nsuits)); n = 0
    for k, stk, ww in S.draw_positions(stock, w, draw):
        for mv in S.gen_plays((cols, ww, state[2]), high, nsuits):
            if k and mv[0] != "w": continue
            n += 1
    f["D11_plays_at_deal"] = n
    # D12: an A or 2 that is face-down with a higher card of its own suit above it in the same column
    f["D12_low_face_down_under_own_suit"] = sum(
        1 for area, p, nd in piles for i, c in enumerate(p[:nd]) if rk(c[0]) <= 1
        and any(d[1] == c[1] and rk(d[0]) > rk(c[0]) for d in p[i + 1:]))
    # D13: total depth of the aces and 2s (cards lying above them in their piles)
    f["D13_A2_depth_total"] = sum(loc[c][1] for c in aces + twos)
    # D14: aces in the stock (not waste) groups
    f["D14_aces_in_stock"] = sum(loc[c][0] == "stock" for c in aces)
    return f
