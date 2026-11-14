"""Exhaustive play-tree generator for small Klondike-style setups ([high][suits][columns][draw]).

Rules follow the study notes:
- Deal row by row as in Klondike (row r: column r face up, columns r+1.. face down). If the cards run out
  mid-deal, any column whose top card is face down has it revealed (a consequence, not an action).
- The rest go to the stock; the deal includes the first draw (up to `draw` cards, last drawn on top).
- Plays: w-h, w-c, c-h, c-c (a c-c play may move any face-up card together with everything on it).
  Building: one rank lower, opposite color. Only the high card (or a run it heads) may fill an empty column.
- Revealing a face-down card uncovered by a play is part of that play.
- An A may never be played (as opposed to dealt) to a tableau column.
- Excluded: moving a high card (or the run it heads) that already sits at the bottom of its column with nothing
  face-down beneath it into another empty column; it only relabels the same position.
- Loop guard: a play may not recreate a board state already reached earlier in the same game.
- Mirrored shuffle orders are removed (only the first instance of each is kept) and the rest renumbered 1..n.
- Play degree is judged ONLY from the plays available at that moment:
  p2 if the moved card could go home right now but this play sends it elsewhere; otherwise p1.
- Draws are neutral actions, not plays (never counted). A draw turns up the next `draw` cards (fewer if the
  stock is short) onto the waste, last one on top. When the stock is empty, the waste is turned over to become
  the stock again (a non-event) and drawing continues; passes are unlimited.
  Draws commute with every play that does not use the waste, so the solver only draws right before a waste play:
  from each node, waste plays are offered at every distinct draw position of the current stock/waste cycle
  (the child records how many draws it took), and all other plays are offered at the current position.
"""
import itertools, json, sys

RANKS = "A23456789XJQK"
SUITS = "♠♥♣♦"
RED = set("♥♦")
COLS = "abcdefg"

def rank(c): return RANKS.index(c[0])
def suit(c): return c[1]
def red(c): return c[1] in RED

def deal(cards, ncols, draw):
    hid = [[] for _ in range(ncols)]; up = [[] for _ in range(ncols)]
    it = iter(cards); done = False
    for r in range(ncols):
        for c in range(r, ncols):
            try: card = next(it)
            except StopIteration: done = True; break
            (up if c == r else hid)[c].append(card)
        if done: break
    for c in range(ncols):           # deck ran out mid-deal: reveal any face-down top card
        if not up[c] and hid[c]: up[c].append(hid[c].pop())
    stock = list(it)
    w = stock[:draw]; stock = stock[draw:]
    return tuple((tuple(h), tuple(u)) for h, u in zip(hid, up)), tuple(w), tuple(stock)

def can_build(card, onto):
    return rank(onto) == rank(card) + 1 and red(onto) != red(card)

def draw_once(stock, w, draw):
    """One draw: turn up the next cards from the stock (recycling the waste when the stock is empty)."""
    if not stock:
        if not w: return stock, w
        stock, w = w, ()                     # waste turned over: its bottom card becomes the next card drawn
    return stock[draw:], w + stock[:draw]

def draw_positions(stock, w, draw):
    """Every distinct stock/waste position reachable by drawing, starting with the current one: [(draws, stock, w)]."""
    out, seen, k = [], set(), 0
    while (stock, w) not in seen:
        seen.add((stock, w)); out.append((k, stock, w))
        stock, w = draw_once(stock, w, draw); k += 1
    return out

def gen_plays(state, high, nsuits):
    cols, w, home = state
    out = []
    def home_ok(card): return home[SUITS.index(suit(card))] == rank(card)
    if w:
        top = w[-1]
        if home_ok(top): out.append(("w", "h", 1))
        for j, (h, u) in enumerate(cols):
            if top[0] == "A": break        # an A may never be played to a tableau column
            if (u and can_build(top, u[-1])) or (not u and not h and top[0] == high):
                out.append(("w", COLS[j], 1))
    for i, (h, u) in enumerate(cols):
        if not u: continue
        if home_ok(u[-1]): out.append((COLS[i], "h", 1))
        for k in range(len(u)):           # move u[k:] (k = index of the run's base card)
            base = u[k]
            if base[0] == "A": continue    # an A may never be played to a tableau column
            for j, (h2, u2) in enumerate(cols):
                if j == i: continue
                if u2:
                    if can_build(base, u2[-1]): out.append((COLS[i], COLS[j], len(u) - k))
                elif not h2 and base[0] == high and not (k == 0 and not h):
                    out.append((COLS[i], COLS[j], len(u) - k))   # skip pure relabel moves
    return out

def apply(state, mv):
    cols, w, home = state
    cols = [list(map(list, c)) for c in cols]; w = list(w); home = list(home)
    src, dst, n = mv
    if src == "w": moved = [w.pop()]
    else:
        h, u = cols[COLS.index(src)]
        moved = u[-n:]; del u[-n:]
        if not u and h: u.append(h.pop())   # reveal
    if dst == "h":
        home[SUITS.index(suit(moved[0]))] += 1
    else:
        cols[COLS.index(dst)][1].extend(moved)
    return (tuple((tuple(h), tuple(u)) for h, u in cols), tuple(w), tuple(home)), moved[0]

def node_of(state, nsuits, stock):
    cols, w, home = state
    n = {"s": len(stock), "w": list(w),
         "cols": {COLS[i]: list(u) for i, (h, u) in enumerate(cols)},
         "h": {SUITS[k]: [RANKS[r] + SUITS[k] for r in range(home[k])] for k in range(nsuits) if home[k]}}
    hid = {COLS[i]: len(h) for i, (h, u) in enumerate(cols) if h}
    if hid: n["hid"] = hid
    return n

def build(state, high, nsuits, total, stock, seen, draw=3):
    node = node_of(state, nsuits, stock)
    cols, w, home = state
    avail = []
    for k, stk, ww in draw_positions(stock, w, draw):
        st = (cols, ww, home)
        for mv in gen_plays(st, high, nsuits):
            if k and mv[0] != "w": continue        # non-waste plays only at the current position (draws commute with them)
            nstate, card = apply(st, mv)
            if (nstate, stk) in seen: continue
            avail.append((mv, card, nstate, stk, k))
    if not avail:
        node["result"] = "W" if sum(home) == total else "L"
        return node
    homeable = {card for (mv, card, *_) in avail if mv[1] == "h"}
    def degree(mv, card): return "p2" if mv[1] != "h" and mv[2] == 1 and card in homeable else "p1"
    avail.sort(key=lambda x: (degree(x[0], x[1]), x[0][1] != "h", x[0][0] != "w", x[4], x[0][0], x[0][1]))
    node["children"] = []
    for mv, card, nstate, stk, k in avail:
        child = {"play": f"{card}{mv[0]}-{mv[1]}", "type": degree(mv, card),
                 "node": build(nstate, high, nsuits, total, stk, seen | {(nstate, stk)}, draw)}
        if k: child["draws"] = k
        node["children"].append(child)
    return node

def stats(state, stock, high, nsuits, total, draw=3, memo=None, onstack=None):
    """Counting mode (no explicit tree): returns (games, wins, losses, fewest_win, most_plays) from this position,
    counting games as play sequences exactly as build() does. Results for repeated positions are reused.
    Same play rules as build(); positions already on the current path are skipped (the loop guard). For setups
    whose positions can repeat (possible with two suits of a colour), reuse can make counts differ slightly
    from build(); two-suit setups cannot repeat a position, so counts are exact there."""
    if memo is None: memo, onstack = {}, set()
    key = (state, stock)
    if key in memo: return memo[key]
    onstack.add(key)
    cols, w, home = state
    kids = []
    for k, stk, ww in draw_positions(stock, w, draw):
        st = (cols, ww, home)
        for mv in gen_plays(st, high, nsuits):
            if k and mv[0] != "w": continue
            nstate, _ = apply(st, mv)
            if (nstate, stk) in onstack: continue
            kids.append((nstate, stk))
    if not kids:
        r = (1, 1, 0, 0, 0) if sum(home) == total else (1, 0, 1, None, 0)
    else:
        g = wn = ls = mx = 0; few = None
        for ns, stk in kids:
            cg, cw, cl, cf, cm = stats(ns, stk, high, nsuits, total, draw, memo, onstack)
            g += cg; wn += cw; ls += cl; mx = max(mx, cm + 1)
            if cf is not None and (few is None or cf + 1 < few): few = cf + 1
        r = (g, wn, ls, few, mx)
    onstack.discard(key)
    memo[key] = r
    return r

def finish(node, k=0):
    if "children" not in node: node["result"] += str(k); return
    for c in node["children"]: finish(c["node"], k + 1)

def games(node, path, out):
    if "children" not in node: out.append((path, node["result"])); return
    for c in node["children"]: games(c["node"], path + [f'{c["play"]} {c["type"]}'], out)

# Mirrors: suit relabelings that keep same-color suits the same color (identical play). Keyed by number of suits.
MIRRORS = {
    1: [],
    2: [{"♠": "♥", "♥": "♠"}],
    3: [{"♠": "♣", "♥": "♥", "♣": "♠"}],
    4: [dict(zip("♠♥♣♦", t)) for t in ("♠♦♣♥", "♥♠♦♣", "♥♣♦♠", "♣♥♠♦", "♣♦♠♥", "♦♠♥♣", "♦♣♥♠")],
}

def is_first_instance(perm, deck, nsuits):
    """True if no mirror of this shuffle order comes earlier in the standard order (it is the first instance)."""
    key = [deck.index(c) for c in perm]
    for m in MIRRORS[nsuits]:
        if [deck.index(c[0] + m[c[1]]) for c in perm] < key:
            return False
    return True

def run(code):
    high, nsuits, ncols, draw = code[0], int(code[1]), int(code[2]), int(code[3])
    deck = [r + s for r in RANKS[: RANKS.index(high) + 1] for s in SUITS[:nsuits]]   # rank-major: A♠ A♥ 2♠ 2♥ …
    res = []
    perms = [p for p in itertools.permutations(deck) if is_first_instance(p, deck, nsuits)]   # mirrors removed
    for i, perm in enumerate(perms, 1):                                                         # renumbered 1..n
        cols, w, stock = deal(list(perm), ncols, draw)
        state = (cols, w, tuple([0] * nsuits))
        root = build(state, high, nsuits, len(deck), stock, {(state, stock)}, draw)
        finish(root)
        gl = []; games(root, [], gl)
        res.append({"id": f"{code}-{i}", "order": " ".join(perm), "root": root, "games": gl})
    return res

if __name__ == "__main__":
    code, out = sys.argv[1], sys.argv[2]
    res = run(code)
    json.dump([{"id": r["id"], "root": r["root"]} for r in res], open(out, "w"), ensure_ascii=False)
    for r in res:
        rt = r["root"]
        print(r["id"], r["order"], "| a/b:", rt["cols"], "hid:", rt.get("hid", {}), "w:", rt["w"], "s:", rt["s"])
        for n, (path, result) in enumerate(r["games"], 1):
            print(f"   {r['id']}.{n}-{result}: " + ", ".join(path))
