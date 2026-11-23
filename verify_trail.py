# -*- coding: utf-8 -*-
"""
verify_trail.py — Independent verifier for the BikeLab Trail Calculator.

Written on 2026-11-23 from the closed-form equations published in the
method article (bikelabstudio.com/articles/trail-model-validation-en.html),
NOT from the calculator's JavaScript. The original 2026 oracle script was
not preserved; this file replaces it and says so.

Standard library only. Run:  python verify_trail.py
Exit code 0 = every check passes.
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- model (method article, sections 2, 4 and 5) -------------------------
# theta = head angle measured from the horizontal, in degrees
# R = wheel radius to the ground (mm), o = fork offset (mm)
def trail_ground(R, o, th):
    t = math.radians(th)
    return (R * math.cos(t) - o) / math.sin(t)

def trail_mechanical(R, o, th):
    return R * math.cos(math.radians(th)) - o

def wheel_flop(R, o, th):
    t = math.radians(th)
    return trail_ground(R, o, th) * math.sin(t) * math.cos(t)

def d_trail_d_offset(th):              # per mm of offset
    return -1 / math.sin(math.radians(th))

def d_trail_d_theta(R, o, th):         # per degree
    t = math.radians(th)
    return (o * math.cos(t) - R) / math.sin(t) ** 2 * math.pi / 180

def d_trail_d_diameter(th):            # per mm of wheel diameter
    return 0.5 / math.tan(math.radians(th))

def front_drop(travel, sag, th):       # vertical drop of the front axle
    return travel * sag * math.sin(math.radians(th))

def theta_front(travel, sag, th, wb):  # front-only compression: steeper (+)
    return th + math.degrees(math.atan(front_drop(travel, sag, th) / wb))

def theta_balanced(ft, fs, th, wb, rt, rs):
    return th + math.degrees(math.atan((front_drop(ft, fs, th) - rt * rs) / wb))

# ---- checks ---------------------------------------------------------------
results = []
def check(name, got, want, tol):
    ok = abs(got - want) <= tol
    results.append(ok)
    print(f"{'OK  ' if ok else 'FAIL'} {name}: {got:.4f} (expected {want} ± {tol})")

gv = json.load(open(os.path.join(HERE, "golden_vectors.json"), encoding="utf-8"))

print("1. Golden vectors (same tolerance as the in-page selfTest)")
for v in gv["ground_trail"]:
    check(f"trail R={v['R']} o={v['offset']} theta={v['theta']}",
          trail_ground(v["R"], v["offset"], v["theta"]), v["trail_mm"], gv["tolerance_mm"])

print("2. Reference case published in the method article (rounded to 0.1)")
R, o, th = 370, 44, 64
check("ground trail", trail_ground(R, o, th), 131.5, 0.05)
check("mechanical trail", trail_mechanical(R, o, th), 118.2, 0.05)
check("wheel flop", wheel_flop(R, o, th), 51.8, 0.05)

print("3. Analytic derivatives vs finite differences (h = 1e-5)")
h = 1e-5
fd_th = (trail_ground(R, o, th + h) - trail_ground(R, o, th - h)) / (2 * h)
fd_o = (trail_ground(R, o + h, th) - trail_ground(R, o - h, th)) / (2 * h)
fd_R = (trail_ground(R + h, o, th) - trail_ground(R - h, o, th)) / (2 * h)
check("d trail / d theta (mm/deg)", d_trail_d_theta(R, o, th), round(fd_th, 6), 1e-4)
check("d trail / d offset", d_trail_d_offset(th), round(fd_o, 6), 1e-4)
check("d trail / d diameter", d_trail_d_diameter(th), round(fd_R / 2, 6), 1e-4)
check("article: d trail / d theta = -7.58 mm/deg", d_trail_d_theta(R, o, th), -7.58, 0.005)

print("4. Sensitivities published in the article")
check("+1 deg slacker", trail_ground(R, o, th - 1) - trail_ground(R, o, th), 7.6, 0.1)
check("+7 mm offset", trail_ground(R, o + 7, th) - trail_ground(R, o, th), -7.8, 0.05)
check("+10 mm diameter", trail_ground(R + 5, o, th) - trail_ground(R, o, th), 2.4, 0.05)
check("27.5 -> 29 in (+38 mm diameter)", trail_ground(R + 19, o, th) - trail_ground(R, o, th), 9.3, 0.05)

print("5. Dynamic scenarios (wheelbase 1250, travel 160, sag 30 %)")
thf = theta_front(160, 0.30, th, 1250)
check("front-only compression: theta", thf, 66.0, 0.05)
check("front-only compression: trail", trail_ground(R, o, thf), 116.7, 0.05)
thb = theta_balanced(160, 0.30, th, 1250, 160, 0.30)
check("balanced sag: theta", thb, 63.8, 0.05)
check("balanced sag: trail", trail_ground(R, o, thb), 133.2, 0.05)

print("6. Sign guard: front compression steepens the head angle and lowers trail")
guard = thf > th and trail_ground(R, o, thf) < trail_ground(R, o, th)
results.append(guard)
print(("OK  " if guard else "FAIL") + " sign guard")

n_ok = sum(results)
print(f"\n{n_ok}/{len(results)} checks passed")
sys.exit(0 if n_ok == len(results) else 1)
