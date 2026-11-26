"""¿Cómo sabe la hora tu reloj? (quartz watch). Illustrations for the engine (see output/engine/SCENES_GUIDE.md)."""
from core import *  # noqa
import cairo, math, random

WX, WY = 540, 1130           # watch / movement centre on screen
MV_S = 420 / 330             # movement drawn at radius 420 (local radius 330)
S0 = 38                      # second shown at frame 0
F_Q = 32768                  # quartz frequency
LEATHER = hx("#5A3530"); BRASS = hx("#9C8560"); PCB = hx("#2F6B4F"); COPPER = hx("#D9853B"); QUARTZ = hx("#DDEBFA")
SILVER = hx("#C9CED8")


def tickv(x):
    """Seconds value with a crisp tick at every integer of x (x = elapsed seconds)."""
    n = math.floor(x); f = x - n
    return n - 1 + eob(min(1.0, f / 0.12))


def vis_freq(f, t):
    """Frequency as seen on screen at time t (Hz)."""
    return f * 10 ** (-slow_log(t))


# ================================================================ pieces
def gear(c, x, y, r, ang, col=BRASS, lw=4, n=None, spokes=True):
    n = n or max(8, int(round(r / 5)))
    h = max(4, min(10, r * 0.14)); ri = r - h
    c.new_path()
    for i in range(n):
        a = ang + 2 * math.pi * i / n; p = 2 * math.pi / n
        for rr, da in ((ri, 0), (r, 0.22 * p), (r, 0.5 * p), (ri, 0.72 * p)):
            c.line_to(x + rr * math.cos(a + da), y + rr * math.sin(a + da))
    c.close_path(); fill_stroke(c, col, INK, lw)
    if spokes and r > 34:
        circle(c, x, y, ri * 0.78); fill_stroke(c, mix(col, INK, 0.35), INK, lw * 0.6)
        for k in range(4):
            a = ang + k * math.pi / 2
            line(c, [(x, y), (x + ri * 0.8 * math.cos(a), y + ri * 0.8 * math.sin(a))], col, max(6, r * 0.16))
    circle(c, x, y, max(5, r * 0.16)); fill_stroke(c, mix(col, WHITE, 0.3), INK, lw * 0.6)


def fork_shape(c, L, tw, gap, amp, base_w, base_h, fill=QUARTZ, lw=5, electrodes=True, a=1.0):
    """Tuning fork, tines pointing to -y from y=0, base below (0..base_h). amp>0 = tines bend outwards."""
    rrect(c, -base_w / 2, -4, base_w, base_h + 4, min(14, base_h / 3)); fill_stroke(c, alpha(fill, a), alpha(INK, a), lw)
    for side in (-1, 1):
        x0 = side * (gap / 2 + tw / 2); n = 18
        L_ = [(x0 + side * amp * (i / n) ** 2 - tw / 2, -L * i / n) for i in range(n + 1)]
        R_ = [(x0 + side * amp * (i / n) ** 2 + tw / 2, -L * i / n) for i in range(n + 1)]
        c.new_path(); c.move_to(*L_[0])
        for p in L_[1:]: c.line_to(*p)
        tx = x0 + side * amp
        c.arc(tx, -L, tw / 2, math.pi, 2 * math.pi)
        for p in reversed(R_): c.line_to(*p)
        c.close_path(); fill_stroke(c, alpha(fill, a), alpha(INK, a), lw)
        if electrodes:
            pts = [(x0 + side * amp * (i / n) ** 2, -L * i / n) for i in range(2, n - 1)]
            line(c, pts, alpha(YEL, 0.85 * a), max(2, tw * 0.22))
    if electrodes:
        line(c, [(-gap / 2 - tw / 2, -L * 0.1), (-gap / 2 - tw / 2, base_h * 0.6)], alpha(YEL, 0.85 * a), max(2, tw * 0.22))
        line(c, [(gap / 2 + tw / 2, -L * 0.1), (gap / 2 + tw / 2, base_h * 0.6)], alpha(YEL, 0.85 * a), max(2, tw * 0.22))
    c.new_path()


def spark(c, x, y, s, t, seed, col=YEL):
    r = random.Random(seed + int(t * 12))
    a = r.uniform(0, 6.28); pts = [(x, y)]
    for i in range(4):
        a += r.uniform(-0.9, 0.9)
        pts.append((pts[-1][0] + math.cos(a) * s * 0.3, pts[-1][1] + math.sin(a) * s * 0.3))
    line(c, pts, col, max(3, s * 0.08))


# ---------------------------------------------------------------- movement (local radius 330, centred 0,0)
CRY = (100, -212)            # quartz can centre
ROT = (190, 82)              # stepper rotor
R1, RP0, RP1, R2 = 80, 16, 18, 108   # gear1, rotor pinion, gear1 pinion, seconds wheel (ratios 5 and 6 -> 30)
BAT = (-138, 150); CHIP = (-150, -160); COIL = (190, -70)

def _g1():
    d0 = RP0 + R1; d1 = RP1 + R2; x1, y1 = ROT; D = math.hypot(x1, y1)
    a = (d1 ** 2 - d0 ** 2 + D ** 2) / (2 * D); h = math.sqrt(max(0, d1 ** 2 - a ** 2))
    ux, uy = x1 / D, y1 / D
    return (a * ux + h * uy, a * uy - h * ux) if (a * uy - h * ux) > (a * uy + h * ux) else (a * ux - h * uy, a * uy + h * ux)
G1 = _g1()


def mv_pt(p, cx=WX, cy=WY, s=MV_S):
    return (cx + p[0] * s, cy + p[1] * s)


def crystal(c, t, see=0.0, vib=0.0, hl=0.0, fast=None):
    x, y = CRY
    if hl > 0: glow(c, x, y, 120, YEL, 0.55 * hl)
    # leads to the board
    for dy in (-7, 7):
        line(c, [(x - 70, y + dy), (-30, y + dy)], hx("#E8C26A"), 4)
    # fork inside (base at the lead end, tines towards the closed end)
    if see > 0:
        c.save(); c.translate(x - 42, y); c.rotate(math.pi / 2)
        f = vis_freq(F_Q, t)
        if f > 7:
            for sg in (-1, 1):
                fork_shape(c, 82, 9, 7, sg * vib, 34, 18, QUARTZ, 2, True, 0.5 * see)
        else:
            fork_shape(c, 82, 9, 7, vib * math.sin(2 * math.pi * F_Q * anim_time(t)), 34, 18, QUARTZ, 2, True, see)
        c.restore()
    # metal can (cylinder)
    rrect(c, x - 65, y - 20, 130, 40, 18)
    g = cairo.LinearGradient(0, y - 20, 0, y + 20)
    g.add_color_stop_rgba(0, *alpha(WHITE, 1 - 0.75 * see)); g.add_color_stop_rgba(0.5, *alpha(SILVER, 1 - 0.8 * see)); g.add_color_stop_rgba(1, *alpha(METAL, 1 - 0.75 * see))
    c.set_source(g); c.fill_preserve(); c.set_source_rgba(*INK); c.set_line_width(4); c.stroke()
    if see < 0.3:
        line(c, [(x - 50, y - 10), (x + 45, y - 10)], alpha(WHITE, 0.7 * (1 - see)), 4)


def movement(c, t, cx=WX, cy=WY, s=MV_S, hl=(), see=0.0, vib=0.0, rotor=0.0, coil=0.0, sec=None, hand_a=0.0, fast=0.0):
    hl = set(hl)
    c.save(); c.translate(cx, cy); c.scale(s, s)
    shadow(c, lambda: circle(c, 0, 0, 332), 12, 16, 0.45)
    rrect(c, 318, -32, 40, 64, 10); fill_stroke(c, RUST, INK, 6)                  # crown
    circle(c, 0, 0, 330); fill_stroke(c, RUST, INK, 8)
    circle(c, 0, 0, 304); fill_stroke(c, DARK, INK, 5)
    circle(c, 0, 0, 294); fill_stroke(c, mix(BRASS, DARK, 0.45), None)
    for i in range(10):                                                         # perlage on the plate
        circle(c, 0, 0, 40 + i * 26); c.set_source_rgba(1, 1, 1, 0.035); c.set_line_width(10); c.stroke()
    for a in (0.5, 2.2, 3.6, 5.2):                                              # screws / jewels
        sx, sy = 270 * math.cos(a), 270 * math.sin(a)
        circle(c, sx, sy, 11); fill_stroke(c, SILVER, INK, 3); line(c, [(sx - 7, sy), (sx + 7, sy)], INK, 3)
    # gear train (seconds wheel in the centre)
    k2 = 1 if "tic" in hl else 0
    gear(c, 0, 0, R2, rotor / 30, mix(BRASS, YEL, 0.5 * k2), 3)
    gear(c, G1[0], G1[1], R1, -rotor / 5, mix(BRASS, YEL, 0.5 * k2), 3)
    gear(c, G1[0], G1[1], RP1 + 4, -rotor / 5, mix(BRASS, WHITE, 0.2), 3, n=8, spokes=False)
    # battery
    bx, by = BAT
    if "pila" in hl: glow(c, bx, by, 170, YEL, 0.5)
    line(c, [(bx, by - 60), (bx, -95)], SILVER, 14)
    circle(c, bx, by, 92)
    g = cairo.LinearGradient(bx - 90, by - 90, bx + 90, by + 90)
    g.add_color_stop_rgba(0, *WHITE); g.add_color_stop_rgba(0.5, *SILVER); g.add_color_stop_rgba(1, *METAL)
    c.set_source(g); c.fill_preserve(); c.set_source_rgba(*INK); c.set_line_width(5); c.stroke()
    circle(c, bx, by, 72); c.set_source_rgba(*alpha(INK, 0.35)); c.set_line_width(3); c.stroke()
    text(c, "+", bx, by - 12, 44, INK, SANS, True); text(c, "1,5 V", bx, by + 34, 28, INK, SANS, True)
    # board + chip
    if "chip" in hl or "div" in hl: glow(c, CHIP[0], CHIP[1], 160, YEL, 0.5)
    rrect(c, -262, -238, 232, 148, 14); fill_stroke(c, PCB, INK, 4)
    for i in range(5):
        line(c, [(-250, -110 - i * 4 - 10 * i), (-215, -110 - i * 14)], alpha(hx("#E8C26A"), 0.6), 3)
    line(c, [(-105, -150), (-60, -150), (-60, -100), (100, -100), (COIL[0] - 30, -100)], hx("#E8C26A"), 4)
    chx, chy = CHIP
    for i in range(5):
        for sd in (-1, 1):
            line(c, [(chx - 34 + i * 17, chy + sd * 38), (chx - 34 + i * 17, chy + sd * 50)], SILVER, 4)
    rrect(c, chx - 48, chy - 40, 96, 80, 8); fill_stroke(c, NIGHT, INK, 4)
    circle(c, chx - 32, chy - 24, 5); c.set_source_rgba(1, 1, 1, 0.3); c.fill()
    if "div" in hl: text(c, "÷2", chx, chy + 14, 40, YEL, SLAB, False)
    # quartz
    crystal(c, t, see, vib, 1.0 if ("cuarzo" in hl or "vib" in hl) else 0.0)
    # coil + stator + rotor (Lavet stepper)
    kx, ky = COIL
    if coil > 0: glow(c, kx, ky, 150, COPPER, 0.7 * coil)
    line(c, [(kx, -160), (250, -160), (250, ROT[1]), (ROT[0] + 50, ROT[1])], METAL, 22, cairo.LINE_CAP_BUTT)
    line(c, [(kx, -165), (kx, ROT[1] - 50)], METAL, 22, cairo.LINE_CAP_BUTT)
    circle(c, ROT[0], ROT[1], 52); fill_stroke(c, METAL, INK, 4)
    circle(c, ROT[0], ROT[1], 38); fill_stroke(c, DARK, None)
    rrect(c, kx - 30, -150, 60, 160, 10); fill_stroke(c, mix(COPPER, YEL, 0.5 * coil), INK, 4)
    for i in range(12):
        line(c, [(kx - 28, -140 + i * 12.5), (kx + 28, -136 + i * 12.5)], alpha(INK, 0.35), 2)
    rx, ry = ROT
    gear(c, rx, ry, RP0 + 3, rotor, SILVER, 2, n=7, spokes=False)
    c.save(); c.translate(rx, ry); c.rotate(rotor)
    c.new_path(); c.arc(0, 0, 32, -math.pi / 2, math.pi / 2); c.close_path(); fill_stroke(c, RED, None)
    c.new_path(); c.arc(0, 0, 32, math.pi / 2, 3 * math.pi / 2); c.close_path(); fill_stroke(c, STEEL, None)
    circle(c, 0, 0, 32); fill_stroke(c, None, INK, 4); circle(c, 0, 0, 7); fill_stroke(c, SILVER, INK, 2)
    c.restore()
    if "tic" in hl: circle(c, rx, ry, 60); c.set_source_rgba(*YEL); c.set_line_width(6); c.stroke()
    # second hand (see-through) on the centre arbor
    if hand_a > 0 and sec is not None:
        a = -math.pi / 2 + sec * math.pi / 30
        line(c, [(-55 * math.cos(a), -55 * math.sin(a)), (285 * math.cos(a), 285 * math.sin(a))], alpha(HOT, 0.9 * hand_a), 7)
        circle(c, 0, 0, 14); fill_stroke(c, alpha(HOT, hand_a), alpha(INK, hand_a), 3)
    circle(c, 0, 0, 8); fill_stroke(c, hx("#B03050"), INK, 2)
    c.restore()


# ---------------------------------------------------------------- the watch from the front (local radius 330)
def watch_face(c, t, sec, strap_a=1.0, face_a=1.0, shimmer=0.0):
    if strap_a > 0:
        c.push_group()
        for sg in (-1, 1):
            rrect(c, -140, (-470 if sg < 0 else 240), 280, 230, 40); fill_stroke(c, LEATHER, INK, 7)
            for dx in (-112, 112):
                y0, y1 = (-450, -250) if sg < 0 else (250, 450)
                c.save(); c.set_dash([12, 10]); line(c, [(dx, y0), (dx, y1)], alpha(CREAM, 0.35), 3); c.restore()
            rrect(c, -160, (-330 if sg < 0 else 270), 320, 60, 16); fill_stroke(c, RUST, INK, 6)   # lugs
        for i in range(4):
            circle(c, 0, 340 + i * 30, 7); fill_stroke(c, INK, None)
        c.pop_group_to_source(); c.paint_with_alpha(strap_a)
    if face_a <= 0: return
    c.push_group()
    shadow(c, lambda: circle(c, 0, 0, 332), 12, 16, 0.45)
    rrect(c, 318, -32, 40, 64, 10); fill_stroke(c, RUST, INK, 6)
    for i in range(5): line(c, [(330, -24 + i * 12), (356, -24 + i * 12)], alpha(INK, 0.4), 3)
    circle(c, 0, 0, 330); fill_stroke(c, RUST, INK, 8)
    circle(c, 0, 0, 304); fill_stroke(c, mix(RUST, INK, 0.25), INK, 4)
    circle(c, 0, 0, 292)
    g = cairo.RadialGradient(-60, -80, 30, 0, 0, 300)
    g.add_color_stop_rgba(0, *CREAM); g.add_color_stop_rgba(1, *CREAM2); c.set_source(g); c.fill()
    for i in range(60):
        a = i * math.pi / 30; big = i % 5 == 0
        r0 = 236 if big else 262
        line(c, [(r0 * math.cos(a), r0 * math.sin(a)), (278 * math.cos(a), 278 * math.sin(a))], INK, 10 if big else 3)
    for n, a in ((12, -90), (3, 0), (6, 90), (9, 180)):
        ar = math.radians(a)
        text(c, str(n), 188 * math.cos(ar), 188 * math.sin(ar) + 24, 66, INK, SLAB, False)
    text(c, "QUARTZ", 0, 110, 26, alpha(INK, 0.6), SANS, True)
    if shimmer > 0:   # something vibrating inside, faintly seen through the dial
        x, y = CRY
        glow(c, x, y + 80, 70, XRAY, 0.25 * shimmer * (0.7 + 0.3 * math.sin(t * 37)))
        for k in range(3):
            r = 18 + ((t * 0.9 + k / 3) % 1) * 50
            c.new_path(); c.arc(x, y + 80, r, 0, 2 * math.pi); c.set_source_rgba(*alpha(STEEL, 0.35 * shimmer * (1 - (r - 18) / 50))); c.set_line_width(3); c.stroke()
        j = 1.6 * math.sin(t * 91)
        rrect(c, x - 36 + j, y + 70, 72, 20, 9); c.set_source_rgba(*alpha(STEEL, 0.22 * shimmer)); c.fill()
    # hands 10:09
    for ang, L, w in ((((10 + 9 / 60) / 12) * 360 - 90, 150, 22), ((9 / 60) * 360 - 90, 238, 15)):
        a = math.radians(ang)
        line(c, [(-26 * math.cos(a), -26 * math.sin(a)), (L * math.cos(a), L * math.sin(a))], INK, w)
    a = -math.pi / 2 + sec * math.pi / 30
    line(c, [(-62 * math.cos(a), -62 * math.sin(a)), (272 * math.cos(a), 272 * math.sin(a))], RED, 6)
    circle(c, -48 * math.cos(a), -48 * math.sin(a), 13); fill_stroke(c, RED, None)
    circle(c, 0, 0, 18); fill_stroke(c, RED, INK, 4)
    c.new_path(); c.arc(0, 0, 270, math.pi * 1.05, math.pi * 1.45); c.set_source_rgba(1, 1, 1, 0.35); c.set_line_width(14); c.stroke()
    c.pop_group_to_source(); c.paint_with_alpha(face_a)


# ---------------------------------------------------------------- badges
def ic_pendulum(c, t):
    a = 0.4 * math.sin(t * 3.2)
    line(c, [(-50, -62), (50, -62)], INK, 8)
    bx, by = 95 * math.sin(a), -62 + 95 * math.cos(a)
    line(c, [(0, -62), (bx, by)], INK, 6); circle(c, bx, by, 24); fill_stroke(c, GOLD, INK, 5)

def ic_key(c, t):
    c.rotate(0.6 + 0.3 * math.sin(t * 2))
    circle(c, 0, -38, 34); fill_stroke(c, YEL, INK, 6); circle(c, 0, -38, 14); fill_stroke(c, CREAM, INK, 4)
    line(c, [(0, -4), (0, 62)], INK, 12)
    line(c, [(0, 40), (24, 40)], INK, 10); line(c, [(0, 58), (20, 58)], INK, 10)

def ic_person(c, t):
    circle(c, -28, -14, 30); fill_stroke(c, ORANGE, INK, 5)
    c.new_path(); c.arc(-28, 70, 52, math.pi, 2 * math.pi); c.close_path(); fill_stroke(c, STEEL, INK, 5)
    rrect(c, 2, -78, 78, 46, 14); fill_stroke(c, WHITE, INK, 4)
    n = 1 + int(t * 2.5) % 3
    text(c, ",".join(str(i + 1) for i in range(n)), 41, -46, 24, INK, SANS, True)


def calendar(c, x, y, k):
    if k <= 0.02: return
    c.save(); c.translate(x, y); c.scale(k, k)
    shadow(c, lambda: rrect(c, -170, -120, 340, 250, 22), 8, 12, 0.4)
    rrect(c, -170, -120, 340, 250, 22); fill_stroke(c, CREAM, INK, 6)
    c.save(); rrect(c, -170, -120, 340, 250, 22); c.clip(); c.rectangle(-170, -120, 340, 70); c.set_source_rgba(*RED); c.fill(); c.restore()
    rrect(c, -170, -120, 340, 250, 22); fill_stroke(c, None, INK, 6)
    for dx in (-90, 90): rrect(c, dx - 9, -140, 18, 46, 9); fill_stroke(c, METAL, INK, 4)
    text(c, "AL MES", 0, -70, 36, WHITE, SLAB, False)
    text(c, "±15 s", 0, 70, 92, INK, SLAB, False)
    c.restore()


# ================================================================ scenes
def scene_front(c, t):
    background(c, t, ORANGE)
    at = anim_time(t)
    sec = S0 + tickv(at)
    up = ease(ramp(t, wt("imposible", "péndulo") - 0.6, wt("imposible", "péndulo") - 0.1))
    z = ease(ramp(t, wt("freno", "vamos"), T_SLOW + 0.2))
    up *= 1 - ease(ramp(t, B("freno")["start"] - 0.5, B("freno")["start"] + 0.3))
    x = ease(ramp(t, T_SLOW - 0.7, T_SLOW + 0.25))
    push = 1.0 + 0.04 * ease(ramp(t, 0, B("imposible")["start"]))
    c.save()
    cam(c, push * (1 - 0.22 * up) * (1 + (MV_S - 1) * z), WX, WY)
    c.translate(0, -130 * up / (1 - 0.22 * up))
    if x > 0: movement(c, t, WX, WY, 1.0, sec=sec, hand_a=0.0)
    c.translate(WX, WY)
    watch_face(c, t, sec, strap_a=1 - x, face_a=1 - x, shimmer=1.0)
    c.restore()
    if up > 0.01:
        icons = [("péndulo", "PÉNDULO", ic_pendulum, 250), ("muelle", "CUERDA", ic_key, 540), ("nadie", "CONTAR", ic_person, 830)]
        out = ease(ramp(t, wt("imposible", "aun") - 0.2, wt("imposible", "aun") + 0.2))
        for w, lab, fn, bx in icons:
            t0 = wt("imposible", w) - 0.15
            k = eob(ramp(t, t0, t0 + 0.3)) * up * (1 - out)
            xt = wt("imposible", "cuerda") + 0.1 if w == "muelle" else t0 + 0.4
            icon_badge(c, bx, 1500, k, lab, lambda cc, fn=fn: fn(cc, t), t, xt)
        tc = wt("imposible", "apenas") - 0.1
        calendar(c, 540, 1500, eob(ramp(t, tc, tc + 0.35)) * up)


def scene_paso1(c, t):
    background(c, t, ORANGE)
    b = B("paso1")
    push = 1.0 + 0.03 * ease(ramp(t, b["start"], wt("paso1", "diapasón")))
    t_d = wt("paso1", "diapasón") - 0.15
    z = ease(ramp(t, t_d, t_d + 0.8))
    s = MV_S * push
    P = mv_pt(CRY, WX, WY, s)
    TGT = (540, 1000); ZS = 2.8
    hl = set()
    if t >= wt("paso1", "pila") - 0.1: hl.add("pila")
    if t >= wt("paso1", "chip") - 0.1: hl.add("chip")
    if t >= wt("paso1", "cuarzo") - 0.1: hl.add("cuarzo")
    c.save()
    c.translate((TGT[0] - P[0]) * z, (TGT[1] - P[1]) * z); cam(c, 1 + (ZS - 1) * z, P[0], P[1])
    movement(c, t, WX, WY, s, hl=hl if z < 0.5 else (), see=z, vib=0.0, sec=S0)
    c.restore()
    if z > 0:
        c.set_source_rgba(*alpha(NIGHT, 0.6 * z)); c.paint()
        c.save(); c.translate((TGT[0] - P[0]) * z, (TGT[1] - P[1]) * z); cam(c, 1 + (ZS - 1) * z, P[0], P[1])
        c.translate(WX, WY); c.scale(s, s); crystal(c, t, z, 0.0, 0.0); c.restore()
    ka = 1 - ease(ramp(t, t_d, t_d + 0.3))
    if ka > 0:
        c.push_group()
        callout(c, "PILA", *mv_pt((BAT[0] - 60, BAT[1] + 40), WX, WY, s), 170, 1560, t, wt("paso1", "pila"))
        callout(c, "CHIP", *mv_pt((CHIP[0] - 30, CHIP[1] - 20), WX, WY, s), 210, 700, t, wt("paso1", "chip"))
        callout(c, "CUARZO", *mv_pt((CRY[0] + 30, CRY[1] - 15), WX, WY, s), 780, 680, t, wt("paso1", "cuarzo"), YEL)
        c.pop_group_to_source(); c.paint_with_alpha(ka)
    if z > 0.6:
        callout(c, "DIAPASÓN", TGT[0] + 25, TGT[1] - 20, 300, 720, t, t_d + 0.6, YEL)
        tg = wt("paso1", "grano") - 0.15
        k = eob(ramp(t, tg, tg + 0.4))
        if k > 0:   # grain of rice (~7 mm) next to the 6 mm can, same scale
            rl = 130 * s * ZS * 1.2
            c.save(); c.translate(540, 1270); c.scale(k, k)
            shadow(c, lambda: (c.save(), c.scale(1, 0.36), circle(c, 0, 0, rl / 2), c.restore()), 8, 10, 0.4)
            c.save(); c.scale(1, 0.36); circle(c, 0, 0, rl / 2); c.restore()
            g = cairo.LinearGradient(0, -60, 0, 60); g.add_color_stop_rgba(0, *WHITE); g.add_color_stop_rgba(1, *CREAM2)
            c.set_source(g); c.fill_preserve(); c.set_source_rgba(*INK); c.set_line_width(6); c.stroke()
            line(c, [(-rl * 0.35, -22), (rl * 0.3, -26)], alpha(WHITE, 0.9), 8)
            c.restore()
            if k > 0.8: text(c, "GRANO DE ARROZ", 540, 1430, 44, CREAM, SLAB, False, outline=INK, olw=8)


# ---------------------------------------------------------------- paso2: the trick of quartz
FK = dict(x=540, yb=1330, L=540, tw=80, gap=64, bw=290, bh=140)

def fork_path_pts():
    x, yb, bh = FK["x"], FK["yb"], FK["bh"]
    return [(x - 40, yb + bh), (x - 40, 1580), (300, 1580)]

def travel(c, pts, k, col=YEL):
    if not (0 < k < 1): return
    L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; d = k * sum(L)
    for (a, b), l in zip(zip(pts, pts[1:]), L):
        if d <= l:
            px, py = a[0] + (b[0] - a[0]) * d / l, a[1] + (b[1] - a[1]) * d / l
            glow(c, px, py, 60, col, 0.9); circle(c, px, py, 11); c.set_source_rgba(1, 1, 1, 1); c.fill(); return
        d -= l

def statement(c, left, right, y, k, lcol=INK, rcol=RED):
    if k <= 0.02: return
    sz = 46; font(c, SLAB, sz); wl = c.text_extents(left).x_advance; wr = c.text_extents(right).x_advance
    aw = 110; tot = wl + aw + wr; bw = tot + 70
    c.save(); c.translate(540, y); c.scale(eob(k), eob(k))
    shadow(c, lambda: rrect(c, -bw / 2, -50, bw, 100, 18), 8, 10, 0.4)
    rrect(c, -bw / 2, -50, bw, 100, 18); fill_stroke(c, CREAM, INK, 6)
    x0 = -tot / 2
    text(c, left, x0, 17, sz, lcol, SLAB, False, "l")
    arrow(c, x0 + wl + 18, 0, x0 + wl + aw - 18, 0, RED, 10, 30)
    text(c, right, x0 + wl + aw, 17, sz, rcol, SLAB, False, "l")
    c.restore()

def scene_paso2(c, t):
    b = B("paso2")
    background(c, t, COLD)
    c.save(); cam(c, 1.0 + 0.04 * ramp(t, b["start"], b["end"]), 540, 1150)
    t_e1 = wt("paso2", "electricidad"); t_d1 = wt("paso2", "dobla"); t_d2 = wt("paso2", "dobla", 1); t_e2 = wt("paso2", "electricidad", 1)
    t_emp = wt("paso2", "empujoncito"); t_rit = wt("paso2", "ritmo")
    bend1 = ease(ramp(t, t_e1 + 0.2, t_d1 + 0.1)) * (1 - ease(ramp(t, t_d2 - 0.6, t_d2 - 0.2)))
    bend2 = ease(ramp(t, t_d2 - 0.15, t_d2 + 0.3)) * (1 - ease(ramp(t, t_e2 + 0.9, t_e2 + 1.3)))
    osc = ease(ramp(t, t_emp + 0.1, t_emp + 0.8))
    ph = 2 * math.pi * F_Q * (anim_time(t) - anim_time(t_emp + 0.1))
    amp = 34 * bend1 - 26 * bend2 + 30 * osc * math.sin(ph)
    x, yb = FK["x"], FK["yb"]
    # chip + wires
    path = fork_path_pts()
    line(c, path, hx("#E8C26A"), 6)
    line(c, [(x + 40, yb + FK["bh"]), (x + 40, 1630), (300, 1630)], hx("#E8C26A"), 6)
    rrect(c, 150, 1550, 150, 110, 12); fill_stroke(c, mix(DARK, LAV, 0.25), LAV, 4)
    text(c, "CHIP", 225, 1618, 34, CREAM, SANS, True)
    # charges on the electrodes
    charge = max(ramp(t, t_e1, t_e1 + 0.4) * (1 - ramp(t, t_d2 - 0.6, t_d2 - 0.2)),
                 ramp(t, t_e2 - 0.1, t_e2 + 0.3) * (1 - ramp(t, t_e2 + 0.9, t_e2 + 1.3)), 0.6 * osc)
    glow(c, x, yb - 250, 380, XRAY, 0.18 + 0.15 * charge)
    c.save(); c.translate(x, yb)
    fork_shape(c, FK["L"], FK["tw"], FK["gap"], amp, FK["bw"], FK["bh"], QUARTZ, 6, True)
    c.restore()
    if charge > 0.05:
        for side in (-1, 1):
            tx = x + side * (FK["gap"] / 2 + FK["tw"] / 2)
            for j, uy in enumerate((0.25, 0.5, 0.75)):
                xx = tx + side * amp * uy ** 2; yy = yb - FK["L"] * uy
                sg = "+" if (side < 0) ^ (osc > 0.5 and math.sin(ph) < 0) else "−"
                circle(c, xx, yy, 22 * charge); fill_stroke(c, RED if sg == "+" else STEEL, INK, 3)
                if charge > 0.6: text(c, sg, xx, yy + 11, 32, WHITE, SANS, True)
    # current going in (empuje del chip) / coming out
    wire = list(reversed(path)) + [(x - 40, yb + 60)]
    travel(c, wire, ramp(t, t_e1 - 0.5, t_e1 + 0.15))
    travel(c, list(reversed(wire)), ramp(t, t_e2 + 0.1, t_e2 + 0.8))
    travel(c, wire, ramp(t, t_emp - 0.4, t_emp + 0.15), HOT)
    # sparks when bending makes electricity
    if t_e2 - 0.1 < t < t_e2 + 1.0:
        for i in range(6):
            side = -1 if i % 2 else 1
            spark(c, x + side * 120, yb - 120 - i * 60, 60, t, i * 7)
    # pressing arrows for "si se dobla"
    kp = ramp(t, t_d2 - 0.4, t_d2) * (1 - ramp(t, t_e2 + 0.7, t_e2 + 1.0))
    if kp > 0:
        for side in (-1, 1):
            ex = x + side * 150; yy = yb - FK["L"] * 0.85
            arrow(c, ex + side * (110 - 0 * kp), yy, ex + side * 10, yy, alpha(HOT, kp), 14, 40)
    c.restore()
    k1 = ramp(t, t_d1 - 0.1, t_d1 + 0.25) * (1 - ramp(t, t_d2 - 0.4, t_d2 - 0.15))
    statement(c, "ELECTRICIDAD", "SE DOBLA", 670, k1)
    k2 = ramp(t, t_e2 - 0.1, t_e2 + 0.25) * (1 - ramp(t, t_emp - 0.5, t_emp - 0.2))
    statement(c, "SE DOBLA", "ELECTRICIDAD", 670, k2)
    kc = 1 - ramp(t, t_d1 - 0.3, t_d1)
    if kc > 0:
        c.push_group(); callout(c, "CUARZO", x - 80, 1000, 220, 900, t, wt("paso2", "cuarzo")); c.pop_group_to_source(); c.paint_with_alpha(kc)
    callout(c, "EMPUJONCITO", 260, 1550, 220, 1430, t, t_emp)
    kv = ramp(t, wt("paso2", "vibra") - 0.1, wt("paso2", "vibra") + 0.3)
    if kv > 0:
        text(c, "VIBRA SOLO", 540, 680, 70 * eob(kv), YEL, SLAB, False, outline=INK, olw=10)
    # rhythm trace
    kr = ease(ramp(t, t_rit - 0.5, t_rit))
    if kr > 0:
        rrect(c, 735, 1020, 200, 170, 14); fill_stroke(c, hx("#1E3A2A"), INK, 5)
        c.save(); rrect(c, 735, 1020, 200, 170, 14); c.clip()
        pts = [(740 + i * 2, 1105 - 50 * kr * math.sin(ph - i * 2 * 0.06)) for i in range(96)]
        line(c, pts, hx("#7CFC9A"), 5); c.restore()
        text(c, "SIEMPRE", 835, 1235, 32, CREAM, SANS, True); text(c, "IGUAL", 835, 1272, 32, CREAM, SANS, True)


# ---------------------------------------------------------------- paso3: divide by two, 15 times
LAD_Y0, LAD_DY = 660, 57

def row_on_times():
    ts = [wt("paso3", "cuenta") - 0.1, wt("paso3", "dos") - 0.05, wt("paso3", "otra") - 0.05, wt("paso3", "otra", 1) - 0.05]
    q = wt("paso3", "15") if any("15" == w["word"] for w in WORDS if w["beat"] == "paso3") else wt("paso3", "quince")
    for i in range(12): ts.append(q - 0.1 + i * 0.1)
    return ts

def scene_paso3(c, t):
    b = B("paso3")
    background(c, t, GREEN)
    c.save(); cam(c, 1.0 + 0.03 * ramp(t, b["start"], b["end"]), 540, 1100)
    ON = row_on_times(); at = anim_time(t)
    text(c, "VECES / SEG.", 425, 638, 22, alpha(LAV, 0.9), SANS, True, "r")
    for k in range(16):
        y = LAD_Y0 + k * LAD_DY
        on = ease(ramp(t, ON[k], ON[k] + 0.2)) if k < len(ON) else 0
        flash = pulse_at(t, ON[k], 0.5)
        if k > 0:
            line(c, [(180, y - LAD_DY + 22), (180, y - 22)], mix(alpha(LAV, 0.3), YEL, on), 5)
            rrect(c, 130, y - 22, 100, 44, 10); fill_stroke(c, mix(DARK, YEL, on), mix(alpha(LAV, 0.5), INK, on), 4)
            text(c, "÷2", 180, y + 12, 32, mix(alpha(LAV, 0.6), INK, on), SLAB, False)
            if flash > 0: glow(c, 180, y, 90, YEL, 0.6 * flash)
        else:
            rrect(c, 110, y - 24, 140, 48, 10); fill_stroke(c, mix(DARK, XRAY, on), INK, 4)
            text(c, "CUARZO", 180, y + 10, 26, INK if on > 0.5 else LAV, SANS, True)
        if on > 0.02:
            v = F_Q >> k
            text(c, dots(v), 425, y + 12, 34, alpha(YEL if k in (0, 15) else CREAM, on), MONO, True, "r")
            # square wave: period doubles every row (scrolls at the real, slowed rate)
            P = 14 * 2 ** k; off = (14 * F_Q * at) % (2 * P) if P < 1e6 else 0
            pts = []; x0, x1 = 460, 900
            c.save(); c.rectangle(x0, y - 30, x1 - x0, 60); c.clip()
            xx = x0 - off
            state = 0
            pts.append((x0 - off, y + 14))
            while xx < x1:
                ya, yb2 = (y + 14, y - 14) if state == 0 else (y - 14, y + 14)
                nx = xx + P
                pts += [(xx, ya), (xx, yb2), (nx, yb2)]
                xx = nx; state ^= 1
            line(c, pts, alpha(hx("#7CFC9A"), on), 4)
            c.restore()
        # pulse travelling down to the next box
        if 0 < k < 16:
            kk = ramp(t, ON[k] - 0.25, ON[k])
            if 0 < kk < 1:
                glow(c, 180, y - LAD_DY + kk * LAD_DY, 40, YEL, 0.9)
    c.restore()
    tq = ON[4]
    kq = ramp(t, tq - 0.1, tq + 0.2) * (1 - ramp(t, ON[15] + 0.8, ON[15] + 1.2))
    if kq > 0:
        n = sum(1 for x in ON[1:] if t >= x)
        c.save(); c.translate(70, LAD_Y0 + 8 * LAD_DY); c.rotate(-math.pi / 2)
        text(c, f"{n} VECES", 0, 0, 36 * eob(kq), YEL, SLAB, False, outline=INK, olw=6); c.restore()
    tp = wt("paso3", "pulso") - 0.2
    kp = eob(ramp(t, tp, tp + 0.4))
    if kp > 0:
        y = LAD_Y0 + 16 * LAD_DY + 40
        c.save(); c.translate(540, y); c.scale(kp, kp)
        glow(c, 0, 0, 260, YEL, 0.4 * (0.7 + 0.3 * math.sin(t * 6)))
        rrect(c, -330, -42, 660, 84, 18); fill_stroke(c, YEL, INK, 6)
        text(c, "1 PULSO / SEGUNDO", 0, 18, 50, INK, SLAB, False)
        c.restore()


# ---------------------------------------------------------------- paso4: the stepper motor
P4_C2 = (620, 1360); P4_R2, P4_RP1, P4_R1, P4_RP0 = 150, 25, 110, 22
P4_C1 = (P4_C2[0] + 175 * math.cos(math.radians(218)), P4_C2[1] + 175 * math.sin(math.radians(218)))
P4_C0 = (P4_C1[0] + 132 * math.cos(math.radians(-104)), P4_C1[1] + 132 * math.sin(math.radians(-104)))

def p4_steps():
    return [wt("paso4", "pasito"), wt("paso4", "mueve"), wt("paso4", "tic")]

def steps_done(t, steps, d=0.22):
    return sum(ease(ramp(t, s, s + d)) for s in steps)

def scene_paso4(c, t):
    b = B("paso4")
    background(c, t, ORANGE)
    c.save(); cam(c, 1.0 + 0.04 * ramp(t, b["start"], b["end"]), 540, 1150)
    ST = p4_steps(); n = steps_done(t, ST)
    rot = math.pi * n; g1 = -rot * P4_RP0 / P4_R1; g2 = -g1 * P4_RP1 / P4_R2
    sec = 58 + n
    x0, y0 = P4_C0
    hl_g = ramp(t, wt("paso4", "engranaje") - 0.2, wt("paso4", "engranaje") + 0.1)
    # dial ring behind the seconds wheel
    cx2, cy2 = P4_C2
    for i in range(-4, 6):
        a = -math.pi / 2 + i * math.pi / 30; big = i % 5 == 0
        line(c, [(cx2 + (268 if big else 280) * math.cos(a), cy2 + (268 if big else 280) * math.sin(a)),
                 (cx2 + 296 * math.cos(a), cy2 + 296 * math.sin(a))], alpha(CREAM, 0.8), 8 if big else 4)
    gear(c, *P4_C2, P4_R2, g2, mix(BRASS, YEL, 0.5 * hl_g), 5)
    gear(c, *P4_C1, P4_R1, g1, mix(BRASS, YEL, 0.5 * hl_g), 5)
    gear(c, *P4_C1, P4_RP1 + 5, g1, mix(SILVER, YEL, 0.3 * hl_g), 4, n=8, spokes=False)
    # coil (pulses arrive from the chip)
    pulses = [s - 0.75 for s in ST]
    coil = max(pulse_at(t, p + 0.45, 0.8) for p in pulses)
    cy = 800
    if coil > 0: glow(c, 500, cy, 260, COPPER, 0.6 * coil)
    line(c, [(x0 - 72, x0 and y0), (x0 - 72, cy), (260, cy)], METAL, 36, cairo.LINE_CAP_BUTT)
    line(c, [(x0 + 72, y0), (x0 + 72, cy - 0), (760, cy)], METAL, 36, cairo.LINE_CAP_BUTT)
    line(c, [(760, cy), (820, cy)], METAL, 36, cairo.LINE_CAP_BUTT)
    line(c, [(260, cy), (260, cy - 1)], METAL, 36)
    circle(c, x0, y0, 100); fill_stroke(c, METAL, INK, 5)
    circle(c, x0, y0, 76); fill_stroke(c, DARK, None)
    rrect(c, 300, cy - 55, 440, 110, 18); fill_stroke(c, mix(COPPER, YEL, 0.5 * coil), INK, 6)
    for i in range(26):
        line(c, [(312 + i * 16.5, cy - 50), (318 + i * 16.5, cy + 50)], alpha(INK, 0.35), 3)
    # field lines while the coil is on
    if coil > 0.05:
        for k in range(3):
            c.new_path(); c.save(); c.translate(520, cy); c.scale(1, 0.45)
            c.arc(0, 0, 280 + k * 40, 0, 2 * math.pi); c.restore()
            c.save(); c.set_dash([14, 12], -t * 60); c.set_source_rgba(*alpha(YEL, 0.5 * coil)); c.set_line_width(4); c.stroke(); c.restore()
        pol = len([s for s in ST if t >= s - 0.3]) % 2
        for sx, lab in ((x0 - 92, "N" if pol else "S"), (x0 + 92, "S" if pol else "N")):
            text(c, lab, sx + (-40 if sx < x0 else 40), y0 + 14, 40, alpha(RED if lab == "N" else XRAY, coil), SLAB, False, outline=INK, olw=6)
    # chip and wire
    rrect(c, 70, 640, 140, 90, 12); fill_stroke(c, mix(DARK, LAV, 0.25), LAV, 4); text(c, "CHIP", 140, 698, 32, CREAM, SANS, True)
    wire = [(210, 685), (290, 685), (290, cy - 30), (300, cy - 30)]
    line(c, wire, hx("#E8C26A"), 6)
    for p in pulses: travel(c, wire, ramp(t, p, p + 0.45))
    # rotor (permanent magnet, steps 180°)
    gear(c, x0, y0, P4_RP0 + 4, rot, SILVER, 3, n=8, spokes=False)
    c.save(); c.translate(x0, y0); c.rotate(rot)
    c.new_path(); c.arc(0, 0, 62, -math.pi / 2, math.pi / 2); c.close_path(); fill_stroke(c, RED, None)
    c.new_path(); c.arc(0, 0, 62, math.pi / 2, 3 * math.pi / 2); c.close_path(); fill_stroke(c, STEEL, None)
    circle(c, 0, 0, 62); fill_stroke(c, None, INK, 5)
    text(c, "N", 30, 13, 34, WHITE, SLAB, False); text(c, "S", -30, 13, 34, WHITE, SLAB, False)
    circle(c, 0, 0, 10); fill_stroke(c, SILVER, INK, 3)
    c.restore()
    # second hand
    a = -math.pi / 2 + sec * math.pi / 30
    line(c, [(cx2 - 60 * math.cos(a), cy2 - 60 * math.sin(a)), (cx2 + 290 * math.cos(a), cy2 + 290 * math.sin(a))], RED, 10)
    circle(c, cx2, cy2, 20); fill_stroke(c, RED, INK, 4)
    c.restore()
    callout(c, "MOTOR", 360, cy - 40, 200, 870, t, wt("paso4", "motorcito"))
    callout(c, "IMÁN", x0 - 40, y0 + 30, 180, 1180, t, wt("paso4", "pasito") - 0.1, YEL)
    callout(c, "ENGRANAJE", P4_C1[0] - 40, P4_C1[1] + 60, 200, 1460, t, wt("paso4", "engranaje"))
    callout(c, "SEGUNDERO", cx2 + 4, cy2 - 120, 850, 1610, t, wt("paso4", "segundero"), HOT)
    tt = ST[2]
    kt = ramp(t, tt, tt + 0.3)
    if kt > 0:
        s = eob(kt) * (1 + 0.1 * pulse_at(t, tt, 0.4))
        c.save(); c.translate(860, 990); c.rotate(-0.12); c.scale(s, s)
        text(c, "¡TIC!", 0, 30, 110, YEL, SLAB, False, outline=INK, olw=14); c.restore()


# ---------------------------------------------------------------- paso5: 32.768 = 2^15
def pow_text(c, x, y, k, size=120):
    """'32.768 = 2^15' centred at x."""
    font(c, SLAB, size); w1 = c.text_extents("32.768 = 2").x_advance
    font(c, SLAB, size * 0.55); w2 = c.text_extents("15").x_advance
    x0 = x - (w1 + w2) / 2
    text(c, "32.768 =", x0, y, size, YEL, SLAB, False, "l", outline=INK, olw=12)
    if k > 0:
        font(c, SLAB, size); wa = c.text_extents("32.768 = ").x_advance
        text(c, "2", x0 + wa, y, size, alpha(WHITE, k), SLAB, False, "l", outline=alpha(INK, k), olw=12)
        text(c, "15", x0 + w1 + 4, y - size * 0.48, size * 0.55, alpha(HOT, k), SLAB, False, "l", outline=alpha(INK, k), olw=10)

def scene_paso5(c, t):
    b = B("paso5")
    background(c, t, YEL)
    c.save(); cam(c, 1.0 + 0.03 * ramp(t, b["start"], b["end"]), 540, 1150)
    t_num = b["start"] - 0.1; t_raro = wt("paso5", "raro") - 0.1; t_dos = wt("paso5", "2") if any(w["word"] == "2" for w in WORDS if w["beat"] == "paso5") else wt("paso5", "dos")
    t_mul = wt("paso5", "multiplicado"); t_q = wt("paso5", "veces") + 0.1
    t_mit = wt("paso5", "partiendo"); t_seg = wt("paso5", "segundo") - 0.1
    k0 = eob(ramp(t, t_num, t_num + 0.35))
    if k0 > 0:
        c.save(); c.translate(540, 720); c.scale(k0, k0)
        if t < t_dos - 0.1:
            text(c, "32.768", 0, 40, 130, YEL, SLAB, False, outline=INK, olw=12)
            kr = eob(ramp(t, t_raro, t_raro + 0.3))
            if kr > 0: text(c, "?", 280, 0, 90 * kr, HOT, SLAB, False, outline=INK, olw=10)
        else:
            pow_text(c, 0, 40, ease(ramp(t, t_dos - 0.1, t_dos + 0.3)))
        c.restore()
    # staircase 1, 2, 4, ... 32.768 (15 doublings)
    T_up = [t_mul - 0.2 + i * (t_q - t_mul + 0.2) / 15 for i in range(16)]
    T_up[0] = t_dos - 0.1
    T_dn = [t_mit + (t_seg - t_mit) * (15 - i) / 15 for i in range(16)]
    for i in range(16):
        k = eob(ramp(t, T_up[i], T_up[i] + 0.25))
        if k <= 0.02: continue
        x = 140 + i * 45; y = 1610 - i * 46
        dn = t >= T_dn[i] - 0.05
        cur = 0 <= t - T_dn[i] < 0.35 if t >= t_mit else False
        col = YEL if (i == 15 and t < t_mit) or (i == 0 and t >= T_dn[0]) else (mix(CREAM, LAV, 0.4) if dn and i > 0 else CREAM)
        c.save(); c.translate(x, y); c.scale(k, k)
        rrect(c, -10, -20, 150, 40, 8); fill_stroke(c, col, INK, 4)
        text(c, dots(2 ** i), 65, 11, 26, INK, MONO, True)
        c.restore()
        if cur: glow(c, x + 65, y, 110, YEL, 0.7)
        if i > 0 and k > 0.5 and t < t_mit:
            text(c, "×2", x - 26, y + 28, 20, alpha(HOT, 0.9), SANS, True)
        if i < 15 and t >= T_dn[i] - 0.05 and t >= t_mit:
            text(c, "÷2", x + 172, y - 16, 22, alpha(XRAY, 0.9), SANS, True)
    kq = ramp(t, t_q - 0.2, t_q + 0.2) * (1 - ramp(t, t_mit - 0.4, t_mit - 0.1))
    if kq > 0: text(c, "15 VECES ×2", 760, 1450, 54 * eob(kq), HOT, SLAB, False, outline=INK, olw=8)
    km = ramp(t, t_mit - 0.2, t_mit + 0.2)
    if km > 0 and t < t_seg + 0.2: text(c, "15 VECES ÷2", 760, 1450, 54 * eob(km), XRAY, SLAB, False, outline=INK, olw=8)
    ks = eob(ramp(t, t_seg, t_seg + 0.35))
    if ks > 0:
        c.save(); c.translate(760, 1460); c.scale(ks, ks)
        rrect(c, -200, -60, 400, 120, 22); fill_stroke(c, YEL, INK, 6)
        text(c, "= 1 SEGUNDO", 0, 20, 52, INK, SLAB, False)
        c.restore()
    c.restore()


# ---------------------------------------------------------------- junto + acelera
def div_strip(c, t, k_on, y=1645):
    if k_on <= 0: return
    at = anim_time(t)
    for i in range(15):
        x = 175 + i * 50
        f = F_Q / 2 ** (i + 1)
        if vis_freq(f, t) > 6: lit = 0.5
        else: lit = 1.0 if (math.floor(2 * f * at) % 2) else 0.15
        rrect(c, x - 20, y - 20, 40, 40, 8); fill_stroke(c, mix(DARK, YEL, lit * k_on), alpha(INK, k_on), 3)
    text(c, "÷2 ×15", 175 + 7 * 50, y + 62, 28, alpha(CREAM, k_on), SANS, True)

def junto_rot(t):
    st = [wt("junto", "tic")]
    return st

def scene_junto(c, t):
    background(c, t, YEL)
    b = B("junto"); end = B("remate")["start"]
    fast = ease(ramp(t, T_REAL + 0.2, end - 0.4))
    shake = 7 * fast
    push = 1.0 + 0.04 * ease(ramp(t, b["start"], end))
    s = MV_S * push
    at = anim_time(t); t_tic = wt("junto", "tic")
    # tic: one step on the word, then real-speed ticks once per second of physical time
    n = ease(ramp(t, t_tic, t_tic + 0.2)) + max(0.0, tickv(at - anim_time(T_REAL)) + 1 if t > T_REAL else 0.0)
    sec = S0 + 3 + n
    hl = set()
    for w, p in (("pila", "pila"), ("chip", "chip"), ("cuarzo", "cuarzo"), ("vibración", "vib"), ("división", "div"), ("tic", "tic")):
        if wt("junto", w) - 0.1 <= t < (end if p in ("vib",) else wt("junto", "tic") + 1.0): hl.add(p)
    if fast > 0.2: hl = {"vib"}
    vib = 5.0 * ramp(t, wt("junto", "vibración") - 0.2, wt("junto", "vibración") + 0.2)
    coil = pulse_at(t, t_tic - 0.1, 0.5)
    c.save()
    c.translate(shake * math.sin(t * 61), shake * math.cos(t * 53))
    movement(c, t, WX, WY, s, hl=hl, see=1.0, vib=vib, rotor=math.pi * n, coil=coil, sec=sec, hand_a=1.0, fast=fast)
    c.restore()
    div_strip(c, t, ramp(t, wt("junto", "división") - 0.2, wt("junto", "división") + 0.1))
    if fast < 0.3:
        c.push_group()
        callout(c, "PILA", *mv_pt((BAT[0] - 60, BAT[1] + 40), WX, WY, s), 160, 1480, t, wt("junto", "pila"))
        callout(c, "CHIP", *mv_pt((CHIP[0] - 30, CHIP[1] - 20), WX, WY, s), 200, 690, t, wt("junto", "chip"))
        callout(c, "CUARZO", *mv_pt((CRY[0] - 30, CRY[1] - 15), WX, WY, s), 520, 650, t, wt("junto", "cuarzo"))
        callout(c, "VIBRACIÓN", *mv_pt((CRY[0] + 50, CRY[1] - 5), WX, WY, s), 820, 730, t, wt("junto", "vibración"), YEL)
        callout(c, "DIVISIÓN", *mv_pt((CHIP[0] + 40, CHIP[1] + 30), WX, WY, s), 230, 1100, t, wt("junto", "división"), YEL)
        callout(c, "TIC", *mv_pt((ROT[0] + 20, ROT[1] + 25), WX, WY, s), 860, 1500, t, wt("junto", "tic"), HOT)
        c.pop_group_to_source(); c.paint_with_alpha(1 - fast / 0.3)
    if fast > 0:
        for i in range(26):
            r0 = 300 + (i * 97 + t * 2600) % 900; a = i * 0.24
            line(c, [(540 + math.cos(a) * r0, 1130 + math.sin(a) * r0), (540 + math.cos(a) * (r0 + 130 * fast), 1130 + math.sin(a) * (r0 + 130 * fast))],
                 alpha(WHITE, 0.35 * fast), 5)
    flash = ramp(t, end - 0.45, end - 0.3) * (1 - ramp(t, end - 0.3, end - 0.1))
    if flash > 0: c.set_source_rgba(1, 1, 1, 0.85 * flash); c.paint()


# ---------------------------------------------------------------- remate: you can't hear it
def ear(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    skin = hx("#F0A57E")
    c.new_path(); c.move_to(40, -150)
    c.curve_to(-90, -170, -140, -40, -95, 40); c.curve_to(-70, 90, -60, 150, -10, 165); c.curve_to(40, 175, 60, 120, 30, 90)
    c.curve_to(10, 70, 70, 30, 85, -40); c.curve_to(100, -110, 80, -145, 40, -150); c.close_path()
    fill_stroke(c, skin, INK, 7)
    c.new_path(); c.move_to(30, -110); c.curve_to(-50, -120, -75, -40, -45, 20); c.curve_to(-30, 60, 10, 50, 20, 10)
    c.set_source_rgba(*mix(skin, RUST, 0.5)); c.set_line_width(12); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    circle(c, 0, -10, 26); fill_stroke(c, mix(skin, INK, 0.45), None)
    c.restore()

def scene_remate(c, t):
    b = B("remate")
    background(c, t, COLD)
    c.save(); cam(c, 1.0 + 0.05 * ramp(t, b["start"], T_LOOP), 540, 1150)
    t_v = wt("remate", "vibración") - 0.15; t_ag = wt("remate", "aguda") - 0.1
    t_oi = wt("remate", "oído") - 0.15; t_no = wt("remate", "oír") - 0.1; t_bro = wt("remate", "ni") - 0.1
    ex, ey = 230, 840; fx, fy = 820, 900
    ke = eob(ramp(t, b["start"] - 0.1, b["start"] + 0.3))
    ear(c, ex, ey, 1.15 * ke)
    # quartz fork, real speed: blur
    kf = eob(ramp(t, t_v, t_v + 0.35))
    if kf > 0:
        glow(c, fx, fy - 60, 160, XRAY, 0.5 * kf)
        c.save(); c.translate(fx, fy); c.scale(kf, kf)
        for sg in (-1, 1): fork_shape(c, 190, 30, 24, sg * 9, 110, 50, QUARTZ, 4, True, 0.55)
        c.restore()
        text(c, "32.768 Hz", fx, fy + 110, 48, YEL, SLAB, False, outline=INK, olw=8)
    # very dense sound waves towards the ear
    kw = ramp(t, t_ag - 0.2, t_ag + 0.3)
    if kw > 0:
        c.save(); c.rectangle(ex + 120, 600, fx - ex - 220, 600); c.clip()
        sp = 14
        for i in range(40):
            r = ((t * 260 + i * sp) % (40 * sp)) + 80
            aa = kw * (1 - r / (40 * sp + 80)) * 0.8
            c.new_path(); c.arc(fx, fy - 60, r, math.pi * 0.82, math.pi * 1.18)
            c.set_source_rgba(*alpha(XRAY, aa)); c.set_line_width(4); c.stroke()
        c.restore()
        text(c, "MUY AGUDA", 540, 1080, 50 * eob(kw), XRAY, SLAB, False, outline=INK, olw=8)
    # hearing range bar (linear, 0 .. 36.000 Hz)
    kb = ease(ramp(t, t_oi, t_oi + 0.5))
    if kb > 0:
        X0, X1, Y = 110, 910, 1290
        fx_ = lambda f: X0 + (X1 - X0) * f / 36000
        line(c, [(X0, Y), (lerp(X0, X1, kb), Y)], alpha(LAV, 0.6), 6)
        for f in range(0, 36001, 5000):
            if fx_(f) <= lerp(X0, X1, kb): line(c, [(fx_(f), Y - 10), (fx_(f), Y + 10)], alpha(LAV, 0.6), 3)
        x20 = fx_(20); x20k = fx_(20000)
        rrect(c, x20, Y - 30, (x20k - x20) * kb, 60, 14); fill_stroke(c, GREEN, INK, 5)
        if kb > 0.9:
            text(c, "LO QUE OYES", (x20 + x20k) / 2, Y + 12, 32, WHITE, SANS, True, outline=INK, olw=5)
            text(c, "20 Hz", x20 + 10, Y + 80, 34, CREAM, SANS, True)
            text(c, "20.000 Hz", x20k, Y + 80, 34, CREAM, SANS, True)
            line(c, [(x20k, Y + 32), (x20k, Y + 46)], CREAM, 4)
        kn = eob(ramp(t, t_no, t_no + 0.35))
        if kn > 0:
            xq = fx_(F_Q)
            c.save(); c.translate(xq, Y); c.scale(kn, kn)
            c.new_path(); c.move_to(0, -38); c.line_to(-22, -80); c.line_to(22, -80); c.close_path(); fill_stroke(c, YEL, INK, 4)
            circle(c, 0, 0, 16); fill_stroke(c, YEL, INK, 4)
            c.restore()
            text(c, "32.768 Hz", xq - 30, Y - 100, 38, YEL, SLAB, False, outline=INK, olw=7)
            xmark(c, ex, ey, 110, t, t_no + 0.1, 20)
    kx = eob(ramp(t, t_bro, t_bro + 0.35))
    if kx > 0:
        c.save(); c.translate(540, 1530); c.rotate(-0.05); c.scale(kx, kx)
        text(c, "NO LO OYES", 0, 0, 110, HOT, SLAB, False, outline=INK, olw=14); c.restore()
    c.restore()


# ================================================================ timeline
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
    ps = [wt("imposible", w) - 0.15 for w in ("péndulo", "muelle", "nadie")] + [wt("imposible", "apenas") - 0.1]
    ps += [wt("paso1", w) for w in ("pila", "chip", "cuarzo")] + [wt("paso1", "diapasón") + 0.45, wt("paso1", "grano") - 0.15]
    ps += [wt("paso2", "dobla") - 0.1, wt("paso2", "electricidad", 1) - 0.1, wt("paso2", "empujoncito"), wt("paso2", "vibra") - 0.1]
    ps += [wt("paso3", "pulso") - 0.2]
    ps += [wt("paso4", w) for w in ("motorcito", "engranaje", "segundero")]
    ps += [wt("paso5", "raro") - 0.1, wt("paso5", "segundo") - 0.1]
    ps += [wt("junto", w) for w in ("pila", "chip", "cuarzo", "vibración", "división")]
    ps += [wt("remate", "vibración") - 0.15, wt("remate", "oír") - 0.1, wt("remate", "ni") - 0.1]
    return ps


def tick_times():
    """Every second-hand step that is animated."""
    ts = []
    prev = math.floor(anim_time(0.0))
    x = 0.0
    while x < B("freno")["end"] + 0.6:
        x += 1 / 30; n = math.floor(anim_time(x))
        if n != prev: ts.append(x); prev = n
    ts += p4_steps() + [wt("junto", "tic")]
    x = T_REAL; a0 = anim_time(T_REAL); prev = 0
    while x < B("remate")["start"] - 0.15:
        x += 1 / 30; n = math.floor(anim_time(x) - a0)
        if n != prev: ts.append(x); prev = n
    return ts


def SFX(put, L):
    np_ = __import__("numpy")
    for tt in tick_times(): put(L["click"](), tt, 0.9)
    for tt in row_on_times()[1:]: put(L["click"](), tt, 0.35)
    def hum(d, f=7040, g=1.0):
        n = int(d * L["SR"]); x = L["tone"](f, d, 0.3) * (1 + 0.3 * np_.sin(2 * np_.pi * 9 * L["t_"](n)))
        return x * 0.05 * g
    for tt in (wt("gancho", "vibra") - 0.1, wt("paso2", "vibra") - 0.3, wt("junto", "vibración") - 0.1, wt("remate", "aguda") - 0.2):
        put(L["shimmer"](), tt, 0.25)
    put(hum(3.0), 0.8, 0.6)
    put(hum(3.0, 7460), wt("paso2", "empujoncito") + 0.2, 0.6)
    put(hum(4.5, 7900), T_REAL + 0.1, 0.8)
    for tt in [wt("paso2", "electricidad") - 0.4, wt("paso2", "electricidad", 1), wt("paso2", "empujoncito") - 0.3]:
        put(L["zap"](0.35), tt, 0.25)
    put(L["ding"](), wt("paso3", "pulso") - 0.2, 0.3)
    put(L["ding"](2093), wt("paso5", "segundo") - 0.1, 0.3)


# ================================================================ thumbnails
def _thumb_watch(c, cx, cy, s):
    """Open movement with half the dial still on, and a glowing quartz fork."""
    movement(c, 2.0, cx, cy, s, hl=(), see=1.0, sec=S0)
    c.save(); c.translate(cx, cy); c.scale(s, s)
    c.save(); c.new_path(); c.move_to(-400, -400); c.line_to(-400, 400); c.line_to(-30, 400); c.line_to(30, -400); c.close_path(); c.clip()
    watch_face(c, 0.0, S0, strap_a=0.0, face_a=1.0)
    c.restore()
    c.restore()

def _thumb_fork(c, x, y, s):
    glow(c, x, y - 160 * s, 360 * s, XRAY, 0.8); glow(c, x, y - 160 * s, 200 * s, WHITE, 0.4)
    c.save(); c.translate(x, y); c.scale(s, s)
    for sg in (-1, 1): fork_shape(c, 330, 52, 40, sg * 16, 190, 80, QUARTZ, 7, True, 0.55)
    fork_shape(c, 330, 52, 40, 0, 190, 80, QUARTZ, 7, True, 0.9)
    c.restore()
    for i in range(3):
        for sg in (-1, 1):
            c.new_path(); c.arc(x, y - 200 * s, (190 + i * 50) * s, -math.pi / 2 + sg * 0.5 - 0.3, -math.pi / 2 + sg * 0.5 + 0.3)
            c.set_source_rgba(*alpha(XRAY, 0.8 - 0.2 * i)); c.set_line_width(9 * s); c.stroke()

def THUMB_V(c):
    background(c, 3.0, XRAY)
    _thumb_watch(c, 540, 1300, 1.25)
    _thumb_fork(c, 560, 1330, 1.05)
    for i, (ln, col) in enumerate([("CRISTAL", WHITE), ("VIBRANDO", YEL)]):
        sz = fit_size(c, ln, SLAB, 200, 980)
        text(c, ln, 540, 380 + i * 220, sz, col, SLAB, False, outline=INK, olw=24)

def THUMB_H(c):
    g = cairo.LinearGradient(0, 0, 0, 720); g.add_color_stop_rgba(0, *BG_TOP); g.add_color_stop_rgba(1, *BG_BOT); c.set_source(g); c.paint()
    glow(c, 960, 380, 420, XRAY, 0.3)
    _thumb_watch(c, 950, 380, 0.92)
    _thumb_fork(c, 960, 420, 0.7)
    for i, (ln, col) in enumerate([("CRISTAL", WHITE), ("VIBRANDO", YEL)]):
        sz = min(fit_size(c, w, SLAB, 130, 560) for w in ("CRISTAL", "VIBRANDO"))
        text(c, ln, 300, 330 + i * 150, sz, col, SLAB, False, outline=INK, olw=20)
