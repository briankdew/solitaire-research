# Shuffle-Type Catalog

Characteristics used to describe shuffles and group them into "shuffle types" (intrinsic game-play mirrors), with the status of each as setups grow. Goal: find which characteristics hold as complexity changes, and which (if any) hold universally.

Tool: `solver/shuffle_types.py <solver-output.json>` computes the D, O and T characteristics below for a setup.

---

## T — Type definition (how shuffles are grouped)

| ID | Characteristic | Definition |
|---|---|---|
| T1 | Line of play | A game's plays as an unordered set: games that make the same plays in a different order are one line |
| T2 | Abstract play | A play with card identities removed: source kind → destination kind, plus degree. Kinds: `w` waste, `c` column, `h` home. E.g. `c>h:p1`, `w>c:p2` |
| T3 | Shuffle type | The multiset of (result, abstract line) over all of a shuffle's lines. Two shuffles with equal T3 play out the same way except for play-order freedom |

## D — Deal characteristics (computed from the deal, before any play)

| ID | Characteristic | Definition |
|---|---|---|
| D1 | Blocking cards | Number of cards that sit above a lower card of their own suit in the same pile (waste, or a column including its face-down cards). Each must leave its pile before the card beneath can go home |
| D2 | First column starts with an ace | Column a's dealt card is an A, so a column empties on the first play |
| D3 | Top waste card | The active waste card after the deal (rank matters: a high card can detour to an empty column; an A just goes home) |
| D4 | Aces exposed at the deal | Aces that are a pile's top card (playable) after the deal |

## O — Outcome characteristics (computed from the game tree)

| ID | Characteristic | Definition |
|---|---|---|
| O1 | Fewest plays | Shortest win (W with the fewest plays) |
| O2 | GM | Number of complete games (play orders counted separately) |
| O3 | Lines | Number of distinct lines of play (T1) |
| O4 | Result profile | Count of games per result (W4, W5, … / L…) |

## H — Relationships found (hypotheses and their status)

| ID | Relationship | A113 | 2113 | 3113 | 4113* | 2223 | 3223 |
|---|---|---|---|---|---|---|---|
| H1 | **O1 ≥ number of cards + D1** for winnable shuffles (each blocking card costs at least one detour) | = 1/1 | = 2/2 | = 4/4 | = 7/7 | = 12/12 | **≥ holds 293/293; equality 249/293 (85%)** |
| H2 | Within a shuffle type, shuffles differ only in O2 (play-order freedom), never in O1, O3 or the set of results | — | — | — | — | holds | **holds 164/164 types** |
| H3 | O2 rises with early freedom: a column empties at once (D2), and cards that are playable straight away | — | — | — | — | trend | D2: avg 61.7 vs 28.3 games ✓. Top waste card A / 2 / 3: avg 59.2 / 32.2 / 26.8 games (the 2223 reading "a 2 in the waste" was really "early freedom") |
| H4 | **Winnability rises with D4 (aces exposed at the deal)** | — | — | — | — | all winnable | **D4 = 2: 72/72 winnable; D4 = 1: 191/216; D4 = 0: 30/72** |
| H5 | Fewer blocking cards (D1) → more winnable shuffles and more games | — | — | — | — | — | D1 0 / 1 / 2 / 3: winnable 131/138, 132/174, 28/42, 2/6; avg games 65.9 / 26.6 / 10.8 / 3.5 |
| H6 | **Choices can decide W vs L** (a node where one play keeps a win possible and another leads only to losses) | never | never | never | never | never | **first seen: 56 shuffles have both winning and losing games. At those nodes every losing play was p¹; the winning alternative was p¹ (121) or p² (13). E.g. 3223-12: `3♠w-h` (p¹, straight home) loses; `3♠w-a` (p², detour) is the only way to win** |

Notes:
- H1: where it is not an equality (44 shuffles, 3223), the blocking card's detour needs somewhere to go: only the high card can fill an empty column, so a lower blocker needs an opposite-colour card one rank higher on the tableau, and placing that card can cost extra plays. The exact cost is not yet captured by a deal characteristic (blocker rank alone does not explain all 44)
- H1 predicts the fewest plays of a win, not whether a shuffle can be won: winnability is H4/H5
- H6 matters for the progressive-degree definitions: a p¹ play (judged in the moment) can be the losing choice, and a p² detour can be the only winning one

## Types found

### 2223 (12 shuffles → 8 types)
| Type | Representative | Members | Lines (O3) | O1 | D1 | Description |
|---|---|---|---|---|---|---|
| A | 2223-1 | 1 | 8 | 4 | 0 | Richest: a column empties early, a 2 in the waste, both detour kinds available |
| B | 2223-2 | 2 | 3 | 5 | 1 | Self-blocked (A♥ under 2♥) |
| C | 2223-3 | 3, 5, 9 | 4 | 4 | 0 | Direct win, or the waste 2 detours |
| D | 2223-4 | 4 | 3 | 4 | 0 | Direct win, or a column 2 detours (p¹ or p²) |
| E | 2223-6 | 6 | 2 | 4 | 0 | Direct win, or one column-2 detour |
| F | 2223-7 | 7 | 3 | 4 | 0 | Direct win, or two ways for the waste 2 to detour |
| G | 2223-8 | 8, 11, 12 | 1 | 4 | 0 | Single line, no detours possible |
| H | 2223-10 | 10 | 1 | 5 | 1 | Single line, self-blocked (forced detour) |

### 3223 (360 shuffles → 164 types)
- SH 360 · GM 14,191 · W 13,968 · L 223. Winnable shuffles 293; unwinnable 67; with both W and L games 56
- Type sizes: 91 types of 1 shuffle, 36 of 2, 10 of 3, 11 of 4, 6 of 5, 2 of 6, 3 of 7, 2 of 8, one each of 9, 11 and 24
- Fewest plays: 6 (120 shuffles), 7 (114), 8 (46), 9 (12), 10 (1); range of games 1–290 per shuffle, lines 1–34
- Full type list with members and per-shuffle characteristics: `data/types-3223.json`; all games: `data/games-3223.txt (generated, not committed)`

---

## Change log
- 2026-11-14 — D1–D4 now also computed directly from the deal (`solver/sampling.py`); they reproduce every 3223 figure for H1, H4 and H5
- 2026-11-14 — 3223 analysed (360 shuffles, 164 types). H1 restated as a lower bound (exact in 85% of 3223). H3 reinterpreted as early freedom. Added H4 (aces exposed → winnable), H5 (blocking cards), H6 (deciding choices; first seen in 3223)
- 2026-11-14 — Catalog started from the 2223 analysis (T1–T3, D1–D4, O1–O4, H1–H3). D1 generalised to any pile after 3223-1
