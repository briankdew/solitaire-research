# Roadmap

Last updated: 2026-11-14

## Goal
Learn how normal Klondike (K473, full deck, draw 3) plays by working up from tiny setups, solving every shuffle, and finding deal characteristics ("shuffle types") that predict how a game plays out, so the data set can be minimized without losing meaningful information.

## Where things stand
- Setups solved and diagrammed: A113, 2113, 3113, 4113* (marked for possible deletion), 2223 (12 shuffles after mirrors), 3223 (all 360 solved; the 164 shuffle-type representatives diagrammed)
- Rules settled: see `solitaire-notes.md` (no A may be played to a column; high card fills an empty column; relabel moves excluded; loop guard; mirrors removed and shuffles renumbered; play degree p¹/p² judged only from the plays available at that moment)
- Diagrams use the vertical layout (see "Diagram Method — vertical layout" in the notes)
- Solver: `solver/solitaire-solver3.py` handles draws and has a fast counting mode `stats()` (validated against full trees)
- Shuffle-type catalog: H1 (fewest plays ≥ cards + blocking cards), H2 (types differ only in play order), H3–H6 recorded with status per setup

## Next steps (in order)
1. **Limited cognates 6223 and 6233** (same 12 cards; 2 columns vs 3). Agreed plan:
   - ~~Calibrate sampling on 3223~~ done: intervals hold their 95% coverage (see "Sampling" in the notes); `solver/sampling.py` is ready for the 10k samples
   - ~~Discovery sample~~ done: 10,000 each (seeds 6223001, 6233001), tables in `data/`; headline results in the notes, H1/H3–H5 in the catalog
   - Pending decision: should D1 (blocking cards) count the stock? It is not counted yet
   - Find patterns with the catalog's deal characteristics; confirm them on a second, independent 10,000 of each
   - Report margins of error; use medians/percentiles for heavy-tailed counts (games per shuffle)
2. **Shuffle types at 6223/6233 scale**: T3 needs every line of play, but a single shuffle can have 10^5–10^7 games. Needs a way to compute lines/types without enumerating games (e.g. on the position graph)
3. **Diagrams with draws**: solver children carry a `draws` count for waste plays; the diagrams don't show it yet (design decision for the user)
4. Toward a full cognate: smallest meeting the draft cognate criteria with 4 suits is 4443 (16 cards)

## Open questions / pending decisions
- Should 4113 be deleted from the data set? (marked `*`)
- Fork lines: direct chain (current) accepted; revisit only if confusing
- Notation font for labels (comparison page exists; user deferred)
- How to show draws (number of draws before a waste play) in the diagrams
- Winnability characteristic: H1 predicts fewest plays only; H4/H5 are trends, not rules

## Session log
- 2026-11-14: sampling method calibrated on 3223; 6223/6233 discovery samples
- 2026-11-11 → 11-14: definitions and notation; A113–4113; diagram styling (horizontal, then vertical layout); 2223 and 3223; mirrors; shuffle-type catalog; draw handling; repository created
