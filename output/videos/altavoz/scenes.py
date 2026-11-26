"""¿Cómo suena un altavoz?  Illustrations (see output/engine/SCENES_GUIDE.md)."""
import math
from core import *  # noqa

TAU = 2 * math.pi
COPPER = hx("#D9853B"); COPPER_D = hx("#8E4F22"); SKIN = hx("#E9A27E"); SKIN_D = hx("#B96A55")
WOOD = RUST; WOOD_D = hx("#9E4636"); CONE = hx("#E8D7B4"); CONE_D = hx("#BFA67C")
M_LOG = CFG["hud"]["max_log"]

# ---------------------------------------------------------------- physical time
TS = T_SLOW + 0.3; T2 = T_REAL + 0.2
AT_S = anim_time(TS)

def AT(t):
    """anim_time, cheap on the slow-motion plateau (linear there)."""
    if TS <= t <= T2: return AT_S + (t - TS) * 10 ** (-M_LOG)
    return anim_time(t)

def fvid(t, f):  # frequency as seen in the video
    return f * 10 ** (-slow_log(t))

def blur_of(fv, lo=3.0): return clamp((fv - lo) / 12.0)

T_EMP = wt("paso3", "empuja")
def phi440(t): return TAU * 440 * (AT(t) - AT(T_EMP))   # sin(phi)=0 & moving forward on "empuja"

# paso1: a "song" waveform with LA as fundamental (harmonics give it a shape)
def i_song(p): return (math.sin(p) + 0.5 * math.sin(2 * p + 0.6) + 0.3 * math.sin(3 * p + 1.3)) / 1.45
def d_song(p): return -math.cos(p) - 0.25 * math.cos(2 * p + 0.6) - 0.1 * math.cos(3 * p + 1.3)
_ta, _tb = wt("paso1", "adelante"), wt("paso1", "atrás")
PH1 = max((k * TAU / 144 for k in range(144)),
          key=lambda o: i_song(TAU * 440 * (AT(_ta + 0.15) - AT(_ta)) + o) - i_song(TAU * 440 * (AT(_tb + 0.2) - AT(_ta)) + o))
def phi1(t): return TAU * 440 * (AT(t) - AT(_ta)) + PH1

# ---------------------------------------------------------------- small helpers
def faded(c, a, fn):
    if a <= 0.01: return
    if a >= 0.99: fn(); return
    c.push_group(); fn(); c.pop_group_to_source(); c.paint_with_alpha(a)

def co(c, label, ax, ay, lx, ly, t, t0, color=CREAM, t1=None, size=34):
    a = 1.0 if t1 is None else 1 - ramp(t, t1, t1 + 0.3)
    faded(c, a, lambda: callout(c, label, ax, ay, lx, ly, t, t0, color, size))

def pill(c, s, x, y, size, fg=INK, bg=CREAM, k=1.0, fam=SLAB, bold=False, border=INK):
    if k <= 0.01: return
    font(c, fam, size, bold); e = c.text_extents(s)
    bw, bh = e.x_advance + size * 1.1, size * 1.6
    c.save(); c.translate(x, y); c.scale(k, k)
    shadow(c, lambda: rrect(c, -bw / 2, -bh / 2, bw, bh, bh / 2), 5, 7, 0.4)
    rrect(c, -bw / 2, -bh / 2, bw, bh, bh / 2); fill_stroke(c, bg, border, 5)
    text(c, s, 0, size * 0.36, size, fg, fam, bold)
    c.restore()

def poly_len(pts):
    return [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]

def point_at(pts, L, s):
    for i, l in enumerate(L):
        if s <= l or i == len(L) - 1:
            u = clamp(s / l) if l else 0
            return pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u
        s -= l
    return pts[-1]

def charges(c, pts, D, sp=34, r=7, a=1.0, smear=0.0):
    L = poly_len(pts); tot = sum(L)
    n = int(tot / sp)
    for i in range(n):
        s = (i * sp + D) % tot
        x, y = point_at(pts, L, s)
        if smear > 0.05:
            xa, ya = point_at(pts, L, clamp(s - smear, 0, tot)); xb, yb = point_at(pts, L, clamp(s + smear, 0, tot))
            line(c, [(xa, ya), (xb, yb)], alpha(YEL, 0.7 * a), r * 2)
        else:
            glow(c, x, y, r * 2.6, YEL, 0.5 * a)
            circle(c, x, y, r); c.set_source_rgba(*alpha(YEL, a)); c.fill()

def speed_lines(c, t, fast, cx=540, cy=1130):
    if fast <= 0: return
    for i in range(26):
        r0 = 330 + (i * 97 + t * 2600) % 900; a = i * 0.2417 * 1.0 + 0.1
        line(c, [(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * (r0 + 140 * fast), cy + math.sin(a) * (r0 + 140 * fast))],
             alpha(WHITE, 0.35 * fast), 5)

# ---------------------------------------------------------------- icons
def music_note(c, x, y, s, col=YEL):
    c.save(); c.translate(x, y); c.scale(s, s)
    for dx in (0, 70):
        c.save(); c.translate(dx, 0); c.rotate(-0.35); c.scale(1.3, 1); circle(c, 0, 0, 18); c.restore()
        fill_stroke(c, col, INK, 5)
    line(c, [(20, -6), (20, -110)], INK, 14); line(c, [(90, -6), (90, -110)], INK, 14)
    c.new_path(); c.move_to(14, -118); c.line_to(96, -138); c.line_to(96, -104); c.line_to(14, -84); c.close_path(); fill_stroke(c, col, INK, 5)
    line(c, [(20, -6), (20, -110)], col, 6); line(c, [(90, -6), (90, -110)], col, 6)
    c.restore()

def brain(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s)
    blobs = [(-38, -10, 34), (0, -30, 38), (38, -12, 34), (-24, 22, 30), (22, 22, 32)]
    for bx, by, r in blobs: circle(c, bx, by, r); c.set_source_rgba(*INK); c.set_line_width(12); c.stroke()
    for bx, by, r in blobs: circle(c, bx, by, r); c.set_source_rgba(*hx("#F4A6B8")); c.fill()
    for pts in ([(-50, -10), (-30, -20), (-20, 0)], [(0, -50), (8, -28), (-6, -12)], [(30, -30), (44, -6), (30, 10)], [(-10, 30), (10, 20), (20, 38)]):
        line(c, pts, hx("#C76F88"), 5)
    c.restore()

def ic_guitar(c):
    c.rotate(-0.65)
    rrect(c, -9, -100, 18, 100, 4); fill_stroke(c, GOLD, INK, 4)
    rrect(c, -14, -122, 28, 26, 6); fill_stroke(c, INK, None)
    circle(c, 0, 34, 44); fill_stroke(c, ORANGE, INK, 5)
    circle(c, 0, -6, 33); fill_stroke(c, ORANGE, INK, 5)
    circle(c, 0, 34, 41); c.set_source_rgba(*ORANGE); c.fill()
    circle(c, 0, 8, 13); fill_stroke(c, INK, None)
    rrect(c, -16, 46, 32, 9, 3); fill_stroke(c, INK, None)
    for dx in (-6, -2, 2, 6): line(c, [(dx, -110), (dx, 50)], CREAM, 2)

def ic_piano(c):
    for i in range(6):
        rrect(c, -75 + i * 25, -45, 25, 90, 3); fill_stroke(c, WHITE, INK, 4)
    for i in (1, 2, 4, 5):
        rrect(c, -75 + i * 25 - 7, -45, 14, 54, 2); fill_stroke(c, INK, None)

def ic_mouthpiece(c):
    brass = hx("#E3B341")
    c.new_path(); c.move_to(-62, -44); c.curve_to(-22, -44, -18, -12, 6, -10); c.line_to(76, -6); c.line_to(76, 6); c.line_to(6, 10)
    c.curve_to(-18, 12, -22, 44, -62, 44); c.close_path(); fill_stroke(c, brass, INK, 5)
    rrect(c, -74, -50, 16, 100, 6); fill_stroke(c, brass, INK, 5)
    c.save(); c.translate(-66, 0); c.scale(0.25, 1); circle(c, 0, 0, 36); c.restore(); fill_stroke(c, INK, None)
    line(c, [(-40, -30), (0, -8)], alpha(WHITE, 0.6), 4)

# ---------------------------------------------------------------- speaker, front view
def spk_front(c, cx, cy, s, z=0.0, bl=0.0, Az=14, t=0.0, glow_k=0.0):
    c.save(); c.translate(cx, cy); c.scale(s, s)
    shadow(c, lambda: rrect(c, -260, -430, 520, 860, 34), 18, 24, 0.45)
    rrect(c, -260, -430, 520, 860, 34); fill_stroke(c, WOOD, INK, 8)
    rrect(c, -236, -406, 472, 812, 24); fill_stroke(c, WOOD_D, alpha(INK, 0.5), 3)
    c.save(); rrect(c, -236, -406, 472, 812, 24); c.clip()
    for i in range(9):  # wood grain
        y0 = -390 + i * 95
        line(c, [(-240 + k * 20, y0 + 10 * math.sin(k * 0.5 + i)) for k in range(25)], alpha(INK, 0.12), 4)
    c.restore()
    rrect(c, -244, -418, 488, 20, 10); c.set_source_rgba(1, 1, 1, 0.13); c.fill()
    # tweeter
    circle(c, 0, -280, 80); fill_stroke(c, METAL, INK, 6)
    circle(c, 0, -280, 62); fill_stroke(c, DARK, INK, 4)
    g = cairo.RadialGradient(-12, -294, 4, 0, -280, 42); g.add_color_stop_rgba(0, *WHITE); g.add_color_stop_rgba(1, *CONE_D)
    circle(c, 0, -280, 40); c.set_source(g); c.fill_preserve(); c.set_source_rgba(*INK); c.set_line_width(4); c.stroke()
    for k in range(4):
        a = k * math.pi / 2 + 0.78; circle(c, 70 * math.cos(a), -280 + 70 * math.sin(a), 5); c.set_source_rgba(*INK); c.fill()
    # woofer
    wy = 90
    if glow_k > 0: glow(c, 0, wy, 330, YEL, 0.5 * glow_k)
    circle(c, 0, wy, 236); fill_stroke(c, METAL, INK, 7)
    for k in range(6):
        a = k * math.pi / 3 + 0.5; circle(c, 222 * math.cos(a), wy + 222 * math.sin(a), 7); c.set_source_rgba(*INK); c.fill()
    circle(c, 0, wy, 212); fill_stroke(c, DARK, INK, 5)

    def cone(zz):
        c.save(); c.translate(0, wy); sc = 1 + zz / 320; c.scale(sc, sc)
        circle(c, 0, 0, 196); c.set_source_rgba(*NIGHT); c.set_line_width(14); c.stroke()  # surround roll
        g = cairo.RadialGradient(-30, -40, 30, 0, 0, 190); g.add_color_stop_rgba(0, *CONE); g.add_color_stop_rgba(1, *CONE_D)
        circle(c, 0, 0, 186); c.set_source(g); c.fill_preserve(); c.set_source_rgba(*INK); c.set_line_width(5); c.stroke()
        for r in (150, 110): circle(c, 0, 0, r); c.set_source_rgba(*alpha(INK, 0.12)); c.set_line_width(3); c.stroke()
        circle(c, 0, 0, 64); fill_stroke(c, RUST, INK, 5)
        c.new_path(); c.arc(-14, -16, 40, math.pi * 1.05, math.pi * 1.55); c.set_source_rgba(1, 1, 1, 0.35); c.set_line_width(7); c.stroke()
        c.restore()
    if bl > 0.02:
        for k in range(6):
            faded(c, 0.3 * bl, lambda k=k: cone(Az * math.sin(TAU * k / 6 + 0.4)))
        faded(c, 1 - 0.6 * bl, lambda: cone(z))
    else:
        cone(z)
    # port + feet
    rrect(c, -110, 330, 220, 40, 20); fill_stroke(c, NIGHT, INK, 5)
    for fx in (-200, 160):
        rrect(c, fx, 428, 40, 22, 6); fill_stroke(c, INK, None)
    c.restore()

def sound_arcs(c, cx, cy, t, k=1.0, speed=0.7, r0=290, r1=520, sides=(0, math.pi), col=YEL):
    if k <= 0.01: return
    for i in range(3):
        ph = (t * speed + i / 3) % 1
        r = lerp(r0, r1, ph); a = k * math.sin(ph * math.pi) * 0.9
        for base in sides:
            c.new_path(); c.arc(cx, cy, r, base - 0.5, base + 0.5)
            c.set_source_rgba(*alpha(col, a)); c.set_line_width(12); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()

# ---------------------------------------------------------------- speaker, side cut-away
# local coords: axis y=0, cone opens towards +x; magnet gap ~x -100..-30
def lead_pts(d):
    pts = [(-340, -300), (100, -300)]
    x1, y1 = 140 + d, -175
    for i in range(1, 9):
        u = i / 8
        pts.append(((1 - u) ** 2 * 100 + 2 * u * (1 - u) * 80 + u * u * x1, (1 - u) ** 2 * -300 + 2 * u * (1 - u) * -210 + u * u * y1))
    pts += [(40 + d, -80), (-30 + d, -66)]
    return pts

def spk_cut(c, ox, oy, s, d=0.0, hl=(), mag=1.0, coil_n=1.0, poles=0.0, cur=0.0, cur_D=0.0, blur=0.0, blurA=30, t=0.0,
            cone_glow=0.0, lead=True, smear=0.0):
    c.save(); c.translate(ox, oy); c.scale(s, s)
    # basket (fixed)
    for sg in (-1, 1):
        line(c, [(-50, sg * 196), (322, sg * 380)], INK, 20); line(c, [(-50, sg * 196), (322, sg * 380)], METAL, 10)
        rrect(c, 314, sg * 380 - 34, 22, 68, 6); fill_stroke(c, METAL, INK, 5)
    # magnet assembly (fixed, can slide in)
    def magnet():
        if "mag" in hl:
            glow(c, -150, 0, 300, YEL, 0.45)
        rrect(c, -252, -202, 44, 404, 8); fill_stroke(c, METAL, INK, 6)
        rrect(c, -214, -42, 246, 84, 10); fill_stroke(c, METAL, INK, 6)
        for sg in (-1, 1):
            y0 = -200 if sg < 0 else 80
            c.new_path(); c.rectangle(-210, y0, 60, 120); fill_stroke(c, STEEL, None)
            c.new_path(); c.rectangle(-150, y0, 60, 120); fill_stroke(c, RED, None)
            c.new_path(); c.rectangle(-210, y0, 120, 120); fill_stroke(c, None, YEL if "mag" in hl else INK, 9 if "mag" in hl else 6)
            text(c, "S", -180, y0 + 76, 46, WHITE, SLAB, False)
            text(c, "N", -120, y0 + 76, 46, WHITE, SLAB, False)
            rrect(c, -90, -200 if sg < 0 else 68, 40, 132, 6); fill_stroke(c, METAL, INK, 6)
        line(c, [(-246, -190), (-216, -190)], alpha(WHITE, 0.3), 5)
    if mag > 0.01:
        c.save(); c.translate(-180 * (1 - ease(mag)), 0); faded(c, clamp(mag * 1.5), magnet); c.restore()

    def moving(dd, full=True):
        for sg in (-1, 1):  # coil former
            line(c, [(-100 + dd, sg * 58), (34 + dd, sg * 62)], INK, 12); line(c, [(-100 + dd, sg * 58), (34 + dd, sg * 62)], CREAM2, 6)
            pts = []
            for i in range(9):  # spider
                u = i / 8
                pts.append((4 + dd * (1 - u) + (8 if i % 2 else -8), sg * (64 + u * 156)))
            line(c, pts, alpha(hx("#D8C79A"), 0.95), 6)
        if cone_glow > 0 or "cone" in hl:
            k = max(cone_glow, 1.0 if "cone" in hl else 0)
            for sg in (-1, 1): line(c, [(30 + dd, sg * 62), (300 + dd, sg * 342)], alpha(YEL, 0.45 * k), 44)
        for sg in (-1, 1):  # cone + surround
            line(c, [(30 + dd, sg * 62), (300 + dd, sg * 342)], INK, 28)
            line(c, [(30 + dd, sg * 62), (300 + dd, sg * 342)], ORANGE2, 16)
            line(c, [(40 + dd, sg * 66 - 3), (290 + dd, sg * 332 - 3)], alpha(WHITE, 0.25), 4)
            c.new_path(); c.arc(306 + dd * 0.5, sg * 360, 20, -math.pi / 2 - 1.2, -math.pi / 2 + 1.2) if sg < 0 else c.arc(306 + dd * 0.5, sg * 360, 20, math.pi / 2 - 1.2, math.pi / 2 + 1.2)
            c.set_source_rgba(*INK); c.set_line_width(12); c.stroke_preserve(); c.set_source_rgba(*DARK); c.set_line_width(6); c.stroke()
        c.new_path(); c.move_to(30 + dd, -62); c.curve_to(98 + dd, -52, 98 + dd, 52, 30 + dd, 62); c.close_path()
        fill_stroke(c, CONE, INK, 6)
        # coil
        if coil_n > 0.01:
            if "coil" in hl: glow(c, -64 + dd, 0, 160, YEL, 0.6)
            if cur > 0: glow(c, -64 + dd, 0, 130, YEL, 0.55 * cur)
            c.save(); rrect(c, -102 + dd, -66, 74, 132, 10); c.clip()
            c.set_source_rgba(*alpha(COPPER, clamp(coil_n * 3))); c.paint()
            n = int(11 * coil_n + 0.999)
            for i in range(n):
                x = -102 + dd + i * 7
                line(c, [(x, -70), (x + 6, 70)], alpha(COPPER_D, 0.9), 3)
            if abs(poles) > 0.02:
                fa = RED if poles > 0 else STEEL; ba = STEEL if poles > 0 else RED
                c.new_path(); c.rectangle(-65 + dd, -70, 40, 140); c.set_source_rgba(*alpha(fa, 0.8 * abs(poles))); c.fill()
                c.new_path(); c.rectangle(-105 + dd, -70, 40, 140); c.set_source_rgba(*alpha(ba, 0.8 * abs(poles))); c.fill()
            c.restore()
            rrect(c, -102 + dd, -66, 74, 132, 10); fill_stroke(c, None, YEL if "coil" in hl else INK, 7 if "coil" in hl else 5)
            if abs(poles) > 0.3:
                text(c, "N" if poles > 0 else "S", -46 + dd, 14, 38, WHITE, SLAB, False, outline=INK, olw=6)
                text(c, "S" if poles > 0 else "N", -84 + dd, 14, 38, WHITE, SLAB, False, outline=INK, olw=6)
        if lead:
            P = lead_pts(dd)
            line(c, P, INK, 13); line(c, P, COPPER, 7)
            if cur > 0 and full: charges(c, P, cur_D, 40, 7, cur, smear)
    if blur > 0.02:
        for k in range(6):
            faded(c, 0.3 * blur, lambda k=k: moving(blurA * math.sin(TAU * k / 6 + 0.4), False))
        faded(c, 1 - 0.55 * blur, lambda: moving(d))
    else:
        moving(d)
    c.restore()

def cut_pt(ox, oy, s, x, y): return ox + x * s, oy + y * s

# ---------------------------------------------------------------- air (longitudinal wave as dots)
def air_field(c, x0, x1, y0, y1, phi, lam, A, front=None, blur=0.0, a=1.0, sp=24, rev=False, t=0.0, rmax=None, hl=0.0):
    if a <= 0.01: return
    k = TAU / lam
    ny = int((y1 - y0) / sp) + 1; nx = int((x1 - x0) / sp) + 1
    for j in range(ny):
        for i in range(nx):
            jx = 6 * math.sin(i * 12.9898 + j * 78.233); jy = 6 * math.sin(i * 39.34 + j * 11.7)
            xr = x0 + i * sp + (sp / 2 if j % 2 else 0) + jx; yr = y0 + j * sp + jy
            if xr > x1: continue
            dist = (x1 - xr) if rev else (xr - x0)
            env = 1.0 if front is None else clamp((front - dist) / 40)
            th = phi - k * dist
            u = A * math.sin(th) * env * (1 - blur); comp = math.cos(th) * env * (1 - blur)
            if blur > 0: u += A * 0.6 * blur * math.sin(t * 61 + i * 2.3 + j * 1.7)
            x = xr - u if rev else xr + u
            col = mix(LAV, YEL, clamp(0.5 + 0.5 * comp)) if comp > 0 else mix(LAV, STEEL, clamp(-comp * 0.8))
            r = 5.5 + 2.4 * comp
            circle(c, x, yr, r); c.set_source_rgba(*alpha(col, a * (0.55 + 0.4 * max(comp, 0)) + hl * 0.3)); c.fill()

def comp_x(phi, lam, x0, x1, which=0.0, rev=False):
    """x of a compression (which=0) or rarefaction (which=pi) zone inside [x0,x1]."""
    k = TAU / lam
    for n in range(-50, 50):
        dist = (phi - which - TAU * n) / k
        if 0.25 * lam <= dist <= (x1 - x0) - 0.15 * lam:
            return (x1 - dist) if rev else (x0 + dist)
    return (x0 + x1) / 2

# ---------------------------------------------------------------- ear (side cut) and face
def ear(c, ex, ey, s=1.0, u=0.0, hl=(), t=0.0):
    c.save(); c.translate(ex, ey); c.scale(s, s)
    rrect(c, 0, -200, 420, 400, 70); fill_stroke(c, SKIN, INK, 6)
    # canal
    rrect(c, -6, -26, 126, 52, 10); fill_stroke(c, hx("#7E3A34"), INK, 5)
    # cochlea
    c.new_path()
    for i in range(60):
        a = i * 0.2; r = 30 - i * 0.42
        (c.move_to if i == 0 else c.line_to)(185 + r * math.cos(a), 10 + r * math.sin(a))
    c.set_source_rgba(*alpha(SKIN_D, 0.9)); c.set_line_width(8); c.stroke()
    line(c, [(150, -10), (130, -6)], SKIN_D, 8)
    # pinna (flap that collects the sound)
    c.new_path(); c.move_to(10, -170); c.curve_to(-80, -190, -105, -60, -40, -34); c.line_to(4, -30); c.close_path(); fill_stroke(c, SKIN, INK, 6)
    c.new_path(); c.move_to(10, 30); c.curve_to(-50, 40, -70, 110, -10, 130); c.line_to(10, 120); c.close_path(); fill_stroke(c, SKIN, INK, 6)
    c.new_path(); c.move_to(-4, -150); c.curve_to(-60, -150, -70, -80, -34, -60); c.set_source_rgba(*SKIN_D); c.set_line_width(6); c.stroke()
    # eardrum
    if "drum" in hl: glow(c, 118, 0, 80, YEL, 0.6)
    c.new_path(); c.move_to(118, -34); c.curve_to(118 + 2.2 * u, -14, 118 + 2.2 * u, 14, 118, 34)
    c.set_source_rgba(*INK); c.set_line_width(13); c.stroke_preserve(); c.set_source_rgba(*(YEL if "drum" in hl else CREAM)); c.set_line_width(7); c.stroke()
    if "ear" in hl:
        rrect(c, 0, -200, 420, 400, 70); c.set_source_rgba(*alpha(YEL, 0.9)); c.set_line_width(8); c.stroke()
    c.restore()

def face(c, x, y, mouth=0.0):
    """Profile facing left; mouth at (x, y)."""
    c.new_path(); c.move_to(x + 60, y - 330); c.curve_to(x - 10, y - 300, x - 20, y - 220, x - 10, y - 150)
    c.line_to(x - 60, y - 60); c.line_to(x - 8, y - 38); c.curve_to(x - 30, y - 24, x - 26, y - 12, x - 14, y - 8 - 12 * mouth)
    c.line_to(x + 10, y - 6 - 10 * mouth); c.line_to(x + 10, y + 8 + 10 * mouth); c.line_to(x - 14, y + 10 + 14 * mouth)
    c.curve_to(x - 26, y + 30 + 14 * mouth, x - 22, y + 60, x - 6, y + 90)
    c.curve_to(x + 20, y + 130, x + 60, y + 130, x + 80, y + 170); c.line_to(x + 90, y + 900); c.line_to(x + 400, y + 900)
    c.line_to(x + 400, y - 330); c.close_path(); fill_stroke(c, SKIN, INK, 7)
    c.new_path(); c.move_to(x + 60, y - 330); c.curve_to(x + 10, y - 330, x + 0, y - 260, x + 30, y - 220)
    c.curve_to(x + 120, y - 230, x + 160, y - 220, x + 400, y - 230); c.line_to(x + 400, y - 360); c.line_to(x + 60, y - 360); c.close_path()
    fill_stroke(c, hx("#3A2A33"), INK, 6)
    circle(c, x + 40, y - 150, 11); fill_stroke(c, INK, None)
    line(c, [(x + 22, y - 178), (x + 58, y - 182)], INK, 6)
    if mouth > 0.05:
        c.save(); c.translate(x - 6, y + 2); c.scale(0.5, 1); circle(c, 0, 0, 14 * mouth + 2); c.restore(); fill_stroke(c, hx("#5A1E22"), None)

# ================================================================ scenes
FRONT_Y = 1110; WOOF = (540, FRONT_Y + 90)
# side cut-away layouts
P2 = (450, 1190, 1.1)      # paso2 / freno reveal
P3 = (270, 1130, 0.8)      # paso3 (air in front)
PJ = (320, 1130, 0.72)     # junto / acelera / remate

def scene_front(c, t):
    background(c, t, ORANGE)
    tb = B("imposible")["start"]; tf = B("freno")["start"]
    tc = wt("imposible", "cuerdas")
    up = ease(ramp(t, tc - 0.6, tc - 0.05)) * (1 - ease(ramp(t, tf - 0.3, tf + 0.4)))
    zoom = ease(ramp(t, tf, T_SLOW + 0.2))
    xk = ease(ramp(t, T_SLOW - 0.7, T_SLOW + 0.4))
    push = 1 + 0.05 * ease(ramp(t, 0, tb))
    fv = fvid(t, 440); bl = blur_of(fv)
    ph = TAU * 440 * anim_time(t)
    def front():
        c.save(); cam(c, push * lerp(1, 0.8, up) * (1 + 1.7 * zoom), WOOF[0], WOOF[1]); c.translate(0, -230 * up)
        c.set_source_rgba(*hx("#3B364B")); c.rectangle(-400, FRONT_Y + 450, W + 800, 26); c.fill()
        c.set_source_rgba(*hx("#4A3B4A")); c.rectangle(-400, FRONT_Y + 476, W + 800, 600); c.fill()
        for i in range(6): c.set_source_rgba(1, 1, 1, 0.04); c.rectangle(-400, FRONT_Y + 500 + i * 40, W + 800, 4); c.fill()
        sound_arcs(c, WOOF[0], WOOF[1], t, (1 - zoom), 0.7 * (1 - zoom) + 0.05)
        tn = wt("gancho", "empuja")
        spk_front(c, 540, FRONT_Y, 1.0, 14 * math.sin(ph), bl, 14, t, glow_k=pulse_at(t, tn - 0.1, 1.0))
        c.restore()
    front_a = 1 - xk
    if front_a > 0.01:
        c.push_group(); front()
        # gancho extras: note LA + brain
        k1 = eob(ramp(t, wt("gancho", "nota") - 0.1, wt("gancho", "nota") + 0.25)) * (1 - ease(ramp(t, tc - 0.8, tc - 0.3)))
        if k1 > 0.02:
            bob = 10 * math.sin(t * 2.5)
            c.save(); c.translate(870, 760 + bob); c.scale(k1, k1); music_note(c, -55, 40, 0.75); c.restore()
            if k1 > 0.5: pill(c, "LA", 870, 830 + bob, 34, INK, YEL, clamp(k1))
        k2 = eob(ramp(t, wt("gancho", "cerebro") - 0.1, wt("gancho", "cerebro") + 0.25)) * (1 - ease(ramp(t, tc - 0.8, tc - 0.3)))
        if k2 > 0.02:
            c.save(); c.translate(185, 780 + 8 * math.sin(t * 2 + 1)); c.scale(k2, k2); brain(c, 0, 0, 1.1); c.restore()
        # imposible: crossed badges
        if up > 0.01:
            for (w, x, lab, fn) in (("cuerdas", 230, "CUERDAS", ic_guitar), ("teclas", 540, "TECLAS", ic_piano), ("boquilla", 850, "BOQUILLA", ic_mouthpiece)):
                t0 = wt("imposible", w) - 0.15
                k = eob(ramp(t, t0, t0 + 0.3)) * up
                icon_badge(c, x, 1470, k, lab, fn, t, t0 + 0.4, r=100)
            for (w, x, y, lab) in (("guitarra", 175, 760, "GUITARRA"), ("piano", 870, 830, "PIANO"), ("cantante", 175, 980, "VOZ")):
                t0 = wt("imposible", w) - 0.1
                k = eob(ramp(t, t0, t0 + 0.3)) * up
                if k > 0.02:
                    c.save(); c.translate(x, y + 6 * math.sin(t * 3 + x)); c.scale(k, k); pill(c, lab, 0, 0, 30, INK, YEL); c.restore()
        c.pop_group_to_source(); c.paint_with_alpha(front_a)
    if xk > 0.01:
        c.push_group()
        ox, oy, s = P2
        c.save(); cam(c, lerp(1.35, 1.0, xk), 560, 1190)
        spk_cut(c, ox, oy, s, 0, (), 1.0, 1.0, t=t)
        c.restore()
        c.pop_group_to_source(); c.paint_with_alpha(xk)

def scene_paso1(c, t):
    background(c, t, YEL)
    t_cab = wt("paso1", "cable"); t_el = wt("paso1", "electricidad"); t_cor = wt("paso1", "corriente"); t_fija = wt("paso1", "fija")
    t_cam = wt("paso1", "cambia"); t_sen = wt("paso1", "sentido"); t_can = wt("paso1", "canción"); t_al = wt("paso1", "altavoz")
    cy = 880
    ox, oy, s = 775, cy + 300 * 0.5, 0.5
    m = ease(ramp(t, t_cam - 0.2, t_cam + 0.5))
    def dc(tt): return 0.75 * ease(ramp(tt, t_cor - 0.2, t_cor + 0.3))
    drift = 150 * 0.75 * max(0.0, t - t_cor)
    D = (1 - m) * drift + m * (150 * 0.75 * max(0.0, t_cam - t_cor) + 70 * d_song(phi1(t)))
    cur_now = (1 - m) * dc(t) + m * i_song(phi1(t))
    on = ease(ramp(t, t_el - 0.2, t_el + 0.4))
    # mini speaker on the right
    ks = eob(ramp(t, t_al - 0.6, t_al - 0.2))
    if ks > 0.01:
        c.save(); c.translate(ox, oy); c.scale(ks, ks); c.translate(-ox, -oy)
        spk_cut(c, ox, oy, s, 6 * m * math.sin(phi1(t)), hl=(), cur=on, cur_D=D * 2, t=t)
        c.restore()
    # cable
    rx = lerp(-40, ox - 340 * s, ease(ramp(t, t_al - 0.3, t_cab + 0.2)))
    if rx > -30:
        rrect(c, -40, cy - 38, rx + 40, 76, 30); fill_stroke(c, hx("#3A3550"), INK, 7)
        rrect(c, -40, cy - 16, rx + 40 + 10, 32, 12); fill_stroke(c, COPPER, INK, 4)
        line(c, [(-40, cy - 28), (rx - 20, cy - 28)], alpha(WHITE, 0.18), 6)
        if on > 0:
            glow(c, rx * 0.5, cy, 360, YEL, 0.18 * on)
            c.save(); c.rectangle(-40, cy - 20, rx + 40, 40); c.clip()
            charges(c, [(-60, cy), (rx + 10, cy)], D, 40, 9, on)
            c.restore()
    # lightning badge on "electricidad"
    kz = eob(ramp(t, t_el - 0.1, t_el + 0.25)) * (1 - ramp(t, t_cor - 0.5, t_cor - 0.2))
    if kz > 0.02:
        c.save(); c.translate(150, 750); c.scale(kz, kz)
        circle(c, 0, 0, 62); fill_stroke(c, CREAM, INK, 6)
        c.new_path(); c.move_to(10, -48); c.line_to(-26, 6); c.line_to(0, 6); c.line_to(-10, 48); c.line_to(28, -10); c.line_to(2, -10); c.close_path()
        fill_stroke(c, YEL, INK, 5); c.restore()
    # direction arrow above cable
    ka = ramp(t, t_cor - 0.2, t_cor + 0.2)
    if ka > 0:
        L = 210 * cur_now * ka
        ax = 300
        if abs(L) > 12: arrow(c, ax - L * 0.5, cy - 110, ax + L * 0.5, cy - 110, YEL, 16, 44)
        if t >= t_sen - 0.1 and abs(cur_now) > 0.25:
            lab = "ADELANTE" if cur_now > 0 else "ATRÁS"
            text(c, lab, ax, cy - 160, 40, YEL, SLAB, False, outline=INK, olw=8)
    # "FIJA" crossed out
    kf = eob(ramp(t, t_fija - 0.1, t_fija + 0.25)) * (1 - ease(ramp(t, t_cam + 0.6, t_cam + 1.0)))
    if kf > 0.02:
        pill(c, "FIJA", 620, cy - 150, 40, INK, CREAM, kf)
        xmark(c, 620, cy - 150, 52 * kf, t, t_fija + 0.35, 12)
    co(c, "CORRIENTE", 200, cy + 20, 250, cy + 170, t, t_cor)
    # oscilloscope
    sx0, sx1, sy0, sy1 = 110, 930, 1290, 1610
    kk = eob(ramp(t, t_cor - 0.1, t_cor + 0.35))
    if kk > 0.02:
        c.save(); c.translate(520, 1450); c.scale(kk, kk); c.translate(-520, -1450)
        shadow(c, lambda: rrect(c, sx0 - 18, sy0 - 18, sx1 - sx0 + 36, sy1 - sy0 + 36, 22), 10, 14, 0.4)
        rrect(c, sx0 - 18, sy0 - 18, sx1 - sx0 + 36, sy1 - sy0 + 36, 22); fill_stroke(c, METAL, INK, 7)
        rrect(c, sx0, sy0, sx1 - sx0, sy1 - sy0, 12); fill_stroke(c, hx("#14281C"), INK, 5)
        for i in range(1, 8): line(c, [(sx0 + i * (sx1 - sx0) / 8, sy0 + 6), (sx0 + i * (sx1 - sx0) / 8, sy1 - 6)], alpha(hx("#7CFC9A"), 0.12), 2)
        ym = (sy0 + sy1) / 2; amp = (sy1 - sy0) * 0.36
        line(c, [(sx0 + 6, ym), (sx1 - 6, ym)], alpha(hx("#7CFC9A"), 0.35), 3)
        text(c, "+ ADELANTE", sx0 + 16, sy0 + 34, 22, alpha(hx("#7CFC9A"), 0.8), MONO, True, "l")
        text(c, "− ATRÁS", sx0 + 16, sy1 - 16, 22, alpha(hx("#7CFC9A"), 0.8), MONO, True, "l")
        win = 4.0; n = 180; pts = []
        for j in range(n + 1):
            ts = t - win * (1 - j / n)
            mm = ease(ramp(ts, t_cam - 0.2, t_cam + 0.5))
            v = (1 - mm) * dc(ts) + (mm * i_song(phi1(ts)) if mm > 0 else 0)
            pts.append((sx0 + 10 + (sx1 - sx0 - 40) * j / n, ym - amp * v))
        c.save(); rrect(c, sx0, sy0, sx1 - sx0, sy1 - sy0, 12); c.clip()
        line(c, pts, alpha(hx("#7CFC9A"), 0.35), 14); line(c, pts, hx("#B9FFC9"), 5)
        c.restore()
        glow(c, *pts[-1], 40, hx("#7CFC9A"), 0.8); circle(c, *pts[-1], 10); c.set_source_rgba(*WHITE); c.fill()
        c.restore()
        kn = eob(ramp(t, t_can - 0.15, t_can + 0.2))
        if kn > 0.02:
            c.save(); c.translate(860, 1250); c.scale(kn, kn); music_note(c, -50, 30, 0.55); c.restore()
    co(c, "LA FORMA DE LA CANCIÓN", 520, 1390, 420, 1215, t, t_can, YEL)

def scene_paso2(c, t):
    background(c, t, ORANGE)
    ox, oy, s = P2
    tv = wt("paso2", "vueltas"); tb = wt("paso2", "bobina"); tcn = wt("paso2", "cono"); tm = wt("paso2", "metida")
    ti = wt("paso2", "imán"); tc = wt("paso2", "corriente"); to = wt("paso2", "imán", 1); tims = wt("paso2", "imanes")
    te = wt("paso2", "empujan"); ta = wt("paso2", "atraen")
    c.save(); cam(c, 1.0 + 0.04 * ramp(t, B("paso2")["start"], B("paso2")["end"]), 450, 1190)
    coil_n = ease(ramp(t, tv - 0.2, tb + 0.1))
    mag = ramp(t, tm - 0.1, ti)
    A = ease(ramp(t, tc, tc + 1.2))
    ph = phi440(t); d = 30 * A * math.sin(ph); vel = math.cos(ph)
    cur = ease(ramp(t, tc - 0.2, tc + 0.3))
    poles = clamp(ease(ramp(t, to - 0.3, to + 0.2)) * vel * 3, -1, 1)
    hl = set()
    if tb - 0.1 <= t < tb + 1.6: hl.add("coil")
    if ti - 0.1 <= t < ti + 1.6: hl.add("mag")
    if tcn - 0.1 <= t < tcn + 1.4: hl.add("cone")
    # stub of the incoming cable
    lx, ly = cut_pt(ox, oy, s, -340, -300)
    line(c, [(-30, ly), (lx, ly)], INK, 30); line(c, [(-30, ly), (lx, ly)], hx("#3A3550"), 20); line(c, [(-30, ly), (lx, ly)], COPPER, 8)
    if cur > 0:
        c.save(); c.rectangle(-30, ly - 20, lx + 30, 40); c.clip(); charges(c, [(-60, ly), (lx, ly)], 60 * math.sin(ph) * A + 40 * (1 - A) * t, 40, 7, cur); c.restore()
    spk_cut(c, ox, oy, s, d, hl, mag, coil_n, poles, cur, 60 * math.sin(ph) * A, t=t)
    if t >= to - 0.3:  # field loops around the coil-magnet
        kf = ease(ramp(t, to - 0.3, to + 0.4)) * abs(vel)
        cx, cy = cut_pt(ox, oy, s, -64 + d, 0)
        for r in (1.0, 1.5):
            for sg in (-1, 1):
                c.save(); c.translate(cx, cy + sg * 80 * s * r); c.scale(1.6, 0.6); c.new_path(); c.arc(0, 0, 70 * r * s, 0, TAU); c.restore()
                c.set_source_rgba(*alpha(YEL, 0.5 * kf)); c.set_line_width(4); c.set_dash([12, 10]); c.stroke(); c.set_dash([])
    c.restore()
    kx = lambda x, y: cut_pt(ox, oy, s, x, y)
    co(c, "BOBINA", *kx(-64, -60), 250, 665, t, tb, YEL, t1=tims - 0.4)
    co(c, "CONO", *kx(180, -210), 760, 665, t, tcn, CREAM, t1=tims - 0.4)
    co(c, "IMÁN", *kx(-150, 140), 200, 1650, t, ti, CREAM)
    co(c, "OTRO IMÁN", *kx(-64, 60), 600, 1650, t, to, YEL)
    # inset: two magnets push or pull
    k = eob(ramp(t, tims - 0.2, tims + 0.2))
    if k > 0.02:
        c.save(); c.translate(540, 700); c.scale(k, k)
        rrect(c, -330, -80, 660, 160, 22); fill_stroke(c, CREAM, INK, 6)
        flip = ease(ramp(t, ta - 0.25, ta + 0.05))
        sep = lerp(70, 30, flip) + (10 * math.sin(t * 9) if t >= te else 0)
        def bar(x, left_col, right_col, lt, rt):
            c.new_path(); c.rectangle(x - 80, -30, 80, 60); fill_stroke(c, left_col, None)
            c.new_path(); c.rectangle(x, -30, 80, 60); fill_stroke(c, right_col, None)
            c.new_path(); c.rectangle(x - 80, -30, 160, 60); fill_stroke(c, None, INK, 5)
            text(c, lt, x - 40, 14, 36, WHITE, SLAB, False); text(c, rt, x + 40, 14, 36, WHITE, SLAB, False)
        bar(-150 - sep, STEEL, RED, "S", "N")
        if flip < 0.5: bar(-150 + 160 + sep - 160 + 160, RED, STEEL, "N", "S")
        else: bar(-150 + 160 + sep - 160 + 160, STEEL, RED, "S", "N")
        mid = -150 + 80 - sep / 2 + sep / 2
        if t >= te - 0.1:
            if flip < 0.5:
                arrow(c, -150 - sep - 90, 0, -150 - sep - 150, 0, HOT, 10, 26); arrow(c, 170 + sep - 160 + 160 - 70, 0, 170 + sep + 40, 0, HOT, 10, 26)
                lab, col = "SE EMPUJAN", HOT
            else:
                lab, col = "SE ATRAEN", GREEN
                arrow(c, -320 + 40, -55, -230, -55, GREEN, 8, 22); arrow(c, 300, -55, 230, -55, GREEN, 8, 22)
            text(c, lab, 215 + 10, 12, 30, col, SLAB, False) if False else None
            text(c, lab, 0, -42, 28, col, SLAB, False)
        c.restore()

def scene_paso3(c, t):
    background(c, t, YEL)
    ox, oy, s = P3
    tco = wt("paso3", "corriente"); tcn = wt("paso3", "cono"); tg = wt("paso3", "golpea"); tai = wt("paso3", "aire")
    tap = wt("paso3", "aprieta"); tes = wt("paso3", "estira"); tem = wt("paso3", "empuja")
    c.save(); cam(c, 1.0 + 0.04 * ramp(t, B("paso3")["start"], B("paso3")["end"]), 540, 1130)
    ph = phi440(t); d = 30 * math.sin(ph); vel = math.cos(ph)
    lam = 230; Apx = 17
    x0 = ox + 300 * s + 22; x1 = 935
    front = max(0.0, (t - tem) * lam * fvid(t, 440) - 0.0) if t > tem else 0.0
    front = 1e9 if t > tem + 8 else front
    air_a = 0.5 + 0.5 * ease(ramp(t, tai - 0.3, tai + 0.2))
    air_field(c, x0, x1, oy - 340 * s + 10, oy + 340 * s - 10, ph + 0.0, lam, Apx, front if t > tem else 0.0, 0.0, air_a, 24, t=t,
              hl=pulse_at(t, tai, 0.8))
    # coil + cone
    hl = set()
    if tcn - 0.1 <= t < tcn + 1.2: hl.add("cone")
    cg = pulse_at(t, tg - 0.1, 0.8)
    lx, ly = cut_pt(ox, oy, s, -340, -300)
    line(c, [(-30, ly), (lx, ly)], INK, 26); line(c, [(-30, ly), (lx, ly)], COPPER, 8)
    poles = clamp(vel * 3, -1, 1)
    spk_cut(c, ox, oy, s, d, hl, 1.0, 1.0, poles, 1.0, 50 * math.sin(ph), t=t, cone_glow=cg)
    c.restore()
    # motion label
    km = ramp(t, tem - 0.3, tem)
    if km > 0 and abs(vel) > 0.2:
        a = clamp((abs(vel) - 0.2) * 3) * km
        if vel > 0:
            faded(c, a, lambda: (arrow(c, 120, 1600, 330, 1600, YEL, 16, 44), text(c, "EMPUJA", 225, 1560, 44, YEL, SLAB, False, outline=INK, olw=8)))
        else:
            faded(c, a, lambda: (arrow(c, 330, 1600, 120, 1600, COLD, 16, 44), text(c, "TIRA", 225, 1560, 44, COLD, SLAB, False, outline=INK, olw=8)))
    # current-direction hint on "corriente cambia de sentido"
    co(c, "CORRIENTE", *cut_pt(ox, oy, s, -250, -300), 200, 665, t, tco, CREAM, t1=tcn - 0.4)
    co(c, "CONO", *cut_pt(ox, oy, s, 180, -230), 400, 665, t, tcn)
    co(c, "AIRE", 760, oy - 200, 800, 665, t, tai, CREAM)
    for lab, which, t0, col in (("APRIETA", 0.0, tap, YEL), ("ESTIRA", math.pi, tes, LAV)):
        if t >= t0:
            xx = comp_x(ph, lam, x0, x1, which)
            yy = 1555 if which == 0 else 1645
            co(c, lab, xx, oy + 340 * s - 20, clamp(xx, 560, 860), yy, t, t0, col)

def scene_paso4(c, t):
    background(c, t, STEEL)
    tap = wt("paso4", "apretones"); tond = wt("paso4", "ondas"); toi = wt("paso4", "oído"); ttim = wt("paso4", "tímpano")
    tig = wt("paso4", "igual"); trap = wt("paso4", "rápido"); tag = wt("paso4", "agudo"); tgr = wt("paso4", "grande"); tfu = wt("paso4", "fuerte")
    tv1 = wt("paso4", "veinte"); tv2 = wt("paso4", "veinte", 1); tmil = wt("paso4", "mil"); t0s = B("paso4")["start"] - 0.25
    gk = ease(ramp(t, trap - 0.7, trap - 0.1))
    dy = 230 * (1 - gk)
    ox, oy, s = 190, 860 + dy, 0.5
    ph = phi440(t); d = 30 * math.sin(ph)
    lam = 300; Apx = 19
    x0 = ox + 300 * s + 18; x1 = 760
    v = lam * fvid(t, 440)
    front = (t - t0s) * v
    air_field(c, x0, x1, oy - 160, oy + 160, ph, lam, Apx, front, 0.0, 1.0, 24, t=t)
    spk_cut(c, ox, oy, s, d, ("cone",) if tig <= t < tig + 1.5 else (), 1.0, 1.0, clamp(math.cos(ph) * 3, -1, 1), 1.0, 50 * math.sin(ph), t=t)
    lx, ly = cut_pt(ox, oy, s, -340, -300)
    line(c, [(-30, ly), (lx, ly)], INK, 18); line(c, [(-30, ly), (lx, ly)], COPPER, 6)
    ex = 775; xe = 775 + 118
    dist_e = xe - x0
    ue = Apx * 1.1 * math.sin(ph - TAU / lam * dist_e) * clamp((front - dist_e) / 40)
    hl = set()
    if t >= ttim - 0.1: hl.add("drum")
    if toi - 0.1 <= t < toi + 1.0: hl.add("ear")
    ear(c, ex, oy, 1.0, ue, hl, t)
    if tig <= t < tig + 1.6:
        k = pulse_at(t, tig, 1.6)
        for (px, py) in ((ox + 60 * s + d * s, oy), (xe, oy)):
            arrow(c, px - 10, py - 210 - 0, px + 50, py - 210, alpha(YEL, k), 8, 22); arrow(c, px + 30, py - 230 + 40, px - 30, py - 190, alpha(YEL, k), 8, 22)
        text(c, "=", (ox + xe) / 2 + 40, oy - 190, 70, alpha(YEL, k), SLAB, False, outline=alpha(INK, k), olw=8)
    xc = comp_x(ph, lam, x0, min(x1, x0 + front), 0.0) if front > lam * 0.5 else x0 + 40
    co(c, "APRETONES", xc, oy - 120, 300, 655, t, tap, YEL)
    co(c, "OÍDO", ex + 60, oy - 160, 870, 655, t, toi)
    co(c, "TÍMPANO", xe, oy - 30, 640, 655, t, ttim, YEL)
    # comparison panels
    for (px, title, sub, tA, tB, col, lamH, ampH) in ((110, "MÁS RÁPIDO", "MÁS AGUDO", trap, tag, YEL, 55, 38), (545, "MÁS GRANDE", "MÁS FUERTE", tgr, tfu, HOT, 110, 72)):
        k = eob(ramp(t, tA - 0.2, tA + 0.2))
        if k <= 0.02: continue
        pw, ph_ = 395, 330; py = 1080
        c.save(); c.translate(px + pw / 2, py + ph_ / 2); c.scale(k, k); c.translate(-(px + pw / 2), -(py + ph_ / 2))
        shadow(c, lambda: rrect(c, px, py, pw, ph_, 20), 8, 10, 0.4)
        rrect(c, px, py, pw, ph_, 20); fill_stroke(c, NIGHT, CREAM, 5)
        text(c, title, px + pw / 2, py + 48, 32, CREAM, SLAB, False)
        c.save(); rrect(c, px, py, pw, ph_, 20); c.clip()
        wave(c, px + 20, px + pw - 20, py + 180, 38, 110, -t * 2.2, alpha(LAV, 0.45), 5)
        kb = ramp(t, tB - 0.3, tB + 0.2)
        if kb > 0: wave(c, px + 20, px + pw - 20, py + 180, lerp(38, ampH, kb), lerp(110, lamH, kb), -t * 2.2 * (110 / lerp(110, lamH, kb)), col, 8)
        c.restore()
        if kb > 0: text(c, sub, px + pw / 2, py + ph_ - 26, 40, col, SLAB, False, outline=INK, olw=8)
        c.restore()
    # hearing range bar
    kr = ramp(t, tv1 - 0.6, tv1 - 0.1)
    if kr > 0:
        bx0, bx1, by = 130, 900, 1520
        def fx(f): return bx0 + (bx1 - bx0) * (math.log10(f) - math.log10(20)) / 3
        faded(c, kr, lambda: text(c, "VIBRACIONES POR SEGUNDO QUE OYES", 515, by - 40, 28, CREAM, SANS, True))
        fill = ease(ramp(t, tv1, tv2 + 0.3))
        rrect(c, bx0 - 8, by - 8, bx1 - bx0 + 16, 56, 28); fill_stroke(c, alpha(NIGHT, kr), alpha(INK, kr), 5)
        if fill > 0:
            g = cairo.LinearGradient(bx0, 0, bx1, 0); g.add_color_stop_rgba(0, *GOLD); g.add_color_stop_rgba(0.5, *ORANGE); g.add_color_stop_rgba(1, *YEL)
            rrect(c, bx0, by, (bx1 - bx0) * fill, 40, 20); c.set_source(g); c.fill()
        kl = eob(ramp(t, tv1 - 0.1, tv1 + 0.2))
        if kl > 0.02: text(c, "20", bx0, by + 92, 36 * kl, CREAM, SLAB, False, outline=INK, olw=6)
        kh = eob(ramp(t, tv2 - 0.1, tv2 + 0.2))
        if kh > 0.02: text(c, "20.000", bx1 - 20, by + 92, 36 * kh, CREAM, SLAB, False, outline=INK, olw=6)
        kL = eob(ramp(t, tmil - 0.05, tmil + 0.3))
        if kL > 0.02:
            x = fx(440)
            c.save(); c.translate(x, by + 20); c.scale(kL, kL)
            line(c, [(0, -40), (0, 40)], INK, 14); line(c, [(0, -36), (0, 36)], RED, 7)
            circle(c, 0, -46, 14); fill_stroke(c, RED, INK, 5)
            c.restore()
            pill(c, "440 · LA", x, by + 82, 30, INK, YEL, kL)

def scene_paso5(c, t):
    background(c, t, ORANGE2)
    tgv = wt("paso5", "graves"); ten = wt("paso5", "enormes"); tlen = wt("paso5", "lento"); tmo = wt("paso5", "mover")
    tai = wt("paso5", "aire"); tcn = wt("paso5", "cono"); tgo = wt("paso5", "golpe")
    # small speaker (agudos)
    tx, ty, ts_ = 210, 745, 0.36
    pt = TAU * 4400 * (AT(t) - AT(tmo)); fvt = fvid(t, 4400)
    air_field(c, tx + 300 * ts_ + 14, 935, ty - 100, ty + 100, pt, 70, 4, None, blur_of(fvt, 8), 0.8, 20, t=t)
    spk_cut(c, tx, ty, ts_, 6 * math.sin(pt), (), 1.0, 1.0, 0, 0, t=t, lead=False)
    pill(c, "AGUDOS · CONO PEQUEÑO", 640, 632, 26, INK, CREAM, eob(ramp(t, B("paso5")["start"] - 0.1, B("paso5")["start"] + 0.3)), SANS, True)
    # big woofer (graves)
    pulse = 1 + 0.05 * pulse_at(t, ten - 0.1, 0.7)
    ox, oy, s = 320, 1265, 0.85 * pulse
    pb = TAU * 110 * (AT(t) - AT(tmo)); d = 48 * math.sin(pb); vel = math.cos(pb)
    x0 = ox + 300 * s + 20; x1 = 935
    air_field(c, x0, x1, oy - 320, oy + 320, pb, 900, 48 * s, None, 0.0, 0.9, 26, t=t, hl=0.0)
    spk_cut(c, ox, oy, s, d, ("cone",) if tcn - 0.1 <= t < tcn + 1.4 else (), 1.0, 1.0, clamp(vel * 3, -1, 1), 0, t=t, lead=False)
    ka = ease(ramp(t, tmo - 0.3, tmo + 0.2))
    if ka > 0 and vel > 0.05:
        for j, yy in enumerate((oy - 200, oy, oy + 200)):
            Lr = 200 * vel * ka
            xx = x0 + 30 + ((t * 0.5 + j * 0.3) % 1) * 40
            arrow(c, xx, yy, xx + Lr, yy, alpha(YEL, 0.9), 26, 62)
    co(c, "GRAVES", *cut_pt(ox, oy, s, 200, -260), 780, 900, t, tgv, YEL)
    kl = eob(ramp(t, tlen - 0.15, tlen + 0.2))
    if kl > 0.02: pill(c, "LENTO: 110 / SEG", 300, 1660, 30, INK, CREAM, kl, SANS, True)
    if t >= tai - 0.2:
        k = eob(ramp(t, tai - 0.2, tai + 0.2))
        c.save(); c.translate(780, oy + 10); c.scale(k, k); c.rotate(-0.05)
        text(c, "MUCHO", 0, -10, 62, WHITE, SLAB, False, outline=INK, olw=12)
        text(c, "AIRE", 0, 60, 62, YEL, SLAB, False, outline=INK, olw=12)
        c.restore()
    co(c, "CONO GRANDE", *cut_pt(ox, oy, s, 160, 200), 760, 1660, t, tcn, YEL)

def junto_view(c, t, fast=0.0, labels=True):
    ox, oy, s = PJ
    fv = fvid(t, 440); bl = blur_of(fv)
    ph = phi440(t); d = 30 * math.sin(ph)
    lam = 230; Apx = 17
    x0 = ox + 300 * s + 18; x1 = 790
    order = [("corriente", "cur"), ("bobina", "coil"), ("imán", "mag"), ("cono", "cone"), ("aire", "air"), ("oído", "ear")]
    tw = {k: wt("junto", w) for w, k in order}
    on = {k for k, v in tw.items() if v - 0.1 <= t < v + 0.9} if fast < 0.05 else set()
    air_field(c, x0, x1, oy - 270, oy + 270, ph, lam, Apx, None, bl, 1.0, 24, t=t, hl=0.6 if "air" in on else 0.0)
    lx, ly = cut_pt(ox, oy, s, -340, -300)
    line(c, [(-30, ly), (lx, ly)], INK, 26); line(c, [(-30, ly), (lx, ly)], hx("#3A3550"), 18); line(c, [(-30, ly), (lx, ly)], COPPER, 7)
    if "cur" in on: glow(c, lx / 2, ly, 200, YEL, 0.6)
    sm = 50 * bl
    c.save(); c.rectangle(-30, ly - 20, lx + 30, 40); c.clip(); charges(c, [(-60, ly), (lx, ly)], 50 * math.sin(ph) * (1 - bl), 40, 7, 1.0, sm); c.restore()
    hl = {k for k in on if k in ("coil", "mag", "cone")}
    spk_cut(c, ox, oy, s, d * (1 - bl), hl, 1.0, 1.0, clamp(math.cos(ph) * 3, -1, 1) * (1 - bl), 1.0, 50 * math.sin(ph) * (1 - bl), blur=bl, t=t, smear=sm)
    ex = 795; xe = ex + 118
    ue = Apx * 1.1 * math.sin(ph - TAU / lam * (xe - x0)) * (1 - bl) + (Apx * bl * math.sin(t * 57))
    ear(c, ex, oy, 1.0, ue, {"drum", "ear"} if "ear" in on else {"drum"} if bl > 0.3 else set(), t)
    if labels:
        a = 1 - clamp(fast * 4)
        def L():
            co(c, "CORRIENTE", 40, ly, 190, 690, t, tw["cur"], YEL)
            co(c, "BOBINA", *cut_pt(ox, oy, s, -64, 60), 330, 1610, t, tw["coil"], YEL)
            co(c, "IMÁN", *cut_pt(ox, oy, s, -150, 140), 130, 1520, t, tw["mag"])
            co(c, "CONO", *cut_pt(ox, oy, s, 180, -230), 470, 690, t, tw["cone"])
            co(c, "AIRE", 690, oy + 230, 650, 1540, t, tw["air"], CREAM)
            co(c, "OÍDO", ex + 40, oy - 170, 850, 690, t, tw["ear"], YEL)
        faded(c, a, L)

def scene_junto(c, t):
    rs = B("remate")["start"]
    fast = ease(ramp(t, T_REAL + 0.2, rs - 0.4))
    background(c, t, mix(YEL, HOT, fast))
    shake = 7 * fast
    c.save(); cam(c, 1.0 + 0.05 * ease(ramp(t, B("junto")["start"], rs)), 540, 1130)
    c.translate(shake * math.sin(t * 61), shake * math.cos(t * 53))
    junto_view(c, t, fast)
    c.restore()
    speed_lines(c, t, fast)
    if fast > 0.3:
        k = clamp((fast - 0.3) * 2)
        text(c, "440 VECES POR SEGUNDO", 540, 1650, 46, alpha(YEL, k), SLAB, False, outline=alpha(INK, k), olw=10)
    flash = ramp(t, rs - 0.5, rs - 0.3) * (1 - ramp(t, rs - 0.3, rs - 0.05))
    if flash > 0: c.set_source_rgba(1, 1, 1, 0.85 * flash); c.paint()

def scene_remate(c, t):
    background(c, t, COLD)
    rs = B("remate")["start"]
    trv = wt("remate", "revés"); tha = wt("remate", "hablas"); tai = wt("remate", "aire"); tcn = wt("remate", "cono")
    tbo = wt("remate", "bobina"); tim = wt("remate", "imán"); tge = wt("remate", "genera"); tco = wt("remate", "corriente")
    tmi = wt("remate", "micrófono")
    ox, oy, s = PJ
    c.save(); cam(c, 1.0 + 0.05 * ramp(t, rs, T_LOOP), 540, 1130)
    lam = 230
    x0 = ox + 300 * s + 18; x1 = 790
    ka = ease(ramp(t, tai - 0.3, tai + 0.3))
    air_field(c, x0, x1, oy - 270, oy + 270, 0, lam, 0, None, ka, 0.5 + 0.5 * ka, 24, rev=True, t=t)
    vib = ease(ramp(t, tcn - 0.4, tcn + 0.2))
    lx, ly = cut_pt(ox, oy, s, -340, -300)
    gen = ease(ramp(t, tge - 0.2, tco + 0.2))
    line(c, [(-30, ly), (lx, ly)], INK, 26); line(c, [(-30, ly), (lx, ly)], hx("#3A3550"), 18); line(c, [(-30, ly), (lx, ly)], COPPER, 7)
    if gen > 0:
        glow(c, lx / 2, ly, 220, YEL, 0.5 * gen)
        c.save(); c.rectangle(-30, ly - 20, lx + 30, 40); c.clip(); charges(c, [(-60, ly), (lx, ly)], -t * 60, 40, 7, gen, 30); c.restore()
    hl = set()
    if tcn - 0.1 <= t < tcn + 1.0: hl.add("cone")
    if tbo - 0.1 <= t < tbo + 1.2: hl.add("coil")
    if tim - 0.1 <= t < tim + 1.2: hl.add("mag")
    spk_cut(c, ox, oy, s, 0, hl, 1.0, 1.0, 0, gen, -t * 60, blur=vib, blurA=22, t=t, smear=30 * gen)
    # face talking
    kf = ease(ramp(t, tha - 0.5, tha))
    if kf > 0:
        fx = lerp(1250, 845, kf)
        talking = tha <= t < tmi + 1.2
        mouth = (0.5 + 0.5 * math.sin(t * 19) * math.sin(t * 7.3)) if talking else 0.1
        if talking:
            for i in range(3):
                p = (t * 1.6 + i / 3) % 1
                r = lerp(30, 200, p); a = math.sin(p * math.pi) * 0.9
                c.new_path(); c.arc(fx - 10, oy, r, math.pi - 0.55, math.pi + 0.55); c.set_source_rgba(*alpha(YEL, a)); c.set_line_width(10); c.stroke()
        face(c, fx, oy, mouth)
    c.restore()
    # direction pill
    flip = ramp(t, trv - 0.3, trv + 0.1)
    kp = eob(ramp(t, rs - 0.05, rs + 0.3)) * (1 - ease(ramp(t, tmi - 0.5, tmi - 0.2)))
    if kp > 0.02:
        sy = abs(math.cos(math.pi * flip))
        c.save(); c.translate(540, 690); c.scale(kp, kp * max(sy, 0.05))
        pill(c, "CORRIENTE → SONIDO" if flip < 0.5 else "SONIDO → CORRIENTE", 0, 0, 40, INK, CREAM if flip < 0.5 else YEL, 1.0, SANS, True)
        c.restore()
    if t >= tai - 0.2 and t < tmi:
        k = ease(ramp(t, tai - 0.2, tai + 0.2)) * (1 - ramp(t, tmi - 0.5, tmi - 0.2))
        arrow(c, 780, oy - 300, 600, oy - 300, alpha(YEL, k), 14, 40)
    t1 = tmi - 0.4
    co(c, "AIRE", 700, oy + 230, 680, 1560, t, tai, CREAM, t1=t1)
    co(c, "CONO", *cut_pt(ox, oy, s, 180, 230), 470, 1640, t, tcn, CREAM, t1=t1)
    co(c, "BOBINA", *cut_pt(ox, oy, s, -64, 60), 280, 1560, t, tbo, YEL, t1=t1)
    co(c, "IMÁN", *cut_pt(ox, oy, s, -150, 140), 110, 1640, t, tim, CREAM, t1=t1)
    co(c, "CORRIENTE", 60, ly, 160, 800, t, tco, YEL, t1=t1)
    km = eob(ramp(t, tmi - 0.2, tmi + 0.25))
    if km > 0.02:
        c.save(); c.translate(540, 700); c.scale(km, km); c.rotate(-0.03)
        text(c, "= MICRÓFONO", 0, 30, 92, YEL, SLAB, False, outline=INK, olw=14)
        c.restore()

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

def POPS():
    P = [wt("gancho", "nota"), wt("gancho", "cerebro")]
    P += [wt("imposible", w) - 0.15 for w in ("cuerdas", "teclas", "boquilla")]
    P += [wt("imposible", w) - 0.1 for w in ("guitarra", "piano", "cantante")]
    P += [wt("paso1", w) for w in ("electricidad", "corriente", "fija", "canción")]
    P += [wt("paso2", "bobina"), wt("paso2", "cono"), wt("paso2", "imán"), wt("paso2", "imán", 1), wt("paso2", "imanes") - 0.2]
    P += [wt("paso3", w) for w in ("corriente", "cono", "aire", "aprieta", "estira")]
    P += [wt("paso4", w) for w in ("apretones", "oído", "tímpano", "rápido", "grande", "veinte")] + [wt("paso4", "veinte", 1), wt("paso4", "mil")]
    P += [wt("paso5", w) for w in ("graves", "lento", "aire", "cono")]
    P += [wt("junto", w) for w in ("corriente", "bobina", "imán", "cono", "aire", "oído")]
    P += [wt("remate", w) for w in ("aire", "cono", "bobina", "imán", "corriente")]
    return sorted(P)

def SFX(put, L):
    import numpy as np
    SR = L["SR"]
    d = B("imposible")["start"]
    x = L["tone"](440, d, 0.05); n = len(x); tt = np.arange(n) / SR
    put(x * np.minimum(1, (d - tt) / 1.2), 0.0, 0.25)
    d2 = DUR - T_LOOP + 0.3
    y = L["tone"](440, d2, 0.6)
    put(y, T_LOOP - 0.2, 0.25)
    put(L["zap"](0.5), wt("paso1", "electricidad"), 0.3)
    put(L["zap"](0.5), wt("paso2", "corriente"), 0.25)
    put(L["ding"](), wt("remate", "micrófono"), 0.4)
    put(L["shimmer"](), wt("paso4", "mil"), 0.3)

# ---------------------------------------------------------------- thumbnails
def _thumb_title(c, x, y0, size, gap, olw):
    for i, (ln, col) in enumerate((("SOLO", WHITE), ("EMPUJA", WHITE), ("AIRE", YEL))):
        text(c, ln, x, y0 + i * gap, size, col, SLAB, False, outline=INK, olw=olw)

def THUMB_V(c):
    background(c, 3.0, ORANGE)
    glow(c, 540, 1380, 700, YEL, 0.35)
    for i, r in enumerate((420, 520, 620)):
        for base in (0, math.pi):
            c.new_path(); c.arc(540, 1380, r, base - 0.45, base + 0.45); c.set_source_rgba(*alpha(YEL, 0.9 - 0.25 * i)); c.set_line_width(18); c.stroke()
    c.save(); c.translate(540, 1290); c.scale(1.15, 1.15); c.translate(-540, -1290)
    spk_front(c, 540, 1290, 1.0, 10, 0.9, 22)
    c.restore()
    _thumb_title(c, 540, 330, 190, 200, 22)

def THUMB_H(c):
    g = cairo.LinearGradient(0, 0, 0, 720); g.add_color_stop_rgba(0, *BG_TOP); g.add_color_stop_rgba(1, *BG_BOT); c.set_source(g); c.paint()
    glow(c, 960, 420, 460, YEL, 0.4)
    for i, r in enumerate((250, 320, 390)):
        c.new_path(); c.arc(960, 430, r, -0.5, 0.5); c.set_source_rgba(*alpha(YEL, 0.9 - 0.25 * i)); c.set_line_width(14); c.stroke()
        c.new_path(); c.arc(960, 430, r, math.pi - 0.5, math.pi + 0.5); c.set_source_rgba(*alpha(YEL, 0.5 - 0.15 * i)); c.set_line_width(14); c.stroke()
    c.save(); c.translate(960, 370); c.scale(0.7, 0.7); c.translate(-540, -1110)
    spk_front(c, 540, 1110, 1.0, 10, 0.9, 22)
    c.restore()
    _thumb_title(c, 370, 210, 128, 150, 18)
