# Solitaire Research

A systematic study of Klondike solitaire, working up from deliberately tiny ("absurd") setups toward a full 52-card, draw-3 game (K473). Every shuffle of a small setup is solved exhaustively, every complete game is recorded, and the results are used to find characteristics of a deal that predict how it plays out.

## Setup codes

`[high card][number of suits][number of tableau columns][draw quantity]`, e.g. `3223` = A–3 in two suits (♠♥), two columns, draw 3. A standard game is `K473`. Shuffles are numbered in standard order (rank first, then suit ♠♥♣♦), with mirrored shuffles removed.

## Layout

| Folder | Contents |
|---|---|
| `notes/` | `solitaire-notes.md`: definitions, rules, notation, per-setup results and diagram conventions. `shuffle-type-catalog.md`: deal/outcome characteristics, shuffle types and the hypotheses tested against each setup |
| `solver/` | `solitaire-solver3.py`: current solver (draws, counting mode). `solitaire-solver2.py`: previous version (no draws). `shuffle_types.py`: shuffle-type analysis. `sampling.py`: random-shuffle samples and 95% intervals. `calibrate.py`: checks the sampling method against a fully solved setup. `summarize.py` / `compare.py`: summary of a sample table, and discovery vs confirmation comparison. `legacy/`: the first single-suit solver |
| `pages/` | `solitaire-play-diagrams.html`: the play-diagram viewer (open in a browser). `vertical-mock.html`: the layout mock-up |
| `data/` | Small result files kept in the repository (game list for 2223, shuffle types and exact per-shuffle table for 3223, 6223/6233 sample tables) |

## Running the solver

Requires Python 3 (standard library only).

```bash
python3 solver/solitaire-solver3.py 3223 3223.json > games-3223.txt
```

Writes every shuffle's game tree to `3223.json` and prints every complete game. Then:

```bash
python3 solver/shuffle_types.py 3223.json
```

prints each shuffle's deal and outcome characteristics and groups the shuffles into shuffle types.

For larger setups (e.g. 6223, 6233) building every game is impractical; use the counting mode `stats()` in `solitaire-solver3.py`, which returns games, wins, losses, fewest win and longest game per shuffle without building the tree. To sample:

```bash
python3 solver/sampling.py 6223 10000 1 sample-6223.csv
```

(setup, sample size, seed, output table).

## Generated data

Large outputs (full game lists, game-tree JSON) are not committed; they can be regenerated with the commands above and are listed in `.gitignore`.
