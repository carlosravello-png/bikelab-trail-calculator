/*
          \ .-~~~-.                steering axis · θ
         .' \         '.
        /    \          \
       |      \          |
       |       \•        |  ┬   • axle · offset ⟂ axis
       |        \        |  │
        \        \      /   R   wheel radius
         '.       \   .'    │
             '-._.-\'       │
____________________\_______┴_______  ground →
                ▲   ▲
                └─T─┘   T = (R·cos θ − offset) / sin θ

┌──────┬─────────────────────────────────────────┐
│ CERJ │ BIKELAB TRAIL CALCULATOR      REV 1.0.0 │
│      │ ORCID 0009-0007-5631-7436     2026      │
└──────┴─────────────────────────────────────────┘
*/
// trail_engine.js — BikeLab Trail Calculator, calculation engine.
// Lines between BEGIN and END are copied byte for byte from the live page
// https://www.bikelabstudio.com/articles/trail-calculator-en.html (2026-11-23).
// SHA-256 of that block: a410d080185a0aa89cd1060ee6febbc26e2e251093ed00f5c9fe5b7ee8cab0aa
// Only the module footer below END was added, to run it outside a browser.
// ---- BEGIN verbatim ----
const rad=d=>d*Math.PI/180, deg=r=>r*180/Math.PI;
const trailGround=(R,o,HA)=>{const h=rad(HA);return (R*Math.cos(h)-o)/Math.sin(h);};
const trailMech=(R,o,HA)=>{const h=rad(HA);return R*Math.cos(h)-o;};
const wheelFlop=(R,o,HA)=>{const h=rad(HA);return trailGround(R,o,HA)*Math.sin(h)*Math.cos(h);};
const dT_doff=HA=>-1/Math.sin(rad(HA));
const dT_dR=HA=>1/Math.tan(rad(HA));
const dT_dHA=(R,o,HA)=>{const h=rad(HA);return (o*Math.cos(h)-R)/(Math.sin(h)**2)*(Math.PI/180);};
const dT_dDia=HA=>0.5/Math.tan(rad(HA));
const frontDrop=(tr,sag,HA)=>tr*sag*Math.sin(rad(HA));
const HA_front=(tr,sag,HA,WB)=>HA+deg(Math.atan(frontDrop(tr,sag,HA)/WB));
const HA_bal=(ft,fs,HA,WB,rt,rs)=>HA+deg(Math.atan((frontDrop(ft,fs,HA)-rt*rs)/WB));
const GOLDEN=[{R:370,o:44,HA:64,t:131.507},{R:365,o:44,HA:66,t:114.344},{R:360,o:51,HA:71,t:70.019},{R:370,o:44,HA:45,t:307.775}];
// ---- END verbatim ----

// selfTestCore: the page's selfTest() conditions without touching the DOM.
function selfTestCore(){
  for (const g of GOLDEN) if (Math.abs(trailGround(g.R,g.o,g.HA)-g.t)>0.02) return false;
  const hd=HA_front(160,0.30,64,1250), t0=trailGround(370,44,64), t1=trailGround(370,44,hd);
  return hd>64 && t1<t0;
}
if (typeof module!=='undefined') module.exports={trailGround,trailMech,wheelFlop,dT_doff,dT_dR,dT_dHA,dT_dDia,frontDrop,HA_front,HA_bal,GOLDEN,selfTestCore};
