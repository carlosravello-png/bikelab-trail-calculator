// check_engine.js — runs the calculator's own engine (trail_engine.js, copied
// verbatim from the live page) against golden_vectors.json and against the
// independent Python verifier's equations on a grid of inputs.
// Run:  node check_engine.js      (Node.js 18+, no dependencies)
const fs = require("fs");
const path = require("path");
const E = require("./trail_engine.js");
const gv = JSON.parse(fs.readFileSync(path.join(__dirname, "golden_vectors.json"), "utf8"));

let ok = 0, n = 0;
for (const v of gv.ground_trail) {
  const got = E.trailGround(v.R, v.offset, v.theta);
  const pass = Math.abs(got - v.trail_mm) <= gv.tolerance_mm;
  n++; if (pass) ok++;
  console.log(`${pass ? "OK  " : "FAIL"} engine trail R=${v.R} o=${v.offset} theta=${v.theta}: ${got.toFixed(4)} (expected ${v.trail_mm})`);
}

// Grid: engine vs a fresh implementation of the published closed form.
const ref = (R, o, th) => { const t = th * Math.PI / 180; return (R * Math.cos(t) - o) / Math.sin(t); };
let worst = 0, cells = 0;
for (let R = 300; R <= 380; R += 10)
  for (let o = 30; o <= 60; o += 2)
    for (let th = 60; th <= 75; th += 0.5) {
      worst = Math.max(worst, Math.abs(E.trailGround(R, o, th) - ref(R, o, th)));
      cells++;
    }
n++; if (worst < 1e-9) ok++;
console.log(`${worst < 1e-9 ? "OK  " : "FAIL"} grid of ${cells} inputs: max |engine - closed form| = ${worst.toExponential(2)} mm`);

const pass = E.selfTestCore();
n++; if (pass) ok++;
console.log(`${pass ? "OK  " : "FAIL"} the page's own selfTest logic (golden vectors + sign guard)`);

console.log(`\n${ok}/${n} checks passed`);
process.exit(ok === n ? 0 : 1);
