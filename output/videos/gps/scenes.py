"""¿Cómo sabe tu móvil dónde estás? (GPS)  Illustrations (pycairo only). Contract: output/engine/SCENES_GUIDE.md"""
from core import *  # noqa

# ---------------------------------------------------------------- colours of this video
SKIN = hx("#F2C6A0"); SKIN2 = hx("#D9A47E")
OCEAN = hx("#2F6BD0"); OCEAN2 = hx("#1D4A9E"); LAND = hx("#4C9A5A"); LAND2 = hx("#3B7E48")
MAPBG = hx("#EEE6D0"); ROAD = hx("#FFFFFF"); ROADE = hx("#C9BFA6"); PARK = hx("#9BCB8A"); RIVER = hx("#8EC3F0")
DOT = hx("#2F80FF"); FOIL = hx("#E0A646"); PANEL = hx("#3355A0")
BLD = hx("#33304A"); BLD2 = hx("#2A2740")

def tfast(t):
    """Stylised animation clock: runs ~30x faster during the acelerón."""
    t0 = T_REAL + 0.2; t1 = B("remate")["start"] - 0.4
    if t <= t0: return t
    acc, x = 0.0, t0
    while x < t:
        dx = min(0.05, t - x); acc += dx * 30 * ease(ramp(x, t0, t1)); x += dx
    return t + acc

def FAST(t): return ease(ramp(t, T_REAL + 0.2, B("remate")["start"] - 0.4))

def tt(beat, w, nth=0, end=False):
    return wt(beat, w, nth, end)


# ---------------------------------------------------------------- drawing pieces
def clockface(c, x, y, r, sec=0.0, wob=0.0, rim=CREAM, hl=0.0, digital=None):
    """Analog clock showing 12:00:sec. wob = jitter of the hands (a bad clock)."""
    c.new_path()
    if hl > 0: glow(c, x, y, r * 1.9, YEL, 0.5 * hl)
    circle(c, x, y, r); fill_stroke(c, rim, INK, max(2, r * 0.12))
    circle(c, x, y, r * 0.82); fill_stroke(c, WHITE, None)
    for i in range(12):
        a = i * math.pi / 6; r0 = r * (0.62 if i % 3 == 0 else 0.7)
        line(c, [(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r * 0.78 * math.cos(a), y + r * 0.78 * math.sin(a))], INK, max(1.5, r * (0.07 if i % 3 == 0 else 0.04)))
    up = -math.pi / 2
    line(c, [(x, y), (x + r * 0.42 * math.cos(up + wob * 0.3), y + r * 0.42 * math.sin(up + wob * 0.3))], INK, max(2, r * 0.11))
    line(c, [(x, y), (x + r * 0.62 * math.cos(up + wob * 0.5), y + r * 0.62 * math.sin(up + wob * 0.5))], INK, max(2, r * 0.08))
    a = up + 2 * math.pi * sec / 60 + wob
    line(c, [(x - r * 0.15 * math.cos(a), y - r * 0.15 * math.sin(a)), (x + r * 0.72 * math.cos(a), y + r * 0.72 * math.sin(a))], RED, max(1.5, r * 0.05))
    circle(c, x, y, max(2, r * 0.08)); c.set_source_rgba(*RED); c.fill()

def atom(c, x, y, r, col=COLD, lw=5):
    for k in range(3):
        c.save(); c.translate(x, y); c.rotate(k * math.pi / 3); c.scale(1, 0.36)
        c.new_path(); c.arc(0, 0, r, 0, 2 * math.pi); c.restore()
        c.set_source_rgba(*col); c.set_line_width(lw); c.stroke()
    circle(c, x, y, r * 0.2); fill_stroke(c, RED, INK, 2)

def satellite(c, x, y, s, sec=0.0, rot=-0.15, hl=0.0, dim=0.0, clock=True):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    if hl > 0: glow(c, 0, 0, 220, YEL, 0.55 * hl)
    for side in (-1, 1):
        line(c, [(side * 36, 0), (side * 62, 0)], INK, 9)
        x0 = 58 if side > 0 else -138
        rrect(c, x0, -30, 80, 60, 6); fill_stroke(c, PANEL, INK, 6)
        for k in (1, 2, 3):
            line(c, [(x0 + 20 * k, -26), (x0 + 20 * k, 26)], alpha(XRAY, 0.55), 2.5)
        line(c, [(x0 + 4, 0), (x0 + 76, 0)], alpha(XRAY, 0.55), 2.5)
    # dish + antenna
    c.new_path(); c.move_to(-22, 44); c.curve_to(-14, 70, 14, 70, 22, 44); c.close_path(); fill_stroke(c, CREAM2, INK, 5)
    line(c, [(0, 52), (0, 74)], INK, 4)
    rrect(c, -40, -46, 80, 92, 10); fill_stroke(c, FOIL, INK, 6)
    line(c, [(-30, -36), (30, -36)], alpha(WHITE, 0.35), 4)
    if clock: clockface(c, 0, 2, 27, sec, rim=CREAM)
    if dim > 0:
        c.set_operator(cairo.OPERATOR_ATOP)
        c.restore(); return
    c.restore()

def house(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.new_path(); c.move_to(-50, 0); c.line_to(0, -42); c.line_to(50, 0); c.close_path(); fill_stroke(c, RED, INK, 5)
    rrect(c, -38, 0, 76, 56, 4); fill_stroke(c, CREAM2, INK, 5)
    rrect(c, -10, 20, 20, 36, 3); fill_stroke(c, GOLD, INK, 3)
    c.restore()

def pin(c, x, y, s=1.0, col=RED):
    """Map pin with its tip at (x, y)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    c.new_path(); c.move_to(0, 0); c.curve_to(-18, -30, -40, -52, -40, -80)
    c.arc(0, -80, 40, math.pi, 2 * math.pi); c.curve_to(40, -52, 18, -30, 0, 0); c.close_path()
    fill_stroke(c, col, INK, 6)
    circle(c, 0, -80, 15); fill_stroke(c, WHITE, INK, 4)
    c.restore()

def map_view(c, x, y, w, h, t, dot=1.0, pinv=0.0, blur=0.0, lw=1.0, dot_at=(0.5, 0.56)):
    """Simple street map filling (x, y, w, h). Coordinates in fractions of the box."""
    c.new_path(); c.set_source_rgba(*MAPBG); c.rectangle(x, y, w, h); c.fill()
    def P(u, v): return (x + u * w, y + v * h)
    rrect(c, *P(0.06, 0.08), 0.34 * w, 0.24 * h, 10 * lw); fill_stroke(c, PARK, None)
    rrect(c, *P(0.62, 0.70), 0.32 * w, 0.22 * h, 10 * lw); fill_stroke(c, hx("#E2D6B8"), None)
    rrect(c, *P(0.10, 0.70), 0.28 * w, 0.20 * h, 10 * lw); fill_stroke(c, hx("#E2D6B8"), None)
    line(c, [P(-0.1, 0.40), P(0.3, 0.36), P(0.6, 0.47), P(1.1, 0.40)], RIVER, 16 * lw)
    roads = [[P(-0.1, 0.56), P(1.1, 0.56)], [P(0.5, -0.1), P(0.5, 1.1)], [P(-0.1, 0.18), P(1.1, 0.26)],
             [P(0.18, -0.1), P(0.24, 1.1)], [P(0.80, -0.1), P(0.76, 1.1)], [P(-0.1, 0.92), P(1.1, 0.84)]]
    for r_ in roads: line(c, r_, ROADE, 20 * lw)
    for r_ in roads: line(c, r_, ROAD, 13 * lw)
    dx, dy = P(*dot_at)
    if blur > 0:  # position smeared over a wide area
        glow(c, dx, dy, blur, DOT, 0.55)
        circle(c, dx, dy, blur * 0.72); c.set_source_rgba(*alpha(DOT, 0.9)); c.set_line_width(3 * lw)
        c.set_dash([10 * lw, 8 * lw]); c.stroke(); c.set_dash([])
    if dot > 0:
        ph = (t * 0.8) % 1
        circle(c, dx, dy, (14 + 40 * ph) * lw); c.set_source_rgba(*alpha(DOT, 0.35 * (1 - ph) * dot)); c.fill()
        circle(c, dx, dy, 15 * lw * dot); fill_stroke(c, DOT, WHITE, 5 * lw)
    if pinv > 0:
        pin(c, dx, dy - 4 * lw, 0.75 * lw * pinv)
    return dx, dy

def airplane(c, x, y, s, col=INK):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-math.pi / 2)
    c.new_path()
    pts = [(46, 0), (36, -5), (8, -6), (-8, -36), (-18, -36), (-8, -6), (-30, -5), (-38, -16), (-46, -16), (-40, 0),
           (-46, 16), (-38, 16), (-30, 5), (-8, 6), (-18, 36), (-8, 36), (8, 6), (36, 5)]
    c.move_to(*pts[0])
    for p in pts[1:]: c.line_to(*p)
    c.close_path(); c.set_source_rgba(*col); c.fill()
    c.restore()

def phone(c, x, y, s, t, screen="map", dot=1.0, pinv=0.0, blur=0.0, airplane_on=0.0, flash=0.0, clock_wob=0.0, clock_hl=0.0):
    """Smartphone centred at (x, y); 260x500 at s=1."""
    c.save(); c.translate(x, y); c.scale(s, s)
    w, h = 260, 500
    shadow(c, lambda: rrect(c, -w / 2, -h / 2, w, h, 40), 10, 14, 0.4)
    rrect(c, -w / 2, -h / 2, w, h, 40); fill_stroke(c, DARK, INK, 7)
    rrect(c, -w / 2 + 8, -h / 2 + 8, w - 16, 20, 10); c.set_source_rgba(1, 1, 1, 0.08); c.fill()
    sx, sy, sw, sh = -w / 2 + 14, -h / 2 + 40, w - 28, h - 84
    c.save(); rrect(c, sx, sy, sw, sh, 14); c.clip()
    if screen == "map":
        map_view(c, sx, sy, sw, sh, t, dot, pinv, blur)
    else:
        c.set_source_rgba(*NIGHT); c.paint()
        clockface(c, 0, -10, 88, 0, clock_wob, hl=clock_hl)
        text(c, "12:00:00", 0, 140, 34, CREAM, MONO, True)
    # status bar
    c.set_source_rgba(*alpha(INK, 0.75)); c.rectangle(sx, sy, sw, 30); c.fill()
    text(c, "12:00", sx + 12, sy + 22, 18, WHITE, SANS, True, "l")
    if airplane_on > 0.5:
        airplane(c, sx + sw - 22, sy + 15, 0.30, YEL)
    else:
        for i in range(4):
            c.set_source_rgba(1, 1, 1, 0.9); c.rectangle(sx + sw - 50 + i * 9, sy + 22 - 4 - i * 4, 6, 4 + i * 4); c.fill()
    if flash > 0: c.set_source_rgba(*alpha(YEL, 0.5 * flash)); c.paint()
    c.restore()
    rrect(c, sx, sy, sw, sh, 14); fill_stroke(c, None, INK, 4)
    rrect(c, -34, -h / 2 + 16, 68, 12, 6); fill_stroke(c, INK, None)
    rrect(c, -40, h / 2 - 30, 80, 10, 5); c.set_source_rgba(1, 1, 1, 0.25); c.fill()
    c.restore()

def hand_back(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -70, 230, 170, 560, 60); fill_stroke(c, SKIN, INK, 7)          # wrist / arm
    rrect(c, -40, 600, 230, 300, 40); fill_stroke(c, hx("#3A4470"), INK, 7)  # sleeve
    c.save(); c.translate(15, 225); c.scale(1, 0.75); c.new_path(); c.arc(0, 0, 150, 0, 2 * math.pi); c.restore()
    fill_stroke(c, SKIN, INK, 7)
    c.restore()

def hand_front(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s)
    for i, fy in enumerate((40, 105, 170)):  # fingers wrapping the left edge
        rrect(c, -166, fy, 58, 52, 24); fill_stroke(c, SKIN, INK, 6)
        line(c, [(-128, fy + 12), (-128, fy + 40)], alpha(SKIN2, 0.9), 4)
    c.save(); c.translate(140, 150); c.rotate(-0.5)  # thumb over the right edge
    rrect(c, -30, -26, 98, 54, 26); fill_stroke(c, SKIN, INK, 6)
    rrect(c, -18, -16, 30, 30, 10); fill_stroke(c, hx("#F7D9C0"), None)
    c.restore()
    c.restore()

CONT = [(0.0, 0.62, 0.30), (0.28, 0.48, 0.28), (0.18, 0.12, 0.26), (0.36, -0.22, 0.30), (0.26, -0.55, 0.22),
        (-1.55, 0.55, 0.33), (-1.35, 0.25, 0.24), (-1.15, -0.25, 0.30), (-1.05, -0.62, 0.20),
        (1.55, 0.62, 0.38), (1.85, 0.42, 0.33), (2.2, 0.15, 0.24), (2.55, -0.45, 0.24), (-0.6, 0.95, 0.25)]

def earth(c, x, y, R, rot=0.25, hl=0.0):
    c.new_path()
    glow(c, x, y, R * 1.35, XRAY, 0.35 + 0.2 * hl)
    circle(c, x, y, R)
    g = cairo.RadialGradient(x - R * 0.35, y - R * 0.4, R * 0.1, x, y, R)
    g.add_color_stop_rgba(0, *mix(OCEAN, XRAY, 0.25)); g.add_color_stop_rgba(1, *OCEAN2)
    c.set_source(g); c.fill_preserve(); c.save(); c.clip()
    for lon, lat, r in CONT:
        l = lon + rot; vis = math.cos(lat) * math.cos(l)
        if vis < -0.15: continue
        px = x + R * math.cos(lat) * math.sin(l); py = y - R * math.sin(lat)
        c.save(); c.translate(px, py); c.scale(max(0.2, math.cos(l)), max(0.35, math.cos(lat)))
        c.new_path(); c.arc(0, 0, r * R, 0, 2 * math.pi); c.restore()
        c.set_source_rgba(*LAND); c.fill()
    sh = cairo.RadialGradient(x - R * 0.4, y - R * 0.45, R * 0.6, x - R * 0.2, y - R * 0.2, R * 1.5)
    sh.add_color_stop_rgba(0, 0, 0, 0, 0); sh.add_color_stop_rgba(1, 0, 0, 0, 0.5)
    c.set_source(sh); c.paint()
    c.restore()
    circle(c, x, y, R); fill_stroke(c, None, INK, 6)

# orbit system: 3 main planes + 3 faint ones; 6 big satellites, ~30 in total
ORB = [(-0.38, 2.15, 0.55), (0.02, 2.25, 0.42), (0.40, 2.05, 0.60), (-0.85, 1.95, 0.5), (0.85, 2.0, 0.45), (-0.12, 1.85, 0.75)]
BIGS = [(0, 3.75), (0, 0.95), (1, 2.25), (1, 5.35), (2, 4.05), (2, 1.45)]

def orb_pt(cx, cy, R, i, u):
    tilt, rx, ry = ORB[i]
    ex, ey = rx * R * math.cos(u), ry * R * math.sin(u)
    return cx + ex * math.cos(tilt) - ey * math.sin(tilt), cy + ex * math.sin(tilt) + ey * math.cos(tilt)

def orbit_arc(c, cx, cy, R, i, front, col, lw):
    n = 60; u0 = 0 if front else math.pi
    pts = [orb_pt(cx, cy, R, i, u0 + math.pi * k / n) for k in range(n + 1)]
    line(c, pts, col, lw)

def earth_system(c, cx, cy, R, t, extra=0.0, hl=None, sec=0.0, dot=None, rings=1.0):
    """Earth + orbit rings + 6 big satellites. Returns screen positions of the big satellites."""
    hl = hl or {}
    pos = [orb_pt(cx, cy, R, i, u) for i, u in BIGS]
    def faint(front):
        if extra <= 0: return
        for i in range(len(ORB)):
            if i >= 3: orbit_arc(c, cx, cy, R, i, front, alpha(XRAY, 0.22 * extra), 2.5)
            for k in range(5):
                u = k * 2 * math.pi / 5 + i * 0.7 + 0.3
                if (math.sin(u) > 0) != front: continue
                if i < 3 and any(abs((u - bu + math.pi) % (2 * math.pi) - math.pi) < 0.5 for bi, bu in BIGS if bi == i): continue
                px, py = orb_pt(cx, cy, R, i, u)
                circle(c, px, py, 7); fill_stroke(c, alpha(FOIL, extra), alpha(INK, extra), 3)
    for i in range(3): orbit_arc(c, cx, cy, R, i, False, alpha(XRAY, 0.35 * rings), 4)
    faint(False)
    for k, (i, u) in enumerate(BIGS):
        if math.sin(u) < 0: satellite(c, *pos[k], 0.27, sec, hl=hl.get(k, 0))
    earth(c, cx, cy, R)
    if dot is not None:
        dx, dy = dot
        glow(c, dx, dy, 40, DOT, 0.8); circle(c, dx, dy, 9); fill_stroke(c, DOT, WHITE, 3)
    for i in range(3): orbit_arc(c, cx, cy, R, i, True, alpha(XRAY, 0.6 * rings), 4)
    faint(True)
    for k, (i, u) in enumerate(BIGS):
        if math.sin(u) >= 0: satellite(c, *pos[k], 0.32, sec, hl=hl.get(k, 0))
    return pos

EC = (540, 1300); ER = 185
EDOT = (EC[0] - 0.30 * ER, EC[1] - 0.55 * ER)

def ring_pulse(c, x, y, r, col=YEL, a=1.0, lw=8):
    if r <= 2: return
    c.new_path(); c.arc(x, y, r, 0, 2 * math.pi); c.set_source_rgba(*alpha(col, 0.25 * a)); c.set_line_width(lw * 3); c.stroke()
    c.new_path(); c.arc(x, y, r, 0, 2 * math.pi); c.set_source_rgba(*alpha(col, a)); c.set_line_width(lw); c.stroke()

def badge_box(c, x, y, lines_, k, w=380, accent=CREAM, hl=0.0):
    """Cream info box with lines [(text, size, colour, fam)], centred at x, y."""
    if k <= 0.02: return
    h = sum(s * 1.25 for _, s, _, _ in lines_) + 30
    c.save(); c.translate(x, y); c.scale(k, k)
    shadow(c, lambda: rrect(c, -w / 2, -h / 2, w, h, 16), 8, 10, 0.4)
    rrect(c, -w / 2, -h / 2, w, h, 16); fill_stroke(c, CREAM, mix(INK, YEL, hl), 6 + 4 * hl)
    yy = -h / 2 + 15
    for s_, sz, col, fam in lines_:
        sz2 = fit_size(c, s_, fam, sz, w - 36, True)
        yy += sz * 1.25
        text(c, s_, 0, yy - sz * 0.3, sz2, col, fam, fam != SLAB)
    c.restore()

def big_label(c, s, x, y, size, col, k=1.0, maxw=880):
    if k <= 0.02: return
    sz = fit_size(c, s, SLAB, size, maxw)
    c.save(); c.translate(x, y); c.scale(eob(k), eob(k))
    text(c, s, 0, sz * 0.35, sz, col, SLAB, False, outline=INK, olw=max(6, sz * 0.16))
    c.restore()

def stars(c, t, y0=600, y1=1150, n=40, a=1.0):
    for i in range(n):
        r_ = random.Random(i * 31 + 5)
        x, y, s = r_.uniform(20, 1060), r_.uniform(y0, y1), r_.uniform(1.2, 3.0)
        c.set_source_rgba(1, 1, 1, a * (0.35 + 0.3 * math.sin(t * 1.7 + i * 1.3)))
        circle(c, x, y, s); c.fill()

def speed_lines(c, t, fast, cx=540, cy=1150):
    if fast <= 0: return
    for i in range(26):
        r0 = 260 + (i * 97 + t * 2600) % 900; a = i * 0.2417 * 1.0 + 0.1
        line(c, [(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * (r0 + 140 * fast), cy + math.sin(a) * (r0 + 140 * fast))],
             alpha(WHITE, 0.35 * fast), 5)


# ---------------------------------------------------------------- front: street, phone, satellites above
BUILD = [(0, 160, 1250), (150, 140, 1150), (280, 170, 1320), (440, 130, 1210), (560, 180, 1100), (730, 150, 1260), (870, 220, 1180)]
F_SATS = [(190, 700, -0.25), (540, 660, 0.05), (880, 715, 0.25)]
PH = (540, 1235)

def street(c, t, up=0.0):
    for i, (x, w, top) in enumerate(BUILD):
        top = top + 40
        rrect(c, x, top, w, 1000, 6); fill_stroke(c, BLD if i % 2 else BLD2, INK, 5)
        for j in range(int((1900 - top) / 60)):
            for k in range(int((w - 30) / 40)):
                if random.Random(i * 1000 + j * 10 + k).random() < 0.45:
                    c.set_source_rgba(*alpha(YEL, 0.55)); c.rectangle(x + 22 + k * 40, top + 30 + j * 60, 18, 26); c.fill()
    glow(c, 540, 1500, 520, ORANGE, 0.18)

def scene_front(c, t):
    background(c, t, ORANGE)
    sp = B("imposible")
    z = ease(ramp(t, B("freno")["start"], T_SLOW + 0.25))
    up = ease(ramp(t, tt("imposible", "espacio") - 0.7, tt("imposible", "espacio") - 0.2)) * (1 - ease(ramp(t, tt("imposible", "aun") - 0.1, tt("imposible", "aun") + 0.5)))
    push = 1.0 + 0.05 * ease(ramp(t, 0, B("freno")["start"]))
    # zoom out: the street shrinks into a dot on the Earth
    Z = math.exp(lerp(math.log(40), 0, ease(z)))      # Earth scale (40 -> 1)
    anchor = (lerp(PH[0], EDOT[0], ease(z)), lerp(PH[1] + 47, EDOT[1], ease(z)))
    a_street = 1 - ease(ramp(z, 0.25, 0.7))
    a_earth = ease(ramp(z, 0.15, 0.55))
    if a_earth > 0:
        c.push_group()
        stars(c, t, 600, 1700, 50)
        c.save(); c.translate(*anchor); c.scale(Z, Z); c.translate(-EDOT[0], -EDOT[1])
        earth_system(c, EC[0], EC[1], ER, t, dot=EDOT, rings=ease(ramp(z, 0.5, 1.0)))
        c.restore()
        c.pop_group_to_source(); c.paint_with_alpha(a_earth)
    if a_street <= 0: return
    c.push_group()
    sk = Z / 40 * push
    c.translate(*anchor); c.scale(sk, sk); c.translate(-PH[0], -(PH[1] + 47))
    stars(c, t, 600, 1050, 35)
    # satellites up there, listening lines down to the phone
    ty = -120 * up
    sec = t  # real-time second hand (it barely moves once the light is slowed down)
    t_esc = tt("gancho", "escuchando")
    for k, (sx, sy, r_) in enumerate(F_SATS):
        if t > t_esc - 0.3:
            for j in range(3):
                ph = ((t - t_esc) * 0.55 + j / 3 + k * 0.21) % 1
                if t - t_esc < 0 and ph > 0.2: continue
                px, py = lerp(sx, PH[0], ph), lerp(sy + 50, PH[1] - 250 + ty, ph)
                a = math.sin(math.pi * ph) * 0.9 * ramp(t, t_esc - 0.3, t_esc + 0.3)
                ang = math.atan2(PH[1] - 250 + ty - sy, PH[0] - sx)
                c.new_path(); c.arc(px, py, 26, ang - 0.7, ang + 0.7); c.set_source_rgba(*alpha(YEL, a)); c.set_line_width(6); c.stroke()
        satellite(c, sx, sy, 0.55, sec, r_, hl=pulse_at(t, tt("gancho", "relojes") - 0.1, 0.8))
    c.save(); c.translate(0, ty)
    street(c, t)
    hand_back(c, PH[0], PH[1], 1.0)
    t_calle = tt("imposible", "calle")
    pk = ramp(t, t_calle - 0.15, t_calle + 0.25)
    bounce = abs(math.sin(math.pi * ramp(t, t_calle + 0.25, t_calle + 1.0) * 2)) * (1 - ramp(t, t_calle + 0.25, t_calle + 1.0))
    c.save(); c.translate(0, 0)
    phone(c, PH[0], PH[1], 1.0, t, pinv=eob(pk))
    c.restore()
    if bounce > 0:  # bounce the pin: redraw it lifted
        pass
    hand_front(c, PH[0], PH[1], 1.0)
    c.restore()
    # 20.000 km dimension line
    t20 = tt("gancho", "veinte") - 0.15
    k = ease(ramp(t, t20, t20 + 0.4)) * (1 - up) * (1 - ramp(z, 0.0, 0.2))
    if k > 0:
        x = 760; y0, y1 = 770, lerp(770, 975, k)
        line(c, [(x, y0), (x, y1)], alpha(YEL, k), 6)
        line(c, [(x - 18, 770), (x + 18, 770)], alpha(YEL, k), 6); line(c, [(x - 18, y1), (x + 18, y1)], alpha(YEL, k), 6)
        big_label(c, "20.000 KM", 880 - 40, 880, 50, alpha(YEL, k), ramp(t, t20 + 0.1, t20 + 0.45), 300)
    c.pop_group_to_source(); c.paint_with_alpha(a_street)
    # imposible: 3 crossed-out badges
    if up > 0.01 and z <= 0:
        def ic_eye(c):
            c.save(); c.translate(0, -8); c.scale(1, 0.55); c.new_path(); c.arc(0, 0, 62, 0, 2 * math.pi); c.restore(); fill_stroke(c, WHITE, INK, 6)
            circle(c, 0, -2, 26); fill_stroke(c, STEEL, INK, 5); circle(c, 0, -2, 10); fill_stroke(c, INK, None)
            for dx in (-30, 0, 30): arrow(c, dx, 36, dx * 1.3, 78, alpha(INK, 0.8), 6, 18)
        def ic_cam(c):
            rrect(c, -62, -36, 124, 84, 12); fill_stroke(c, METAL, INK, 6)
            rrect(c, -30, -52, 50, 20, 6); fill_stroke(c, METAL, INK, 5)
            circle(c, 0, 6, 28); fill_stroke(c, INK, INK, 4); circle(c, 0, 6, 14); fill_stroke(c, COLD, None)
            circle(c, 42, -20, 7); fill_stroke(c, RED, None)
        def ic_send(c):
            rrect(c, -30, -20, 60, 96, 10); fill_stroke(c, DARK, INK, 5)
            rrect(c, -22, -10, 44, 70, 5); fill_stroke(c, MAPBG, None)
            arrow(c, 0, -22, 0, -82, HOT, 10, 30)
        for name, x, fn, lab in [("espacio", 250, ic_eye, "TE VEN"), ("cámara", 540, ic_cam, "CÁMARA"), ("manda", 830, ic_send, "ENVÍA")]:
            t0 = tt("imposible", name) - 0.2
            kk = eob(ramp(t, t0, t0 + 0.3)) * up
            icon_badge(c, x, 1515, kk, lab, fn, t, t0 + 0.35)


# ---------------------------------------------------------------- paso 1: Earth, orbits, satellites with atomic clocks
INSET = (245, 790, 150)

def scene_paso1(c, t):
    background(c, t, COLD)
    b = B("paso1")
    stars(c, t, 600, 1700, 50)
    c.save(); cam(c, 1.0 + 0.05 * ease(ramp(t, T_SLOW + 0.5, b["end"])), EC[0], EC[1])
    t30 = tt("paso1", "treinta") - 0.1
    extra = ease(ramp(t, t30, t30 + 0.6))
    t_rel = tt("paso1", "relojes") - 0.2
    hl = {k: pulse_at(t, tt("paso1", "satélites") - 0.1 + k * 0.08, 0.7) for k in range(6)}
    hl[0] = max(hl[0], ease(ramp(t, t_rel, t_rel + 0.3)))
    pos = earth_system(c, EC[0], EC[1], ER, t, extra=extra, hl=hl, dot=EDOT)
    c.restore()
    s_ = 1.0 + 0.05 * ease(ramp(t, T_SLOW + 0.5, b["end"]))
    sp = [(EC[0] + (x - EC[0]) * s_, EC[1] + (y - EC[1]) * s_) for x, y in pos]
    callout(c, "ÓRBITA · 20.000 KM", *orb_pt(EC[0] + 0, EC[1], ER * s_, 1, 0.35), 760, 1660, t, tt("paso1", "giran") - 0.1, XRAY, 30)
    k30 = eob(ramp(t, t30, t30 + 0.35))
    if k30 > 0:
        badge_box(c, 790, 1010 if t < t_rel else 1010, [("UNOS 30", 50, RED, SLAB), ("SATÉLITES GPS", 28, INK, SANS)], k30, 300)
    # inset: one satellite enlarged, with its atomic clock
    k = eob(ramp(t, t_rel, t_rel + 0.4))
    if k > 0.02:
        ix, iy, ir = INSET
        line(c, [sp[0], (lerp(sp[0][0], ix, ease(ramp(t, t_rel, t_rel + 0.3))), lerp(sp[0][1], iy + ir, ease(ramp(t, t_rel, t_rel + 0.3))))], alpha(WHITE, 0.8), 4)
        c.save(); c.translate(ix, iy); c.scale(k, k)
        shadow(c, lambda: circle(c, 0, 0, ir + 14), 10, 14, 0.4)
        circle(c, 0, 0, ir + 14); fill_stroke(c, GOLD, INK, 7)
        c.save(); circle(c, 0, 0, ir); c.clip(); c.set_source_rgba(*NIGHT); c.paint()
        t_em = tt("paso1", "emite") - 0.1
        if t > t_em:
            for j in range(4):
                ph = ((t - t_em) * 0.45 + j / 4) % 1
                ring_pulse(c, 0, 0, 60 + ph * 140, YEL, (1 - ph) * ramp(t, t_em, t_em + 0.4), 5)
        satellite(c, 0, -4, 0.82, 0.0, -0.1)
        c.restore()
        circle(c, 0, 0, ir); fill_stroke(c, None, INK, 5)
        # atomic badge
        circle(c, 100, 100, 44); fill_stroke(c, CREAM, INK, 5); atom(c, 100, 100, 32, COLD, 4)
        c.restore()
        if k > 0.6:
            callout(c, "RELOJ ATÓMICO", ix + 100, iy + 100, ix + 40, iy + 225, t, tt("paso1", "atómicos") - 0.1, YEL, 28)
    # the message bubble
    t_msg = tt("paso1", "mensaje") - 0.15
    km = eob(ramp(t, t_msg, t_msg + 0.35))
    if km > 0.02:
        bx, by, bw, bh = 425, 680, 520, 190
        c.save(); c.translate(bx + bw / 2, by + bh / 2); c.scale(km, km); c.translate(-(bx + bw / 2), -(by + bh / 2))
        shadow(c, lambda: rrect(c, bx, by, bw, bh, 22), 8, 10, 0.4)
        c.new_path(); c.move_to(bx + 6, by + 120); c.line_to(bx - 38, by + 150); c.line_to(bx + 6, by + 150); c.close_path(); fill_stroke(c, CREAM, INK, 5)
        rrect(c, bx, by, bw, bh, 22); fill_stroke(c, CREAM, INK, 6)
        t_soy = tt("paso1", "soy") - 0.1; t_hora = tt("paso1", "hora") - 0.15
        if t < t_soy:
            for j in range(3):
                circle(c, bx + bw / 2 - 40 + 40 * j, by + bh / 2, 12 + 4 * math.sin(t * 8 - j)); c.set_source_rgba(*alpha(INK, 0.6)); c.fill()
        else:
            n = int(clamp((t - t_soy) / 0.5) * 17)
            s1 = "SOY EL SATÉLITE 7"[:max(1, n)]
            text(c, s1, bx + 26, by + 70, fit_size(c, "SOY EL SATÉLITE 7", SLAB, 42, bw - 52), INK, SLAB, False, "l")
            if t >= t_hora:
                us = int(max(0.0, anim_time(t) - anim_time(t_hora)) * 1e6)
                s2 = f"HORA 12:00:00,{us:06d}"
                kh = ramp(t, t_hora, t_hora + 0.2)
                text(c, s2, bx + 26, by + 146, fit_size(c, "HORA 12:00:00,000000", MONO, 40, bw - 52, True), alpha(RED, kh), MONO, True, "l")
        c.restore()


# ---------------------------------------------------------------- paso 2: the signal travels, the phone compares clocks
S2 = (760, 735); P2 = (300, 1315)
def horizon(c, t, cy=2700, R=1250, glow_a=0.35):
    glow(c, 540, cy - R + 40, 700, XRAY, glow_a * 0.5)
    circle(c, 540, cy, R)
    g = cairo.LinearGradient(0, cy - R, 0, cy - R + 400)
    g.add_color_stop_rgba(0, *mix(LAND, OCEAN, 0.2)); g.add_color_stop_rgba(1, *OCEAN2)
    c.set_source(g); c.fill_preserve(); c.set_source_rgba(*INK); c.set_line_width(7); c.stroke()
    c.new_path(); c.arc(540, cy, R + 14, math.pi * 1.2, math.pi * 1.8); c.set_source_rgba(*alpha(XRAY, 0.5)); c.set_line_width(8); c.stroke()

def scene_paso2(c, t):
    background(c, t, COLD)
    b = B("paso2")
    stars(c, t, 600, 1300, 40)
    c.save(); cam(c, 1.0 + 0.04 * ease(ramp(t, b["start"] - 0.25, b["end"])), 540, 1100)
    horizon(c, t)
    t_go = tt("paso2", "viaja") - 0.1; t_in = tt("paso2", "llegar", end=True)
    D = math.dist(S2, P2)
    frac = ramp(t, t_go, t_in)
    arrived = t >= t_in
    # dotted path
    if t > t_go - 0.3:
        c.new_path(); c.move_to(S2[0], S2[1] + 40); c.line_to(*P2)
        c.set_source_rgba(*alpha(YEL, 0.35)); c.set_line_width(4); c.set_dash([12, 14]); c.stroke(); c.set_dash([])
    if 0 < frac < 1:
        c.save(); c.rectangle(0, 600, W, 1100); c.clip()
        for j in range(3):
            r = frac * D - j * 70
            ring_pulse(c, S2[0], S2[1], r, YEL, (1 - 0.3 * j), 8 - 2 * j)
        c.restore()
        px, py = lerp(S2[0], P2[0], frac), lerp(S2[1], P2[1], frac)
        glow(c, px, py, 60, YEL, 0.8)
    if arrived:
        a = 1 - ramp(t, t_in, t_in + 0.8)
        if a > 0: ring_pulse(c, P2[0], P2[1] - 60, 90 + 160 * (1 - a), YEL, a, 8)
    hand_back(c, P2[0], P2[1], 0.5)
    phone(c, P2[0], P2[1], 0.5, t, flash=pulse_at(t, t_in - 0.1, 0.6))
    hand_front(c, P2[0], P2[1], 0.5)
    satellite(c, S2[0], S2[1], 0.75, 0.0, 0.15, hl=pulse_at(t, tt("paso2", "mensaje") - 0.1, 0.8))
    c.restore()
    # clock boxes
    t_cmp = tt("paso2", "compara") - 0.1
    hl = ease(ramp(t, t_cmp, t_cmp + 0.3)) * (1 - ease(ramp(t, tt("paso2", "distancia") - 0.2, tt("paso2", "distancia") + 0.3)))
    k1 = eob(ramp(t, tt("paso2", "mensaje") - 0.1, tt("paso2", "mensaje") + 0.25))
    badge_box(c, 300, 760, [("SALIÓ", 26, RED, SANS), ("12:00:00,000", 40, INK, MONO)], k1, 360, hl=hl)
    t_tar = tt("paso2", "tarda") - 0.15
    k2 = eob(ramp(t, t_tar, t_tar + 0.3))
    ms = int(round(67 * frac))
    badge_box(c, 720, 1400, [("LLEGÓ" if arrived else "EN CAMINO…", 26, RED if arrived else STEEL, SANS), (f"12:00:00,{ms:03d}", 40, INK, MONO)], k2, 360, hl=max(hl, pulse_at(t, t_in - 0.1, 0.5)))
    # tag "≈ 0,07 s" on the path
    t_c = tt("paso2", "siete") - 0.1
    kc = eob(ramp(t, t_c, t_c + 0.35)) * (1 - ease(ramp(t, t_cmp - 0.3, t_cmp)))
    if kc > 0.02:
        big_label(c, "0,07 s", 220, 1090, 60, YEL, kc, 340)
    # subtraction and distance
    kd = eob(ramp(t, t_cmp + 0.2, t_cmp + 0.55))
    t_dist = tt("paso2", "distancia") - 0.2
    kx = ramp(t, t_dist - 0.6, t_dist - 0.3)
    lines_ = [("DIFERENCIA", 24, STEEL, SANS), ("0,067 s", 50, RED, SLAB)]
    if kx > 0: lines_ += [("× 300.000 km/s", 34, INK, SANS)]
    if t >= t_dist: lines_ += [("≈ 20.000 km", 46, RED, SANS)]
    badge_box(c, 230, 1000, lines_, kd, 360)
    kk = ease(ramp(t, t_dist, t_dist + 0.5))
    if kk > 0:  # dimension along the path
        a = math.atan2(P2[1] - S2[1], P2[0] - S2[0]); nx, ny = math.sin(a), -math.cos(a)
        o = 60
        p0 = (S2[0] - nx * o, S2[1] - ny * o); p1 = (lerp(S2[0], P2[0], kk) - nx * o, lerp(S2[1], P2[1], kk) - ny * o)
        p0 = (S2[0] + nx * o, S2[1] + ny * o); p1 = (lerp(S2[0], P2[0], kk) + nx * o, lerp(S2[1], P2[1], kk) + ny * o)
        line(c, [p0, p1], YEL, 6)
        mx, my = (S2[0] + P2[0]) / 2 + nx * 120, (S2[1] + P2[1]) / 2 + ny * 120
        c.save(); c.translate(mx, my); c.rotate(a + math.pi)
        text(c, "20.000 KM", 0, 16, 46 * kk, YEL, SLAB, False, outline=INK, olw=8)
        c.restore()


# ---------------------------------------------------------------- paso 3: spheres -> one point
E3 = (540, 1350); R3 = 240
P3 = (E3[0] + R3 * math.cos(math.radians(-112)), E3[1] + R3 * math.sin(math.radians(-112)))
S3 = [(205, 800), (850, 780), (905, 1300)]
C3 = [YEL, XRAY, ORANGE]

def scene_paso3(c, t):
    background(c, t, COLD)
    b = B("paso3")
    stars(c, t, 600, 1700, 45)
    c.save(); cam(c, 1.0 + 0.04 * ease(ramp(t, b["start"] - 0.25, b["end"])), 540, 1150)
    earth(c, *E3, R3)
    t_es = tt("paso3", "esfera") - 0.3; t_tr = tt("paso3", "tres") - 0.15
    t_cr = tt("paso3", "cruzan") - 0.1; t_tu = tt("paso3", "tú") - 0.25
    starts = [t_es, t_tr, t_tr + 0.35]
    c.save(); c.rectangle(0, 600, W, H); c.clip()
    for i, (S, col) in enumerate(zip(S3, C3)):
        k = ease(ramp(t, starts[i], starts[i] + 0.9))
        if k <= 0: continue
        r = math.dist(S, P3)
        a0 = math.atan2(P3[1] - S[1], P3[0] - S[0])
        c.new_path(); c.arc(S[0], S[1], r, a0 - math.pi * k, a0 + math.pi * k)
        c.set_source_rgba(*alpha(col, 0.95)); c.set_line_width(7); c.stroke()
        line(c, [S, P3], alpha(col, 0.35 * k), 3)
    c.restore()
    for i, S in enumerate(S3):
        k = eob(ramp(t, (b["start"] - 0.2) if i == 0 else starts[i] - 0.2, (b["start"] + 0.15) if i == 0 else starts[i] + 0.15))
        if k > 0.02: satellite(c, S[0], S[1], 0.45 * k, 0.0, 0.1 * (i - 1), hl=pulse_at(t, starts[i], 0.8))
    kp = ease(ramp(t, t_cr, t_cr + 0.4))
    if kp > 0:
        glow(c, P3[0], P3[1], 90 + 20 * math.sin(t * 5), WHITE, 0.8 * kp)
        circle(c, *P3, 12 * kp); fill_stroke(c, WHITE, INK, 4)
    ku = ramp(t, t_tu, t_tu + 0.35)
    if ku > 0:
        pin(c, P3[0], P3[1], 0.9 * eob(ku))
    c.restore()
    # captions on the illustration
    k1 = eob(ramp(t, t_es, t_es + 0.35)) * (1 - ease(ramp(t, t_tr - 0.3, t_tr)))
    big_label(c, "1 SATÉLITE = 1 ESFERA", 540, 1660, 52, YEL, k1)
    k2 = eob(ramp(t, t_cr, t_cr + 0.35)) * (1 - ease(ramp(t, t_tu - 0.3, t_tu)))
    big_label(c, "3 ESFERAS = 1 PUNTO", 540, 1660, 52, WHITE, k2)
    callout(c, "TÚ", P3[0] - 20, P3[1] - 80, 250, 1010, t, t_tu + 0.15, YEL, 46)
    k3 = eob(ramp(t, t_tu, t_tu + 0.35))
    big_label(c, "ESE PUNTO ERES TÚ", 540, 1660, 52, YEL, k3)


# ---------------------------------------------------------------- paso 4: the phone's bad clock, 4th satellite
PH4 = (250, 830)
def scene_paso4(c, t):
    background(c, t, ORANGE)
    b = B("paso4")
    stars(c, t, 600, 1000, 25)
    c.save(); cam(c, 1.0 + 0.04 * ease(ramp(t, b["start"] - 0.25, b["end"])), 540, 1150)
    t_mal = tt("paso4", "malo") - 0.2; t_mi = tt("paso4", "millonésima") - 0.2; t_300 = tt("paso4", "trescientos") - 0.2
    t_4 = tt("paso4", "cuarto") - 0.2; t_cor = tt("paso4", "corregir") - 0.1
    fix = ease(ramp(t, t_cor, t_cor + 0.8))
    wob = ramp(t, t_mal, t_mal + 0.3) * (1 - fix) * (0.35 * math.sin(t * 9) + 0.2 * math.sin(t * 23 + 1))
    shake = 4 * abs(wob)
    phone(c, PH4[0] + shake * math.sin(t * 40), PH4[1], 0.56, t, screen="clock", clock_wob=wob, clock_hl=pulse_at(t, t_cor, 0.8))
    # map panel
    mx, my, mw, mh = 130, 1060, 820, 560
    shadow(c, lambda: rrect(c, mx, my, mw, mh, 26), 12, 16, 0.4)
    c.save(); rrect(c, mx, my, mw, mh, 26); c.clip()
    blur = 150 * ease(ramp(t, t_300, t_300 + 0.6)) * (1 - fix)
    jit = (20 * math.sin(t * 7), 14 * math.cos(t * 9)) if blur > 10 else (0, 0)
    dx, dy = map_view(c, mx, my, mw, mh, t, 1.0, 0.0, blur, 2.2, (0.5 + jit[0] / mw * (blur / 150), 0.56 + jit[1] / mh * (blur / 150)))
    c.restore()
    rrect(c, mx, my, mw, mh, 26); fill_stroke(c, None, INK, 8)
    kr = ease(ramp(t, t_300 + 0.3, t_300 + 0.8)) * (1 - fix)
    if kr > 0:  # ruler 300 m
        cx0, cy0 = mx + mw * 0.5, my + mh * 0.56
        x0, x1 = cx0 - 150, cx0 - 150 + 300 * kr
        line(c, [(x0, cy0 + 190), (x1, cy0 + 190)], INK, 8)
        line(c, [(x0, cy0 + 172), (x0, cy0 + 208)], INK, 8); line(c, [(x1, cy0 + 172), (x1, cy0 + 208)], INK, 8)
        text(c, "300 m", cx0, cy0 + 170 - 8, 46, alpha(RED, kr), SLAB, False, outline=alpha(CREAM, kr), olw=8)
    c.restore()
    callout(c, "RELOJ BARATO", PH4[0] + 60, PH4[1] + 60, 540, 1000, t, t_mal, HOT, 32)
    # 1 µs = 300 m
    k1 = eob(ramp(t, t_mi, t_mi + 0.35)); kout = ease(ramp(t, t_4 - 0.7, t_4 - 0.3))
    if k1 > 0 and kout < 1:
        c.save(); c.translate(0, -60 * kout)
        a = 1 - kout
        c.push_group()
        big_label(c, "1 µs", 700, 720, 84, WHITE, k1, 380)
        big_label(c, "= 300 m", 700, 840, 64, YEL, ramp(t, t_300, t_300 + 0.35), 400)
        c.pop_group_to_source(); c.paint_with_alpha(a); c.restore()
    # 4th satellite
    k4 = eob(ramp(t, t_4, t_4 + 0.4))
    if k4 > 0.02:
        s4 = (740, 760)
        sig = ramp(t, t_4 + 0.3, t_cor)
        if sig > 0:
            px, py = lerp(s4[0], PH4[0] + 70, sig), lerp(s4[1], PH4[1] - 40, sig)
            line(c, [s4, (px, py)], alpha(YEL, 0.8), 6)
            glow(c, px, py, 40, YEL, 0.9)
        satellite(c, s4[0], s4[1], 0.62 * k4, 0.0, 0.12, hl=pulse_at(t, t_4 + 0.1, 0.8))
        text(c, "4º", s4[0] + 120, s4[1] - 60, 60 * k4, YEL, SLAB, False, outline=INK, olw=9)
    if fix > 0:
        big_label(c, "RELOJ CORREGIDO", 540, 1680 - 10, 46, hx("#7CFC9A"), ramp(t, t_cor + 0.1, t_cor + 0.45))


# ---------------------------------------------------------------- paso 5: time runs faster up there
def scene_paso5(c, t):
    background(c, t, COLD)
    b = B("paso5")
    stars(c, t, 600, 1100, 30)
    c.save(); cam(c, 1.0 + 0.04 * ease(ramp(t, b["start"] - 0.25, b["end"])), 540, 1150)
    t_up = tt("paso5", "allí") - 0.2; t_ti = tt("paso5", "tiempo") - 0.2; t_rap = tt("paso5", "rápido") - 0.2
    t_cor = tt("paso5", "corrigiera") - 0.3; t_10 = tt("paso5", "diez") - 0.2; t_dia = tt("paso5", "día") - 0.1
    # both clocks: identical until "rápido", then the satellite one gets ahead (stylised: +38 µs a day)
    ahead = 2.2 * max(0.0, t - t_rap) ** 1.2
    base = 6 * max(0.0, t - t_up)
    ka = eob(ramp(t, t_up, t_up + 0.4)); kb = eob(ramp(t, t_ti, t_ti + 0.4))
    if ka > 0.02:
        satellite(c, 150, 680, 0.42 * ka, 0.0, -0.1, clock=False)
        c.save(); c.translate(290, 820); c.scale(ka, ka); clockface(c, 0, 0, 120, base + ahead, hl=pulse_at(t, t_rap, 1.0)); c.restore()
        text(c, "EN EL SATÉLITE", 290, 990, 32 * ka, CREAM, SANS, True)
    if kb > 0.02:
        c.save(); c.translate(790, 820); c.scale(kb, kb); clockface(c, 0, 0, 120, base); c.restore()
        text(c, "EN LA TIERRA", 790, 990, 32 * kb, CREAM, SANS, True)
        house(c, 930, 690, 0.8 * kb)
    kr = eob(ramp(t, t_rap, t_rap + 0.35))
    if kr > 0.02:
        badge_box(c, 540, 730, [("MÁS RÁPIDO", 24, RED, SANS), ("+38 µs/día", 40, INK, SANS)], kr, 250)
    # map with the drifting pin
    km = eob(ramp(t, t_cor, t_cor + 0.4))
    if km > 0.02:
        mx, my, mw, mh = 130, 1110, 820, 500
        c.save(); c.translate(540, my + mh / 2); c.scale(km, km); c.translate(-540, -(my + mh / 2))
        shadow(c, lambda: rrect(c, mx, my, mw, mh, 26), 12, 16, 0.4)
        c.save(); rrect(c, mx, my, mw, mh, 26); c.clip()
        map_view(c, mx, my, mw, mh, t, 0.0, 0.0, 0.0, 2.0, (0.2, 0.56))
        tx, ty = mx + 0.2 * mw, my + 0.56 * mh
        # true position (dot) and the drifting fix
        circle(c, tx, ty, 22); fill_stroke(c, DOT, WHITE, 8)
        drift = ease(ramp(t, t_cor + 0.3, t_dia + 0.3))
        px, py = lerp(tx, mx + 0.86 * mw, drift), lerp(ty, my + 0.38 * mh, drift)
        if drift > 0.02:
            c.new_path(); c.move_to(tx, ty); c.line_to(px, py); c.set_source_rgba(*RED); c.set_line_width(6); c.set_dash([16, 12]); c.stroke(); c.set_dash([])
        pin(c, px, py, 1.2)
        c.restore()
        rrect(c, mx, my, mw, mh, 26); fill_stroke(c, None, INK, 8)
        c.restore()
        if km > 0.9:
            callout(c, "ESTÁS AQUÍ", tx, ty - 20, 300, 1062, t, t_cor + 0.4, CREAM, 30)
    k10 = eob(ramp(t, t_10, t_10 + 0.35))
    big_label(c, "10 KM AL DÍA", 540, 1668, 70, YEL, k10, 700) if k10 > 0 else None
    c.restore()


# ---------------------------------------------------------------- junto + acelerón: everything at once
SJ = [(170, 790), (400, 690), (690, 700), (900, 830)]
PJ = (540, 1215)
def scene_junto(c, t):
    fast = FAST(t)
    background(c, t, YEL)
    stars(c, t, 600, 1250, 45)
    b = B("junto")
    shake = 7 * fast
    c.save(); cam(c, 1.0 + 0.05 * ease(ramp(t, b["start"] - 0.25, B("remate")["start"])), 540, 1150)
    c.translate(shake * math.sin(t * 61), shake * math.cos(t * 53))
    ts = {w: tt("junto", w) - 0.1 for w in ["satélites", "relojes", "señal", "retraso", "esferas", "tú"]}
    horizon(c, t, 2300, 1000)
    tf = tfast(t)
    # spheres
    ke = ease(ramp(t, ts["esferas"], ts["esferas"] + 0.6))
    if ke > 0:
        c.save(); c.rectangle(0, 600, W, 1120); c.clip()
        for i, S in enumerate(SJ):
            r = math.dist(S, (PJ[0], PJ[1] - 60))
            c.new_path(); c.arc(S[0], S[1], r, 0, 2 * math.pi)
            c.set_source_rgba(*alpha([YEL, XRAY, ORANGE, GREEN][i], 0.55 * ke)); c.set_line_width(5); c.stroke()
        c.restore()
    # signals
    if t >= ts["señal"]:
        c.save(); c.rectangle(0, 600, W, 1120); c.clip()
        for i, S in enumerate(SJ):
            D = math.dist(S, PJ)
            ph = ((tf - ts["señal"]) * 0.45 + i * 0.27) % 1
            if fast < 0.6:
                ring_pulse(c, S[0], S[1], ph * D, YEL, (1 - fast) * (1 - 0.6 * ph) * ramp(t, ts["señal"], ts["señal"] + 0.3), 6)
            if fast > 0:  # real speed: the signal is basically instant -> flashing beams
                fl = 0.5 + 0.5 * math.sin(t * 47 + i * 2.1)
                line(c, [S, (PJ[0], PJ[1] - 60)], alpha(YEL, fast * (0.3 + 0.7 * fl)), 6 + 6 * fl)
        c.restore()
    hand_back(c, PJ[0], PJ[1], 0.42)
    phone(c, PJ[0], PJ[1], 0.42, t, pinv=ease(ramp(t, ts["tú"], ts["tú"] + 0.3)), flash=0.6 * fast * (0.5 + 0.5 * math.sin(t * 37)))
    hand_front(c, PJ[0], PJ[1], 0.42)
    for i, S in enumerate(SJ):
        satellite(c, S[0], S[1], 0.42, 0.0, -0.2 + 0.13 * i, hl=max(pulse_at(t, ts["satélites"] + 0.1 * i, 0.8), 0.6 * fast))
        if t >= ts["relojes"]:
            kk = ease(ramp(t, ts["relojes"] + 0.08 * i, ts["relojes"] + 0.08 * i + 0.3))
            glow(c, S[0], S[1] + 1, 50, YEL, 0.6 * kk * (1 - ramp(t, ts["relojes"] + 0.8, ts["relojes"] + 1.4)))
    c.restore()
    if fast < 0.3:
        a = 1 - fast / 0.3
        c.push_group()
        callout(c, "SATÉLITES", *SJ[1], 400, 900, t, ts["satélites"])
        callout(c, "RELOJES", SJ[2][0], SJ[2][1] + 5, 760, 950, t, ts["relojes"], YEL)
        callout(c, "SEÑAL", 355, 1002, 190, 1080, t, ts["señal"], YEL)
        if t >= ts["retraso"]:
            badge_box(c, 830, 1130, [("RETRASO", 24, RED, SANS), ("0,067 s", 38, INK, MONO)], eob(ramp(t, ts["retraso"], ts["retraso"] + 0.35)), 230)
        callout(c, "ESFERAS", 816, 1307, 860, 1440, t, ts["esferas"], XRAY)
        callout(c, "TÚ", PJ[0] - 10, PJ[1] - 60, 300, 1250, t, ts["tú"], YEL, 44)
        c.pop_group_to_source(); c.paint_with_alpha(a)
    speed_lines(c, t, fast)
    flash = ramp(t, B("remate")["start"] - 0.45, B("remate")["start"] - 0.3) * (1 - ramp(t, B("remate")["start"] - 0.3, B("remate")["start"] - 0.05))
    if flash > 0: c.set_source_rgba(1, 1, 1, 0.85 * flash); c.paint()


# ---------------------------------------------------------------- remate: airplane mode, it only listens
def scene_remate(c, t):
    background(c, t, ORANGE)
    b = B("remate")
    c.save(); cam(c, 1.0 + 0.03 * ease(ramp(t, b["start"], T_LOOP)), 540, 1150)
    stars(c, t, 600, 1050, 35)
    t_av = tt("remate", "avión") - 0.2; t_ha = tt("remate", "habla") - 0.1; t_es = tt("remate", "escucha") - 0.15
    for k, (sx, sy, r_) in enumerate(F_SATS):
        for j in range(3):
            ph = ((t - b["start"]) * 0.55 + j / 3 + k * 0.21) % 1
            px, py = lerp(sx, PH[0], ph), lerp(sy + 50, PH[1] - 250, ph)
            a = math.sin(math.pi * ph) * 0.9
            ang = math.atan2(PH[1] - 250 - sy, PH[0] - sx)
            c.new_path(); c.arc(px, py, 26, ang - 0.7, ang + 0.7); c.set_source_rgba(*alpha(YEL, a)); c.set_line_width(6); c.stroke()
        satellite(c, sx, sy, 0.55, t, r_)
    street(c, t)
    hand_back(c, PH[0], PH[1], 1.0)
    phone(c, PH[0], PH[1], 1.0, t, airplane_on=float(t >= t_av))
    hand_front(c, PH[0], PH[1], 1.0)
    c.restore()
    # airplane badge
    ka = eob(ramp(t, t_av, t_av + 0.35))
    if ka > 0.02:
        def ic(c):
            airplane(c, 0, 0, 1.4, STEEL)
        icon_badge(c, 230, 1000, ka * 0.8, "MODO AVIÓN", ic)
    # inward arrows only; outward crossed
    ki = ease(ramp(t, t_ha - 0.6, t_ha - 0.2))
    if ki > 0:
        for sx, sy, _ in F_SATS:
            tx_, ty_ = PH[0] + (sx - PH[0]) * 0.25, PH[1] - 265
            ex, ey = lerp(sx, tx_, 0.85), lerp(sy + 60, ty_, 0.85)
            x0, y0 = lerp(sx, tx_, 0.3), lerp(sy + 60, ty_, 0.3)
            arrow(c, x0, y0, lerp(x0, ex, ki), lerp(y0, ey, ki), hx("#7CFC9A"), 12, 36)
    ko = ease(ramp(t, t_ha, t_ha + 0.35))
    if ko > 0:
        arrow(c, 800, 1020, 800, lerp(1020, 840, ko), HOT, 14, 40)
        xmark(c, 800, 930, 60, t, t_ha + 0.3, 16)
        if ko > 0.9: text(c, "NO ENVÍA", 800, 1110, 32, HOT, SANS, True, outline=INK, olw=6)
    ke = ramp(t, t_es, t_es + 0.35)
    if ke > 0:
        big_label(c, "SOLO ESCUCHA", 540, 1620, 96, YEL, ke)


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
    ps = [tt("gancho", "veinte"), tt("imposible", "espacio") - 0.2, tt("imposible", "cámara") - 0.2, tt("imposible", "manda") - 0.2,
          tt("imposible", "calle") - 0.1]
    ps += [tt("paso1", "giran"), tt("paso1", "treinta") - 0.1, tt("paso1", "relojes") - 0.2, tt("paso1", "atómicos"), tt("paso1", "mensaje") - 0.15]
    ps += [tt("paso2", "mensaje") - 0.1, tt("paso2", "tarda") - 0.15, tt("paso2", "siete") - 0.1, tt("paso2", "compara") + 0.1, tt("paso2", "distancia") - 0.2]
    ps += [tt("paso3", "cruzan"), tt("paso3", "tú") - 0.2]
    ps += [tt("paso4", "malo") - 0.2, tt("paso4", "millonésima") - 0.2, tt("paso4", "trescientos") - 0.2, tt("paso4", "cuarto") - 0.2, tt("paso4", "corregir")]
    ps += [tt("paso5", "allí") - 0.2, tt("paso5", "tiempo") - 0.2, tt("paso5", "rápido") - 0.2, tt("paso5", "corrigiera") - 0.3, tt("paso5", "diez") - 0.2]
    ps += [tt("junto", w) - 0.1 for w in ["satélites", "relojes", "retraso", "esferas", "tú"]]
    ps += [tt("remate", "avión") - 0.2, tt("remate", "escucha") - 0.15]
    return ps


def SFX(put, L):
    def ping(g=0.5): return L["tone"](1200, 0.25, 0.005, 0.08)
    def tick(): return L["click"]()
    # signals leaving / arriving
    for x in [tt("gancho", "escuchando"), tt("paso1", "emite"), tt("paso1", "emite") + 2.2, tt("paso2", "viaja") - 0.1,
              tt("paso3", "esfera") - 0.3, tt("paso3", "tres") - 0.15, tt("paso3", "tres") + 0.2, tt("paso4", "cuarto"),
              tt("junto", "señal") - 0.1, tt("remate", "habla") - 0.5]:
        put(ping(), x, 0.45)
    put(L["tone"](1600, 0.4, 0.005, 0.12), tt("paso2", "llegar", end=True), 0.5)  # arrival
    put(L["tone"](900, 0.6, 0.005, 0.2), tt("paso3", "cruzan"), 0.4)
    put(L["shimmer"](), tt("paso3", "tú") - 0.2, 0.35)
    put(L["shimmer"](), tt("paso4", "corregir"), 0.3)
    # ticking: the atomic clock's microseconds, the paso 5 clocks
    t0 = tt("paso1", "hora")
    for k in range(int(B("paso1")["end"] + 0.6 - t0) + 1): put(tick(), t0 + k * 1.0, 0.5)
    x = tt("paso5", "allí")
    while x < tt("paso5", "corrigiera"):
        put(tick(), x, 0.45); x += 0.5
    x = tt("paso4", "malo") - 0.2
    while x < tt("paso4", "corregir"):  # irregular ticking of the cheap clock
        put(tick(), x, 0.35); x += 0.38 + 0.18 * math.sin(x * 7)
    # acelerón: a flurry of tiny pings
    x = T_REAL + 0.4
    while x < B("remate")["start"] - 0.5:
        put(L["tone"](1200 + 200 * math.sin(x * 9), 0.08, 0.002, 0.03), x, 0.18); x += 0.12
    # remate: pings coming in
    for k in range(4): put(ping(), B("remate")["start"] + 0.4 + k * 1.2, 0.3)


# ---------------------------------------------------------------- thumbnails
def _thumb_scene(c, t=2.0):
    stars(c, t, 600, 1100, 40)
    for k, (sx, sy, r_) in enumerate(F_SATS):
        for j in range(2):
            ph = 0.3 + j * 0.35
            px, py = lerp(sx, PH[0], ph), lerp(sy + 50, PH[1] - 250, ph)
            ang = math.atan2(PH[1] - 250 - sy, PH[0] - sx)
            c.new_path(); c.arc(px, py, 30, ang - 0.7, ang + 0.7); c.set_source_rgba(*YEL); c.set_line_width(8); c.stroke()
        satellite(c, sx, sy, 0.62, 8, r_, hl=0.6)
    street(c, t)
    hand_back(c, PH[0], PH[1], 1.0)
    phone(c, PH[0], PH[1], 1.0, 0.3, pinv=1.0)
    hand_front(c, PH[0], PH[1], 1.0)

def THUMB_V(c):
    background(c, 3.0, ORANGE)
    c.save(); c.translate(0, 170); cam(c, 1.15, 540, 1150); _thumb_scene(c); c.restore()
    for i, ln in enumerate(["SOLO", "ESCUCHA"]):
        sz = fit_size(c, ln, SLAB, 200, 960)
        text(c, ln, 540, 330 + i * 210, sz, YEL if i else WHITE, SLAB, False, outline=INK, olw=22)

def THUMB_H(c):
    g = cairo.LinearGradient(0, 0, 0, 720); g.add_color_stop_rgba(0, *BG_TOP); g.add_color_stop_rgba(1, *BG_BOT); c.set_source(g); c.paint()
    glow(c, 960, 380, 420, ORANGE, 0.35)
    c.save(); c.translate(960 - 540 * 0.62, 410 - 1235 * 0.62); c.scale(0.62, 0.62); _thumb_scene(c); c.restore()
    for i, ln in enumerate(["SOLO", "ESCUCHA"]):
        sz = fit_size(c, ln, SLAB, 150, 640)
        text(c, ln, 360, 320 + i * 170, sz, YEL if i else WHITE, SLAB, False, outline=INK, olw=20)
