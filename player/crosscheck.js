// Plays random games with the engine and writes every position with its legal plays, for crosscheck.py.
const E = require("./engine.js");
const out = [];
for (const code of ["2223", "3223", "6223", "6233", "4443", "9343", "K473"]) {
  const cfg = E.parseCode(code);
  for (let g = 0; g < 150; g++) {
    const rand = E.rng32(1000 * g + code.charCodeAt(0));
    const order = E.randomOrder(cfg, rand);
    let s = E.deal(order, cfg);
    out.push({ code, order, deal: { cols: s.cols, waste: s.waste, stock: s.stock } });
    for (let t = 0; t < 200 && !s.over; t++) {
      const plays = E.legalPlays(s, cfg).map(p => `${p.src} ${p.dst} ${p.n}`);
      out.push({ code, cols: s.cols, waste: s.waste, stock: s.stock, home: s.home, plays });
      const opts = E.options(s, cfg);
      s = E.apply(s, opts[Math.floor(rand() * opts.length)], cfg);
      if (s.last && s.last.draw) out.push({ code, drew: true, before: out[out.length - 1], waste: s.waste, stock: s.stock });
    }
  }
}
process.stdout.write(JSON.stringify(out));
