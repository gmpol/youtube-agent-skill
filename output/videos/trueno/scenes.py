"""¿Por qué suena el trueno?  Illustrations (pycairo only). Contract: output/engine/SCENES_GUIDE.md"""
from core import *  # noqa

# ---------------------------------------------------------------- colours of this video
SKIN = hx("#F2C6A0")
GROUND = hx("#2B3836"); GROUND2 = hx("#223029")
HILL1 = hx("#2A2740"); HILL2 = hx("#36314C")
CLOUD_T = hx("#5A5378"); CLOUD_B = hx("#2C283E")
ROOF = hx("#4A3048"); TREE = hx("#2F4A3A")


def wq(beat, w, nth=0, end=False):
    """wt() but never before the beat starts (whisper puts some first words early, in the pause)."""
    return max(wt(beat, w, nth, end), B(beat)["start"] - 0.05)

def SS(k): return B(k)["start"] - 0.25

def faded(c, a, fn):
    if a <= 0.01: return
    if a >= 0.99: fn(); return
    c.push_group(); fn(); c.pop_group_to_source(); c.paint_with_alpha(a)

def flash_k(t, t0, d=0.3): return (1 - ramp(t, t0, t0 + d)) if t >= t0 else 0.0

def white(c, a):
    if a > 0.005: c.set_source_rgba(1, 1, 1, min(1, a)); c.paint()


# ---------------------------------------------------------------- lightning
_BC = {}
def bolt_path(seed, x0, y0, x1, y1, depth=6, jag=0.22, branches=3, blen=0.35):
    key = (seed, x0, y0, x1, y1, depth, jag, branches, blen)
    if key in _BC: return _BC[key]
    R = random.Random(seed)
    pts = [(x0, y0), (x1, y1)]
    disp = math.dist((x0, y0), (x1, y1)) * jag
    for _ in range(depth):
        new = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            L = math.dist(a, b) or 1; nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
            o = R.uniform(-1, 1) * disp
            new += [(mx + nx * o, my + ny * o), b]
        pts = new; disp *= 0.55
    br = []
    for i in range(branches):
        k = R.randint(len(pts) // 6, len(pts) * 2 // 3); sx, sy = pts[k]
        ang = math.atan2(y1 - y0, x1 - x0) + R.choice([-1, 1]) * R.uniform(0.45, 0.9)
        L = math.dist((x0, y0), (x1, y1)) * blen * R.uniform(0.55, 1)
        sub = bolt_path(seed * 7 + i + 1, sx, sy, sx + math.cos(ang) * L, sy + math.sin(ang) * L, max(2, depth - 2), jag, 0)[0]
        br.append((k / len(pts), sub))
    _BC[key] = (pts, br)
    return pts, br

def _prefix(pts, f):
    if f >= 1: return pts
    n = max(2, int(len(pts) * f) + 1); return pts[:n]

def draw_bolt(c, bolt, k=1.0, grow=1.0, s=1.0, col=YEL):
    if k <= 0.01 or grow <= 0: return
    main, br = bolt
    paths = [(_prefix(main, grow), 1.0)]
    for f0, sub in br:
        if grow > f0: paths.append((_prefix(sub, clamp((grow - f0) / max(0.05, 1 - f0) * 1.6)), 0.55))
    head = paths[0][0][-1]
    for p, w in paths:
        line(c, p, alpha(col, 0.10 * k), 74 * s * w); line(c, p, alpha(col, 0.22 * k), 34 * s * w)
    for i in range(0, len(paths[0][0]), 10):
        x, y = paths[0][0][i]; glow(c, x, y, 120 * s, col, 0.10 * k)
    for p, w in paths: line(c, p, alpha(INK, k), 18 * s * w)
    for p, w in paths: line(c, p, alpha(col, k), 11 * s * w)
    for p, w in paths: line(c, p, alpha(WHITE, k), 4.5 * s * w)
    if grow < 1: glow(c, head[0], head[1], 90 * s, WHITE, 0.8 * k)

def bolt_at(bolt, f):
    pts = bolt[0]; return pts[min(len(pts) - 1, int(f * (len(pts) - 1)))]

def strike(t, t0, hold=3.0, fade=0.5, freeze=False):
    """Visibility of a bolt that strikes at t0 (flickers like return strokes, then fades)."""
    if t < t0: return 0.0
    dt = t - t0
    fl = 1.0 if freeze else (0.55 + 0.45 * abs(math.cos(dt * 19))) if dt < 1.2 else 0.85
    return fl * (1 - ramp(dt, hold, hold + fade))


# ---------------------------------------------------------------- pieces
def make_cloud(seed, x0, x1, ytop, ybot):
    R = random.Random(seed); w = x1 - x0; h = ybot - ytop
    cs = []; n = max(5, int(w / 120))
    for i in range(n):
        u = (i + 0.5) / n
        r = h * R.uniform(0.30, 0.40) * (0.8 + 0.3 * math.sin(math.pi * u))
        cs.append((x0 + w * u + R.uniform(-12, 12), ybot - r * 0.95, r))
    for i in range(n - 1):
        u = (i + 1) / n; r = h * R.uniform(0.30, 0.40)
        cs.append((x0 + w * u + R.uniform(-20, 20), ytop + r + R.uniform(0, h * 0.08), r))
    bar = (x0 + w * 0.06, ytop + h * 0.35, w * 0.88, h * 0.55)
    return cs, bar

def cloud_path(c, cl):
    cs, (bx, by, bw, bh) = cl
    c.new_path()
    for (x, y, r) in cs: circle(c, x, y, r)
    rrect(c, bx, by, bw, bh, bh / 2)

def draw_cloud(c, cl, lit=0.0, top=CLOUD_T, bot=CLOUD_B, lw=8, a=1.0):
    cs, bar = cl
    y0 = min(y - r for x, y, r in cs); y1 = max(y + r for x, y, r in cs)
    cloud_path(c, cl); c.set_source_rgba(*alpha(INK, a)); c.set_line_width(lw * 2); c.stroke()
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgba(0, *alpha(mix(top, LAV, lit), a)); g.add_color_stop_rgba(1, *alpha(mix(bot, top, lit * 0.6), a))
    cloud_path(c, cl); c.set_source(g); c.fill()
    for (x, y, r) in cs[len(cs) // 2:]:
        c.new_path(); c.arc(x, y, r * 0.78, math.pi * 1.1, math.pi * 1.55)
        c.set_source_rgba(1, 1, 1, (0.10 + 0.25 * lit) * a); c.set_line_width(7); c.stroke()

def house(c, x, y, s, t, col=RUST, lit=1.0, rattle=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, 48, -238, 28, 70, 4); fill_stroke(c, mix(col, INK, 0.3), INK, 5)
    c.new_path(); c.rectangle(-100, -150, 200, 150); fill_stroke(c, col, INK, 6)
    c.new_path(); c.move_to(-124, -140); c.line_to(0, -250); c.line_to(124, -140); c.close_path(); fill_stroke(c, ROOF, INK, 6)
    rrect(c, -17, -82, 34, 82, 6); fill_stroke(c, mix(DARK, GOLD, 0.4), INK, 5)
    for i, wx in enumerate((-78, 32)):
        dx = rattle * 6 * math.sin(t * 90 + i * 2); dy = rattle * 3 * math.cos(t * 77 + i)
        glow(c, wx + 23 + dx, -95 + dy, 80, YEL, 0.45 * lit)
        rrect(c, wx + dx, -118 + dy, 46, 46, 5); fill_stroke(c, mix(DARK, YEL, lit), INK, 5)
        line(c, [(wx + 23 + dx, -118 + dy), (wx + 23 + dx, -72 + dy)], INK, 3); line(c, [(wx + dx, -95 + dy), (wx + 46 + dx, -95 + dy)], INK, 3)
        if rattle > 0.05:
            for j in (-1, 1):
                line(c, [(wx + 23 + j * 36, -128), (wx + 23 + j * 44, -112), (wx + 23 + j * 36, -96)], alpha(WHITE, 0.8 * rattle), 4)
    c.restore()

def tree(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -10, -90, 20, 90, 4); fill_stroke(c, hx("#4A3428"), INK, 5)
    c.new_path()
    for (cx, cy, r) in [(-30, -110, 42), (28, -112, 40), (0, -150, 46)]: circle(c, cx, cy, r)
    c.set_source_rgba(*INK); c.set_line_width(10); c.stroke_preserve(); c.set_source_rgba(*TREE); c.fill()
    c.restore()

def person(c, x, y, s=1.0, hear=0.0, see=0.0):
    """Side view, facing left. Feet at (x, y). Ear ≈ (x+10s, y-258s), eye ≈ (x-26s, y-262s)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    if see > 0: glow(c, -20, -262, 150, YEL, 0.7 * see)
    if hear > 0: glow(c, 10, -258, 140, HOT, 0.75 * hear)
    rrect(c, -34, -100, 28, 100, 12); fill_stroke(c, DARK, INK, 5)
    rrect(c, 4, -100, 28, 100, 12); fill_stroke(c, DARK, INK, 5)
    rrect(c, -50, -215, 100, 135, 40); fill_stroke(c, STEEL, INK, 6)
    rrect(c, -16, -195, 30, 105, 14); fill_stroke(c, mix(STEEL, INK, 0.25), INK, 5)
    circle(c, 0, -262, 50); fill_stroke(c, SKIN, INK, 6)
    c.new_path(); c.arc(4, -266, 53, math.pi * 1.08, math.pi * 2.02); c.close_path(); fill_stroke(c, hx("#3B2A2A"), INK, 5)
    circle(c, -28, -258, 7); c.set_source_rgba(*INK); c.fill()
    c.new_path(); c.move_to(-48, -258); c.line_to(-60, -246); c.line_to(-47, -242); fill_stroke(c, SKIN, INK, 4)
    c.save(); c.translate(12, -254); c.scale(0.7, 1); circle(c, 0, 0, 15); c.restore(); fill_stroke(c, mix(SKIN, HOT, 0.25 + 0.6 * hear), INK, 4)
    c.restore()

def charge(c, x, y, sign, r=20, k=1.0):
    if k <= 0.02: return
    c.save(); c.translate(x, y); c.scale(k, k)
    circle(c, 0, 0, r); fill_stroke(c, RED if sign > 0 else STEEL, INK, 4)
    text(c, "+" if sign > 0 else "−", 0, r * 0.55, r * 1.6, WHITE, SANS, True)
    c.restore()

def crystal(c, x, y, s, ang, a=1.0):
    for i in range(3):
        aa = ang + i * math.pi / 3
        dx, dy = math.cos(aa) * s, math.sin(aa) * s
        line(c, [(x - dx, y - dy), (x + dx, y + dy)], alpha(INK, a), 9)
    for i in range(3):
        aa = ang + i * math.pi / 3
        dx, dy = math.cos(aa) * s, math.sin(aa) * s
        line(c, [(x - dx, y - dy), (x + dx, y + dy)], alpha(XRAY, a), 4.5)
        for sg in (-1, 1):
            px, py = x + sg * dx * 0.6, y + sg * dy * 0.6
            for b in (-0.7, 0.7):
                line(c, [(px, py), (px + sg * math.cos(aa + b) * s * 0.35, py + sg * math.sin(aa + b) * s * 0.35)], alpha(WHITE, a), 3)

def hail(c, x, y, r, a=1.0):
    circle(c, x, y, r); fill_stroke(c, alpha(CREAM2, a), alpha(INK, a), 4)
    circle(c, x - r * 0.35, y - r * 0.35, r * 0.28); c.set_source_rgba(1, 1, 1, 0.8 * a); c.fill()

def sun_icon(c, x, y, r):
    for i in range(10):
        a = i * math.pi / 5
        line(c, [(x + math.cos(a) * r * 1.25, y + math.sin(a) * r * 1.25), (x + math.cos(a) * r * 1.6, y + math.sin(a) * r * 1.6)], ORANGE, max(3, r * 0.18))
    circle(c, x, y, r); fill_stroke(c, YEL, INK, max(3, r * 0.12))

def tag(c, s, x, y, k, size=34, fg=INK, bg=CREAM, fam=SANS, bold=True):
    if k <= 0.02: return
    p = eob(k)
    font(c, fam, size, bold); e = c.text_extents(s); bw, bh = e.x_advance + 36, size + 26
    c.save(); c.translate(x, y); c.scale(p, p)
    shadow(c, lambda: rrect(c, -bw / 2, -bh / 2, bw, bh, 12), 6, 8, 0.4)
    rrect(c, -bw / 2, -bh / 2, bw, bh, 12); fill_stroke(c, bg, INK, 5)
    text(c, s, 0, size * 0.36, size, fg, fam, bold)
    c.restore()

def big(c, s, x, y, size, col, k=1.0, olw=12, fam=SLAB):
    if k <= 0.02: return
    p = eob(k)
    c.save(); c.translate(x, y); c.scale(p, p)
    text(c, s, 0, 0, size, col, fam, fam != SLAB, outline=INK, olw=olw)
    c.restore()

def sound_arcs(c, cx, cy, R, a0, a1, k=1.0, n=3, gap=34, col=CREAM, lw=9):
    for j in range(n):
        r = R - j * gap
        if r <= 6: continue
        a = k * (1 - j / (n + 0.5))
        c.new_path(); c.arc(cx, cy, r, a0, a1); c.set_source_rgba(*alpha(INK, a)); c.set_line_width(lw + 7)
        c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
        c.new_path(); c.arc(cx, cy, r, a0, a1); c.set_source_rgba(*alpha(col, a)); c.set_line_width(lw); c.stroke()

def stopwatch(c, x, y, r, secs, k=1.0, maxs=12, readout=True):
    if k <= 0.02: return
    p = eob(k)
    c.save(); c.translate(x, y); c.scale(p, p)
    rrect(c, -16, -r - 34, 32, 24, 6); fill_stroke(c, METAL, INK, 4)
    line(c, [(0, -r - 10), (0, -r)], INK, 8)
    shadow(c, lambda: circle(c, 0, 0, r), 6, 8, 0.4)
    circle(c, 0, 0, r); fill_stroke(c, CREAM, INK, 7)
    a1 = -math.pi / 2 + 2 * math.pi * min(secs, maxs) / maxs
    if secs > 0.01:
        c.new_path(); c.move_to(0, 0); c.arc(0, 0, r - 10, -math.pi / 2, a1); c.close_path(); c.set_source_rgba(*alpha(HOT, 0.35)); c.fill()
    for i in range(maxs):
        a = -math.pi / 2 + 2 * math.pi * i / maxs
        line(c, [(math.cos(a) * (r - 8), math.sin(a) * (r - 8)), (math.cos(a) * (r - 20), math.sin(a) * (r - 20))], INK, 4)
    line(c, [(0, 0), (math.cos(a1) * (r - 14), math.sin(a1) * (r - 14))], RED, 7)
    circle(c, 0, 0, 8); c.set_source_rgba(*INK); c.fill()
    if readout:
        s = f"{secs:.1f} s".replace(".", ",")
        text(c, s, 0, r + 58, 46, YEL, MONO, True, outline=INK, olw=8)
    c.restore()

def rain(c, t, a=0.22, n=70, y0=600, y1=1700):
    ph = anim_time(t) * 1500 + t * 12
    for i in range(n):
        R = random.Random(i * 31)
        x = R.uniform(-40, W + 40); yy = y0 + (R.uniform(0, y1 - y0) + ph * R.uniform(0.8, 1.2)) % (y1 - y0)
        x -= (yy - y0) * 0.18
        line(c, [(x, yy), (x - 8, yy + 38)], (0.75, 0.8, 1.0, a * R.uniform(0.5, 1)), 3)

def flat_ground(c, gy, col=GROUND):
    c.new_path(); c.move_to(-20, gy + 10)
    for i in range(0, W + 41, 40): c.line_to(i, gy + 6 * math.sin(i / 130))
    c.line_to(W + 20, H + 20); c.line_to(-20, H + 20); c.close_path(); fill_stroke(c, col, INK, 7)
    for i in range(14):
        gx = 40 + i * 77
        line(c, [(gx, gy + 6 * math.sin(gx / 130) + 2), (gx + 6, gy - 14), (gx + 12, gy + 4)], alpha(TREE, 0.9), 4)


# ---------------------------------------------------------------- front: storm over a small town
FCLOUD = make_cloud(3, -80, 1160, 560, 860)
FBOLT = bolt_path(11, 450, 830, 300, 1198, 6, 0.2, 3, 0.32)
FBOLT2 = bolt_path(19, 640, 840, 300, 1198, 6, 0.22, 2, 0.3)
IMPACT = (300, 1198)

def town(c, t, lit=0.0, rattle=0.0):
    c.new_path(); c.move_to(-20, 1260); c.curve_to(200, 1170, 420, 1230, 640, 1190); c.curve_to(820, 1160, 960, 1210, 1100, 1180)
    c.line_to(1100, 2600); c.line_to(-20, 2600); c.close_path(); fill_stroke(c, mix(HILL1, LAV, 0.25 * lit), INK, 6)
    c.new_path(); c.move_to(-20, 1340); c.curve_to(120, 1290, 220, 1200, 300, 1196); c.curve_to(400, 1200, 520, 1300, 660, 1350)
    c.line_to(660, 2600); c.line_to(-20, 2600); c.close_path(); fill_stroke(c, mix(HILL2, LAV, 0.3 * lit), INK, 6)
    if lit > 0: glow(c, IMPACT[0], IMPACT[1], 260, YEL, 0.55 * lit)
    c.new_path(); c.move_to(-20, 1420); c.curve_to(300, 1380, 700, 1400, 1100, 1385)
    c.line_to(1100, 2600); c.line_to(-20, 2600); c.close_path(); fill_stroke(c, mix(GROUND, LAV, 0.2 * lit), INK, 7)
    tree(c, 120, 1410, 0.9)
    house(c, 505, 1405, 0.5, t, GOLD, 1.0, rattle * 0.7)
    house(c, 905, 1400, 0.62, t, ORANGE2, 1.0, rattle * 0.8)
    house(c, 700, 1408, 0.92, t, RUST, 1.0, rattle)
    line(c, [(-20, 1560), (1100, 1545)], alpha(INK, 0.35), 18)  # road

def ic_clouds(c):
    for dx, col in ((-38, LAV), (38, METAL)):
        c.new_path()
        for (x, y, r) in [(dx - 20, 8, 22), (dx + 14, 6, 24), (dx - 2, -14, 24)]: circle(c, x, y, r)
        c.set_source_rgba(*INK); c.set_line_width(10); c.stroke_preserve(); c.set_source_rgba(*col); c.fill()
    for i in range(8):
        a = i * math.pi / 4
        line(c, [(math.cos(a) * 8, -40 + math.sin(a) * 8), (math.cos(a) * 20, -40 + math.sin(a) * 20)], ORANGE, 5)

def ic_crack(c):
    rrect(c, -62, -46, 124, 92, 10); fill_stroke(c, METAL, INK, 5)
    line(c, [(-10, -46), (8, -18), (-12, 4), (14, 22), (2, 46)], INK, 7)
    line(c, [(8, -18), (40, -10)], INK, 5); line(c, [(-12, 4), (-44, 14)], INK, 5)
    for (x, y) in [(52, -56), (64, 40), (-58, -58)]:
        c.new_path(); c.move_to(x, y); c.line_to(x + 12, y + 6); c.line_to(x + 4, y + 16); c.close_path(); fill_stroke(c, METAL, INK, 3)

def ic_drum(c):
    line(c, [(-50, -70), (6, -30)], hx("#C9A46A"), 9); line(c, [(52, -72), (-4, -30)], hx("#C9A46A"), 9)
    c.new_path(); c.move_to(-58, -18); c.line_to(-58, 40); c.curve_to(-58, 66, 58, 66, 58, 40); c.line_to(58, -18); c.close_path()
    fill_stroke(c, RED, INK, 5)
    for i in range(5):
        x = -50 + i * 25
        line(c, [(x, -10), (x + 12, 50)], alpha(CREAM, 0.9), 4)
    c.save(); c.translate(0, -18); c.scale(1, 0.3); circle(c, 0, 0, 58); c.restore(); fill_stroke(c, CREAM2, INK, 5)
    circle(c, -50, -70, 9); fill_stroke(c, CREAM2, INK, 3); circle(c, 52, -72, 9); fill_stroke(c, CREAM2, INK, 3)

T_S1 = 0.5
T_S2 = wt("imposible", "temblar") - 1.0
T_FR = wt("freno", "vamos")

def scene_front(c, t):
    background(c, t, STEEL)
    t_nub = wt("imposible", "nubes"); t_rom = wt("imposible", "rompiendo"); t_tam = wt("imposible", "tambor")
    up = ease(ramp(t, wq("imposible", "trueno") - 0.2, t_nub - 0.3))
    z = ease(ramp(t, T_FR, T_SLOW + 0.2)); up *= 1 - z
    push = 1 + 0.04 * ease(ramp(t, 0, 7))
    k1 = strike(t, T_S1, 3.8, 0.6); k2 = strike(t, T_S2, 1.6, 0.5); k3 = strike(t, T_FR, 99, 1, freeze=True)
    kb = max(k1, k3); lit = max(kb, k2) * 0.8
    fl = max(flash_k(t, T_S1), flash_k(t, T_S2), flash_k(t, T_FR))
    t_oy = wt("gancho", "oyes") - 0.4; t_tem = wt("imposible", "temblar") - 0.5
    ring_k = 0.0; rattle = 0.0
    c.save()
    cam(c, 1 - 0.14 * up, 540, 600)
    cam(c, push * (1 + 0.7 * z), 430, 900)
    if lit > 0: glow(c, 380, 950, 800, XRAY, 0.18 * lit)
    town(c, t, lit)
    rain(c, t, 0.22)
    draw_cloud(c, FCLOUD, lit * 0.9)
    glow(c, 640, 760, 260, XRAY, 0.10 + 0.05 * math.sin(t * 2.3))
    grow1 = ramp(t, T_S1, T_S1 + 0.12); grow3 = ramp(t, T_FR, T_FR + 0.15)
    if k3 > 0: draw_bolt(c, FBOLT, k3, grow3)
    elif k1 > 0: draw_bolt(c, FBOLT, k1, grow1)
    if k2 > 0: draw_bolt(c, FBOLT2, k2, ramp(t, T_S2, T_S2 + 0.12))
    if max(kb, k2) > 0.05: glow(c, IMPACT[0], IMPACT[1], 120, WHITE, 0.7 * max(kb, k2))
    # thunder rings reaching the houses
    for t0 in (t_oy, t_tem):
        if t0 <= t < t0 + 1.8:
            R = (t - t0) * 650
            sound_arcs(c, IMPACT[0], IMPACT[1] - 40, R, -1.1, 0.35, 1 - ramp(t, t0 + 1.0, t0 + 1.8), 3, 40)
            rattle = max(rattle, math.sin(math.pi * ramp(t, t0 + 0.45, t0 + 1.6)))
    if rattle > 0:
        c.save(); c.rectangle(0, 1100, W, 330); c.clip()
        house(c, 700, 1408, 0.92, t, RUST, 1.0, rattle)
        c.restore()
    c.restore()
    white(c, 0.55 * fl)
    # gancho callouts (30.000 °C, 5x the Sun)
    def gan():
        ax, ay = bolt_at(FBOLT, 0.5)
        callout(c, "30.000 °C", ax + 8, ay, 790, 960, t, wq("gancho", "treinta") - 0.1, HOT, 44)
        k = ramp(t, wq("gancho", "cinco") - 0.1, wq("gancho", "cinco") + 0.25)
        if k > 0:
            p = eob(k); c.save(); c.translate(790, 1080); c.scale(p, p)
            shadow(c, lambda: rrect(c, -175, -52, 350, 104, 14), 6, 8, 0.4)
            rrect(c, -175, -52, 350, 104, 14); fill_stroke(c, CREAM, INK, 5)
            sun_icon(c, -118, 0, 26)
            text(c, "× 5", 30, -2, 48, RED, SLAB, False)
            text(c, "LA SUPERFICIE DEL SOL", 30, 36, 20, INK, SANS, True)
            c.restore()
    faded(c, 1 - ramp(t, wq("imposible", "trueno") - 0.4, wq("imposible", "trueno")), gan)
    # imposible: crossed-out badges
    if up > 0.01:
        for (t0, x, lab, fn) in [(t_nub, 250, "NUBES", ic_clouds), (t_rom, 540, "ROMPER", ic_crack), (t_tam, 830, "TAMBOR", ic_drum)]:
            k = eob(ramp(t, t0 - 0.15, t0 + 0.15)) * up
            icon_badge(c, x, 1500, k, lab, fn, t, t0 + 0.35, 95)
    # freno: fade into the cut-away cloud
    xr = ease(ramp(t, T_SLOW - 0.6, T_SLOW + 0.3))
    if xr > 0:
        c.push_group(); draw_paso1(c, t); c.pop_group_to_source(); c.paint_with_alpha(xr)


# ---------------------------------------------------------------- paso 1: inside the cloud
P1CLOUD = make_cloud(8, 70, 1010, 630, 1160)
P1GY = 1570
P1BOLT = bolt_path(23, 480, 1150, 420, P1GY, 6, 0.2, 3, 0.3)

def _p1_items():
    R = random.Random(5)
    cr = [(R.uniform(150, 930), R.uniform(0, 1), R.uniform(0, 6.28), R.uniform(22, 34)) for _ in range(13)]
    hl = [(R.uniform(150, 930), R.uniform(0, 1), R.uniform(14, 22)) for _ in range(10)]
    ch = []
    for i in range(26):
        sg = 1 if i % 2 else -1; k = i // 2
        tx = 175 + (k % 9) * 92 + (40 if k >= 9 else 0) + R.uniform(-10, 10)
        ty = (712 + (k // 9) * 48) if sg > 0 else (1090 - (k // 9) * 48)
        ch.append((R.uniform(180, 900), R.uniform(760, 1060), tx, ty, sg))
    return cr, hl, ch
P1CR, P1HL, P1CH = _p1_items()

def draw_paso1(c, t):
    background(c, t, STEEL)
    t_hie = wt("paso1", "hielo"); t_gra = wt("paso1", "granizo"); t_cho = wt("paso1", "chocan")
    t_sep = wt("paso1", "separan"); t_car = wt("paso1", "cargas"); t_acu = wt("paso1", "acumulan"); t_dem = wt("paso1", "demasiadas")
    t_chi = wt("paso1", "chispa"); t_gig = wt("paso1", "gigante"); t_sue = wt("paso1", "suelo"); t_ray = wt("paso1", "rayo")
    c.save(); cam(c, 1 + 0.04 * ramp(t, SS("paso1"), B("paso2")["start"]), 540, 1100)
    kb = strike(t, t_chi - 0.1, 99, 1, freeze=True); grow = ease(ramp(t, t_chi - 0.1, t_chi + 0.35))
    lit = 0.6 * kb
    # ground
    c.new_path(); c.move_to(-20, P1GY + 20); c.curve_to(250, P1GY - 10, 600, P1GY + 10, 1100, P1GY - 10)
    c.line_to(1100, H + 20); c.line_to(-20, H + 20); c.close_path(); fill_stroke(c, mix(GROUND, LAV, 0.2 * lit), INK, 7)
    tree(c, 170, P1GY + 6, 0.55); house(c, 800, P1GY + 2, 0.42, t, RUST, 1.0)
    # ground + charges
    ng = int(clamp((t - t_acu + 0.1) / 0.06, 0, 11)) if t >= t_acu - 0.1 else 0
    for i in range(ng):
        kk = ramp(t, t_acu - 0.1 + i * 0.06, t_acu + 0.15 + i * 0.06)
        neu = 1 - 0.55 * ramp(t, t_chi + 0.3, t_chi + 1.0) * (abs(i - 3.5) < 2.5)
        faded(c, neu, lambda i=i, kk=kk: charge(c, 110 + i * 86, P1GY + 46, 1, 17, eob(kk)))
    # field strain
    if t >= t_dem - 0.2 and grow < 1:
        a = 0.6 * ramp(t, t_dem - 0.2, t_dem + 0.4) * (0.6 + 0.4 * math.sin(t * 30))
        c.set_dash([14, 14])
        for i in range(6):
            x = 200 + i * 130
            line(c, [(x, 1160), (x + 10 * math.sin(t * 7 + i), P1GY - 10)], alpha(YEL, a * 0.6), 3)
        c.set_dash([])
    # cloud: translucent cut-away (yellow halo when it is about to discharge)
    if t >= t_dem - 0.1 and grow < 1:
        cloud_path(c, P1CLOUD); c.set_source_rgba(*alpha(YEL, (0.3 + 0.2 * math.sin(t * 25)) * ramp(t, t_dem - 0.1, t_dem + 0.3))); c.set_line_width(40); c.stroke()
    draw_cloud(c, P1CLOUD, lit, top=hx("#4A4466"), bot=hx("#2A2640"))
    c.save(); cloud_path(c, P1CLOUD); c.clip()
    glow(c, 540, 900, 520, XRAY, 0.10)
    line(c, [(60, 1000), (1020, 1000)], alpha(WHITE, 0.0), 1)
    ph = t * 0.06
    for i, (x, u, a0, s) in enumerate(P1CR):  # ice crystals rise
        y = 1130 - ((u + ph) % 1) * 460
        crystal(c, x + 10 * math.sin(t * 0.8 + i), y, s, a0 + t * 0.3)
    for i, (x, u, r) in enumerate(P1HL):  # hail falls
        y = 680 + ((u + ph * 1.4) % 1) * 440
        hail(c, x + 8 * math.sin(t + i), y, r)
    if t >= t_cho - 0.1:  # collisions
        for i in range(7):
            q = (t * 0.7 + i / 7) % 1
            if q < 0.18:
                R = random.Random(i * 13 + int(t * 0.7 + i / 7))
                x, y = R.uniform(200, 880), R.uniform(760, 1060); s = 26 * math.sin(math.pi * q / 0.18)
                glow(c, x, y, 70, YEL, 0.7 * math.sin(math.pi * q / 0.18))
                for j in range(6):
                    a = j * math.pi / 3 + i
                    line(c, [(x + math.cos(a) * s * 0.3, y + math.sin(a) * s * 0.3), (x + math.cos(a) * s, y + math.sin(a) * s)], YEL, 4)
    # charges separate
    if t >= t_cho:
        mv = ease(ramp(t, t_sep, t_sep + 1.6))
        nn = len(P1CH) + (8 if t >= t_dem else 0)
        for i, (x0, y0, tx, ty, sg) in enumerate(P1CH):
            k = eob(ramp(t, t_cho + i * 0.03, t_cho + 0.3 + i * 0.03))
            x = lerp(x0, tx, mv) + 3 * math.sin(t * 3 + i); y = lerp(y0, ty, mv) + 3 * math.cos(t * 2.6 + i)
            neu = 1 - 0.6 * ramp(t, t_chi + 0.3, t_chi + 1.0) * (sg < 0 and abs(x - 470) < 260)
            faded(c, neu, lambda x=x, y=y, sg=sg, k=k: charge(c, x, y, sg, 18, k))
        if t >= t_dem - 0.1:  # too many: extra negative charges crowd the bottom
            for j in range(8):
                k = eob(ramp(t, t_dem - 0.1 + j * 0.05, t_dem + 0.2 + j * 0.05))
                charge(c, 220 + j * 85, 1132 - (j % 2) * 20, -1, 18, k * (1 - 0.7 * ramp(t, t_chi + 0.3, t_chi + 1.0)))
    c.restore()
    draw_bolt(c, P1BOLT, kb, grow)
    if grow >= 1: glow(c, 420, P1GY, 160, WHITE, 0.6 * kb)
    c.restore()
    white(c, 0.5 * flash_k(t, t_chi + 0.2, 0.35))
    # callouts
    def hg():
        x, u, a0, s = P1CR[2]; y = 1130 - ((u + t * 0.06) % 1) * 460
        callout(c, "HIELO", x + 10 * math.sin(t * 0.8 + 2), y, 250, 668, t, t_hie - 0.1, XRAY)
        x, u, r = P1HL[4]; y = 680 + ((u + t * 0.06 * 1.4) % 1) * 440
        callout(c, "GRANIZO", x + 8 * math.sin(t + 4), y, 830, 668, t, t_gra - 0.1, CREAM)
    faded(c, 1 - ramp(t, t_car + 0.6, t_car + 0.9), hg)
    callout(c, "CARGAS +", P1CH[1][2], P1CH[1][3], 250, 668, t, t_car, HOT)
    callout(c, "CARGAS −", P1CH[0][2], P1CH[0][3], 230, 1230, t, t_car + 0.3, XRAY)
    callout(c, "CHISPA GIGANTE", *bolt_at(P1BOLT, 0.55), 790, 1330, t, t_gig - 0.1, YEL)
    callout(c, "SUELO", 800, P1GY + 40, 800, 1665, t, t_sue - 0.1, CREAM)
    big(c, "¡RAYO!", 215, 1430, 84, YEL, ramp(t, t_ray - 0.1, t_ray + 0.25))

def scene_paso1(c, t): draw_paso1(c, t)


# ---------------------------------------------------------------- paso 2: the channel, close up
def chan2(y): return 420 + 16 * math.sin(y / 85) + 7 * math.sin(y / 31 + 1)
P2MOL = [(x, y, a) for (x, y, a) in [(random.Random(i).uniform(70, 760), random.Random(i + 500).uniform(630, 1680), random.Random(i + 900).uniform(0, 6.3)) for i in range(90)]
         if abs(x - chan2(y)) > 85 and not (x > 560 and y > 1440)][:44]

def draw_channel(c, cxf, y0, y1, w, heat, k=1.0):
    pts = [(cxf(y), y) for y in range(int(y0), int(y1) + 1, 8)]
    if len(pts) < 2: return
    gc = mix(XRAY, ORANGE, heat); body = mix(hx("#CFE3FF"), YEL, heat)
    line(c, pts, alpha(gc, 0.08 * k), w * 5); line(c, pts, alpha(gc, 0.16 * k), w * 2.8)
    line(c, pts, alpha(INK, k), w + 14); line(c, pts, alpha(body, k), w); line(c, pts, alpha(WHITE, 0.9 * k), w * 0.42)

def molecule(c, x, y, a, col, s=1.0):
    dx, dy = math.cos(a) * 9 * s, math.sin(a) * 9 * s
    for sg in (-1, 1):
        circle(c, x + sg * dx, y + sg * dy, 9 * s); fill_stroke(c, col, INK, 3)

def thermometer(c, x, ytop, ybot, frac, col):
    rrect(c, x - 26, ytop, 52, ybot - ytop + 20, 26); fill_stroke(c, CREAM, INK, 6)
    lv = lerp(ybot - 10, ytop + 26, clamp(frac))
    rrect(c, x - 12, lv, 24, ybot - lv + 20, 12); c.set_source_rgba(*col); c.fill()
    circle(c, x, ybot + 46, 46); fill_stroke(c, col, INK, 6)
    for i in range(7):
        yy = lerp(ybot - 10, ytop + 26, i / 6)
        line(c, [(x + 26, yy), (x + 42, yy)], CREAM, 4)

def scene_paso2(c, t):
    t_chi = wt("paso2", "chispa"); t_can = wt("paso2", "canal"); t_poc = wt("paso2", "pocos"); t_cal = wt("paso2", "calienta")
    t_tre = wt("paso2", "treinta"); t_gra = wt("paso2", "grados"); t_fra = wt("paso2", "fracción")
    heat = ease(ramp(t, t_cal - 0.2, t_gra + 0.2))
    background(c, t, mix(STEEL, HOT, heat))
    c.save(); cam(c, 1 + 0.04 * ramp(t, SS("paso2"), B("paso3")["start"]), 540, 1150)
    head = lerp(560, 1780, ease(ramp(t, SS("paso2") + 0.2, t_can)))
    for i, (x, y, a) in enumerate(P2MOL):
        near = math.exp(-abs(x - chan2(y)) / 170)
        j = (2 + 16 * heat * near)
        molecule(c, x + j * math.sin(t * 23 + i * 1.7), y + j * math.cos(t * 19 + i), a + t * (0.3 + 5 * heat * near), mix(LAV, HOT, heat * near))
    draw_channel(c, chan2, 560, head, 90, heat)
    if head < 1770: glow(c, chan2(head), head, 140, WHITE, 0.9)
    c.restore()
    # ruler: "pocos centímetros"
    k = ramp(t, t_poc - 0.2, t_poc + 0.3)
    if k > 0:
        y = 1505; cx = chan2(y); px = 45  # 1 cm = 45 px: the channel is ~2 cm
        c.save(); c.translate(cx, y); c.scale(eob(k), eob(k))
        rrect(c, -180, -28, 360, 56, 8); fill_stroke(c, CREAM2, INK, 5)
        for i in range(-4, 5):
            line(c, [(i * px, -28), (i * px, -8 if i % 2 else 2)], INK, 3)
        line(c, [(-45, -40), (-45, -110)], YEL, 5); line(c, [(45, -40), (45, -110)], YEL, 5)
        c.restore()
        big(c, "POCOS CM", cx, 1610, 56, YEL, k, 10)
    callout(c, "CANAL DE AIRE", chan2(800) + 50, 800, 230, 680, t, t_can - 0.1, XRAY)
    # thermometer shoots to 30.000 °C
    kt = ramp(t, t_cal - 0.5, t_cal - 0.1)
    if kt > 0:
        x, yt, yb = 870, 820, 1350
        hc = mix(COLD, HOT, heat)
        c.save(); c.translate(x, 1100); c.scale(eob(kt), eob(kt)); c.translate(-x, -1100)
        thermometer(c, x, yt, yb, heat, hc)
        c.restore()
        ys = lerp(yb - 10, yt + 26, 5500 / 30000)
        ks = ramp(t, t_tre - 0.1, t_tre + 0.2)
        if ks > 0:
            line(c, [(x - 26, ys), (x - 70, ys)], CREAM, 5)
            c.save(); c.translate(690, ys); c.scale(eob(ks), eob(ks))
            rrect(c, -140, -30, 250, 60, 10); fill_stroke(c, INK, alpha(WHITE, 0.95), 3)
            sun_icon(c, -110, 0, 13)
            text(c, "SOL: 5.500 °C", -8, 10, 26, YEL, SANS, True)
            c.restore()
        v = 20 + (30000 - 20) * heat
        s = f"{dots(round(v / 100) * 100) if v > 1000 else int(v)} °C"
        rrect(c, 620, 1450, 300, 84, 12); fill_stroke(c, hx("#1E3A2A"), INK, 5)
        vs = fit_size(c, s, MONO, 48, 270, True)
        text(c, s, 770, 1508, vs, mix(hx("#7CFC9A"), HOT, heat), MONO, True)
    tag(c, "EN < 0,001 s", 770, 1640, ramp(t, t_fra - 0.1, t_fra + 0.25), 30, RED)


# ---------------------------------------------------------------- paso 3: it explodes -> shock wave
def chan3(y): return 540 + 12 * math.sin(y / 90 + 1) + 6 * math.sin(y / 29)
P3DOTS = [(60 + i * 54 + (j % 2) * 27, 630 + j * 50) for i in range(18) for j in range(22)]
P3V = 240  # px/s, ring speed in this slow motion

def p3_rings(t):
    e0 = wt("paso3", "expande") - 0.1; tx = wt("paso3", "explosión") - 0.25
    rs = [(e0, 1.0)] + [(e0 + 1.1 * i, 0.4) for i in range(1, 8) if e0 + 1.1 * i < tx - 0.4] + [(tx, 1.35)]
    rs += [(tx + 1.0 * i, 0.4) for i in range(1, 4)]
    return [(te, s, (t - te) * P3V) for te, s in rs if t >= te]

def ring_x(R, y, cy=1150):
    rx, ry = 55 + R, 620 + 0.35 * R
    q = 1 - ((y - cy) / ry) ** 2
    return 540 + rx * math.sqrt(max(0, q))

def scene_paso3(c, t):
    t_cal = wt("paso3", "caliente"); t_exp = wt("paso3", "expande"); t_rap = wt("paso3", "rápido"); t_emp = wt("paso3", "empuja")
    t_x = wt("paso3", "explosión"); t_ond = wt("paso3", "onda"); t_tru = wt("paso3", "trueno")
    background(c, t, HOT)
    rings = p3_rings(t)
    c.save(); cam(c, 1 + 0.04 * ramp(t, SS("paso3"), B("paso4")["start"]), 540, 1150)
    for (x, y) in P3DOTS:
        d = abs(x - 540); sg = 1 if x >= 540 else -1
        disp = 0.0; br = 0.0
        for te, s, R in rings:
            Rr = 55 + R
            e = math.exp(-((d - Rr) / 34) ** 2)
            disp += s * 30 * e / (1 + R / 500); br += s * e
        xx = x + sg * disp
        if abs(xx - 540) < 75 + 60 * ramp(t, t_exp, t_exp + 0.6): continue
        circle(c, xx, y, 6 + 3 * min(1, br)); c.set_source_rgba(*mix(alpha(LAV, 0.45), alpha(CREAM, 1), min(1, br))); c.fill()
    c.save(); c.rectangle(0, 610, W, 1100); c.clip()
    for te, s, R in rings:
        a = min(1, s) * clamp(1 - R / 620)
        if a <= 0.02: continue
        rx, ry = 55 + R, 620 + 0.35 * R
        for lw, col in ((14 * s + 8, alpha(INK, a)), (14 * s, alpha(mix(CREAM, YEL, 0.4), a))):
            c.new_path(); c.save(); c.translate(540, 1150); c.scale(rx, ry); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
            c.set_source_rgba(*col); c.set_line_width(lw); c.stroke()
    c.restore()
    if t_x - 0.25 <= t < t_x + 1.2:  # explosion burst
        k = math.sin(math.pi * ramp(t, t_x - 0.25, t_x + 1.2))
        glow(c, 540, 1150, 420, ORANGE, 0.6 * k)
        c.new_path()
        for i in range(24):
            a = i * math.pi / 12; r = (260 if i % 2 else 150) * k
            c.line_to(540 + math.cos(a) * r, 1150 + math.sin(a) * r * 1.3)
        c.close_path(); fill_stroke(c, alpha(YEL, 0.85 * k), alpha(INK, k), 6)
    w = 90 + 70 * ease(ramp(t, t_exp - 0.1, t_exp + 0.6))
    draw_channel(c, chan3, 560, 1780, w, 1.0)
    if t >= t_emp - 0.1 and rings:  # pushing arrows on the main front
        ka = ramp(t, t_emp - 0.1, t_emp + 0.3) * (1 - ramp(t, t_emp + 2.2, t_emp + 2.6))
        R = rings[0][2]
        if ka > 0 and R < 600:
            for y in (900, 1150, 1400):
                xr = ring_x(R, y)
                for sg in (-1, 1):
                    x0 = 540 + sg * (xr - 540)
                    arrow(c, x0 + sg * 10, y, x0 + sg * (10 + 80 * ka), y, alpha(YEL, ka), 10, 30)
    c.restore()
    callout(c, "30.000 °C", chan3(780) + 70, 780, 840, 760, t, t_cal - 0.1, HOT, 40)
    tag(c, "MÁS RÁPIDO QUE EL SONIDO", 540, 660, ramp(t, t_rap - 0.1, t_rap + 0.25), 32, RED)
    callout(c, "EXPLOSIÓN", 560, 1000, 840, 880, t, t_x - 0.1, ORANGE, 36)
    big_r = [r for r in rings if r[1] > 1.2]
    if big_r:
        R = big_r[0][2]; y = 1380
        callout(c, "ONDA DE CHOQUE", min(1000, ring_x(R, y)), y, 540, 1625, t, t_ond - 0.1, YEL, 38)
    big(c, "= EL TRUENO", 540, 1530, 80, YEL, ramp(t, t_tru - 0.1, t_tru + 0.25))


# ---------------------------------------------------------------- paso 4: light first, sound later
P4GY = 1440
P4CLOUD = make_cloud(14, -80, 560, 620, 860)
P4BOLT = bolt_path(31, 270, 845, 215, P4GY, 6, 0.2, 2, 0.3)
P4SRC = (245, 1140)
P4PX = 880
P4EAR = (P4PX + 10, P4GY - 258); P4EYE = (P4PX - 26, P4GY - 262)

def side_world(c, t, cl, bolt, gy, kb, grow, px, hear=0.0, see=0.0, lit=0.0):
    rain(c, t, 0.16)
    flat_ground(c, gy, mix(GROUND, LAV, 0.2 * lit))
    tree(c, 470, gy + 4, 0.6); house(c, 610, gy + 4, 0.45, t, RUST, 1.0)
    draw_cloud(c, cl, lit)
    draw_bolt(c, bolt, kb, grow)
    if kb > 0.3 and grow >= 1: glow(c, bolt[0][-1][0], gy, 120, WHITE, 0.5 * kb)
    person(c, px, gy, 1.0, hear, see)

def scene_paso4(c, t):
    t_luz = wt("paso4", "luz") - 0.15; t_ins = wt("paso4", "instante"); t_son = wt("paso4", "sonido"); t_340 = wt("paso4", "trescientos")
    t_ves = wt("paso4", "ves"); t_oy = wt("paso4", "oyes")
    background(c, t, STEEL)
    c.save(); cam(c, 1 + 0.03 * ramp(t, SS("paso4"), B("paso5")["start"]), 540, 1150)
    kb = max(strike(t, t_luz, 1.6, 0.6), 0.22 * (t >= t_luz + 2.2)) if t >= t_luz else 0
    kb = max(kb, 0.22 * ramp(t, t_luz + 1.8, t_luz + 2.2))
    D = math.dist(P4SRC, P4EAR) - 20
    R = D * ramp(t, t_luz, t_oy)
    hear = math.sin(math.pi * ramp(t, t_oy - 0.1, t_oy + 1.2))
    see = math.sin(math.pi * ramp(t, t_luz + 0.05, t_luz + 1.2)) + 0.8 * pulse_at(t, t_ves - 0.1, 0.8)
    side_world(c, t, P4CLOUD, P4BOLT, P4GY, kb, ramp(t, t_luz, t_luz + 0.1), P4PX, hear, min(1, see), kb * 0.7)
    # light: arrives at once
    if t >= t_luz + 0.03:
        a = 1 - 0.75 * ramp(t, t_luz + 2.0, t_luz + 3.0)
        line(c, [P4SRC, P4EYE], alpha(YEL, 0.25 * a), 22)
        c.set_dash([22, 16]); line(c, [P4SRC, P4EYE], alpha(YEL, a), 7); c.set_dash([])
    # sound: a slow wavefront
    if t >= t_luz and R > 10:
        ka = 1 - ramp(t, t_oy + 0.2, t_oy + 1.0)
        c.save(); c.rectangle(0, 600, W, P4GY - 600); c.clip()
        sound_arcs(c, P4SRC[0], P4SRC[1], R, -1.05, 1.05, ka, 3, 36)
        c.restore()
    c.restore()
    white(c, 0.5 * flash_k(t, t_luz))
    secs = 6 * ramp(t, t_luz, t_oy)
    stopwatch(c, 760, 745, 66, secs, ramp(t, t_luz - 0.2, t_luz + 0.15), 12)
    callout(c, "LUZ: AL INSTANTE", lerp(P4SRC[0], P4EYE[0], 0.5), lerp(P4SRC[1], P4EYE[1], 0.5), 520, 1010, t, t_luz + 0.3, YEL, 32)
    ang = 0.42
    callout(c, "SONIDO: 340 M/S", P4SRC[0] + R * math.cos(ang), P4SRC[1] + R * math.sin(ang), 540, 1600, t, t_340 - 0.2, CREAM, 34)
    tag(c, "1º LO VES", 800, 1085, ramp(t, t_ves - 0.2, t_ves + 0.15), 30, RED)
    k = ramp(t, t_oy - 0.1, t_oy + 0.25)
    if k > 0:
        tag(c, "2º LO OYES", 560, 1330, k, 30, RED)
        big(c, "¡BRUM!", 690, 1250, 56, CREAM, k, 9)


# ---------------------------------------------------------------- paso 5: count and divide
P5GY = 1460
P5CLOUD = make_cloud(14, -80, 520, 850, 1050)
P5BOLT = bolt_path(37, 250, 1035, 215, P5GY, 6, 0.2, 2, 0.3)
P5SRC = (235, 1250)
P5PX = 880
P5EAR = (P5PX + 10, P5GY - 258)

def scene_paso5(c, t):
    t_f = SS("paso5") + 0.4; t_tr = wt("paso5", "trueno") + 0.1
    t_div = wt("paso5", "divide"); t_3 = wt("paso5", "tres"); t_mm = wt("paso5", "más"); t_km = wt("paso5", "kilómetros"); t_tor = wt("paso5", "tormenta")
    background(c, t, STEEL)
    kb = strike(t, t_f, 1.2, 0.5)
    hear = math.sin(math.pi * ramp(t, t_tr - 0.1, t_tr + 1.0))
    side_world(c, t, P5CLOUD, P5BOLT, P5GY, max(kb, 0.2 * (t > t_f)), ramp(t, t_f, t_f + 0.1), P5PX, hear, 0.0, kb * 0.6)
    R = (math.dist(P5SRC, P5EAR) - 20) * ramp(t, t_f, t_tr)
    if t >= t_f and R > 10:
        c.save(); c.rectangle(0, 860, W, P5GY - 860); c.clip()
        sound_arcs(c, P5SRC[0], P5SRC[1], R, -0.9, 0.95, 1 - ramp(t, t_tr + 0.2, t_tr + 0.9), 3, 34)
        c.restore()
    white(c, 0.45 * flash_k(t, t_f))
    secs = 6 * ramp(t, t_f, t_tr)
    k_sw = ramp(t, t_f - 0.3, t_f) * (1 - ramp(t, t_div + 0.2, t_div + 0.5))
    faded(c, clamp(k_sw * 1.5), lambda: stopwatch(c, 720, 1040, 62, int(secs) if secs < 6 else 6.0, 1.0, 12))
    if t_f <= t < t_tr + 0.4:  # counting out loud
        n = min(6, int(secs) + 1)
        big(c, str(n) if secs < 5.99 else "6", 860, 1000, 60, YEL, ramp(t, t_f + (n - 1) * (t_tr - t_f) / 6, t_f + (n - 1) * (t_tr - t_f) / 6 + 0.15), 9)
    # the equation
    parts = [("6 s", WHITE, t_tr + 0.15), ("÷ 3", WHITE, t_3 - 0.2), ("≈", WHITE, t_mm - 0.1), ("2 km", YEL, t_km - 0.1)]
    size = 112
    def fam(s): return SANS if s == "≈" else SLAB
    ws = []
    for p in parts: font(c, fam(p[0]), size, fam(p[0]) == SANS); ws.append(c.text_extents(p[0]).x_advance)
    gap = 34
    tot = sum(ws) + gap * (len(ws) - 1); sc = min(1, 940 / tot); x = 540 - tot * sc / 2
    for (s, col, t0), wd in zip(parts, ws):
        big(c, s, x + wd * sc / 2, 790, size * sc, col, ramp(t, t0, t0 + 0.25), 14, fam(s))
        x += (wd + gap) * sc
    if t >= t_tr + 0.1:
        k = ramp(t, t_tr + 0.1, t_tr + 0.4) * (1 - ramp(t, t_3 + 0.4, t_3 + 0.8))
        if k > 0: tag(c, "CUENTA: 6 SEGUNDOS", 540, 650, k, 30, RED)
    # distance bar
    kd = ease(ramp(t, t_km - 0.1, t_km + 0.6))
    if kd > 0:
        y = 1575; x0 = 215; x1 = lerp(x0, P5PX, kd)
        line(c, [(x0, y - 26), (x0, y + 26)], YEL, 7)
        line(c, [(x0, y), (x1, y)], alpha(INK, 1), 16); line(c, [(x0, y), (x1, y)], YEL, 8)
        if kd > 0.98: line(c, [(P5PX, y - 26), (P5PX, y + 26)], YEL, 7)
        big(c, "UNOS 2 KM", 548, 1650, 54, YEL, ramp(t, t_km + 0.3, t_km + 0.6), 9)
    callout(c, "TORMENTA", 260, 960, 690, 930, t, t_tor - 0.1, CREAM, 36)


# ---------------------------------------------------------------- junto + acelerón
JGY = 1440
JCLOUD = make_cloud(22, -80, 660, 620, 870)
JSRC = (300, 1150)
JPX = 880
JEAR = (JPX + 10, JGY - 258)
JPLUS = [(80 + i * 78, 690 + (i % 2) * 22) for i in range(7)]
JMIN = [(90 + i * 76, 820 - (i % 2) * 22) for i in range(7)]

def tfast(t):
    t0 = T_REAL + 0.2; t1 = B("remate")["start"] - 0.4
    if t <= t0: return t
    acc, x = 0.0, t0
    while x < min(t, t1 + 3):
        dx = min(0.05, t - x); acc += dx * 14 * ease(ramp(x, t0, t1)); x += dx
    return t + acc

def scene_junto(c, t):
    b = B("junto")
    fast = ease(ramp(t, T_REAL + 0.2, B("remate")["start"] - 0.4))
    tf = tfast(t)
    tw = {k: wq("junto", k) - 0.1 for k in ["cargas", "chispa", "calor", "explosión", "onda", "oído"]}
    background(c, t, HOT)
    shake = 8 * fast
    c.save(); cam(c, 1 + 0.05 * ease(ramp(t, b["start"], B("remate")["start"])), 540, 1150)
    c.translate(shake * math.sin(t * 61), shake * math.cos(t * 53))
    # strikes: one stays during junto; in the acelerón they repeat, each one a different bolt
    if fast > 0.02:
        n = int(tf * 0.9); ph = (tf * 0.9) % 1
        bolt = bolt_path(40 + n % 7, 320, 860, 290 + 40 * math.sin(n), JGY, 6, 0.2, 3, 0.3)
        kb = 1 - ph * 0.8; grow = ramp(ph, 0, 0.08); lit = kb * 0.8; fl = 0.35 * (1 - ramp(ph, 0, 0.2)) * fast
    else:
        bolt = bolt_path(40, 320, 860, 290, JGY, 6, 0.2, 3, 0.3)
        kb = strike(t, tw["chispa"], 99, 1, True); grow = ramp(t, tw["chispa"], tw["chispa"] + 0.2); lit = 0.5 * kb
        fl = 0.4 * flash_k(t, tw["chispa"])
    side_world(c, t, JCLOUD, bolt, JGY, 0, 1, JPX, 0, 0, lit)
    kc = ramp(t, tw["cargas"], tw["cargas"] + 0.3)
    for i, (x, y) in enumerate(JPLUS):
        charge(c, x + 3 * math.sin(tf * 3 + i), y, 1, 18, eob(clamp(kc * 2 - i * 0.12)))
    for i, (x, y) in enumerate(JMIN):
        charge(c, x + 3 * math.sin(tf * 3 + i), y, -1, 18, eob(clamp(kc * 2 - i * 0.12)))
    kh = ease(ramp(t, tw["calor"], tw["calor"] + 0.4))
    if kh > 0:
        for p in bolt[0][::12]: glow(c, p[0], p[1], 150, HOT, 0.25 * kh * kb)
    draw_bolt(c, bolt, kb, grow)
    # explosion + rings travelling to the ear
    kx = ramp(t, tw["explosión"], tw["explosión"] + 0.2)
    if kx > 0 and fast < 0.05:
        pk = math.sin(math.pi * ramp(t, tw["explosión"], tw["explosión"] + 1.0))
        if pk > 0:
            c.new_path()
            for i in range(20):
                a = i * math.pi / 10; r = (150 if i % 2 else 80) * pk
                c.line_to(JSRC[0] + math.cos(a) * r, JSRC[1] + math.sin(a) * r)
            c.close_path(); fill_stroke(c, alpha(YEL, 0.8 * pk), alpha(INK, pk), 5)
    D = math.dist(JSRC, JEAR) - 20
    hear = 0.0
    if t >= tw["explosión"]:
        c.save(); c.rectangle(0, 600, W, JGY - 600); c.clip()
        per = 1.1; speed = 420
        t0 = tw["explosión"]
        u = tf - t0
        for k in range(int(u / per) + 1):
            R = (u - k * per) * speed
            if 0 < R < D + 60:
                sound_arcs(c, JSRC[0], JSRC[1], R, -0.85, 0.9, clamp(1 - (R - D) / 60) * (1 if k > 0 or fast > 0 else 1), 2, 30, CREAM, 8)
                hear = max(hear, clamp(1 - abs(R - D) / 140))
        c.restore()
    ko = ramp(t, tw["oído"], tw["oído"] + 0.3)
    person(c, JPX, JGY, 1.0, max(ko * 0.6, hear) if t >= tw["onda"] else 0, 0.6 * fast)
    if fast > 0:  # speed lines
        for i in range(24):
            r0 = 300 + (i * 97 + t * 2400) % 900
            a = i * 0.26
            line(c, [(540 + math.cos(a) * r0, 1150 + math.sin(a) * r0), (540 + math.cos(a) * (r0 + 130 * fast), 1150 + math.sin(a) * (r0 + 130 * fast))],
                 alpha(WHITE, 0.3 * fast), 5)
    c.restore()
    white(c, fl)
    def labels():
        callout(c, "CARGAS", 330, 740, 790, 700, t, tw["cargas"], HOT)
        callout(c, "CHISPA", *bolt_at(bolt, 0.3), 120, 990, t, tw["chispa"], YEL)
        callout(c, "CALOR", *bolt_at(bolt, 0.62), 120, 1250, t, tw["calor"], HOT)
        callout(c, "EXPLOSIÓN", JSRC[0] + 30, JSRC[1] - 20, 600, 980, t, tw["explosión"], ORANGE)
        callout(c, "ONDA", JSRC[0] + 330 * math.cos(0.3), JSRC[1] + 330 * math.sin(0.3), 600, 1580, t, tw["onda"], CREAM)
        callout(c, "OÍDO", JEAR[0] + 6, JEAR[1], 860, 1580, t, tw["oído"], CREAM)
    faded(c, 1 - ramp(t, T_REAL, T_REAL + 0.6), labels)
    t_fl = B("remate")["start"]
    white(c, 0.85 * ramp(t, t_fl - 0.45, t_fl - 0.3) * (1 - ramp(t, t_fl - 0.3, t_fl - 0.1)))


# ---------------------------------------------------------------- remate: a long bolt, sound arrives in pieces
RGY = 1390
RCLOUD = make_cloud(51, -80, 1160, 590, 790)
RBOLT = bolt_path(61, 120, 770, 520, RGY, 7, 0.28, 5, 0.32)
RPX = 880
REAR = (RPX + 10, RGY - 258)
RCOLS = [YEL, ORANGE, HOT, XRAY, LAV]

def _rpoints():
    pts = RBOLT[0]
    ds = [math.dist(p, REAR) for p in pts]
    dmin = min(ds); u = dmin / 2  # nearest bit: "2 km"
    out = []
    for km in [2 + 0.5 * j for j in range(12)]:
        target = km * u
        if target > max(ds): break
        i = min(range(len(pts)), key=lambda j: abs(ds[j] - target) + (0 if pts[j][1] > 780 else 999))
        if abs(ds[i] - target) < u * 0.1 and all(abs(i - o[0]) > 8 for o in out):
            out.append((i, pts[i], km, ds[i]))
    return out
RPTS = _rpoints()

def scene_remate(c, t):
    b = B("remate")
    t0 = b["start"]; t_lin = wt("remate", "línea"); t_tro = wt("remate", "trozo"); t_dis = wt("remate", "distancia")
    t_son = wt("remate", "sonido"); t_par = wt("remate", "partes"); t_ret = wt("remate", "retumba")
    background(c, t, STEEL)
    c.save(); cam(c, 1 + 0.04 * ramp(t, t0, T_LOOP), 540, 1100)
    kb = strike(t, t0 + 0.05, 99, 1) * (0.85 + 0.15 * pulse_at(t, t_lin - 0.1, 0.6))
    side_world(c, t, RCLOUD, RBOLT, RGY, 0, 1, RPX, 0, 0, 0.5 * kb)
    draw_bolt(c, RBOLT, kb, ramp(t, t0 + 0.05, t0 + 0.4))
    te = t_son - 0.3
    s0 = 0.8 * min(p[3] for p in RPTS)  # wavefronts already travelled this far when we start watching
    dmax = max(p[3] for p in RPTS); v = (dmax - s0) / max(0.5, (t_ret - 0.1) - te)
    hear = 0.0
    for n, (i, p, km, d) in enumerate(RPTS):
        col = RCOLS[n % len(RCOLS)]
        kd = ease(ramp(t, t_dis - 0.2 + n * 0.15, t_dis + 0.3 + n * 0.15))
        if kd > 0:
            ex, ey = lerp(p[0], REAR[0], kd), lerp(p[1], REAR[1], kd)
            c.set_dash([4, 16]); line(c, [p, (ex, ey)], alpha(col, 0.95), 6); c.set_dash([])
        # sound piece travelling along its own line
        if t >= te:
            s = s0 + (t - te) * v
            if s < d:
                f = s / d; x, y = lerp(p[0], REAR[0], f), lerp(p[1], REAR[1], f)
                a = math.atan2(REAR[1] - p[1], REAR[0] - p[0])
                for j in range(3):
                    r = 26 + j * 0
                    c.new_path(); c.arc(x - math.cos(a) * j * 16, y - math.sin(a) * j * 16, r, a - 0.9, a + 0.9)
                    c.set_source_rgba(*alpha(INK, 1 - j * 0.3)); c.set_line_width(12); c.stroke()
                    c.new_path(); c.arc(x - math.cos(a) * j * 16, y - math.sin(a) * j * 16, r, a - 0.9, a + 0.9)
                    c.set_source_rgba(*alpha(col, 1 - j * 0.3)); c.set_line_width(6); c.stroke()
            else:
                hear = max(hear, 1 - ramp(t, te + (d - s0) / v, te + (d - s0) / v + 0.6))
    for n, (i, p, km, d) in enumerate(RPTS):
        k = ramp(t, t_tro - 0.1 + n * 0.12, t_tro + 0.2 + n * 0.12)
        if k > 0:
            circle(c, p[0], p[1], 17 * eob(k)); fill_stroke(c, RCOLS[n % len(RCOLS)], INK, 5)
    person(c, RPX, RGY, 1.0, max(hear, 0.7 * ramp(t, t_ret - 0.2, t_ret + 0.2)), 0)
    c.restore()
    white(c, 0.5 * flash_k(t, t0 + 0.05))
    for n, (i, p, km, d) in enumerate(RPTS):
        k = ramp(t, t_dis + 0.2 + n * 0.15, t_dis + 0.5 + n * 0.15)
        mx, my = lerp(p[0], REAR[0], 0.45), lerp(p[1], REAR[1], 0.45)
        tag(c, f"{km:g} KM".replace(".", ","), mx, my - 26, k, 26, RCOLS[n % len(RCOLS)], INK)
    callout(c, "VARIOS KM DE RAYO", *bolt_at(RBOLT, 0.25), 700, 860, t, t_lin - 0.1, YEL, 32)
    # what the ear receives: pieces arriving one after another
    kp = ramp(t, te - 0.4, te)
    if kp > 0:
        x0, x1, y0, y1 = 110, 930, 1520, 1660
        def panel():
            rrect(c, x0, y0, x1 - x0, y1 - y0, 16); fill_stroke(c, alpha(INK, 0.9), alpha(CREAM, 0.9), 4)
            text(c, "LO QUE OYES", x0 + 20, y0 + 30, 22, LAV, SANS, True, "l")
            span = 3.6; ym = (y0 + y1) / 2 + 12
            def X(tt): return x0 + 20 + (x1 - x0 - 40) * (tt - te) / span
            cur = min(t, te + span)
            for n, (i, p, km, d) in enumerate(RPTS):
                ta = te + (d - s0) / v
                if cur <= ta: continue
                pts = []
                tt = ta
                while tt < cur:
                    dt = tt - ta
                    pts.append((X(tt), ym + 40 * math.exp(-dt * 2.6) * math.sin(dt * 40 + n) * min(1, dt * 20)))
                    tt += 0.012
                if len(pts) > 1: line(c, pts, alpha(RCOLS[n % len(RCOLS)], 0.95), 5)
            line(c, [(X(cur), y0 + 40), (X(cur), y1 - 12)], alpha(WHITE, 0.6), 3)
        faded(c, kp, panel)
    tag(c, "POR PARTES", 790, 1480, ramp(t, t_par - 0.15, t_par + 0.2), 28, RED)
    big(c, "¡RETUMBA!", 380, 1490, 66, YEL, ramp(t, t_ret - 0.1, t_ret + 0.25), 11)


# ---------------------------------------------------------------- timeline
SCENES = [
    ("front", 0.0, T_SLOW + 0.5, scene_front),
    ("paso1", T_SLOW + 0.5, SS("paso2"), scene_paso1),
    ("paso2", SS("paso2"), SS("paso3"), scene_paso2),
    ("paso3", SS("paso3"), SS("paso4"), scene_paso3),
    ("paso4", SS("paso4"), SS("paso5"), scene_paso4),
    ("paso5", SS("paso5"), SS("junto"), scene_paso5),
    ("junto", SS("junto"), B("remate")["start"] - 0.1, scene_junto),
    ("remate", B("remate")["start"] - 0.1, T_LOOP + 0.15, scene_remate),
]
LOOP_FN = scene_front
XF = {"remate": 0.08}


def POPS():
    ps = [wq("gancho", "treinta") - 0.1, wq("gancho", "cinco") - 0.1]
    ps += [wt("imposible", w) - 0.15 for w in ("nubes", "rompiendo", "tambor")]
    ps += [wt("paso1", w) - 0.1 for w in ("hielo", "granizo", "cargas", "gigante", "suelo", "rayo")]
    ps += [wt("paso2", w) - 0.1 for w in ("canal", "pocos", "treinta", "fracción")]
    ps += [wt("paso3", w) - 0.1 for w in ("caliente", "rápido", "onda", "trueno")]
    ps += [wt("paso4", w) - 0.15 for w in ("trescientos", "ves")] + [wt("paso4", "luz") + 0.15]
    ps += [wt("paso5", w) - 0.1 for w in ("tres", "más", "kilómetros", "tormenta")] + [wt("paso5", "trueno") + 0.25]
    ps += [wq("junto", k) - 0.1 for k in ["cargas", "chispa", "calor", "explosión", "onda", "oído"]]
    ps += [wt("remate", w) - 0.1 for w in ("línea", "trozo", "distancia", "partes", "retumba")]
    return ps


def SFX(put, L):
    import numpy as np
    SR = L["SR"]
    def thunder(d=2.5, dec=0.8, fc=300):
        n = int(d * SR); tt = L["t_"](n)
        nz = L["noise"](d, fc); nz = nz / (np.abs(nz).max() + 1e-9)
        e = np.minimum(1, tt / 0.04) * np.exp(-tt / dec) * (0.65 + 0.35 * np.sin(2 * np.pi * 2.3 * tt + 1) ** 2)
        x = nz * e * 1.6
        bm = L["boom"](); x[:len(bm)] += 0.7 * bm[:n]
        return x
    # gancho / imposible / freno flashes, thunder after each one
    put(L["zap"](0.25), T_S1, 0.7); put(thunder(2.6), T_S1 + 0.5, 0.55)
    put(thunder(2.8, 1.0), wt("gancho", "oyes") - 0.4, 0.8)
    put(L["zap"](0.25), T_S2, 0.6); put(thunder(2.6, 0.9), wt("imposible", "temblar") - 0.5, 0.8)
    put(L["zap"](0.3), T_FR, 0.6)
    # paso1 spark
    put(L["zap"](0.4), wt("paso1", "chispa") - 0.1, 0.7); put(thunder(2.0, 0.6, 220), wt("paso1", "chispa") + 0.6, 0.45)
    # paso3: expansion and the shock wave
    put(L["whoosh"](0.6, False), wt("paso3", "expande") - 0.2, 0.5)
    put(L["boom"](), wt("paso3", "explosión") - 0.25, 0.8)
    put(thunder(2.2, 0.7), wt("paso3", "trueno") - 0.2, 0.6)
    # paso4/5: flash first, thunder when the wave reaches the ear
    put(L["zap"](0.25), wt("paso4", "luz") - 0.15, 0.7); put(thunder(2.4, 0.8), wt("paso4", "oyes") - 0.05, 0.7)
    t5 = SS("paso5") + 0.4
    put(L["zap"](0.25), t5, 0.6); put(thunder(1.8, 0.6), wt("paso5", "trueno") + 0.1, 0.55)
    for i in range(6): put(L["click"](), t5 + i * (wt("paso5", "trueno") + 0.1 - t5) / 6, 0.6)
    # junto
    put(L["zap"](0.3), wq("junto", "chispa") - 0.1, 0.6); put(L["boom"](), wq("junto", "explosión") - 0.1, 0.6)
    # acelerón: strikes every ~0.5 s
    tt = T_REAL + 0.3
    while tt < B("remate")["start"] - 0.5:
        put(L["zap"](0.18), tt, 0.4); put(thunder(1.2, 0.35), tt + 0.15, 0.4)
        tt += max(0.3, 0.9 - 0.15 * (tt - T_REAL))
    # remate: the long bolt and the pieces arriving one after another
    t0 = B("remate")["start"] + 0.05
    put(L["zap"](0.35), t0, 0.7)
    te = wt("remate", "sonido") - 0.3
    s0 = 0.8 * min(p[3] for p in RPTS)
    dmax = max(p[3] for p in RPTS); v = (dmax - s0) / max(0.5, (wt("remate", "retumba") - 0.1) - te)
    for (i, p, km, d) in RPTS: put(thunder(1.6, 0.45, 260), te + (d - s0) / v, 0.5)
    put(thunder(3.0, 1.1), wt("remate", "retumba") - 0.1, 0.7)


# ---------------------------------------------------------------- thumbnails ("CIELO EXPLOTANDO")
TBOLT = bolt_path(77, 560, 760, 380, 1500, 6, 0.2, 4, 0.35)

def _thumb_scene(c, t=3.0):
    glow(c, 470, 1150, 900, XRAY, 0.25)
    c.new_path(); c.move_to(-900, 1560); c.line_to(-20, 1560); c.curve_to(200, 1500, 300, 1470, 380, 1490); c.curve_to(520, 1510, 700, 1580, 1100, 1560)
    c.line_to(1100, 1940); c.line_to(-900, 1940); c.close_path(); fill_stroke(c, mix(HILL2, LAV, 0.3), INK, 7)
    glow(c, 380, 1490, 320, YEL, 0.6)
    c.new_path(); c.move_to(-900, 1640); c.line_to(-20, 1640); c.curve_to(300, 1600, 700, 1620, 1100, 1610); c.line_to(1100, 1940); c.line_to(-900, 1940); c.close_path()
    fill_stroke(c, mix(GROUND, LAV, 0.2), INK, 7)
    house(c, 760, 1640, 1.25, t, RUST, 1.0, 0.8)
    tree(c, 150, 1640, 1.1)
    rain(c, 2.0, 0.25, 60, 700, 1900)
    draw_cloud(c, make_cloud(5, -100, 1180, 620, 860), 0.9)
    draw_bolt(c, TBOLT, 1.0, 1.0, 1.6)
    glow(c, 380, 1490, 160, WHITE, 0.8)
    sound_arcs(c, 380, 1440, 300, -1.0, 0.1, 0.9, 3, 44, CREAM, 11)

def THUMB_V(c):
    background(c, 3.0, STEEL)
    _thumb_scene(c)
    for i, ln in enumerate(["CIELO", "EXPLOTANDO"]):
        sz = fit_size(c, ln, SLAB, 210, 980)
        text(c, ln, 540, 330 + i * 215, sz, YEL if i else WHITE, SLAB, False, outline=INK, olw=22)

def THUMB_H(c):
    g = cairo.LinearGradient(0, 0, 0, 720); g.add_color_stop_rgba(0, *BG_TOP); g.add_color_stop_rgba(1, *BG_BOT); c.set_source(g); c.paint()
    c.save(); c.translate(560, -400); c.scale(0.66, 0.66); _thumb_scene(c); c.restore()
    for i, ln in enumerate(["CIELO", "EXPLOTANDO"]):
        sz = fit_size(c, ln, SLAB, 150, 640)
        text(c, ln, 350, 320 + i * 170, sz, YEL if i else WHITE, SLAB, False, outline=INK, olw=20)
