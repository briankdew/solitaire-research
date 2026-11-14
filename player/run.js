// Batch runner: plays every shuffle of a set with the chosen rules and scores it against the solver.
// Usage: node run.js <set.csv> <code> [rules e.g. R8,R1] [runs per shuffle] [seed] [out.csv]
const fs = require("fs"), E = require("./engine.js");
const [file, code, rulesArg = "", runsArg = "1", seedArg = "1", outFile] = process.argv.slice(2);
const cfg = E.parseCode(code), active = rulesArg ? rulesArg.split(",") : [], runs = +runsArg, seed = +seedArg;
const lines = fs.readFileSync(file, "utf8").trim().split("\n"), head = lines[0].split(",");
const rows = lines.slice(1).map(l => Object.fromEntries(l.split(",").map((v, i) => [head[i], v])));
const res = { W: 0, Lw: 0, Lu: 0, S: 0 }, out = ["id,order,winnable,runs,won"];
const tally = {};
rows.forEach((r, i) => {
  const order = r.order.split(" "); let won = 0;
  for (let k = 0; k < runs; k++) {
    const g = E.play(order, cfg, active, seed + i * runs + k, false);
    if (g.result === "W") { res.W++; won++; } else if (g.result === "S") res.S++; else res[r.winnable === "1" ? "Lw" : "Lu"]++;
    for (const [id, [a, m]] of Object.entries(g.tally)) { const t = (tally[id] = tally[id] || { a: 0, m: 0, aW: 0, mW: 0 }); t.a += a; t.m += m; if (g.result === "W") { t.aW += a; t.mW += m; } }
  }
  out.push([r.id || i + 1, r.order, r.winnable, runs, won].join(","));
});
const n = rows.length * runs, wn = rows.filter(r => r.winnable === "1").length * runs;
console.log(`${code} ${file.split("/").pop()} rules [${active.join(" › ") || "none: random"}], ${runs} run(s) per shuffle, seed ${seed}`);
console.log(`  games ${n}: won ${res.W} (${(100 * res.W / n).toFixed(1)}%), lost winnable ${res.Lw}, lost unwinnable ${res.Lu}, stopped ${res.S}`);
console.log(`  won of winnable: ${(100 * res.W / wn).toFixed(1)}%`);
for (const r of E.RULES) { const t = tally[r.id]; if (t) console.log(`  ${r.id} ${r.name.padEnd(26)} followed ${(100 * t.m / t.a).toFixed(0)}% of ${t.a} decisions where it applied`); }
if (outFile) fs.writeFileSync(outFile, out.join("\n") + "\n");
