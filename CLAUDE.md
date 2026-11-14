# Working agreement for this project

- The user leads; follow their direction step by step. Keep comments to a minimum and ask only for clarification. If the user breaks a Klondike rule, explain how briefly.
- Make visual/design changes one at a time so each can be evaluated; don't bundle unrequested changes.
- Keep `notes/solitaire-notes.md` (definitions, rules, results, diagram conventions) and `notes/shuffle-type-catalog.md` (characteristics, types, hypotheses with per-setup status, change log) up to date as decisions are made.
- Read `notes/ROADMAP.md` first in a new session: it holds the current state, open questions and next steps.
- Commit and push changes to this repository as work progresses (it is the master copy). No personal details (e.g. the user's email) in commits or files.
- Keep this repository separate from the user's game-play app repository; never attach or read that repository from here.

# Published pages (claude.ai artifacts)

| Page | URL | Source |
|---|---|---|
| Solitaire Play Diagrams | https://claude.ai/artifact/MdKigeMNb2CJehidHiZygh | `pages/solitaire-play-diagrams.html` |
| Solitaire Rule Player | https://claude.ai/artifact/NY4GwDxqt6kcKYYWQsziRq | `player/page.html` + `player/engine.js`, built by `python3 player/build.py` into `pages/solitaire-player.html` |
| Vertical Play Mock-up | https://claude.ai/artifact/R3726UuvVfB4FH9BoWuGxf | `pages/vertical-mock.html` |
| Card Suit Fonts (comparison) | https://claude.ai/artifact/PzGVDrcgNJHR2psCoLeq8q | not in repo |
| Notation Fonts (comparison) | https://claude.ai/artifact/3GmqEWtuQBSVyu2aTA5TVt | not in repo |

To update a page from a new session, read it with the Artifact tool's `read` action (or start from the repo source), edit, and publish with the existing `url` so the link stays the same; then copy the source back into `pages/` and commit. For the Rule Player, edit `player/page.html` / `player/engine.js`, rebuild, and publish `pages/solitaire-player.html` with its `url`.
