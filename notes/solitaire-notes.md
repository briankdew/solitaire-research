# Solitaire Notes

## Game Code
`[high card][number of suits][number of tableau columns][draw quantity]`
- Standard full-deck draw-3 Klondike = **K473**
- Default draw = 3 unless otherwise specified

## Objective
Move every card to home (h).
- **Highest objective:** win the same game in the fewest plays.

## Play Types (tentative)
- Judged ONLY by the plays available at that moment, never by where they lead. Several plays can be progressive at once (not zero-sum)
- Degrees of progressive (ranking system to grow with complexity):
  - **p¹** (first degree): the direct path
  - **p²** (second degree): the same card had a more direct play available at that moment (so far: a card sent to the empty column when it could have gone straight home)
- Earlier labels map as: p → p¹, r → p². What we called "regressive" so far was only relatively regressive
- In a game that doesn't end in W, everything after the last progressive play is illegal, and therefore regressive by definition
- Solver rule today: p² if the same card has a home play available but this play sends it elsewhere; otherwise p¹. No look-ahead

## Suit Order
♠ ♥ ♣ ♦

## Shuffle Types
Characteristics used to group shuffles into "shuffle types" (intrinsic play mirrors) are kept in `notes/shuffle-type-catalog.md`, with their status per setup. Computed by `solver/shuffle_types.py`.

## Mirrored Shuffles
A mirror is a shuffle order with identical rank order whose suits have been relabeled so that same-color suits stay the same color (it plays identically). Keep the first instance (lowest shuffle number, per suit hierarchy ♠♥♣♦); disregard subsequent mirrors.
- **2 suits** (♠♥): 1 mirror — ♠ maps to ♥ | ♥ maps to ♠
- **3 suits** (♠♥♣): 1 mirror — ♠ maps to ♣ | ♥ maps to ♥ | ♣ maps to ♠
- **4 suits** (♠♥♣♦): 7 mirrors (each shuffle has 8 equivalent versions):
  1. ♠ maps to ♠ | ♥ maps to ♦ | ♣ maps to ♣ | ♦ maps to ♥
  2. ♠ maps to ♥ | ♥ maps to ♠ | ♣ maps to ♦ | ♦ maps to ♣
  3. ♠ maps to ♥ | ♥ maps to ♣ | ♣ maps to ♦ | ♦ maps to ♠
  4. ♠ maps to ♣ | ♥ maps to ♥ | ♣ maps to ♠ | ♦ maps to ♦
  5. ♠ maps to ♣ | ♥ maps to ♦ | ♣ maps to ♠ | ♦ maps to ♥
  6. ♠ maps to ♦ | ♥ maps to ♠ | ♣ maps to ♥ | ♦ maps to ♣
  7. ♠ maps to ♦ | ♥ maps to ♣ | ♣ maps to ♥ | ♦ maps to ♠
- Applied by the solver: mirrors removed and remaining shuffles renumbered 1..n in standard order (the study is only concerned with non-mirror shuffles). Single-suit setups are unaffected

## Areas
- **s**: stock (noted by card count, e.g. `0s`). Always shown in the board state; the count of hidden cards can affect whether to play the active waste card
- **w**: waste (`--w` = empty)
- Stock/waste view (philosophical): stock = unseen cards only; once seen, a card is effectively part of the waste
  - Turning the waste over into a "new stock" is a non-event (a leftover from physical play)
  - Once the stock is empty: either play the active waste card, or draw (move the bottom group of cards, by draw qty, to the top to expose a new active card)
- **c**: columns, labeled a, b, c, …
- **h**: home (= "foundation"; never `f`, which is a column label). Suit pile implied by card suit; home always starts empty

## Actions
Three distinct actions: **deal**, **draw**, **play**
- **Play** (= "move"): any card (incl. top card of a run) moved w-c, w-h, c-c, or c-h
- A play must always be a legal move under the rules
- High card fills an empty column (only the high card from the game code may do so)
- An A may never be played (as opposed to dealt) to a tableau column. An exposed A can always go straight home, so any A-to-column play was always p². Overrides "high card fills an empty column" in A-high setups
- **Deal** and **draw** are neutral (not plays); they make plays available
- The deal includes the first draw (the player sees every card the rules allow before the first play)
- Consequences, not actions: revealing a hidden column card; turning the waste over
- No play is ever made from the stock

## Notation
- Card + location: `A♠a` = A♠ face-up on column a
- 10 is written `X` (every card designation is 2 characters, e.g. `X♥`)
- Play: card + from-to, e.g. `A♠a-h`
- Empty pile: `--` + area, e.g. `--w`, `--a`
- A play includes revealing any hidden card it uncovers
- Result: W/L + total plays, e.g. `W1`
- Shuffle orders numbered in standard (lexicographic) order; first card listed = first dealt
- Game ID: `[game code]-[shuffle order number]`, e.g. `2113-1`
- Full game ID: `[game ID].[game play number]-[result]`, e.g. `2113-1.1-W2`

---

## Cognate Criteria (draft)
A setup [H][S][C][3] is a **limited cognate** of K473 when:
1. It builds stacks (at least 3 ranks, both colours)
2. After the deal (C(C+1)/2 cards to the tableau, then the first draw) the waste is full and at least one full draw remains in the stock
3. Stock + waste is an exact multiple of the draw (K473: 24 = 8 × 3), so draw groupings repeat until a waste play shifts them
4. Columns ≥ suits, so every suit's high card can be played to an empty column (justified); extra columns likely add new play characteristics (speculative)
- Smallest 2-suit limited cognate: **6223** (12 cards; 9 in stock + waste = 3 draws). Condition 3 with 2 suits and 2 columns needs 2H − 3 ≡ 0 (mod 3), so H = 3 (no stock draw) or H = 6
- A **full cognate** also needs two suits of each colour (every card has two possible build targets) and face-down depth > 1. Smallest meeting 1–4 with 4 suits: **4443** (16 cards; 6 in stock + waste)
- Note: columns = suits leaves no spare column once every high card holds one; K473 has 7 columns for 4 kings (3 spare)

## Solver
- `solver/solitaire-solver3.py` (current): adds draw handling and a fast counting mode. Same results as solver2 on every setup without draws (A113–3223)
- Draws: neutral (never counted). A draw turns up the next 3 cards (fewer if short) onto the waste, last on top; an empty stock is refilled by turning the waste over (non-event); passes unlimited
- Draws only matter for waste plays, so each node offers waste plays at every distinct draw position of the stock/waste cycle (the child records the number of draws) and all other plays at the current position
- Counting mode `stats()`: games, wins, losses, fewest win, longest game per shuffle without building the tree; matches full trees on all 3223 shuffles and 600 sampled 4223/5223 shuffles. About 1–2 ms per 6223/6233 shuffle
- Scale: 6223 and 6233 each have 239,500,800 shuffles after mirrors (~3 days single-threaded in counting mode); diagrams/type analysis need full trees, which can reach millions of games for one shuffle

## Player (rule-driven play, no solver)
- `player/engine.js`: plays a shuffle forward with the solver's rules (cross-checked against the solver: 1,050 deals, 35,812 positions, 14,473 draws, no difference; `player/crosscheck.js` | `crosscheck.py`)
- **What the player sees (no memory):** face-up column cards and the number of face-down cards per column; the waste cards of the latest draw still on the waste (if none are left, the waste's top card); the top card of each home pile; the number of cards in the stock; the number of plays made so far in the current pass
- **Actions:** every legal play, plus draw. A draw is one of the choices (it is a decision the player makes)
- **Game end:** W when every card is home. L when no play and no draw is possible, or when the stock must be turned over after a full pass in which no play was made (pass limit). S (stopped) after 3,000 actions (safety; cannot happen with 2 suits)
- **Decisions:** the active rules, in their order, each narrow the options (a rule is skipped when it would keep none or all of them); the player then picks at random (seeded) among what is left. Every decision is labelled with how it was made (only option / decided by rules / random of n) and with every rule it matches (the rule would have kept the chosen option) or goes against; a random choice that matches no rule is a "no-rule random" decision
- **Starter rules** (tentative, to be replaced by the user's): R1 home, R2 A or 2 home, R3 reveal a face-down card, R4 empty a column, R5 high card to an empty column, R6 waste to column, R7 column to column, R8 play before drawing, R9 no detour (avoid p²)
- **Scoring:** the solver's results are used only to score finished games: won / lost but winnable / lost, not winnable
- Page: Solitaire Rule Player (see CLAUDE.md). Batch runs: `node player/run.js <set.csv> <code> [rules] [games per shuffle] [seed] [out.csv]`
- First runs (seed 1): 3223, 100 games per shuffle: no rules 26.4% of winnable games won; R8 alone 92.2%; R8 › R1 88.6% (sending cards home first loses some winnable games, as H6 found). 6233 discovery, R8: 71.2% of winnable won

## Sampling (for setups too large to solve every shuffle)
- `solver/sampling.py`: draws a shuffle by shuffling the full deck uniformly and keeping the first instance of its mirror class (all mirror classes are the same size, so mirror-removed shuffles are sampled uniformly); with replacement. Each shuffle becomes one table row: order, D1–D4, stock size, games, wins, losses, winnable, fewest, most
- 95% intervals: proportions by Wilson score; means by normal approximation; medians/percentiles by a distribution-free order-statistic (binomial) interval
- D1 counts blocking cards in the columns (face-down cards included), the waste and the stock, each kept as its own column of the table. In the stock each draw's group of 3 is a pile (last drawn on top). Stock blockers are soft: e.g. 6223 A♠ 6♥ 4♠ 6♠ 2♥ 2♠ 5♥ 5♠ A♥ 3♠ 3♥ 4♥ has 4♥ on 3♥ in the last stock group, but once 2♠ and A♥ have gone home the stock regroups on the next pass and 4♥ falls into a group of its own; the shuffle is won in 12 plays
- **Calibration on 3223** (`solver/calibrate.py`; exact table `data/exact-3223.csv`): counting mode reproduces all totals (14,191 games, 13,968 W, 223 L, 293 winnable). The sampler reaches all 360 shuffles uniformly (360,000 draws: chi-square 357 on 359 df). 2,000 samples at each of n = 50, 100, 200, 500, 1000:
  - Proportions (winnable, H1 equality, winnable by D4 and D1 level): coverage 94–96% at every n
  - Mean games per shuffle: coverage 92% at n = 50, 94% at 100, 95–96% from 200 on (heavy tail; fine at 10,000)
  - Median and 90th percentile of games: coverage 96–99% (conservative because counts tie)
  - Mean error at n = 1000: winnable ±1.0 points, mean games ±1.3, median games ±0.7
  - Expected 95% margins at n = 10,000: about ±1 percentage point for any proportion over the whole sample (wider for subgroups: ±1.96·√(p(1−p)/m) for a subgroup of m)

## Purpose
Build a knowledge base of played games for analysis.

---

## Games

### A113
- Suit: ♠
- Shuffle orders: 1 (A♠)
- Setups: 1 (`A♠a`, `--w`, `0s`)
- Plays available: 1 (`A♠a-h`)
- Results: 1 (`W1`)
- Full game: `A113-1.1-W1` (1. A♠a-h p). Node IDs: `1-0` → `1-1` (W1)

### 2113
- Suit: ♠
- Shuffle orders: 2 (2!)
  1. A♠ 2♠
  2. 2♠ A♠

#### 2113-1
- Setup: `A♠a`, `2♠w`, `0s`
- Plays available: 1 (`A♠a-h`)
- After `A♠a-h`: `--a`, `2♠w`, `0s`, `A♠h`
  - Plays available: 2 (`2♠w-h` p¹ → W2, `2♠w-a` p² → W3)
  - p/r judged on the plays visible to the player + highest objective

- Full games:
  ```
  2113-1.1-W2   Setup: A♠a, 2♠w, 0s
  1. A♠a-h   p¹
  2. 2♠w-h   p¹
  W2
  ```
  ```
  2113-1.2-W3   Setup: A♠a, 2♠w, 0s
  1. A♠a-h   p¹
  2. 2♠w-a   p²
  3. 2♠a-h   p¹
  W3
  ```

#### 2113-2
- Setup: `2♠a`, `A♠w`, `0s`
- Plays available: 1 (`A♠w-h` p¹). `A♠w-a` illegal (same color)
- After `A♠w-h`: `2♠a`, `--w`, `0s`, `A♠h`
  - Plays available: 1 (`2♠a-h` p¹)
- Full games:
  ```
  2113-2.1-W2   Setup: 2♠a, A♠w, 0s
  1. A♠w-h   p¹
  2. 2♠a-h   p¹
  W2
  ```
- Node IDs: `1-0` → `1-1` → `1-2` (W2)

### 3113
- Suit: ♠
- Shuffle orders: 6 (3!)
  1. A♠ 2♠ 3♠
  2. A♠ 3♠ 2♠
  3. 2♠ A♠ 3♠
  4. 2♠ 3♠ A♠
  5. 3♠ A♠ 2♠
  6. 3♠ 2♠ A♠

#### 3113-1
- Setup: `A♠a`, `2♠ 3♠w` (bottom → top; 3♠ active), `0s`
- Plays: only one available at each state (3♠ must fill the empty column before 2♠ is reachable)
- Full games:
  ```
  3113-1.1-W4   Setup: A♠a, 2♠ 3♠w, 0s
  1. A♠a-h   p¹
  2. 3♠w-a   p¹
  3. 2♠w-h   p¹
  4. 3♠a-h   p¹
  W4
  ```
- Node IDs: `1-0` → `1-1` → `1-2` → `1-3` → `1-4` (W4)

#### 3113-2
- Setup: `A♠a`, `3♠ 2♠w` (bottom → top; 2♠ active), `0s`
- After `A♠a-h` → `2♠w-h`: `--a`, `3♠w`, `0s`, `A♠ 2♠h`
  - Plays available: 2 (`3♠w-h` p¹ → W3, `3♠w-a` p² → W4)
- Full games:
  ```
  3113-2.1-W3   Setup: A♠a, 3♠ 2♠w, 0s
  1. A♠a-h   p¹
  2. 2♠w-h   p¹
  3. 3♠w-h   p¹
  W3
  ```
  ```
  3113-2.2-W4   Setup: A♠a, 3♠ 2♠w, 0s
  1. A♠a-h   p¹
  2. 2♠w-h   p¹
  3. 3♠w-a   p²
  4. 3♠a-h   p¹
  W4
  ```
- Node IDs: `1-0` → `1-1` → `1-2` → `1-3` (W3); fork after `1-2` → `2-3` → `2-4` (W4)

#### 3113-3
- Setup: `2♠a`, `A♠ 3♠w` (bottom → top; 3♠ active), `0s`
- Plays available: 0. 3♠ can't go home (home empty) or onto 2♠ (must be lower + opposite color); 2♠ can't go home; no empty column; cycling the waste returns the same order
- Full game: `3113-3.1-L0` (no plays). Node IDs: `1-0` (L0)
- First loss in the study

#### 3113-4
- Setup: `2♠a`, `3♠ A♠w` (bottom → top; A♠ active), `0s`
- After `A♠w-h` → `2♠a-h`: `--a`, `3♠w`, `0s`, `A♠ 2♠h`
  - Plays available: 2 (`3♠w-h` p¹ → W3, `3♠w-a` p² → W4)
- Full games:
  ```
  3113-4.1-W3   Setup: 2♠a, 3♠ A♠w, 0s
  1. A♠w-h   p¹
  2. 2♠a-h   p¹
  3. 3♠w-h   p¹
  W3
  ```
  ```
  3113-4.2-W4   Setup: 2♠a, 3♠ A♠w, 0s
  1. A♠w-h   p¹
  2. 2♠a-h   p¹
  3. 3♠w-a   p²
  4. 3♠a-h   p¹
  W4
  ```
- Node IDs: `1-0` → `1-1` → `1-2` → `1-3` (W3); fork after `1-2` → `2-3` → `2-4` (W4)

#### 3113-5
- Setup: `3♠a`, `A♠ 2♠w` (bottom → top; 2♠ active), `0s`
- Plays available: 0. 2♠ can't go home (home empty) or onto 3♠ (same color); 3♠ can't go home; no empty column; cycling the waste returns the same order
- Full game: `3113-5.1-L0` (no plays). Node IDs: `1-0` (L0)

#### 3113-6
- Setup: `3♠a`, `2♠ A♠w` (bottom → top; A♠ active), `0s`
- Only one play available at each state
- Full games:
  ```
  3113-6.1-W3   Setup: 3♠a, 2♠ A♠w, 0s
  1. A♠w-h   p¹
  2. 2♠w-h   p¹
  3. 3♠a-h   p¹
  W3
  ```
- Node IDs: `1-0` → `1-1` → `1-2` → `1-3` (W3)

#### 3113 summary
- SH 6 · GM 8 · W 6 · L 2
- Losses (3113-3, 3113-5): A♠ buried under the other waste card with no empty column and no legal move for the top waste card
- Forks (3113-2, 3113-4): 3♠ can go home (W3) or to the empty column first (p², W4)
- 3113-1 is the only shuffle where the high-card-to-empty-column play is required to win

### 4113 *
- * Marked for possible deletion: nothing learned that informs standard Klondike; adding suits without adding columns judged not informative either
- Suit: ♠ · Shuffle orders: 24 (4!) · generated by exhaustive solver (`solver/legacy/solitaire-solver.py`), checked against hand-built 2113 and 3113
- Deal: first card to a; the other three all go to the waste on the first draw (last drawn on top). Waste order never changes (≤3 cards, draw-3)
- SH 24 · GM 27 · W 10 · L 17
  - Winnable shuffles: 7 (3, 4, 6, 10, 12, 18, 24); forked (W4 or W5): 6, 12, 18
  - First losses after plays: L1 (2, 5, 16, 22), L2 (1)
  - Plays in lost games are judged like any other play (see Play Types); all 4113 markings stand
- All games (shuffle order first → last dealt; setup a / w bottom→top):
```
4113-1 A♠ 2♠ 3♠ 4♠ | setup a: ['A♠'] w: ['2♠', '3♠', '4♠']
   4113-1.1-L2: A♠a-h p¹, 4♠w-a p¹
4113-2 A♠ 2♠ 4♠ 3♠ | setup a: ['A♠'] w: ['2♠', '4♠', '3♠']
   4113-2.1-L1: A♠a-h p¹
4113-3 A♠ 3♠ 2♠ 4♠ | setup a: ['A♠'] w: ['3♠', '2♠', '4♠']
   4113-3.1-W5: A♠a-h p¹, 4♠w-a p¹, 2♠w-h p¹, 3♠w-h p¹, 4♠a-h p¹
4113-4 A♠ 3♠ 4♠ 2♠ | setup a: ['A♠'] w: ['3♠', '4♠', '2♠']
   4113-4.1-W5: A♠a-h p¹, 2♠w-h p¹, 4♠w-a p¹, 3♠w-h p¹, 4♠a-h p¹
4113-5 A♠ 4♠ 2♠ 3♠ | setup a: ['A♠'] w: ['4♠', '2♠', '3♠']
   4113-5.1-L1: A♠a-h p¹
4113-6 A♠ 4♠ 3♠ 2♠ | setup a: ['A♠'] w: ['4♠', '3♠', '2♠']
   4113-6.1-W4: A♠a-h p¹, 2♠w-h p¹, 3♠w-h p¹, 4♠w-h p¹
   4113-6.2-W5: A♠a-h p¹, 2♠w-h p¹, 3♠w-h p¹, 4♠w-a p², 4♠a-h p¹
4113-7 2♠ A♠ 3♠ 4♠ | setup a: ['2♠'] w: ['A♠', '3♠', '4♠']
   4113-7.1-L0: 
4113-8 2♠ A♠ 4♠ 3♠ | setup a: ['2♠'] w: ['A♠', '4♠', '3♠']
   4113-8.1-L0: 
4113-9 2♠ 3♠ A♠ 4♠ | setup a: ['2♠'] w: ['3♠', 'A♠', '4♠']
   4113-9.1-L0: 
4113-10 2♠ 3♠ 4♠ A♠ | setup a: ['2♠'] w: ['3♠', '4♠', 'A♠']
   4113-10.1-W5: A♠w-h p¹, 2♠a-h p¹, 4♠w-a p¹, 3♠w-h p¹, 4♠a-h p¹
4113-11 2♠ 4♠ A♠ 3♠ | setup a: ['2♠'] w: ['4♠', 'A♠', '3♠']
   4113-11.1-L0: 
4113-12 2♠ 4♠ 3♠ A♠ | setup a: ['2♠'] w: ['4♠', '3♠', 'A♠']
   4113-12.1-W4: A♠w-h p¹, 2♠a-h p¹, 3♠w-h p¹, 4♠w-h p¹
   4113-12.2-W5: A♠w-h p¹, 2♠a-h p¹, 3♠w-h p¹, 4♠w-a p², 4♠a-h p¹
4113-13 3♠ A♠ 2♠ 4♠ | setup a: ['3♠'] w: ['A♠', '2♠', '4♠']
   4113-13.1-L0: 
4113-14 3♠ A♠ 4♠ 2♠ | setup a: ['3♠'] w: ['A♠', '4♠', '2♠']
   4113-14.1-L0: 
4113-15 3♠ 2♠ A♠ 4♠ | setup a: ['3♠'] w: ['2♠', 'A♠', '4♠']
   4113-15.1-L0: 
4113-16 3♠ 2♠ 4♠ A♠ | setup a: ['3♠'] w: ['2♠', '4♠', 'A♠']
   4113-16.1-L1: A♠w-h p¹
4113-17 3♠ 4♠ A♠ 2♠ | setup a: ['3♠'] w: ['4♠', 'A♠', '2♠']
   4113-17.1-L0: 
4113-18 3♠ 4♠ 2♠ A♠ | setup a: ['3♠'] w: ['4♠', '2♠', 'A♠']
   4113-18.1-W4: A♠w-h p¹, 2♠w-h p¹, 3♠a-h p¹, 4♠w-h p¹
   4113-18.2-W5: A♠w-h p¹, 2♠w-h p¹, 3♠a-h p¹, 4♠w-a p², 4♠a-h p¹
4113-19 4♠ A♠ 2♠ 3♠ | setup a: ['4♠'] w: ['A♠', '2♠', '3♠']
   4113-19.1-L0: 
4113-20 4♠ A♠ 3♠ 2♠ | setup a: ['4♠'] w: ['A♠', '3♠', '2♠']
   4113-20.1-L0: 
4113-21 4♠ 2♠ A♠ 3♠ | setup a: ['4♠'] w: ['2♠', 'A♠', '3♠']
   4113-21.1-L0: 
4113-22 4♠ 2♠ 3♠ A♠ | setup a: ['4♠'] w: ['2♠', '3♠', 'A♠']
   4113-22.1-L1: A♠w-h p¹
4113-23 4♠ 3♠ A♠ 2♠ | setup a: ['4♠'] w: ['3♠', 'A♠', '2♠']
   4113-23.1-L0: 
4113-24 4♠ 3♠ 2♠ A♠ | setup a: ['4♠'] w: ['3♠', '2♠', 'A♠']
   4113-24.1-W4: A♠w-h p¹, 2♠w-h p¹, 3♠w-h p¹, 4♠a-h p¹
```

### 2223
- Suits ♠♥ · 2 columns · draw 3 · Shuffle orders: 24 (4!), 12 after removing mirrors; cards ordered rank first then suit (A♠ A♥ 2♠ 2♥) for numbering
- Deal (Klondike row order): card 1 → a face-up; card 2 → b face-down; card 3 → b face-up (on the hidden card); card 4 → stock, then into the waste on the first draw. Stock 0
- Generated by `solver/solitaire-solver2.py` (multi-column, multi-suit, face-down cards); it reproduces A113/2113/3113 exactly
- Solver rules added (flag for review):
  - A high card (or the run it heads) already at the bottom of its column with nothing face-down beneath it may not move to another empty column (pure relabel; would loop forever)
  - No play may recreate a board state already reached in the same game
- SH 12 · GM 109 · W 109 · L 0 (every shuffle and every game is a win). History: 24 shuffles / 488 games → no-A-to-column rule → 218 games → mirrors removed → 12 shuffles / 109 games
- Best (fewest-play) win per shuffle: W4 in 10 shuffles, W5 in 2 (2223-2, 2223-10)
- Many "different games" are the same plays in a different order (transpositions)
- New in the diagrams: face-down cards drawn as plain card backs at the bottom (left) of a column pile. No column building remains in 2223 under the no-A rule (first possible with a 3, e.g. 3223)
- Full game list: `data/games-2223.txt`

### 3223 (all 360 shuffles solved; shuffle 3223-1 diagrammed)
- Suits ♠♥ · 2 columns · draw 3 · 720 shuffle orders, 360 after removing mirrors
- Deal: card 1 → a; card 2 → b face-down; card 3 → b face-up; cards 4–6 → waste on the first draw (stock 0). Draws never change the waste order (≤3 cards)
- 3223-1 (A♠ A♥ 2♠ 2♥ 3♠ 3♥): a: A♠ | b: [1 down] 2♠ | w: 2♥ 3♠ 3♥ (3♥ active)
  - GM 50 · W 50 · L 0. Fewest plays W7 (6 games); W8 15, W9 19, W10 10
  - First column building in the study: 2♠ onto 3♥ (`2♠b-a`, p² because 2♠ could go straight home)
  - Full game list: `data/games-3223.txt (generated, not committed)`
- All 360: SH 360 · GM 14,191 · W 13,968 · L 223 · winnable shuffles 293 · 164 shuffle types (see the shuffle-type catalog)
- First setup where a choice can lose a winnable game (56 shuffles)

### 6223 and 6233 (limited cognates; discovery and confirmation samples of 10,000 each)
- Same 12 cards (A–6 ♠♥), draw 3; 239,500,800 shuffles each after mirrors. Sampled with `solver/sampling.py` (seeds 6223001, 6233001); tables `data/sample-6223-discovery.csv`, `data/sample-6233-discovery.csv`; summary by `solver/summarize.py`. No repeated shuffle in either sample
- 6223: 2 columns (a 1 card; b 1 down + 1 up), waste 3, stock 6 · 6233: 3 columns (a 1; b 1 down + 1; c 2 down + 1), waste 3, stock 3
- Margins are 95% intervals

| | 6223 | 6233 |
|---|---|---|
| Winnable shuffles | 49.2% (48.3–50.2) | 59.5% (58.5–60.5) |
| Shuffles with a losing game | 95.8% | 80.9% |
| Every game won | 4.2% | 19.1% |
| Games per shuffle: median | 86 (68–109) | 2,935 (2,416–3,518) |
| Games per shuffle: 90th percentile | 35,862 | 466,416 |
| Games per shuffle: mean / max | 14,471 / 997,424 | 282,179 / 50,894,877 |
| Share of all games won | 99.1% | 99.9% |
| Fewest plays (winnable): mean, range | 14.2, 12–21 | 15.3, 12–22 |
| No play possible after the deal | 12.4% | 7.6% |

- The longest game per shuffle is bimodal: either the game stalls within a few plays, or it runs 16–22 plays
- Most games are won even in shuffles that can be lost: losing games are few but spread over most shuffles
- **Confirmation** (seeds 6223002, 6233002; `data/sample-*-confirmation.csv`; compared by `solver/compare.py`): of 62 winnability comparisons (overall and by each level of D1–D4), 59 agree within their 95% margin and 3 differ marginally (z 2.1–2.2, all 6233: no play after the deal 7.6% vs 6.8%, winnable with D2 = 0, winnable with D1 = 2). About 3 are expected by chance at the 5% level, and no trend changes direction. Every median of games agrees. H1 (fixed blockers) holds in all 4,908 and 6,056 winnable confirmation shuffles. Confirmation winnable: 6223 49.1% (48.1–50.1), 6233 60.6% (59.6–61.5). One 6223 shuffle occurs in both samples and one twice in the confirmation sample (expected ≈ 0.6 such repeats)

### Pattern so far (single suit, 1 column, draw 3)
| Setup | SH | GM | W | L | Winnable shuffles |
|---|---|---|---|---|---|
| A113 | 1 | 1 | 1 | 0 | 1 |
| 2113 | 2 | 3 | 3 | 0 | 2 |
| 3113 | 6 | 8 | 6 | 2 | 4 |
| 4113 | 24 | 27 | 10 | 17 | 7 |
| 2223 | 12 | 109 | 109 | 0 | 12 |
| 3223 | 360 | 14,191 | 13,968 | 223 | 293 |

---

## Diagram Method — vertical layout (current, applied to Solitaire Play Diagrams)
Supersedes the horizontal layout notes further below (kept for history).
- One felt panel per node; plays flow DOWN, forks step RIGHT
- Panel columns: `s/w` (stock count card on top, waste below) | tableau a, b, … (counter card with the face-down count on top only when there are face-down cards) | one home pile per suit (top card only). All piles stack downward
- Gaps: 9px between tableau columns and between home piles (room for glows); 18px group gaps after s/w and after the last tableau column
- Cards 21×14px: rank 10pt + suit 10.5pt Libertinus Mono (0.3px outline), each glyph's top 2px below the card top; 1px overlap down a pile; two-part card shadow (soft downward + soft edge shadow above each card, blur 2)
- No grey "receded" faces, no played-card colour, no selection outline in this layout
- Empty column / empty home pile: dark felt slot (#215042, border #6a887a); empty stock: dulled #7a3c44
- Node ID: plain text just above the panel, `FF-PPP` with the fork number in gold
- Play: white glow (#fbfaf5) on the right of the card(s) picked up, gold glow (#bf9000) on the left of where they land (blur 2, offset 3.5px); gold connector from the bottom of the picked-up run to the top of the destination column in the next node; p² / p³ / p⁴ = 2 / 3 / 4 short dashes mid-connector
- Forks: copy of the forking node in the new fork column, fill #456d5f, no border, labelled `FF-PPP.fN` in muted colours (#c4ac70 fork number, #aeaeae rest). Fork lines are horizontal and chained: origin → .f1 → .f2 …, drawn under the panels. The true fork structure stays in the data
- Below each final node: full game ID (e.g. `2223-7.1-W4`) with the W/L part in gold, same size as the node ID, no shadow
- Column labels once per diagram, over the first fork column
- Mock-up page used to develop this: https://claude.ai/artifact/R3726UuvVfB4FH9BoWuGxf (`pages/vertical-mock.html`)

## Diagram Method (draft)
Play diagrams ("Solitaire Play Diagrams"), read left to right (one "Setup [game code]" section per setup, one "Shuffle [game ID]" tree per shuffle; A113 first): https://claude.ai/artifact/MdKigeMNb2CJehidHiZygh
- Page: opens with all "Setup XXXX" headers collapsed (#215042); a setup expands to its shuffle list (area #295f4e); a shuffle expands to its node diagram (#2f6b57)
- Header counts (right-justified, aligned columns): Setup = SH (shuffles) · GM (full games) · W · L; Shuffle = GM · W · L. Counted from the diagram data
- Box = board state (s, w, each column, h). Box position across = number of plays made (deal = 0)
- Play connector (same fork): one curved gold arrow from the node border at the played card's slot to the next node's border at its destination slot; no text labels. Line style by degree: all progressive degrees gold (#bf9000); p¹ solid; p² / p³ / p⁴ = solid with 2 / 3 / 4 short dashes (3px dash, 2.5px gap) centered on the connector; truly regressive (r, not yet defined) = dashed grey (#8a8a8a)
- Fork: copy of the forking node (no node ID, phantom-line border at 60% opacity) placed directly below it in the new fork row; phantom vertical line (node-border color, 60% opacity) joins original to copy; the fork's first play connector runs from the copy to the fork's first node
- Fork: first available play continues on the same row; each other play drops to a new row below
- Each row ends with its result + full game ID
- Node ID: `[fork]-[play]`, zero-padded `FF-PPP` in the diagram (e.g. `01-000`; fork digits in gold)
  - Top row = fork 1; deal/setup box = play 0 (`1-0`)
  - Each play along a fork = play + 1
  - Each new row = next fork number; its first box keeps the play number it occupies (same column as the box above it)
  - The fork is the decision between nodes (right of the shared node); a new fork's first node is the result of its first play that differs from the fork above
  - 2113-1: `1-0` → `1-1` → `1-2` (W2); decision after `1-1` → `2-2` → `2-3` (W3)
- Styling (from mock-up, at 1:1 px; fonts in pt: node ID 7, location labels 11, stock 8, cards 11, play label 10): felt-green table; each node is an outlined vertical stack of slots (s card back with count, w, columns, one h slot per suit); row labels left of first node; play notation above arrow, type in gold italic below
- Face-up piles (waste, column runs, home piles): every face-up card shown left to right, bottom of pile to top, edges touching line-on-line; each later card's shadow falls over the card beneath. Node widens to fit its longest pile
- Home-pile labels (h♠, h♥, …): PT Mono suit glyph (loaded with suits included) at 10pt, top aligned with the top of the h, 2px gap after the h, in suit color, no halo
- Selected card (the card about to be played from this node): overlay outline, same size/corner radius as the card, 1px black (#000) stroke fully outside the card edge, plus inset shadow inside all four card edges (black 80%, blur 2, no offset). Tried: 2px in #9c8e63, two-tone #453e2c/#c4bba1, #453e2c, #100e0a, #0d004b (indigo), #1c1f24 (card ink), 1px #322c15. Final: 1px black + inset shadow, no fill, no outer shadow of its own (card keeps its own shadow). Original node shows the selection for fork 1's play; each fork's phantom copy shows the selection for that fork's play
- Played card (the card just played into this node): face color #e5ddaf (requested as "#e5ddaf1"; assumed typo)
- A card that was just played and is selected again gets both
- Stock cell: s>0 = card back (#7c1e30, light border, shadow) with the count; s=0 = no shadow, no text, fill #7a3c44, border #6a887a
- Waste and home piles only: the top (playable) card has the normal face; cards beneath it have a grey face (#b7b7b7). Column runs keep normal faces
- Card-face font: Libertinus Mono Regular, 11pt (face-up cards only); rank 11pt, suit 12pt, both with a 0.3px same-color outline
- Built from a tree of states (each state lists its plays → next states), so it should extend to any setup
