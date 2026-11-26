"""¿Por qué late tu corazón?  Illustrations (pycairo only). Contract: output/engine/SCENES_GUIDE.md

Anatomical conventions: the heart is drawn as seen from the front, so the patient's RIGHT side (blue, deoxygenated
blood, goes to the lungs) is on the SCREEN LEFT and the LEFT side (red, goes to the body) on the screen right.
One cardiac cycle is u in [0, 1): SA node fires (0) -> P wave / atria activate (0.02-0.13) -> atria squeeze
(0.07-0.27) -> QRS (0.20-0.27) -> AV valves close = "PUM" (0.25) -> ventricles squeeze (0.24-0.62), T wave
(0.40-0.56) -> semilunar valves close = second "PUM" (0.56).
"""
from core import *  # noqa

# ---------------------------------------------------------------- colours of this video
MUSC = hx("#D8646C"); MUSC_D = hx("#9E3C48"); MUSC_L = hx("#F08A8C")
BLUEB = hx("#4C6CCB"); REDB = hx("#D8343F")
BRAIN = hx("#F2A7B5"); SKIN = hx("#F2C6A0"); ECGG = hx("#7CFC9A"); LUNG = hx("#E88A95")
BODY_T, BODY_B = hx("#4A4468"), hx("#2E2A44")

HC = (540, 1150); HS = 0.95          # where the big cut-away heart sits
BPM = 70; F = BPM / 60.0
NODE = (-168, -182)                  # sinoatrial node (top of the right atrium, next to the vena cava)
AVN = (-40, -28)                     # atrioventricular node


def hs(p, cx=HC[0], cy=HC[1], s=HS):
    return (cx + s * p[0], cy + s * p[1])


# ---------------------------------------------------------------- small helpers
def spath(c, pts):
    """Closed smooth (Catmull-Rom) path through pts."""
    n = len(pts); c.new_sub_path(); c.move_to(*pts[0])
    for i in range(n):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c.curve_to(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6,
                   p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, p2[0], p2[1])
    c.close_path()

def centroid(pts): return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))

def sq(pts, k, ctr=None):
    cx, cy = ctr or centroid(pts)
    return [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in pts]

def faded(c, a, fn):
    if a <= 0.01: return
    if a >= 0.99: fn(); return
    c.push_group(); fn(); c.pop_group_to_source(); c.paint_with_alpha(a)

def bump(u, a, b):
    return math.sin(math.pi * ramp(u, a, b)) ** 2 if a < u < b else 0.0

def interp(t, pts):
    if t <= pts[0][0]: return pts[0][1]
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if t <= t1: return lerp(v0, v1, (t - t0) / (t1 - t0))
    return pts[-1][1]

def polyline_partial(pts, k):
    """First fraction k (by length) of a polyline."""
    L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; d = k * sum(L); out = [pts[0]]
    for i, l in enumerate(L):
        if d >= l: out.append(pts[i + 1]); d -= l
        else:
            a, b = pts[i], pts[i + 1]; out.append((a[0] + (b[0] - a[0]) * d / l, a[1] + (b[1] - a[1]) * d / l)); break
    return out

def point_on(pts, d):
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; l = math.dist(a, b)
        if d <= l: return (a[0] + (b[0] - a[0]) * d / max(l, 1e-6), a[1] + (b[1] - a[1]) * d / max(l, 1e-6))
        d -= l
    return pts[-1]

def flow(c, pts, k, col, t, lw=16):
    """Blood-flow arrow drawn along pts up to fraction k, with dots running along it."""
    if k <= 0.01: return
    q = polyline_partial(pts, k)
    if len(q) < 2: return
    line(c, q, INK, lw + 10); line(c, q, col, lw)
    tot = sum(math.dist(q[i], q[i + 1]) for i in range(len(q) - 1))
    for j in range(int(tot / 55) + 1):
        d = (j * 55 + t * 140) % max(tot, 1)
        x, y = point_on(q, d); circle(c, x, y, lw * 0.28); c.set_source_rgba(1, 1, 1, 0.8); c.fill()
    a, b = q[-2], q[-1]
    if math.dist(a, b) > 1:
        ang = math.atan2(b[1] - a[1], b[0] - a[0]); hd = lw * 2.6
        c.new_path(); c.move_to(b[0] + math.cos(ang) * hd * 0.5, b[1] + math.sin(ang) * hd * 0.5)
        c.line_to(b[0] - hd * math.cos(ang - 0.6), b[1] - hd * math.sin(ang - 0.6))
        c.line_to(b[0] - hd * math.cos(ang + 0.6), b[1] - hd * math.sin(ang + 0.6)); c.close_path()
        fill_stroke(c, col, INK, 5)

def chip(c, x, y, label, k, col=CREAM, size=34, bg=INK, fam=SANS):
    if k <= 0.02: return
    font(c, fam, size, True); e = c.text_extents(label); bw, bh = e.x_advance + 36, size + 26
    c.save(); c.translate(x, y); c.scale(eob(k), eob(k))
    rrect(c, -bw / 2, -bh / 2, bw, bh, 12); fill_stroke(c, bg, alpha(WHITE, 0.95), 3)
    text(c, label, 0, size * 0.36, size, col, fam, True)
    c.restore()

def big_word(c, s, x, y, size, col, k, olw=12):
    if k <= 0.02: return
    c.save(); c.translate(x, y); c.scale(eob(k), eob(k))
    text(c, s, 0, size * 0.35, size, col, SLAB, False, outline=INK, olw=olw)
    c.restore()

def burst(c, x, y, r, k, col=YEL, n=10):
    """Sound burst: short radiating strokes."""
    if k <= 0 or k >= 1: return
    for i in range(n):
        a = i * 2 * math.pi / n + 0.2
        r0 = r * (0.6 + 0.7 * k); r1 = r0 + 40 * (1 - k)
        line(c, [(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * r1, y + math.sin(a) * r1)], alpha(col, 1 - k), 8)


# ---------------------------------------------------------------- the cardiac cycle
def cyc(u):
    u = u % 1.0
    d = dict(u=u)
    d["node"] = (1 - u / 0.06) if u < 0.06 else 0.0
    d["pa"] = ramp(u, 0.0, 0.13)                 # atrial activation front
    d["ca"] = bump(u, 0.07, 0.27)                # atrial contraction
    d["pv"] = ramp(u, 0.19, 0.29)                # ventricular activation front
    d["cv"] = bump(u, 0.24, 0.62)                # ventricular contraction
    d["ta"] = 1 - ramp(u, 0.24, 0.36) if u < 0.36 else 0.0
    d["tv"] = (1 - ramp(u, 0.55, 0.66)) if 0.19 <= u < 0.66 else 0.0
    d["av"] = 1 - (ease(ramp(u, 0.232, 0.252)) - ease(ramp(u, 0.575, 0.62)))   # AV valves open
    d["sl"] = ease(ramp(u, 0.265, 0.29)) - ease(ramp(u, 0.54, 0.562))          # semilunar valves open
    return d

def ecg(u):
    u %= 1.0
    if 0.02 < u < 0.12: return 0.13 * math.sin(math.pi * (u - 0.02) / 0.10)
    if 0.20 <= u < 0.215: return -0.12 * (u - 0.2) / 0.015
    if 0.215 <= u < 0.235: return lerp(-0.12, 1.0, (u - 0.215) / 0.02)
    if 0.235 <= u < 0.255: return lerp(1.0, -0.28, (u - 0.235) / 0.02)
    if 0.255 <= u < 0.27: return lerp(-0.28, 0, (u - 0.255) / 0.015)
    if 0.40 < u < 0.56: return 0.3 * math.sin(math.pi * (u - 0.40) / 0.16)
    return 0.0

U0 = 0.75
def u_global(t): return F * anim_time(t) + U0

def P3():
    return [(B("paso3")["start"] - 0.4, 0.86), (wt("paso3", "chispa"), 1.0), (wt("paso3", "ola"), 1.065),
            (wt("paso3", "aprietan"), 1.12), (wt("paso3", "aurículas"), 1.165), (wt("paso3", "después"), 1.20),
            (wt("paso3", "ventrículos"), 1.25), (wt("paso3", "abajo"), 1.40), (B("paso4")["start"], 1.52)]
def P4():
    return [(B("paso4")["start"] - 0.4, 0.66), (wt("paso4", "abren"), 0.95), (wt("paso4", "cierran"), 1.25),
            (wt("paso4", "cierran") + 0.65, 1.56), (wt("paso4", "pum"), 2.25), (wt("paso4", "pum") + 0.34, 2.56),
            (B("paso5")["start"], 2.95)]
def PJ():
    return [(B("junto")["start"] - 0.4, 0.86), (wt("junto", "marcapasos"), 1.0), (wt("junto", "chispa"), 1.06),
            (wt("junto", "aurículas"), 1.16), (wt("junto", "ventrículos"), 1.27), (wt("junto", "válvulas"), 1.45),
            (wt("junto", "pum"), 1.56)]

def bpm5(t):
    return lerp(70, 140, ease(ramp(t, wt("paso5", "corres"), wt("paso5", "rápido") + 0.2)))

def u5(t):
    t0 = B("paso5")["start"] - 0.4; acc = 0.0; x = t0
    while x < t:
        dx = min(0.02, t - x); acc += dx * bpm5(x + dx / 2) / 60; x += dx
    return 0.75 + acc

def u_junto(t):
    tp = wt("junto", "pum")
    if t <= tp: return interp(t, PJ())
    return 1.56 + F * (anim_time(t) - anim_time(tp))

def u_remate(t):
    t0 = B("remate")["start"] - 0.2
    return 0.75 + F * (anim_time(t) - anim_time(t0))


# ---------------------------------------------------------------- heart geometry (local units, ~600 px wide)
OUTER = [(-250, -205), (-130, -232), (-20, -222), (120, -248), (265, -215), (322, -70), (305, 85), (215, 225),
         (100, 312), (25, 292), (-140, 205), (-278, 65), (-305, -85)]
RA = [(-262, -170), (-170, -202), (-88, -172), (-82, -78), (-122, -40), (-230, -44), (-282, -100)]
LA = [(82, -200), (165, -214), (255, -186), (274, -126), (226, -90), (112, -90), (80, -142)]
RV = [(-248, 14), (-150, -2), (-62, 4), (-24, 40), (-16, 120), (-48, 196), (-128, 182), (-218, 112)]
LV = [(22, -14), (132, -20), (246, 8), (258, 108), (198, 196), (104, 258), (40, 178), (20, 62)]
VESSELS = [  # (points, width, colour)
    ([(-195, -415), (-192, -185)], 58, BLUEB),                                                      # superior vena cava
    ([(-40, -200), (-40, -322), (-84, -374), (-170, -386), (-262, -376)], 52, BLUEB),               # pulmonary artery
    ([(40, -200), (40, -350), (80, -420), (160, -432), (226, -388), (242, -270)], 58, REDB),        # aorta
    ([(372, -212), (255, -176)], 34, REDB), ([(372, -118), (262, -128)], 34, REDB),                 # pulmonary veins
]
TV = ((-212, -20), (-110, -20), 54)       # tricuspid hinges + flap length
MV = ((118, -56), (230, -56), 58)         # mitral
PV = ((-62, -206), (-18, -206), 23)       # pulmonary valve
AV_ = ((18, -206), (62, -206), 23)        # aortic valve
CH_C = {"RA": centroid(RA), "LA": centroid(LA), "RV": centroid(RV), "LV": centroid(LV)}

def tube(c, pts, w, col):
    line(c, pts, INK, w + 12); line(c, pts, col, w)
    line(c, [(x - w * 0.2, y) for x, y in pts], alpha(WHITE, 0.22), w * 0.22)

def outer_pts(st):
    out = []
    for x, y in OUTER:
        wv = clamp((y + 60) / 200 + 0.5)
        k = 1 - 0.05 * st["ca"] * (1 - wv) - 0.075 * st["cv"] * wv
        out.append((x * k, 30 + (y - 30) * k))
    return out

def flap(c, hinge, ang, L, lw=13):
    x, y = hinge
    p = [(x, y), (x + math.cos(ang) * L, y + math.sin(ang) * L)]
    line(c, p, INK, lw + 8); line(c, p, CREAM2, lw)

def heart(c, x, y, s, u=0.9, cut=True, hl=(), wave=True, node=None, valves_hl=0.0, glow_a=0.0, t=0.0, st=None):
    """Front view of the heart centred at (x, y), scale s. cut=False: closed organ. node: override SA-node flash."""
    st = st or cyc(u)
    c.save(); c.translate(x, y); c.scale(s, s)
    if glow_a > 0: glow(c, 0, 0, 520, HOT, glow_a)
    for pts, w, col in VESSELS: tube(c, pts, w, col)
    op = outer_pts(st)
    shadow(c, lambda: spath(c, op), 12, 16, 0.4)
    spath(c, op)
    g = cairo.LinearGradient(-300, -250, 300, 320)
    g.add_color_stop_rgba(0, *MUSC_L); g.add_color_stop_rgba(0.55, *MUSC); g.add_color_stop_rgba(1, *MUSC_D)
    c.set_source(g); c.fill_preserve(); c.set_source_rgba(*INK); c.set_line_width(8); c.stroke()
    if not cut:
        line(c, [(10, -205), (35, -40), (62, 140), (92, 290)], alpha(MUSC_D, 0.9), 9)
        line(c, [(10, -205), (35, -40), (62, 140), (92, 290)], alpha(hx("#F6D27A"), 0.5), 4)
        c.save(); c.translate(-150, -120); c.rotate(-0.5); c.scale(1, 0.55); circle(c, 0, 0, 70); c.restore()
        c.set_source_rgba(1, 1, 1, 0.22); c.fill()
        c.restore(); return
    ra, la = sq(RA, 1 - 0.17 * st["ca"]), sq(LA, 1 - 0.17 * st["ca"])
    rv, lv = sq(RV, 1 - 0.2 * st["cv"]), sq(LV, 1 - 0.2 * st["cv"])
    # outflow channels (RV -> pulmonary artery, LV -> aorta) and the AV openings
    for x0, x1, y0, col in [(-62, -18, 30, BLUEB), (18, 62, 0, REDB)]:
        c.new_path(); c.rectangle(x0, -236, x1 - x0, y0 + 236); c.set_source_rgba(*col); c.fill()
    for pts, col in [(ra, BLUEB), (rv, BLUEB), (la, REDB), (lv, REDB)]:
        spath(c, pts); fill_stroke(c, col, MUSC_D, 6)
    for x0, x1, y0, y1, col in [(-205, -117, -50, 14, BLUEB), (125, 223, -96, -8, REDB)]:
        c.new_path(); c.rectangle(x0, y0, x1 - x0, y1 - y0); c.set_source_rgba(*col); c.fill()
    for x0, x1, y0, col in [(-62, -18, 0, BLUEB), (18, 62, -16, REDB)]:
        c.new_path(); c.rectangle(x0, -236, x1 - x0, y0 + 236); c.set_source_rgba(*col); c.fill()
        line(c, [(x0, y0), (x0, -232)], MUSC_D, 5); line(c, [(x1, y0), (x1, -232)], MUSC_D, 5)
    # highlights
    hlmap = {"right": [ra, rv], "left": [la, lv], "atria": [ra, la], "ventricles": [rv, lv]}
    for key in hl:
        for pts in hlmap.get(key, []):
            spath(c, pts); c.set_source_rgba(*alpha(YEL, 0.85)); c.set_line_width(9); c.stroke()
    if "muscle" in hl:
        spath(c, op); c.set_source_rgba(*alpha(YEL, 0.9)); c.set_line_width(12); c.stroke()
    # electrical wave
    if wave:
        for pts_list, origin, prog, tint, Rmax in [([ra, la], NODE, st["pa"], st["ta"], 470), ([rv, lv], AVN, st["pv"], st["tv"], 370)]:
            if tint <= 0.01 or prog <= 0: continue
            R = max(prog * Rmax, 2); R1 = R + 28
            c.save(); c.new_path()
            for pts in pts_list: spath(c, pts)
            c.clip()
            gr = cairo.RadialGradient(origin[0], origin[1], 0, origin[0], origin[1], R1)
            fa = 1.0 if prog < 1 else 0.0
            gr.add_color_stop_rgba(0, *alpha(YEL, 0.30 * tint)); gr.add_color_stop_rgba(max(0, (R - 60) / R1), *alpha(YEL, 0.36 * tint))
            gr.add_color_stop_rgba(R / R1, *alpha(hx("#FFF6B0"), max(0.36 * tint, 0.95 * fa)))
            gr.add_color_stop_rgba(1, *alpha(YEL, 0)); c.set_source(gr); c.paint()
            c.restore()
        # conduction paths: internodal (node -> AV node) and the bundle down the septum
        if 0 < st["pa"] and st["ta"] > 0:
            line(c, polyline_partial([NODE, (-110, -110), AVN], min(1, st["pa"] * 1.6)), alpha(YEL, 0.9 * st["ta"]), 7)
        if 0 < st["pv"] and st["tv"] > 0:
            line(c, polyline_partial([AVN, (2, 20), (2, 200), (70, 252)], st["pv"] * 1.3), alpha(YEL, 0.95 * st["tv"]), 7)
            line(c, polyline_partial([(2, 150), (2, 200), (-70, 186)], clamp(st["pv"] * 1.6 - 0.6)), alpha(YEL, 0.95 * st["tv"]), 6)
    # valves
    av_ang = st["av"]; sl = st["sl"]
    (h1, h2, L) = TV
    flap(c, h1, lerp(0.12, 1.25, av_ang), L); flap(c, h2, lerp(math.pi - 0.12, math.pi - 1.25, av_ang), L)
    (h1, h2, L) = MV
    flap(c, h1, lerp(0.12, 1.25, av_ang), L); flap(c, h2, lerp(math.pi - 0.12, math.pi - 1.25, av_ang), L)
    for (h1, h2, L) in (PV, AV_):
        flap(c, h1, lerp(0.35, -1.35, sl), L, 9); flap(c, h2, lerp(math.pi - 0.35, math.pi + 1.35, sl), L, 9)
    if valves_hl > 0:
        for (h1, h2, L) in (TV, MV, PV, AV_):
            mx, my = (h1[0] + h2[0]) / 2, (h1[1] + h2[1]) / 2
            glow(c, mx, my, 90, YEL, 0.55 * valves_hl)
    # SA node
    fl = st["node"] if node is None else node
    nx, ny = NODE
    glow(c, nx, ny, 70 + 60 * fl, YEL, 0.25 + 0.7 * fl)
    for i in range(7):
        a = i * math.pi / 3
        px, py = (nx, ny) if i == 6 else (nx + 19 * math.cos(a), ny + 19 * math.sin(a))
        circle(c, px, py, 10); fill_stroke(c, mix(YEL, WHITE, 0.7 * fl), INK, 3)
    c.restore()


# ---------------------------------------------------------------- icons (drawn around 0,0 in a ~140 px box)
def ic_remote(c):
    c.save(); c.rotate(-0.35)
    rrect(c, -34, -72, 68, 144, 18); fill_stroke(c, DARK, INK, 5)
    circle(c, 0, -46, 12); fill_stroke(c, RED, INK, 3)
    for i in range(3):
        for j in range(2):
            circle(c, -14 + j * 28, -10 + i * 26, 8); fill_stroke(c, CREAM2, None)
    c.restore()

def ic_stop(c):
    c.new_path()
    for i in range(8):
        a = math.pi / 8 + i * math.pi / 4; c.line_to(76 * math.cos(a), 76 * math.sin(a))
    c.close_path(); fill_stroke(c, RED, INK, 6)
    c.new_path()
    for i in range(8):
        a = math.pi / 8 + i * math.pi / 4; c.line_to(64 * math.cos(a), 64 * math.sin(a))
    c.close_path(); c.set_source_rgba(*WHITE); c.set_line_width(5); c.stroke()
    text(c, "STOP", 0, 14, 38, WHITE, SANS, True)

def ic_moon(c):
    c.push_group()
    circle(c, -12, 6, 62); fill_stroke(c, YEL, INK, 6)
    c.set_operator(cairo.OPERATOR_CLEAR); circle(c, 22, -18, 52); c.fill(); c.set_operator(cairo.OPERATOR_OVER)
    c.pop_group_to_source(); c.paint()
    text(c, "z", 40, 0, 40, STEEL, SLAB, False); text(c, "z", 62, -34, 30, STEEL, SLAB, False)

def brain_path(c, col, lw=12):
    lobes = [(-48, -22, 38), (-12, -44, 40), (30, -38, 38), (58, -2, 34), (38, 30, 32), (-2, 30, 36), (-44, 22, 36), (-66, -4, 30)]
    for x, y, r in lobes: circle(c, x, y, r)
    c.set_source_rgba(*INK); c.set_line_width(lw); c.stroke()
    for x, y, r in lobes: circle(c, x, y, r)
    c.set_source_rgba(*col); c.fill()
    fold = mix(col, INK, 0.45)
    line(c, [(-8, -78), (-2, -50), (-10, -24), (0, 0), (-6, 30), (4, 62)], fold, 5)
    line(c, [(-56, -30), (-34, -14), (-50, 8)], fold, 5); line(c, [(32, -50), (40, -20), (24, -4)], fold, 5)
    line(c, [(36, 18), (52, 36)], fold, 5); line(c, [(-40, 40), (-24, 52)], fold, 5)

def ic_brain(c): brain_path(c, BRAIN)
def ic_brain_grey(c): brain_path(c, hx("#9C98A8"))

def ic_runner(c):
    segs = [[(-6, 15), (20, 36), (14, 66)], [(-6, 15), (-26, 40), (-54, 44)], [(8, -32), (-6, 15)],
            [(5, -24), (30, -4), (48, -20)], [(5, -24), (-20, -8), (-38, -26)]]
    for s_ in segs: line(c, s_, INK, 22)
    for s_ in segs: line(c, s_, STEEL, 12)
    circle(c, 18, -56, 18); fill_stroke(c, STEEL, INK, 5)
    for i in range(3): line(c, [(-80, -20 + i * 24), (-56, -20 + i * 24)], alpha(INK, 0.6), 5)

def ic_scared(c):
    circle(c, 0, 0, 64); fill_stroke(c, YEL, INK, 6)
    for sx in (-24, 24):
        circle(c, sx, -12, 15); fill_stroke(c, WHITE, INK, 4)
        circle(c, sx, -10, 6); c.set_source_rgba(*INK); c.fill()
        line(c, [(sx - 14, -40 - (sx > 0) * 2), (sx + 14, -44 + (sx > 0) * 2)], INK, 5)
    c.save(); c.translate(0, 30); c.scale(1, 1.3); circle(c, 0, 0, 12); c.restore(); fill_stroke(c, INK, None)
    c.new_path(); c.move_to(52, -38); c.curve_to(62, -20, 66, -10, 58, -4); c.curve_to(48, 0, 44, -14, 52, -38); fill_stroke(c, XRAY, INK, 3)

def ic_lungs(c):
    line(c, [(0, -70), (0, -20)], INK, 18); line(c, [(0, -70), (0, -20)], CREAM2, 9)
    for sgn in (-1, 1):
        c.new_path(); c.move_to(sgn * 10, -30)
        c.curve_to(sgn * 40, -70, sgn * 70, -40, sgn * 66, 20); c.curve_to(sgn * 64, 60, sgn * 30, 70, sgn * 12, 50)
        c.curve_to(sgn * 8, 20, sgn * 8, -10, sgn * 10, -30); c.close_path(); fill_stroke(c, LUNG, INK, 5)
        line(c, [(0, -20), (sgn * 22, 0), (sgn * 34, 22)], alpha(INK, 0.6), 4)

def ic_body(c):
    circle(c, 0, -52, 22); fill_stroke(c, STEEL, INK, 5)
    c.new_path(); c.move_to(-34, -20); c.line_to(34, -20); c.line_to(26, 30); c.line_to(-26, 30); c.close_path(); fill_stroke(c, STEEL, INK, 5)
    for sx in (-14, 14): line(c, [(sx, 30), (sx * 1.3, 70)], INK, 16); line(c, [(sx, 30), (sx * 1.3, 70)], STEEL, 8)
    for sx in (-1, 1): line(c, [(sx * 34, -18), (sx * 50, 26)], INK, 14); line(c, [(sx * 34, -18), (sx * 50, 26)], STEEL, 7)
    glow(c, 8, -4, 26, HOT, 0.9)

def mini_heart(c, x, y, s, col=RED):
    c.save(); c.translate(x, y); c.scale(s, s); c.new_path()
    c.move_to(0, 30); c.curve_to(-60, -10, -40, -60, 0, -30); c.curve_to(40, -60, 60, -10, 0, 30); c.close_path()
    fill_stroke(c, col, INK, 5 / max(s, 0.3)); c.restore()

def fist(c, a):
    """Outline of a fist (knuckles to the viewer), in heart-local units, same size as the heart."""
    if a <= 0.01: return
    c.save(); c.set_dash([20, 12])
    col = alpha(CREAM, 0.95 * a); fillc = alpha(CREAM, 0.13 * a)
    c.new_path(); c.move_to(-232, 20); c.curve_to(-250, 200, -150, 330, -60, 345); c.line_to(150, 345)
    c.curve_to(230, 300, 270, 160, 250, 20); c.close_path()
    c.set_source_rgba(*fillc); c.fill_preserve(); c.set_source_rgba(*col); c.set_line_width(6); c.stroke()
    for i in range(4):
        rrect(c, -238 + i * 122, -230, 118, 250, 52)
        c.set_source_rgba(*fillc); c.fill_preserve(); c.set_source_rgba(*col); c.set_line_width(6); c.stroke()
    c.save(); c.translate(-30, 70); c.rotate(-0.12); rrect(c, -210, -50, 330, 100, 50); c.restore()
    c.set_source_rgba(*alpha(CREAM, 0.18 * a)); c.fill_preserve(); c.set_source_rgba(*col); c.set_line_width(6); c.stroke()
    c.restore()


# ---------------------------------------------------------------- ECG strips
def ecg_panel(c, x0, x1, y, h, a=1.0):
    rrect(c, x0, y - h / 2, x1 - x0, h, 16); fill_stroke(c, alpha(hx("#10201A"), 0.85 * a), alpha(ECGG, 0.35 * a), 3)
    for gx in range(int(x0) + 30, int(x1), 40):
        line(c, [(gx, y - h / 2 + 6), (gx, y + h / 2 - 6)], alpha(ECGG, 0.07 * a), 2)

def ecg_scroll(c, x0, x1, y, amp, u_now, ppc, a=1.0, head=None):
    head = head or x1
    pts = []; x = x0
    while x <= head:
        pts.append((x, y - amp * ecg(u_now - (head - x) / ppc))); x += 3
    n = len(pts); k = 6
    for j in range(k):
        seg = pts[j * n // k: (j + 1) * n // k + 1]
        if len(seg) > 1: line(c, seg, alpha(ECGG, a * (0.25 + 0.75 * (j + 1) / k)), 6)
    hx_, hy_ = pts[-1]
    glow(c, hx_, hy_, 40, ECGG, 0.8 * a); circle(c, hx_, hy_, 8); c.set_source_rgba(*alpha(WHITE, a)); c.fill()

def ecg_window(c, x0, x1, y, amp, ua, ub, u_now, a=1.0):
    if u_now <= ua: return None
    pts = []; uu = ua; n = 300
    for i in range(n + 1):
        uu = ua + (ub - ua) * i / n
        if uu > u_now: break
        pts.append((x0 + (x1 - x0) * i / n, y - amp * ecg(uu)))
    if len(pts) > 1:
        line(c, pts, alpha(ECGG, a), 7)
        glow(c, *pts[-1], 40, ECGG, 0.8 * a); circle(c, *pts[-1], 8); c.set_source_rgba(1, 1, 1, a); c.fill()
    return lambda uu: (x0 + (x1 - x0) * (uu - ua) / (ub - ua), y - amp * ecg(uu))


# ---------------------------------------------------------------- person
TORSO = [(-48, -40), (48, -40), (58, 20), (200, 52), (275, 130), (300, 330), (305, 720), (-305, 720), (-300, 330),
         (-275, 130), (-200, 52), (-58, 20)]
HEAD_Y = 735; NECK = HEAD_Y + 125
F_HEART = (598, 1075); F_S = 0.24

def person(c, cx, hy, t, a=1.0):
    ny = hy + 125
    c.save(); c.translate(cx, ny)
    spath(c, TORSO)
    g = cairo.LinearGradient(0, -40, 0, 700)
    g.add_color_stop_rgba(0, *alpha(BODY_T, a)); g.add_color_stop_rgba(0.7, *alpha(BODY_B, 0.9 * a)); g.add_color_stop_rgba(1, *alpha(BODY_B, 0))
    c.set_source(g); c.fill_preserve()
    g2 = cairo.LinearGradient(0, -40, 0, 700)
    g2.add_color_stop_rgba(0, *alpha(LAV, 0.85 * a)); g2.add_color_stop_rgba(0.75, *alpha(LAV, 0.4 * a)); g2.add_color_stop_rgba(1, *alpha(LAV, 0))
    c.set_source(g2); c.set_line_width(6); c.stroke()
    for sx in (-1, 1):
        c.new_path(); c.move_to(sx * 212, 150); c.curve_to(sx * 222, 330, sx * 222, 500, sx * 214, 700)
        c.set_source(g2); c.set_line_width(4); c.stroke()
    c.restore()
    circle(c, cx, hy, 105)
    gh = cairo.RadialGradient(cx - 30, hy - 40, 10, cx, hy, 110)
    gh.add_color_stop_rgba(0, *alpha(hx("#5A5480"), a)); gh.add_color_stop_rgba(1, *alpha(BODY_T, a))
    c.set_source(gh); c.fill_preserve(); c.set_source_rgba(*alpha(LAV, 0.85 * a)); c.set_line_width(6); c.stroke()
    blink = 0.15 if (t % 3.7) < 0.12 else 1.0
    for sx in (-34, 34):
        c.save(); c.translate(cx + sx, hy - 8); c.scale(1, blink); circle(c, 0, 0, 11); c.restore()
        c.set_source_rgba(*alpha(CREAM, 0.9 * a)); c.fill()
    c.new_path(); c.arc(cx, hy + 22, 34, 0.35, math.pi - 0.35); c.set_source_rgba(*alpha(CREAM, 0.8 * a)); c.set_line_width(6); c.stroke()


# ---------------------------------------------------------------- scenes
def scene_front(c, t):
    background(c, t, HOT)
    u = u_global(t); st = cyc(u)
    t_ctrl = wt("imposible", "controlas"); t_z0 = wt("freno", "vamos")
    z = ease(ramp(t, t_z0, T_SLOW + 0.2))
    up = ease(ramp(t, t_ctrl - 0.35, t_ctrl)) * (1 - ease(ramp(t, t_z0 - 0.3, t_z0 + 0.5)))
    push = 1 + 0.03 * ease(ramp(t, 0, B("imposible")["start"]))
    sA = push * (1 - 0.2 * up)
    Fe = (540 + sA * (F_HEART[0] - 540), 640 + sA * (F_HEART[1] - 640))
    Sz = (HS / (F_S * sA)) ** z
    P = (lerp(Fe[0], HC[0], z), lerp(Fe[1], HC[1], z))
    xr = ease(ramp(t, T_SLOW - 0.8, T_SLOW + 0.1))
    pa = 1 - ease(ramp(t, t_z0 + 0.4, T_SLOW - 0.2))
    beat = 0.6 * st["cv"] + 0.4 * st["ca"]
    c.save()
    c.translate(*P); c.scale(Sz, Sz); c.translate(-Fe[0], -Fe[1])
    cam(c, sA, 540, 640)
    if pa > 0: person(c, 540, HEAD_Y, t, pa)
    glow(c, F_HEART[0], F_HEART[1], 170 * (1 + 0.35 * beat), HOT, (0.45 + 0.4 * beat) * (1 - xr))
    faded(c, 1 - xr, lambda: heart(c, F_HEART[0], F_HEART[1], F_S, u, cut=False, st=st))
    faded(c, xr, lambda: heart(c, F_HEART[0], F_HEART[1], F_S, u, cut=True, st=st))
    c.restore()
    # gancho: "100.000 al día"
    k = ramp(t, wt("gancho", "cien") - 0.15, wt("gancho", "cien") + 0.2) * (1 - ramp(t, t_ctrl - 0.5, t_ctrl - 0.2))
    if k > 0:
        c.save(); c.translate(200, 1010); c.scale(eob(k), eob(k))
        rrect(c, -150, -70, 300, 140, 18); fill_stroke(c, CREAM, INK, 6)
        text(c, "100.000", 0, 6, 54, RED, SLAB, False); text(c, "LATIDOS AL DÍA", 0, 48, 24, INK, SANS, True)
        c.restore()
    # ECG monitor
    ea = (1 - up) * (1 - z) if t > 1 else 1.0
    ea = (1 - up) * (1 - z)
    if ea > 0.01:
        ecg_panel(c, 70, 1010, 1615, 150, ea)
        ecg_scroll(c, 100, 900, 1640, 85, u, 330, ea)
        mini_heart(c, 958, 1580, 0.42 * (1 + 0.25 * beat), alpha(RED, ea))
    # imposible: control / parar / descansar, crossed out
    if up > 0.01:
        for name, x, lab, fn in [("controlas", 250, "CONTROLARLO", ic_remote), ("parar", 540, "PARARLO", ic_stop),
                                 ("duermes", 830, "DESCANSAR", ic_moon)]:
            t0 = wt("imposible", name) - 0.15
            kk = eob(ramp(t, t0, t0 + 0.3)) * up
            icon_badge(c, x, 1480, kk, lab, fn, t, t0 + 0.4)
        t0 = wt("imposible", "nadie") - 0.2
        kk = eob(ramp(t, t0, t0 + 0.35)) * up
        if kk > 0.02:
            for i, (dx, dy, r) in enumerate([(660, 790, 10), (700, 770, 15)]):
                circle(c, dx, dy, r * kk); fill_stroke(c, CREAM, INK, 4)
            icon_badge(c, 830, 720, kk, "", ic_brain, r=95)
            c.save(); c.translate(905, 660); c.scale(kk, kk); c.rotate(0.15 * math.sin(t * 4))
            text(c, "?", 0, 40, 130, YEL, SLAB, False, outline=INK, olw=12); c.restore()


def scene_paso1(c, t):
    background(c, t, HOT)
    u = u_global(t)
    tm = wt("paso1", "músculo"); tp = wt("paso1", "puño"); t4 = wt("paso1", "cuatro")
    tr = wt("paso1", "derecho"); tpl = wt("paso1", "pulmones"); tl = wt("paso1", "izquierdo"); tc = wt("paso1", "cuerpo")
    hl = set()
    if tm - 0.1 <= t < tm + 1.0: hl.add("muscle")
    if tr - 0.2 <= t < tl - 0.2: hl.add("right")
    if t >= tl - 0.2: hl.add("left")
    c.save(); cam(c, 1.0 + 0.03 * ease(ramp(t, B("paso1")["start"], B("paso1")["end"])), *HC)
    heart(c, HC[0], HC[1], HS, u, hl=hl)
    c.save(); c.translate(*HC); c.scale(HS, HS)
    fa = ease(ramp(t, tp - 0.15, tp + 0.3)) * (1 - ease(ramp(t, t4 + 0.5, t4 + 1.0)))
    fist(c, fa)
    c.restore()
    c.restore()
    if fa > 0.02: big_word(c, "TAMAÑO DE UN PUÑO", 540, 1600, 56, CREAM, fa)
    callout(c, "MÚSCULO", *hs((318, -20)), 840, 1490, t, tm - 0.05)
    # 4 chambers numbered in blood-flow order
    kout = 1 - ease(ramp(t, tr - 0.4, tr))
    for i, key in enumerate(["RA", "RV", "LA", "LV"]):
        k = eob(ramp(t, t4 + 0.12 * i, t4 + 0.12 * i + 0.3)) * kout
        if k <= 0.02: continue
        x, y = hs(CH_C[key])
        c.save(); c.translate(x, y); c.scale(k, k)
        circle(c, 0, 0, 36); fill_stroke(c, CREAM, INK, 5); text(c, str(i + 1), 0, 15, 42, INK, SLAB, False)
        c.restore()
    if kout > 0: big_word(c, "4 CÁMARAS", 540, 1600, 62, YEL, ramp(t, t4 + 0.25, t4 + 0.55) * kout * (fa < 0.3))
    # lungs / body
    icon_badge(c, 165, 745, eob(ramp(t, tpl - 0.25, tpl + 0.1)), "PULMONES", ic_lungs, r=80)
    icon_badge(c, 880, 745, eob(ramp(t, tc - 0.25, tc + 0.1)), "CUERPO", ic_body, r=80)
    rpath = [hs(p) for p in [(-170, -125), (-160, -30), (-130, 95), (-62, 80), (-40, -60), (-40, -318), (-110, -380), (-262, -380)]] + [(232, 768)]
    lpath = [hs(p) for p in [(170, -140), (168, -40), (150, 110), (70, 80), (40, -60), (40, -350), (92, -418), (170, -428)]] + [(806, 760)]
    flow(c, rpath, ease(ramp(t, tr, tpl + 0.1)), XRAY, t)
    flow(c, lpath, ease(ramp(t, tl, tc + 0.1)), hx("#FF8A80"), t)
    chip(c, 250, 1600, "LADO DERECHO", ramp(t, tr - 0.1, tr + 0.25), XRAY)
    chip(c, 800, 1600, "LADO IZQUIERDO", ramp(t, tl - 0.1, tl + 0.25), hx("#FF8A80"))


def paso2_blinks():
    t0 = wt("paso2", "encienden")
    return [t0 + 1.0 * i for i in range(7)]

def scene_paso2(c, t):
    background(c, t, YEL)
    b = B("paso2")
    zk = ease(ramp(t, b["start"] - 0.1, wt("paso2", "derecho") + 0.3))
    Z = lerp(1.0, 1.85, zk) * (1 + 0.03 * ramp(t, b["start"], b["end"]))
    N0 = hs(NODE); tgt = (lerp(N0[0], 470, zk), lerp(N0[1], 1060, zk))
    fl = 0.0; rings = []
    for tb in paso2_blinks():
        if t >= tb - 0.05:
            fl = max(fl, 1 - ramp(t, tb, tb + 0.45)); rings.append(t - tb)
    c.save(); c.translate(*tgt); c.scale(Z, Z); c.translate(-N0[0], -N0[1])
    heart(c, HC[0], HC[1], HS, 0.85, node=fl if t >= wt("paso2", "células") - 0.2 else 0.0, wave=False)
    for dt in rings:
        if 0 <= dt < 0.9:
            r = 20 + 150 * dt
            c.new_path(); c.arc(N0[0], N0[1], r * HS, 0, 2 * math.pi)
            c.set_source_rgba(*alpha(YEL, 0.8 * (1 - dt / 0.9))); c.set_line_width(6); c.stroke()
    c.restore()
    def zp(p):
        return (tgt[0] + Z * (p[0] - N0[0]), tgt[1] + Z * (p[1] - N0[1]))
    ax, ay = zp(N0)
    ka = 1 - ramp(t, wt("paso2", "marcapasos") - 0.3, wt("paso2", "marcapasos"))
    faded(c, ka, lambda: callout(c, "GRUPITO DE CÉLULAS", ax + 30, ay - 30, 700, 700, t, wt("paso2", "células") - 0.1))
    callout(c, "MARCAPASOS NATURAL", ax + 20, ay - 30, 640, 700, t, wt("paso2", "marcapasos") - 0.05, YEL, 38)
    chip(c, 470, 1300, "¡SE ENCIENDE SOLO!", ramp(t, wt("paso2", "solas") - 0.1, wt("paso2", "solas") + 0.25) *
         (1 - ramp(t, wt("paso2", "cerebro") - 0.5, wt("paso2", "cerebro") - 0.2)), YEL, 38)
    tb = wt("paso2", "cerebro") - 0.15
    kb = eob(ramp(t, tb, tb + 0.35))
    icon_badge(c, 760, 1430, kb, "", ic_brain_grey, r=100)
    if kb > 0.3:
        xmark(c, 760, 1430, 66 * kb, t, wt("paso2", "mandarlo") - 0.2)
        text(c, "NO HACE FALTA", 760, 1590, 40, alpha(CREAM, clamp(kb)), SLAB, False, outline=INK, olw=8)


def scene_paso3(c, t):
    background(c, t, YEL)
    b = B("paso3")
    u = interp(t, P3()); st = cyc(u)
    c.save(); cam(c, 1.0 + 0.03 * ease(ramp(t, b["start"], b["end"])), W / 2, 1080)
    c.translate(0, -40)
    heart(c, HC[0], HC[1], HS, u, st=st,
          hl=({"atria"} if wt("paso3", "aurículas") - 0.1 <= t < wt("paso3", "segundo") else set()) |
             ({"ventricles"} if t >= wt("paso3", "ventrículos") - 0.1 else set()))
    c.restore()
    def S(p): x, y = hs(p); return (W / 2 + (x - W / 2) * 1.0, y - 40)
    callout(c, "CHISPA", *S(NODE), 240, 700, t, wt("paso3", "chispa") - 0.05, YEL)
    callout(c, "AURÍCULAS", *S(CH_C["LA"]), 830, 700, t, wt("paso3", "aurículas") - 0.05)
    callout(c, "VENTRÍCULOS", *S(CH_C["RV"]), 230, 1430, t, wt("paso3", "ventrículos") - 0.05)
    kd = ramp(t, wt("paso3", "fracción") - 0.1, wt("paso3", "fracción") + 0.2) * (1 - ramp(t, wt("paso3", "ventrículos") + 0.3, wt("paso3", "ventrículos") + 0.6))
    if kd > 0:
        ax, ay = S(AVN); glow(c, ax, ay, 60 + 10 * math.sin(t * 10), YEL, 0.7 * kd)
        chip(c, 840, 1150, "≈ 0,15 s", kd, YEL, 40, fam=MONO)
    # ECG drawn in sync
    ecg_panel(c, 90, 990, 1580, 160)
    f = ecg_window(c, 120, 960, 1615, 95, 0.96, 1.62, u)
    if f:
        if u > 1.10:
            x, y = f(1.07); text(c, "P", x, y - 26, 34, YEL, SLAB, False, outline=INK, olw=6)
        if u > 1.26:
            x, y = f(1.235); text(c, "QRS", x + 70, y + 30, 34, YEL, SLAB, False, outline=INK, olw=6)


def scene_paso4(c, t):
    background(c, t, HOT)
    b = B("paso4")
    u = interp(t, P4()); st = cyc(u)
    vh = ramp(t, wt("paso4", "válvulas") - 0.2, wt("paso4", "válvulas") + 0.2) * (1 - ramp(t, wt("paso4", "cuando") - 0.3, wt("paso4", "cuando")))
    c.save(); cam(c, 1.0 + 0.04 * ease(ramp(t, b["start"], b["end"])), W / 2, 1100)
    c.translate(0, -30)
    heart(c, HC[0], HC[1], HS, u, st=st, valves_hl=vh, wave=False)
    # blood moving forward through whichever valves are open
    if st["av"] > 0.5:
        for p0, p1, col in [((-160, -110), (-160, 70), XRAY), ((175, -140), (175, 70), hx("#FF8A80"))]:
            for j in range(3):
                ph = (t * 0.9 + j / 3) % 1
                x, y = lerp(p0[0], p1[0], ph), lerp(p0[1], p1[1], ph)
                c.save(); c.translate(*hs((x, y))); arrow(c, 0, -14, 0, 18, alpha(col, math.sin(math.pi * ph) * st["av"]), 8, 24); c.restore()
    if st["sl"] > 0.3:
        for xx, col in [(-40, XRAY), (40, hx("#FF8A80"))]:
            for j in range(3):
                ph = (t * 1.2 + j / 3) % 1
                y = lerp(-60, -300, ph)
                c.save(); c.translate(*hs((xx, y))); arrow(c, 0, 16, 0, -16, alpha(col, math.sin(math.pi * ph) * st["sl"]), 8, 24); c.restore()
    c.restore()
    def S(p): x, y = hs(p); return (W / 2 + (x - W / 2) * 1.02, 1100 + (y - 30 - 1100) * 1.02)
    tv = wt("paso4", "válvulas") - 0.05
    callout(c, "VÁLVULAS", *S((175, -56)), 540, 690, t, tv)
    callout(c, "VÁLVULAS", *S((-160, -20)), 540, 690, t, tv + 0.1)
    # "solo hacia delante"
    kd = ramp(t, wt("paso4", "solo") - 0.1, wt("paso4", "solo") + 0.25)
    if kd > 0:
        c.save(); c.translate(540, 1585); c.scale(eob(kd), eob(kd))
        rrect(c, -300, -70, 600, 140, 20); fill_stroke(c, CREAM, INK, 6)
        arrow(c, -230, 0, -110, 0, GREEN, 18, 46); text(c, "SÍ", -40, 16, 44, GREEN, SLAB, False)
        arrow(c, 150, 0, 40, 0, RED, 18, 46); text(c, "NO", 225, 16, 44, RED, SLAB, False)
        c.restore()
        if kd > 0.6: xmark(c, 635, 1585, 48, t, wt("paso4", "delante"), 12)
    # PUM on each closing
    tclose = [(wt("paso4", "cierran"), (150, 1110), "PUM"), (wt("paso4", "cierran") + 0.65, (860, 880), "PUM"),
              (wt("paso4", "pum"), (150, 1110), "PUM"), (wt("paso4", "pum") + 0.34, (860, 880), "PUM")]
    for t0, (x, y), s_ in tclose:
        k = ramp(t, t0 - 0.03, t0 + 0.25) * (1 - ramp(t, t0 + 0.8, t0 + 1.0))
        if k > 0:
            burst(c, x, y, 90, ramp(t, t0, t0 + 0.5))
            big_word(c, s_, x, y, 84, YEL, k)


def scene_paso5(c, t):
    background(c, t, HOT)
    b = B("paso5")
    u = u5(t); st = cyc(u); bpm = bpm5(t)
    hx_, hy_, hsc = 690, 1080, 0.68
    c.save(); cam(c, 1.0 + 0.03 * ramp(t, b["start"], b["end"]), W / 2, 1100)
    heart(c, hx_, hy_, hsc, u, st=st, glow_a=0.15 + 0.25 * st["cv"])
    c.restore()
    node = (hx_ + hsc * NODE[0], hy_ + hsc * NODE[1])
    tb = wt("paso5", "cerebro") - 0.2
    kb = eob(ramp(t, tb, tb + 0.35))
    icon_badge(c, 240, 770, kb, "", ic_brain, r=100)
    # nerve: brain -> SA node
    tn = wt("paso5", "acelerarla") - 0.2
    kn = ease(ramp(t, tn, tn + 0.6))
    if kn > 0:
        pts = [(330, 820), (470, 900), node]
        q = polyline_partial(pts, kn)
        c.save(); c.set_dash([16, 12]); line(c, q, alpha(CREAM, 0.7), 5); c.restore()
    chip(c, 240, 950, "ACELERAR ▲", ramp(t, wt("paso5", "acelerarla") - 0.1, wt("paso5", "acelerarla") + 0.2), GREEN)
    chip(c, 240, 1035, "FRENAR ▼", ramp(t, wt("paso5", "frenarla") - 0.1, wt("paso5", "frenarla") + 0.2), XRAY)
    tm = wt("paso5", "marcapasos") - 0.2
    km = ramp(t, tm, tm + 0.3)
    if km > 0:
        pts = [(330, 820), (470, 900), node]
        L = sum(math.dist(pts[i], pts[i + 1]) for i in range(2))
        line(c, pts, alpha(YEL, 0.9 * km), 9)
        for j in range(3):
            d = ((t - tm) * 500 + j * L / 3) % L
            x, y = point_on(pts, d); glow(c, x, y, 34, YEL, 0.9 * km); circle(c, x, y, 9); c.set_source_rgba(1, 1, 1, km); c.fill()
        glow(c, *node, 70, YEL, 0.8 * km)
        chip(c, 560, 760, "MÁS RÁPIDO", ramp(t, wt("paso5", "rápido") - 0.25, wt("paso5", "rápido") + 0.1), YEL, 40)
    icon_badge(c, 230, 1260, eob(ramp(t, wt("paso5", "corres") - 0.2, wt("paso5", "corres") + 0.15)), "CORRES", ic_runner, r=95)
    icon_badge(c, 230, 1520, eob(ramp(t, wt("paso5", "asustas") - 0.2, wt("paso5", "asustas") + 0.15)), "TE ASUSTAS", ic_scared, r=95)
    # own bpm badge
    kp = eob(ramp(t, wt("paso5", "corres") - 0.3, wt("paso5", "corres")))
    if kp > 0.02:
        c.save(); c.translate(700, 1505); c.scale(kp, kp)
        rrect(c, -175, -75, 350, 150, 20); fill_stroke(c, CREAM, INK, 6)
        beat = 0.6 * st["cv"] + 0.4 * st["ca"]
        mini_heart(c, -110, 0, 1.1 * (1 + 0.25 * beat))
        rrect(c, -50, -50, 205, 100, 12); fill_stroke(c, hx("#1E3A2A"), INK, 4)
        text(c, f"{bpm:.0f}", 95, 24, 62, hx("#7CFC9A") if bpm < 100 else HOT, MONO, True, "r")
        text(c, "LPM", 125, 14, 22, CREAM, SANS, True)
        c.restore()
        text(c, "LATIDOS POR MINUTO", 700, 1618, 26, alpha(CREAM, clamp(kp)), SANS, True)


def scene_junto(c, t):
    background(c, t, HOT)
    b = B("junto")
    u = u_junto(t); st = cyc(u)
    fast = ease(ramp(t, T_REAL + 0.2, B("remate")["start"] - 0.4))
    shake = 7 * fast
    c.save(); cam(c, 1.0 + 0.05 * ease(ramp(t, b["start"], B("remate")["start"])), W / 2, 1080)
    c.translate(shake * math.sin(t * 61), shake * math.cos(t * 53) - 40)
    order = [("marcapasos", None), ("chispa", None), ("aurículas", "atria"), ("ventrículos", "ventricles")]
    hl = {p for w, p in order if p and wt("junto", w) - 0.1 <= t < wt("junto", w) + 0.9}
    vh = ramp(t, wt("junto", "válvulas") - 0.1, wt("junto", "válvulas") + 0.2) * (1 - ramp(t, wt("junto", "pum") + 0.3, wt("junto", "pum") + 0.7))
    heart(c, HC[0], HC[1], HS, u, st=st, hl=hl, valves_hl=vh, glow_a=0.25 * fast * st["cv"])
    c.restore()
    def S(p): x, y = hs(p); return (W / 2 + (x - W / 2) * 1.0, y - 40)
    if fast < 0.3:
        la = 1 - ramp(t, T_REAL - 0.2, T_REAL + 0.3)
        def labels():
            callout(c, "MARCAPASOS", *S(NODE), 230, 690, t, wt("junto", "marcapasos") - 0.05, YEL)
            callout(c, "CHISPA", *S((-110, -110)), 210, 1300, t, wt("junto", "chispa") - 0.05, YEL)
            callout(c, "AURÍCULAS", *S(CH_C["LA"]), 830, 690, t, wt("junto", "aurículas") - 0.05)
            callout(c, "VENTRÍCULOS", *S(CH_C["LV"]), 800, 1420, t, wt("junto", "ventrículos") - 0.05)
            callout(c, "VÁLVULAS", *S((-160, -20)), 200, 1440, t, wt("junto", "válvulas") - 0.05)
        faded(c, la, labels)
        tp = wt("junto", "pum")
        big_word(c, "PUM-PUM", 540, 1580, 96, YEL, ramp(t, tp - 0.05, tp + 0.25) * la)
        burst(c, 540, 1560, 150, ramp(t, tp, tp + 0.6))
    if fast > 0.01:  # real speed: scrolling ECG
        ecg_panel(c, 70, 1010, 1600, 150, fast)
        ecg_scroll(c, 100, 900, 1625, 80, u, 330, fast)
        for i in range(26):
            r0 = 320 + (i * 97 + t * 2600) % 900; a = i * 0.2417
            line(c, [(540 + math.cos(a) * r0, 1100 + math.sin(a) * r0), (540 + math.cos(a) * (r0 + 130 * fast), 1100 + math.sin(a) * (r0 + 130 * fast))],
                 alpha(WHITE, 0.35 * fast), 5)
    flash = ramp(t, B("remate")["start"] - 0.45, B("remate")["start"] - 0.3) * (1 - ramp(t, B("remate")["start"] - 0.3, B("remate")["start"] - 0.1))
    if flash > 0: c.set_source_rgba(1, 1, 1, 0.85 * flash); c.paint()


def jug(c, x, y, level, t, k=1.0):
    """Measuring jug (5 L marks), bottom-centre at (x, y)."""
    w, h = 290, 430
    c.save(); c.translate(x, y); c.scale(k, k)
    c.new_path(); c.arc(w / 2 + 10, -h + 150, 80, -math.pi / 2, math.pi / 2); c.set_source_rgba(*INK); c.set_line_width(36); c.stroke()
    c.new_path(); c.arc(w / 2 + 10, -h + 150, 80, -math.pi / 2, math.pi / 2); c.set_source_rgba(*alpha(XRAY, 0.6)); c.set_line_width(22); c.stroke()
    rrect(c, -w / 2, -h, w, h, 30); c.set_source_rgba(*alpha(XRAY, 0.16)); c.fill()
    c.save(); rrect(c, -w / 2, -h, w, h, 30); c.clip()
    top = -16 - (h - 60) * level
    c.new_path(); c.move_to(-w / 2, 0)
    for i in range(31):
        xx = -w / 2 + w * i / 30; c.line_to(xx, top + 7 * math.sin(xx / 30 + t * 5))
    c.line_to(w / 2, 0); c.close_path()
    g = cairo.LinearGradient(0, top, 0, 0); g.add_color_stop_rgba(0, *REDB); g.add_color_stop_rgba(1, *mix(REDB, INK, 0.35))
    c.set_source(g); c.fill()
    c.restore()
    for i in range(1, 6):
        yy = -16 - (h - 60) * i / 5
        line(c, [(-w / 2 + 14, yy), (-w / 2 + 60, yy)], alpha(WHITE, 0.85), 5)
        text(c, f"{i} L", -w / 2 + 70, yy + 10, 28, alpha(WHITE, 0.9), SANS, True, "l")
    rrect(c, -w / 2, -h, w, h, 30); c.set_source_rgba(*INK); c.set_line_width(8); c.stroke()
    line(c, [(-w / 2 + 30, -h + 30), (-w / 2 + 30, -60)], alpha(WHITE, 0.25), 12)
    c.restore()

CIRC = [(0, 0), (-60, -150), (-20, -300), (30, -300), (80, -150), (10, 0),
        (120, 140), (140, 420), (40, 520), (-60, 520), (-150, 420), (-110, 140)]

def scene_remate(c, t):
    background(c, t, HOT)
    b = B("remate")
    u = u_remate(t); st = cyc(u); beat = 0.6 * st["cv"] + 0.4 * st["ca"]
    back = ease(ramp(t, T_LOOP - 0.7, T_LOOP + 0.15))
    sc = lerp(0.78, 1.0, back); dx = lerp(-215, 0, back); dy = lerp(70, 0, back)
    t5 = wt("remate", "cinco"); tmin = wt("remate", "minuto"); tsang = wt("remate", "toda"); tcada = wt("remate", "minuto", 1)
    c.save(); c.translate(540 + dx, 640 + dy); c.scale(sc, sc); c.translate(-540, -640)
    person(c, 540, HEAD_Y, t)
    # blood circulating around the body (on "toda la sangre de tu cuerpo")
    kc = ease(ramp(t, tsang - 0.3, tsang + 0.4)) * (1 - back)
    if kc > 0:
        pts = [(F_HEART[0] + x, F_HEART[1] + y) for x, y in CIRC] + [F_HEART]
        L = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        line(c, pts, alpha(REDB, 0.35 * kc), 10)
        sp = 300 * (1 + 1.2 * ramp(t, wt("remate", "parar") - 0.6, wt("remate", "parar")))
        for j in range(18):
            d = (j * L / 18 + (t - tsang) * sp) % L
            x, y = point_on(pts, d)
            col = REDB if (d / L) % 0.5 < 0.25 else BLUEB
            circle(c, x, y, 11); fill_stroke(c, col, INK, 3)
    glow(c, F_HEART[0], F_HEART[1], 170 * (1 + 0.35 * beat), HOT, 0.45 + 0.4 * beat)
    heart(c, F_HEART[0], F_HEART[1], F_S, u, cut=False, st=st)
    c.restore()
    ja = 1 - ease(ramp(t, T_LOOP - 0.6, T_LOOP))
    hxs, hys = 540 + dx + sc * (F_HEART[0] - 540), 640 + dy + sc * (F_HEART[1] - 640)
    kj = eob(ramp(t, t5 - 0.25, t5 + 0.15)) * ja
    if kj > 0.02:
        lvl = ease(ramp(t, t5, tcada + 0.3))
        # stream from the heart into the jug
        if lvl < 1:
            pts = [(hxs + 30, hys - 10), (560, 1010), (800, 1010), (800, 1100)]
            line(c, pts, alpha(INK, ja), 26); line(c, pts, alpha(REDB, ja), 16)
            for j in range(5):
                d = (j * 70 + t * 300) % 320
                x, y = point_on(pts, d); circle(c, x, y, 5); c.set_source_rgba(1, 1, 1, 0.7 * ja); c.fill()
        jug(c, 800, 1550, lvl, t, kj)
        big_word(c, "5 L", 790, 800, 120, CREAM, ramp(t, wt("remate", "litros") - 0.2, wt("remate", "litros") + 0.15) * ja)
        big_word(c, "/ MIN", 830, 915, 70, YEL, ramp(t, tmin - 0.15, tmin + 0.2) * ja)
        chip(c, 230, 700, "EN REPOSO", ramp(t, wt("remate", "reposo") - 0.1, wt("remate", "reposo") + 0.2) * ja, CREAM)
    else:
        chip(c, 230, 700, "EN REPOSO", ramp(t, wt("remate", "reposo") - 0.1, wt("remate", "reposo") + 0.2) * ja, CREAM)
    big_word(c, "¡SIN PARAR!", 330, 1640, 66, YEL, ramp(t, wt("remate", "parar") - 0.5, wt("remate", "parar") - 0.2) * ja)


# ---------------------------------------------------------------- timeline
SCENES = [
    ("front", 0.0, T_SLOW + 0.5, scene_front),
    ("paso1", T_SLOW + 0.5, B("paso2")["start"] - 0.25, scene_paso1),
    ("paso2", B("paso2")["start"] - 0.25, B("paso3")["start"] - 0.25, scene_paso2),
    ("paso3", B("paso3")["start"] - 0.25, B("paso4")["start"] - 0.25, scene_paso3),
    ("paso4", B("paso4")["start"] - 0.25, B("paso5")["start"] - 0.25, scene_paso4),
    ("paso5", B("paso5")["start"] - 0.25, B("junto")["start"] - 0.25, scene_paso5),
    ("junto", B("junto")["start"] - 0.25, B("remate")["start"] - 0.1, scene_junto),
    ("remate", B("remate")["start"] - 0.1, T_LOOP + 0.15, scene_remate),
]
LOOP_FN = scene_front
XF = {"remate": 0.08}

def u_at(t):
    """(scene name, u) used for the heart at time t (None: no beat in that scene)."""
    for name, a, b_, fn in SCENES:
        if a <= t < b_: break
    if name in ("front", "paso1"): return name, u_global(t)
    if name == "paso2": return name, None
    if name == "paso3": return name, interp(t, P3())
    if name == "paso4": return name, interp(t, P4())
    if name == "paso5": return name, u5(t)
    if name == "junto": return name, u_junto(t)
    return name, u_remate(t)


def POPS():
    ps = [wt("gancho", "cien") - 0.15]
    ps += [wt("imposible", w) - 0.15 for w in ("controlas", "parar", "duermes")] + [wt("imposible", "nadie") - 0.2]
    ps += [wt("paso1", w) - 0.05 for w in ("músculo", "puño", "cuatro", "pulmones", "cuerpo")]
    ps += [wt("paso2", "células") - 0.1, wt("paso2", "solas") - 0.1, wt("paso2", "marcapasos") - 0.05, wt("paso2", "cerebro") - 0.15]
    ps += [wt("paso3", "chispa") - 0.05, wt("paso3", "aurículas") - 0.05, wt("paso3", "fracción") - 0.1, wt("paso3", "ventrículos") - 0.05]
    ps += [wt("paso4", "válvulas") - 0.05, wt("paso4", "solo") - 0.1]
    ps += [wt("paso5", "cerebro") - 0.2, wt("paso5", "acelerarla") - 0.1, wt("paso5", "frenarla") - 0.1, wt("paso5", "corres") - 0.2,
           wt("paso5", "asustas") - 0.2, wt("paso5", "rápido") - 0.25]
    ps += [wt("junto", k) - 0.05 for k in ["marcapasos", "chispa", "aurículas", "ventrículos", "válvulas", "pum"]]
    ps += [wt("remate", "reposo") - 0.1, wt("remate", "cinco") - 0.25, wt("remate", "litros") - 0.2, wt("remate", "minuto") - 0.15]
    return ps


def SFX(put, L):
    """Soft lub-dub on every beat of the heart that is on screen (S1 at u=.25, S2 at u=.56), louder in paso4."""
    lub = L["tone"](55, 0.12, 0.005, 0.05); dub = L["tone"](62, 0.11, 0.005, 0.045)
    dt = 0.004; t = 0.0; prev = None
    while t < T_LOOP + 0.15:
        name, u = u_at(t)
        if u is not None and prev and prev[0] == name and prev[1] is not None:
            g = 1.1 if name == "paso4" else (0.45 if name in ("front", "remate", "junto") else 0.55)
            for ph, snd in ((0.25, lub), (0.56, dub)):
                if math.floor(u - ph) > math.floor(prev[1] - ph): put(snd, t, g)
        prev = (name, u); t += dt
    for tb in paso2_blinks(): put(L["click"](), tb, 0.35)
    put(L["zap"](0.5), wt("paso3", "chispa") - 0.05, 0.25)
    put(L["zap"](0.4), wt("junto", "chispa") - 0.05, 0.2)


# ---------------------------------------------------------------- thumbnails
def _spark(c, x, y, s):
    glow(c, x, y, 160 * s, YEL, 0.9)
    c.save(); c.translate(x, y); c.scale(s, s); c.new_path()
    for px, py in [(10, -90), (-40, 10), (-5, 10), (-20, 90), (45, -20), (8, -20), (30, -90)]: c.line_to(px, py)
    c.close_path(); fill_stroke(c, YEL, INK, 6); c.restore()

def THUMB_V(c):
    background(c, 3.0, HOT)
    st = cyc(0.42)
    glow(c, 560, 1180, 620, HOT, 0.6)
    heart(c, 560, 1200, 1.25, st=st, cut=False)
    _spark(c, 330, 880, 1.5)
    for i, ln in enumerate(["NADIE", "LO MANDA"]):
        sz = fit_size(c, ln, SLAB, 190, 960)
        text(c, ln, 540, 330 + i * 200, sz, YEL if i else WHITE, SLAB, False, outline=INK, olw=22)

def THUMB_H(c):
    g = cairo.LinearGradient(0, 0, 0, 720); g.add_color_stop_rgba(0, *BG_TOP); g.add_color_stop_rgba(1, *BG_BOT); c.set_source(g); c.paint()
    glow(c, 960, 410, 460, HOT, 0.7)
    heart(c, 960, 420, 0.72, st=cyc(0.42), cut=False)
    _spark(c, 825, 245, 0.9)
    for i, ln in enumerate(["NADIE", "LO MANDA"]):
        sz = fit_size(c, ln, SLAB, 150, 640)
        text(c, ln, 360, 320 + i * 170, sz, YEL if i else WHITE, SLAB, False, outline=INK, olw=20)
