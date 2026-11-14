/* Solitaire player engine: the same rules as solver/solitaire-solver3.py, played forward by a rule-driven player
   that sees only what is visible on the table. Works in the browser (window.SolitaireEngine) and in Node (require).

   What the player sees (no memory): face-up column cards and the number of face-down cards per column; the waste
   cards of the latest draw that are still on the waste (if none are left, the waste's top card); the top card of
   each home pile; the number of cards in the stock; the number of plays made so far in the current pass.

   Game end: W when every card is home. L when no play and no draw is possible, or when the stock has to be turned
   over after a full pass in which no play was made (the pass limit). S (stopped) after MAX_ACTIONS actions.
*/
(function (root) {
"use strict";
const RANKS = "A23456789XJQK", SUITS = "♠♥♣♦", COLS = "abcdefg";
const MAX_ACTIONS = 3000;
const rank = c => RANKS.indexOf(c[0]);
const red = c => c[1] === "♥" || c[1] === "♦";
const canBuild = (card, onto) => rank(onto) === rank(card) + 1 && red(onto) !== red(card);

function parseCode(code) {
  return { code, high: code[0], nsuits: +code[1], ncols: +code[2], draw: +code[3] };
}
function deckOf(cfg) {
  const out = [];
  for (const r of RANKS.slice(0, RANKS.indexOf(cfg.high) + 1)) for (const s of SUITS.slice(0, cfg.nsuits)) out.push(r + s);
  return out;
}
const MIRRORS = {
  1: [], 2: ["♥♠"], 3: ["♣♥♠"],
  4: ["♠♦♣♥", "♥♠♦♣", "♥♣♦♠", "♣♥♠♦", "♣♦♠♥", "♦♠♥♣", "♦♣♥♠"],
};
function firstInstance(perm, deck, nsuits) {
  // the first instance (in standard order) of this shuffle's mirror class
  const key = p => p.map(c => deck.indexOf(c));
  let best = perm, bk = key(perm);
  for (const m of MIRRORS[nsuits]) {
    const alt = perm.map(c => c[0] + m[SUITS.indexOf(c[1])]);
    const k = key(alt);
    for (let i = 0; i < k.length; i++) { if (k[i] !== bk[i]) { if (k[i] < bk[i]) { best = alt; bk = k; } break; } }
  }
  return best;
}
function parseOrder(text, cfg) {
  // accepts "A♠ 2♥ …", "A♠2♥…", letters s/h/c/d and 10 for X
  const t = text.replace(/10/g, "X").replace(/[shcd]/gi, ch => ({ s: "♠", h: "♥", c: "♣", d: "♦" })[ch.toLowerCase()]);
  const cards = t.replace(/[^A2-9XJQK♠♥♣♦]/gi, "").toUpperCase().match(/[A2-9XJQK][♠♥♣♦]/g) || [];
  const deck = deckOf(cfg);
  const ok = cards.length === deck.length && deck.every(c => cards.includes(c));
  return ok ? cards : null;
}

// ---------- random numbers (seeded) ----------
function rng32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6D2B79F5) >>> 0; let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function randomOrder(cfg, rand) {
  const deck = deckOf(cfg), p = deck.slice();
  for (let i = p.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [p[i], p[j]] = [p[j], p[i]]; }
  return firstInstance(p, deck, cfg.nsuits);
}

// ---------- deal ----------
function deal(cards, cfg) {
  const { ncols, draw } = cfg;
  const cols = Array.from({ length: ncols }, () => ({ down: [], up: [] }));
  let i = 0, done = false;
  for (let r = 0; r < ncols && !done; r++) {
    for (let c = r; c < ncols; c++) {
      if (i >= cards.length) { done = true; break; }
      (c === r ? cols[c].up : cols[c].down).push(cards[i++]);
    }
  }
  for (const col of cols) if (!col.up.length && col.down.length) col.up.push(col.down.pop());   // deck ran out mid-deal
  const stock = cards.slice(i);
  const waste = stock.splice(0, draw);
  return { cols, stock, waste, home: Array(cfg.nsuits).fill(0), fan: waste.length,
           playsThisPass: 0, pass: 1, plays: 0, actions: 0, over: null, last: null };
}
const clone = s => ({ ...s, cols: s.cols.map(c => ({ down: c.down.slice(), up: c.up.slice() })),
                      stock: s.stock.slice(), waste: s.waste.slice(), home: s.home.slice() });

// ---------- legal plays (same order as gen_plays in the solver) ----------
function legalPlays(s, cfg) {
  const out = [], homeOk = c => s.home[SUITS.indexOf(c[1])] === rank(c);
  if (s.waste.length) {
    const top = s.waste[s.waste.length - 1];
    if (homeOk(top)) out.push({ src: "w", dst: "h", n: 1, card: top });
    if (top[0] !== "A") s.cols.forEach((col, j) => {
      const u = col.up;
      if ((u.length && canBuild(top, u[u.length - 1])) || (!u.length && !col.down.length && top[0] === cfg.high))
        out.push({ src: "w", dst: COLS[j], n: 1, card: top });
    });
  }
  s.cols.forEach((col, i) => {
    const u = col.up; if (!u.length) return;
    if (homeOk(u[u.length - 1])) out.push({ src: COLS[i], dst: "h", n: 1, card: u[u.length - 1] });
    for (let k = 0; k < u.length; k++) {
      const base = u[k]; if (base[0] === "A") continue;          // an A may never be played to a column
      s.cols.forEach((c2, j) => {
        if (j === i) return;
        const u2 = c2.up;
        if (u2.length) { if (canBuild(base, u2[u2.length - 1])) out.push({ src: COLS[i], dst: COLS[j], n: u.length - k, card: base }); }
        else if (!c2.down.length && base[0] === cfg.high && !(k === 0 && !col.down.length))
          out.push({ src: COLS[i], dst: COLS[j], n: u.length - k, card: base });   // pure relabel moves excluded
      });
    }
  });
  return out;
}

// ---------- options = plays (with what is visible about them) + draw ----------
function options(s, cfg) {
  const plays = legalPlays(s, cfg);
  const homeable = new Set(plays.filter(p => p.dst === "h").map(p => p.card));
  const opts = plays.map(p => {
    const src = p.src === "w" ? null : s.cols[COLS.indexOf(p.src)];
    const dstCol = p.dst === "h" ? null : s.cols[COLS.indexOf(p.dst)];
    return { kind: "play", ...p,
      degree: p.dst !== "h" && p.n === 1 && homeable.has(p.card) ? "p2" : "p1",
      reveals: !!src && p.n === src.up.length && src.down.length > 0,
      empties: !!src && p.n === src.up.length && src.down.length === 0,
      toEmpty: !!dstCol && !dstCol.up.length,
      label: `${p.card}${p.src}-${p.dst}` };
  });
  if (s.stock.length || s.waste.length) opts.push({ kind: "draw", label: s.stock.length ? "draw" : "draw (stock turned over)" });
  return opts;
}

// ---------- what the player can see ----------
function view(s, cfg) {
  return {
    cols: s.cols.map(c => ({ down: c.down.length, up: c.up.slice() })),
    waste: s.fan > 0 ? s.waste.slice(-s.fan) : s.waste.slice(-1),
    wasteCount: s.waste.length, stock: s.stock.length,
    home: s.home.map((h, k) => (h ? RANKS[h - 1] + SUITS[k] : null)),
    playsThisPass: s.playsThisPass, high: cfg.high,
  };
}

// ---------- applying an action ----------
function apply(s0, opt, cfg) {
  const s = clone(s0); s.actions++;
  if (opt.kind === "draw") {
    if (!s.stock.length) {
      if (s.playsThisPass === 0) { s.over = { result: "L", why: "a full pass with no play" }; s.last = null; return s; }
      s.stock = s.waste; s.waste = []; s.pass++; s.playsThisPass = 0;
    }
    const drawn = s.stock.splice(0, cfg.draw);
    s.waste.push(...drawn); s.fan = drawn.length; s.last = { draw: drawn };
  } else {
    let moved;
    if (opt.src === "w") { moved = [s.waste.pop()]; if (s.fan > 0) s.fan--; }
    else {
      const col = s.cols[COLS.indexOf(opt.src)];
      moved = col.up.splice(col.up.length - opt.n, opt.n);
      if (!col.up.length && col.down.length) col.up.push(col.down.pop());   // reveal
    }
    if (opt.dst === "h") s.home[SUITS.indexOf(moved[0][1])]++;
    else s.cols[COLS.indexOf(opt.dst)].up.push(...moved);
    s.plays++; s.playsThisPass++; s.last = { moved };
  }
  const total = deckOf(cfg).length;
  if (s.home.reduce((a, b) => a + b, 0) === total) s.over = { result: "W", why: `all cards home in ${s.plays} plays` };
  else if (!options(s, cfg).length) s.over = { result: "L", why: "no play and no draw" };
  else if (s.actions >= MAX_ACTIONS) s.over = { result: "S", why: `stopped after ${MAX_ACTIONS} actions` };
  return s;
}

// ---------- rules ----------
// Each rule keeps the options it prefers. It "applies" at a decision when it keeps some options but not all.
const RULES = [
  { id: "R1", name: "Home", desc: "Play a card home", keep: o => o.filter(x => x.dst === "h") },
  { id: "R2", name: "A or 2 home", desc: "Play an A or 2 home", keep: o => o.filter(x => x.dst === "h" && rank(x.card) <= 1) },
  { id: "R3", name: "Reveal", desc: "A play that turns up a face-down card", keep: o => o.filter(x => x.reveals) },
  { id: "R4", name: "Empty a column", desc: "A play that leaves a column empty", keep: o => o.filter(x => x.empties) },
  { id: "R5", name: "High card to empty column", desc: "Move the high card (or its run) to an empty column", keep: o => o.filter(x => x.toEmpty) },
  { id: "R6", name: "Waste to column", desc: "Play the waste card to a column", keep: o => o.filter(x => x.src === "w" && x.dst !== "h") },
  { id: "R7", name: "Column to column", desc: "Move a card or run between columns", keep: o => o.filter(x => x.kind === "play" && x.src !== "w" && x.dst !== "h") },
  { id: "R8", name: "Play before drawing", desc: "Make any play rather than draw", keep: o => o.filter(x => x.kind === "play") },
  { id: "R9", name: "No detour", desc: "Avoid sending elsewhere a card that could go home now (p²)", keep: o => o.filter(x => x.degree !== "p2") },
];
const ruleById = id => RULES.find(r => r.id === id);

function decide(opts, v, active, rand) {
  let cand = opts; const narrowedBy = [];
  for (const id of active) {
    const k = ruleById(id).keep(cand, v);
    if (k.length && k.length < cand.length) { cand = k; narrowedBy.push(id); }
  }
  const choice = cand[Math.floor(rand() * cand.length)];
  const matches = [], against = [];
  for (const r of RULES) {
    const k = r.keep(opts, v);
    if (k.length && k.length < opts.length) (k.includes(choice) ? matches : against).push(r.id);
  }
  let how;
  if (opts.length === 1) how = "only option";
  else if (cand.length === 1) how = `decided by ${narrowedBy.join(" › ")}`;
  else how = `random of ${cand.length}` + (narrowedBy.length ? ` after ${narrowedBy.join(" › ")}` : "");
  const tag = opts.length === 1 ? "" : matches.length ? `matches ${matches.join(", ")}` : (narrowedBy.length ? "" : "no-rule random");
  return { choice, how, matches, against, tag, narrowedBy };
}

// ---------- a whole game ----------
function play(order, cfg, active, seed, keepSteps = true) {
  const rand = rng32(seed);
  let s = deal(order, cfg);
  const steps = keepSteps ? [{ state: s }] : null;
  const tally = {};                       // rule id -> [applied, matched]
  while (!s.over) {
    const opts = options(s, cfg);
    if (!opts.length) { s = { ...s, over: { result: "L", why: "no play and no draw" } }; break; }
    const v = view(s, cfg);
    const d = decide(opts, v, active, rand);
    for (const id of d.matches) (tally[id] = tally[id] || [0, 0])[1]++;
    for (const id of d.matches.concat(d.against)) (tally[id] = tally[id] || [0, 0])[0]++;
    s = apply(s, d.choice, cfg);
    if (keepSteps) steps.push({ state: s, options: opts, ...d });
  }
  return { result: s.over.result, why: s.over.why, plays: s.plays, actions: s.actions, steps, tally };
}

const API = { RANKS, SUITS, COLS, RULES, MAX_ACTIONS, parseCode, deckOf, firstInstance, parseOrder, rng32, randomOrder,
              deal, legalPlays, options, view, apply, decide, play, clone };
if (typeof module !== "undefined" && module.exports) module.exports = API; else root.SolitaireEngine = API;
})(typeof window !== "undefined" ? window : globalThis);
