"""¿Por qué el cielo es azul?  Illustrations (pycairo only). Contract: output/engine/SCENES_GUIDE.md"""
from core import *  # noqa

# ---------------------------------------------------------------- colours of this video
SKY_TOP, SKY_HOR = hx("#1F63D6"), hx("#8FD0FF")
SET_TOP, SET_HOR = hx("#4A2F6E"), hx("#FF8A3A")
PALE_TOP, PALE_HOR = hx("#545B70"), hx("#8D96A8")
RL = hx("#FF4A3A")      # red light
BL = hx("#3D8BFF")      # blue light
VI = hx("#9B5CFF")      # violet
RAINBOW = [RL, hx("#FF9A2E"), YEL, hx("#5CD65C"), hx("#3FC7F5"), BL, VI]
EARTH, LAND = hx("#2E4E8F"), hx("#4C9A5A")
SKIN = hx("#F2C6A0")

def wl_rgb(l, a=1.0):
    if l < 440: r, g, b = (440 - l) / 60 * 0.75, 0, 1
    elif l < 490: r, g, b = 0, (l - 440) / 50, 1
    elif l < 510: r, g, b = 0, 1, (510 - l) / 20
    elif l < 580: r, g, b = (l - 510) / 70, 1, 0
    elif l < 645: r, g, b = 1, (645 - l) / 65, 0
    else: r, g, b = 1, 0, 0
    f = 0.45 + 0.55 * (l - 380) / 40 if l < 420 else (0.45 + 0.55 * (700 - l) / 50 if l > 650 else 1.0)
    return (r * f + 0.12, g * f + 0.1, b * f + 0.1, a)


def tfast(t):
    """Stylised animation clock: runs ~25x faster during the acelerón."""
    t0 = T_REAL + 0.2; t1 = B("remate")["start"] - 0.4
    if t <= t0: return t
    acc, x = 0.0, t0
    while x < min(t, t1 + 3):
        dx = min(0.05, t - x); acc += dx * 25 * ease(ramp(x, t0, t1)); x += dx
    return t + acc


# ---------------------------------------------------------------- drawing pieces
def ray(c, x0, y0, ang, L, lam, amp, ph, col, lw=6, fade=0.0):
    """Wavy ray: a sine along direction ang, starting at (x0, y0), length L. ph = travelling phase (rad)."""
    if L < 4: return
    ca, sa = math.cos(ang), math.sin(ang)
    n = max(3, int(L / 5))
    pts = []
    for i in range(n + 1):
        s = L * i / n
        o = amp * math.sin(2 * math.pi * s / lam - ph)
        pts.append((x0 + ca * s - sa * o, y0 + sa * s + ca * o))
    if fade <= 0: line(c, pts, col, lw); return
    k = 4
    for j in range(k):
        seg = pts[j * n // k: (j + 1) * n // k + 1]
        if len(seg) > 1: line(c, seg, alpha(col, 1 - fade * j / k), lw)


def sun(c, x, y, r, t, rays=True, col=None):
    col = col or YEL
    glow(c, x, y, r * 3.2, YEL, 0.55)
    if rays:
        c.save(); c.translate(x, y); c.rotate(t * 0.25)
        for i in range(12):
            a = i * math.pi / 6
            c.new_path(); c.move_to(math.cos(a - 0.12) * r * 1.12, math.sin(a - 0.12) * r * 1.12)
            c.line_to(math.cos(a) * r * 1.55, math.sin(a) * r * 1.55)
            c.line_to(math.cos(a + 0.12) * r * 1.12, math.sin(a + 0.12) * r * 1.12); c.close_path()
            fill_stroke(c, ORANGE2 if col == YEL else col, INK, 4)
        c.restore()
    circle(c, x, y, r); fill_stroke(c, col, INK, 6)
    circle(c, x - r * 0.3, y - r * 0.3, r * 0.28); c.set_source_rgba(1, 1, 1, 0.45); c.fill()


def n2(c, x, y, ang, s=1.0, col=None, o2=False):
    """Air molecule: two atoms (N2, or O2 if o2)."""
    col = col or (ORANGE if o2 else LAV)
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    for dx in (-11, 11):
        circle(c, dx, 0, 15); fill_stroke(c, col, INK, 5)
    circle(c, -14, -5, 4); c.set_source_rgba(1, 1, 1, 0.6); c.fill()
    c.restore()


CLOUDS = [(0.18, 0.20, 1.0), (0.62, 0.36, 0.8), (1.05, 0.14, 0.7)]

def cloud(c, x, y, s, col):
    for dx, dy, r in [(-60, 8, 34), (-22, -14, 46), (26, -6, 40), (62, 10, 30), (0, 14, 36)]:
        circle(c, x + dx * s, y + dy * s, r * s)
    c.set_source_rgba(*col); c.fill()
    c.new_path()


def landscape(c, x, y, w, h, t, sunset=0.0, sat=1.0, sun_pos=(0.76, 0.22), hz=0.74, sun_r=None, clouds=True, sun_rays=False):
    top = mix(mix(PALE_TOP, SKY_TOP, sat), SET_TOP, sunset)
    hor = mix(mix(PALE_HOR, SKY_HOR, sat), SET_HOR, sunset)
    g = cairo.LinearGradient(0, y, 0, y + h * hz)
    g.add_color_stop_rgba(0, *top); g.add_color_stop_rgba(0.65, *mix(top, hor, 0.55)); g.add_color_stop_rgba(1, *hor)
    c.new_path(); c.rectangle(x, y, w, h); c.set_source(g); c.fill()
    sx, sy = x + w * sun_pos[0], y + h * sun_pos[1]; r = sun_r or w * 0.075
    if sunset > 0: glow(c, sx, sy, r * 7, hx("#FF7A2F"), 0.55 * sunset)
    glow(c, sx, sy, r * 3.2, mix(hx("#FFF6C8"), hx("#FFB347"), sunset), 0.75)
    circle(c, sx, sy, r); c.set_source_rgba(*mix(hx("#FFF8D8"), hx("#FF7A2F"), sunset)); c.fill()
    if clouds:
        ccol = mix(alpha(WHITE, 0.95), hx("#FFB089", 0.95), sunset)
        for i, (cx_, cy_, s_) in enumerate(CLOUDS):
            px = x + ((cx_ * w + t * 9 * (1 + 0.3 * i)) % (w + 320)) - 160
            cloud(c, px, y + h * cy_ + 6, s_ * w / 900, alpha(INK, 0.12))
            cloud(c, px, y + h * cy_, s_ * w / 900, ccol)
    for k, (base, amp, fr, ph, col) in enumerate([(hz - 0.02, 0.05, 1.7, 0.4, mix(hx("#5DAE63"), hx("#7A4A4A"), sunset)),
                                                   (hz + 0.06, 0.04, 2.3, 2.0, mix(hx("#3E8A4C"), hx("#4B2E3C"), sunset))]):
        c.new_path(); c.move_to(x, y + h)
        for i in range(41):
            u = i / 40
            c.line_to(x + w * u, y + h * (base - amp * math.sin(u * math.pi * fr + ph)))
        c.line_to(x + w, y + h); c.close_path(); fill_stroke(c, col, INK, 5)
    for tx, ts in [(0.14, 1.0), (0.22, 0.75), (0.86, 0.9)]:  # little trees on the front hill
        bx = x + w * tx; by = y + h * (hz + 0.06 - 0.04 * math.sin(tx * math.pi * 2.3 + 2.0)) + 4
        rrect(c, bx - 5 * ts, by - 40 * ts, 10 * ts, 42 * ts, 3); fill_stroke(c, hx("#6B4A3A"), INK, 3)
        circle(c, bx, by - 52 * ts, 26 * ts); fill_stroke(c, mix(hx("#2F7D43"), hx("#3B2A30"), sunset), INK, 4)


WIN = (100, 650, 880, 760)   # the front window x, y, w, h

def window(c, x, y, w, h, t, r=70, inner=None, **kw):
    shadow(c, lambda: rrect(c, x - 26, y - 26, w + 52, h + 52, r + 22), 14, 20, 0.45)
    rrect(c, x - 26, y - 26, w + 52, h + 52, r + 22); fill_stroke(c, GOLD, INK, 8)
    c.save(); rrect(c, x, y, w, h, r); c.clip()
    landscape(c, x, y, w, h, t, **kw)
    if inner: inner(c)
    c.new_path(); c.move_to(x + 40, y); c.line_to(x + 170, y); c.line_to(x, y + 260); c.line_to(x, y + 90); c.close_path()
    c.set_source_rgba(1, 1, 1, 0.10); c.fill()
    c.restore()
    rrect(c, x, y, w, h, r); fill_stroke(c, None, INK, 7)


def person(c, x, y, s=1.0, look=-1.2):
    """Cartoon person, feet at (x, y). look = gaze angle (-pi/2 straight up). Returns the eye position."""
    c.save(); c.translate(x, y); c.scale(s, s)
    line(c, [(-13, 0), (-10, -62)], INK, 17); line(c, [(13, 0), (10, -62)], INK, 17)
    line(c, [(-13, 0), (-10, -62)], STEEL, 9); line(c, [(13, 0), (10, -62)], STEEL, 9)
    line(c, [(-26, -118), (-40, -68)], INK, 15); line(c, [(26, -118), (40, -68)], INK, 15)
    line(c, [(-26, -118), (-40, -68)], ORANGE2, 8); line(c, [(26, -118), (40, -68)], ORANGE2, 8)
    rrect(c, -30, -138, 60, 86, 24); fill_stroke(c, ORANGE, INK, 5)
    hx_, hy_ = 0, -170
    circle(c, hx_, hy_, 33); fill_stroke(c, SKIN, INK, 5)
    ex, ey = hx_ + 20 * math.cos(look), hy_ + 20 * math.sin(look)
    circle(c, ex, ey, 8); fill_stroke(c, WHITE, INK, 3)
    circle(c, ex + 2.5 * math.cos(look), ey + 2.5 * math.sin(look), 4); c.set_source_rgba(*INK); c.fill()
    c.restore()
    return x + ex * s, y + ey * s


# --- badge icons (drawn around 0,0 inside a r=105 badge)
def ic_pane(c):
    rrect(c, -58, -68, 116, 136, 10); fill_stroke(c, alpha(XRAY, 0.35), INK, 6)
    line(c, [(-58, 0), (58, 0)], INK, 5); line(c, [(0, -68), (0, 68)], INK, 5)
    for dx in (-30, 28):
        line(c, [(dx - 14, -40), (dx + 10, -58)], alpha(WHITE, 0.9), 6)
        line(c, [(dx - 18, 30), (dx + 12, 8)], alpha(WHITE, 0.9), 6)

def ic_paint(c):
    c.new_path(); c.move_to(-50, -40); c.line_to(-44, 62); c.curve_to(-20, 74, 20, 74, 44, 62); c.line_to(50, -40); c.close_path()
    fill_stroke(c, METAL, INK, 6)
    rrect(c, -48, -10, 96, 40, 6); fill_stroke(c, CREAM2, INK, 4)
    c.save(); c.translate(0, -40); c.scale(1, 0.3); circle(c, 0, 0, 50); c.restore(); fill_stroke(c, BL, INK, 5)
    c.new_path(); c.move_to(30, -40); c.curve_to(40, -20, 30, 0, 36, 20); c.curve_to(42, 32, 54, 24, 52, 8); c.curve_to(52, -10, 46, -30, 44, -40)
    c.close_path(); fill_stroke(c, BL, INK, 4)
    c.new_path(); c.arc(0, -40, 60, math.pi * 1.05, math.pi * 1.95); c.set_source_rgba(*INK); c.set_line_width(5); c.stroke()

def ic_glass(c):
    c.new_path(); c.move_to(-46, -66); c.line_to(-36, 66); c.line_to(36, 66); c.line_to(46, -66)
    c.set_source_rgba(1, 1, 1, 0.0)
    c.new_path(); c.move_to(-42, -20); c.line_to(-36, 66); c.line_to(36, 66); c.line_to(42, -20); c.close_path()
    fill_stroke(c, alpha(XRAY, 0.45), None)
    c.save(); c.translate(0, -20); c.scale(1, 0.18); circle(c, 0, 0, 42); c.restore(); fill_stroke(c, alpha(WHITE, 0.6), None)
    c.new_path(); c.move_to(-46, -66); c.line_to(-36, 66); c.line_to(36, 66); c.line_to(46, -66)
    c.set_source_rgba(*INK); c.set_line_width(6); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
    line(c, [(-26, -50), (-20, 40)], alpha(WHITE, 0.9), 6)

def check(c, x, y, s, t, t0):
    k = ramp(t, t0, t0 + 0.3)
    if k <= 0: return
    p1, p2, p3 = (x - s, y), (x - s * 0.3, y + s * 0.7), (x + s * 1.1, y - s * 0.8)
    k1 = ease(clamp(k * 2)); k2 = ease(clamp(k * 2 - 1))
    pts = [p1, (lerp(p1[0], p2[0], k1), lerp(p1[1], p2[1], k1))]
    if k2 > 0: pts.append((lerp(p2[0], p3[0], k2), lerp(p2[1], p3[1], k2)))
    line(c, pts, INK, 26); line(c, pts, GREEN, 15)

def brain(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    lobes = [(-62, -10, 42), (-34, -46, 44), (12, -56, 46), (54, -32, 42), (66, 12, 36), (30, 34, 42), (-20, 30, 44), (0, -4, 50)]
    for lx, ly, r in lobes: circle(c, lx, ly, r + 6)
    c.set_source_rgba(*INK); c.fill()
    for lx, ly, r in lobes: circle(c, lx, ly, r)
    c.set_source_rgba(*hx("#F4A3B8")); c.fill()
    for pts in [[(-60, -14), (-40, -26), (-30, -8), (-12, -20)], [(10, -40), (24, -22), (44, -30)], [(-24, 20), (-6, 6), (12, 20), (34, 10)],
                [(48, 0), (62, 20)], [(-40, -50), (-24, -40)]]:
        line(c, pts, hx("#C46A85"), 6)
    line(c, [(0, -96), (0, 66)], alpha(hx("#C46A85"), 0.0), 1)
    c.restore()


# ---------------------------------------------------------------- side view of the atmosphere
def atmo(c, t, cx, cy, R, th, blue=0.35, land=True):
    """Earth (centre cx, cy, radius R) with an atmosphere shell th px thick."""
    g = cairo.RadialGradient(cx, cy, R, cx, cy, R + th)
    g.add_color_stop_rgba(0, *alpha(mix(XRAY, BL, blue), 0.75))
    g.add_color_stop_rgba(0.6, *alpha(mix(XRAY, BL, blue), 0.35))
    g.add_color_stop_rgba(1, *alpha(XRAY, 0))
    c.new_path(); c.arc(cx, cy, R + th, 0, 2 * math.pi); c.set_source(g); c.fill()
    circle(c, cx, cy, R + th); c.set_source_rgba(*alpha(XRAY, 0.25)); c.set_line_width(3); c.set_dash([10, 14]); c.stroke(); c.set_dash([])
    circle(c, cx, cy, R); fill_stroke(c, EARTH, INK, 8)
    if land:
        c.save(); circle(c, cx, cy, R - 4); c.clip()
        for a, rr, dd in [(-1.95, 0.10, 0.03), (-1.62, 0.06, 0.02), (-1.28, 0.12, 0.04), (-0.9, 0.09, 0.02), (-2.3, 0.08, 0.03)]:
            px, py = cx + R * (1 + dd) * math.cos(a), cy + R * (1 + dd) * math.sin(a)
            c.save(); c.translate(px, py); c.rotate(a + math.pi / 2); c.scale(1, 0.45); circle(c, 0, 0, R * rr); c.restore()
            fill_stroke(c, LAND, INK, 4)
        c.restore()


def surf(cx, cy, R, x):
    return cy - math.sqrt(max(0, R * R - (x - cx) ** 2))


# ---------------------------------------------------------------- front (gancho + imposible + freno)
BADGES = [("transparente", 250, "TRANSPARENTE", ic_pane, False), ("pintura", 540, "PINTURA", ic_paint, True),
          ("vaso", 830, "VASO", ic_glass, True)]

def scene_front(c, t):
    background(c, t, COLD)
    tz0 = wt("freno", "vamos")
    z = ease(ramp(t, tz0, T_SLOW + 0.2))
    t_in = wt("imposible", "transparente") - 0.5
    t_out0 = wt("imposible", "encima") - 0.2
    up = ease(ramp(t, t_in, t_in + 0.5)) * (1 - ease(ramp(t, t_out0, t_out0 + 0.6)))
    push = 1.0 + 0.04 * ease(ramp(t, 0, B("imposible")["start"]))
    t_cab = wt("imposible", "cabeza") - 0.2; t_todo = wt("imposible", "todo")
    sat = 1.0 + 0.0 * t
    pk = ease(ramp(t, t_cab, t_cab + 0.4))
    x, y, w, h = WIN
    c.save()
    cam(c, push * (1 + 2.4 * z * z), W / 2, 760)
    c.translate(W / 2, y); c.scale(1 - 0.17 * up, 1 - 0.17 * up); c.translate(-W / 2, -y)

    def inner(c):
        # gancho: tiny air molecules in the sky bounce blue light ("rebota la luz azul")
        tr = wt("gancho", "rebota") - 0.2
        kb = ramp(t, tr, tr + 0.5) * (1 - ramp(t, B("imposible")["start"] - 0.3, B("imposible")["start"] + 0.3))
        if kb > 0:
            for i, (mx, my) in enumerate([(300, 820), (520, 760), (700, 900), (420, 960), (860, 800)]):
                glow(c, mx, my, 120, BL, 0.35 * kb)
                for j in range(6):
                    a = j * math.pi / 3 + i
                    ray(c, mx + 22 * math.cos(a), my + 22 * math.sin(a), a, 105 * ease(kb), 24, 5, t * 9, alpha(BL, kb), 5, 0.8)
                n2(c, mx, my, i * 0.9 + t * 0.4, 0.85 * ease(kb))
        if pk > 0 and z < 0.6:  # "encima de tu cabeza"
            c.push_group()
            ex, ey = person(c, 540, y + h - 40, 0.9 * eob(pk), -1.45)
            if t >= t_todo - 0.2:
                for j in range(7):
                    a = -math.pi / 2 + (j - 3) * 0.42
                    kk = ramp(t, t_todo - 0.2 + j * 0.05, t_todo + 0.3 + j * 0.05)
                    L = 260 * ease(kk)
                    arrow(c, ex + math.cos(a) * (300), ey + math.sin(a) * 300, ex + math.cos(a) * (300 - L) * 1.0 + math.cos(a) * 40 * (kk > 0.95),
                          ey + math.sin(a) * (300 - L) + math.sin(a) * 40 * (kk > 0.95), alpha(BL, kk), 8, 26) if kk > 0.05 else None
            c.pop_group_to_source(); c.paint_with_alpha(1 - z / 0.6)

    window(c, x, y, w, h, t, inner=inner, sat=sat)
    c.restore()

    # "casi seis veces más que la roja"
    t6 = wt("gancho", "seis") - 0.15
    k6 = eob(ramp(t, t6, t6 + 0.35)) * (1 - ease(ramp(t, B("imposible")["start"] - 0.2, B("imposible")["start"] + 0.2)))
    if k6 > 0.02:
        c.save(); c.translate(540, 1555); c.scale(k6, k6)
        rrect(c, -330, -62, 660, 124, 24); fill_stroke(c, CREAM, INK, 6)
        rrect(c, -306, -40, 210, 80, 14); fill_stroke(c, BL, INK, 4)
        text(c, "AZUL", -201, 16, 44, WHITE, SLAB, False)
        text(c, "≈ 6×", 0, 20, 58, INK, SANS, True)
        rrect(c, 96, -40, 210, 80, 14); fill_stroke(c, RL, INK, 4)
        text(c, "ROJA", 201, 16, 44, WHITE, SLAB, False)
        c.restore()
    # imposible: three badges
    if up > 0.01:
        for word, bx, lab, fn, crossed in BADGES:
            t0 = wt("imposible", word) - 0.15
            k = eob(ramp(t, t0, t0 + 0.3)) * up
            if k <= 0.02: continue
            icon_badge(c, bx, 1500, k, lab, fn, t, (t0 + 0.4) if crossed else None)
            if not crossed and k > 0.3: check(c, bx + 70, 1430, 40 * k, t, t0 + 0.4)
    # freno: fade into the side view of the atmosphere (paso1's opening frame)
    xa = ease(ramp(t, T_SLOW - 0.7, T_SLOW + 0.35))
    if xa > 0:
        c.push_group(); scene_paso1(c, t); c.pop_group_to_source(); c.paint_with_alpha(xa)


# ---------------------------------------------------------------- paso 1: white light = all the colours, each a wave
P1_SUN = (150, 760)
P1_EARTH = (540, 1640 + 2400, 2400, 110)

def scene_paso1(c, t):
    background(c, t)
    b = B("paso1")
    cx, cy, R, th = P1_EARTH
    atmo(c, t, cx, cy, R, th, 0.4)
    sx, sy = P1_SUN
    t_on = wt("paso1", "onda") - 0.2
    oy = 300 * (1 - ease(ramp(t, t_on - 0.9, t_on + 0.1)))
    sy += oy
    t_luz = wt("paso1", "luz") - 0.2
    t_col = wt("paso1", "colores") - 0.1
    kb = ease(ramp(t, t_luz, t_luz + 0.8))
    ks = ease(ramp(t, t_col, t_col + 0.7))
    xs = 330  # split point
    ph = t * 5
    if kb > 0:  # white beam
        xe = lerp(sx + 80, 1010, kb)
        x_w = min(xe, lerp(1010, xs, ks))
        glow(c, (sx + x_w) / 2, sy, 160, WHITE, 0.10)
        line(c, [(sx + 80, sy), (x_w, sy)], alpha(WHITE, 0.25), 34)
        line(c, [(sx + 80, sy), (x_w, sy)], WHITE, 12)
        if ks > 0:  # fans into the colours
            for i, col in enumerate(RAINBOW):
                dy = (i - 3) * 30 * ks
                x1 = lerp(xs, 1010, ks)
                pts = [(xs + (x1 - xs) * u / 30, sy + dy * (u / 30) ** 0.8 * 1.0) for u in range(31)]
                line(c, pts, col, 9)
    callout(c, "PARECE BLANCA", sx + 300, sy, 600, 650 + oy, t, wt("paso1", "blanca") - 0.1, WHITE)
    callout(c, "TODOS LOS COLORES", 900, sy + 60, 720, 900 + oy * 0.6, t, t_col + 0.2, YEL)
    # wave rows
    rows = [("roja", RL, 280, 1080, "ROJA", "larga", "LARGA", "tranquila", "TRANQUILA"),
            ("azul", BL, 180, 1370, "AZUL", "corta", "CORTA", "nerviosa", "NERVIOSA")]
    for i, (w0, col, lam, yy, lab, w1, lab1, w2, lab2) in enumerate(rows):
        tw = wt("paso1", w0) - 0.15
        k = eob(ramp(t, tw, tw + 0.35))
        if t < t_on - 0.4 or k <= 0.02:
            # before the word: faint hint panel once "onda" is said
            continue
        c.save(); c.translate(540, yy); c.scale(k, k); c.translate(-540, -yy)
        rrect(c, 70, yy - 120, 940, 240, 26); fill_stroke(c, alpha(NIGHT, 0.92), INK, 6)
        c.save(); rrect(c, 70, yy - 120, 940, 240, 26); c.clip()
        glow(c, 540, yy, 420, col, 0.18)
        # same speed for both colours: the short wave has to wiggle faster (higher frequency)
        v = 380.0
        phase = 2 * math.pi * v * tfast(t) / lam
        wave(c, 90, 990, yy + 10, 58, lam, -phase, alpha(col, 0.35), 22)
        wave(c, 90, 990, yy + 10, 58, lam, -phase, col, 10)
        c.restore()
        rrect(c, 70, yy - 120, 940, 240, 26); fill_stroke(c, None, INK, 6)
        rrect(c, 96, yy - 140, 170, 50, 12); fill_stroke(c, col, INK, 4)
        text(c, lab, 181, yy - 102, 34, WHITE, SLAB, False)
        # one wavelength ruler
        t1 = wt("paso1", w1) - 0.15
        k1 = ramp(t, t1, t1 + 0.4)
        if k1 > 0:
            # crests of sin(2pi x/lam - phase): x = lam*(1/4 + phase/2pi + n)
            off = (lam * (0.25 + (-phase) / (2 * math.pi))) % lam  # crest position, follows the wave (wave() uses x - x0)
            xa_ = 90 + off + lam if 90 + off < 330 else 90 + off
            xb_ = xa_ + lam * ease(k1)
            yr = yy - 75
            line(c, [(xa_, yr), (xb_, yr)], CREAM, 6)
            line(c, [(xa_, yr - 16), (xa_, yr + 16)], CREAM, 6); line(c, [(xb_, yr - 16), (xb_, yr + 16)], alpha(CREAM, k1), 6)
            text(c, lab1, (xa_ + xb_) / 2, yr - 18, 34, CREAM, SLAB, False, outline=INK, olw=8) if k1 > 0.6 else None
        t2 = wt("paso1", w2) - 0.1
        k2 = eob(ramp(t, t2, t2 + 0.3))
        if k2 > 0.02:
            c.save(); c.translate(860, yy + 118); c.scale(k2, k2)
            sz = 30
            font(c, SANS, sz, True); bw = c.text_extents(lab2).x_advance + 34
            rrect(c, -bw / 2, -26, bw, 52, 26); fill_stroke(c, CREAM, INK, 4)
            text(c, lab2, 0, 11, sz, col if i == 1 else RED, SANS, True)
            c.restore()
        c.restore()
    sun(c, sx, sy, 72, t)


# ---------------------------------------------------------------- paso 2: tiny air molecules, much smaller than a wave
P2_E = (540, 900 + 2600, 2600, 130)
P2_SRC = (600, 838)
P2_MAG = (540, 1265, 315)
_r = random.Random(7)
MOLS2 = []
while len(MOLS2) < 30:
    px, py = _r.uniform(-290, 290), _r.uniform(-290, 290)
    if px * px + py * py < 285 ** 2 and all(math.dist((px, py), m[:2]) > 82 for m in MOLS2):
        MOLS2.append((px, py, _r.uniform(0, 6.28), len(MOLS2) % 5 == 4))

def scene_paso2(c, t):
    background(c, t, COLD)
    b = B("paso2")
    cx, cy, R, th = P2_E
    atmo(c, t, cx, cy, R, th, 0.35)
    sxy = (115, 680)
    t_ent = wt("paso2", "entrar") - 0.3
    kb = ease(ramp(t, t_ent, t_ent + 0.9))
    if kb > 0:
        ex, ey = lerp(sxy[0], P2_SRC[0], kb), lerp(sxy[1], P2_SRC[1], kb)
        line(c, [sxy, (ex, ey)], alpha(WHITE, 0.25), 28); line(c, [sxy, (ex, ey)], WHITE, 10)
    sun(c, *sxy, 48, t)
    callout(c, "ATMÓSFERA", 880, surf(cx, cy, R, 880) - 70, 830, 660, t, wt("paso2", "atmósfera") - 0.1, XRAY)
    # magnifier
    mx, my, mr = P2_MAG
    t_mol = wt("paso2", "muchísimas") - 0.3
    km = eob(ramp(t, t_mol, t_mol + 0.45))
    if km > 0.02:
        r_ = mr * km
        sx_, sy_ = P2_SRC
        circle(c, sx_, sy_, 22); c.set_source_rgba(*WHITE); c.set_line_width(4); c.stroke()
        for sgn in (-1, 1):
            line(c, [(sx_ + sgn * 20, sy_ + 8), (mx + sgn * r_ * 0.97, my - r_ * 0.25)], alpha(WHITE, 0.5), 3)
        shadow(c, lambda: circle(c, mx, my, r_ + 22), 14, 18, 0.45)
        circle(c, mx, my, r_ + 22); fill_stroke(c, GOLD, INK, 8)
        c.save(); circle(c, mx, my, r_); c.clip()
        g = cairo.RadialGradient(mx, my, 20, mx, my, r_)
        g.add_color_stop_rgba(0, *hx("#2B3A66")); g.add_color_stop_rgba(1, *hx("#1A2140")); c.set_source(g); c.paint()
        t_dim = wt("paso2", "diminutas") - 0.2
        shrink = ease(ramp(t, t_dim, t_dim + 1.0))
        # the beam passing through
        glow(c, mx, my, r_ * 0.9, WHITE, 0.08 * (1 - shrink))
        lam_big = 2 * r_ * 0.78
        for k in range(3):
            yy = my - 120 + k * 120
            ray(c, mx - r_, yy, 0, 2 * r_, 70, 10, t * 6 + k, alpha(WHITE, 0.35 * (1 - shrink)), 4)
        if shrink > 0:  # one wave of (blue) light, drawn to scale against the molecules
            wave(c, mx - r_, mx + r_, my + 20, 120 * km, lam_big, 0, alpha(BL, 0.35 * shrink), 24)
            wave(c, mx - r_, mx + r_, my + 20, 120 * km, lam_big, 0, alpha(BL, shrink), 10)
        for i, (px, py, a0, o2) in enumerate(MOLS2):
            jx = 5 * math.sin(t * 3 + i * 1.3); jy = 5 * math.cos(t * 2.6 + i)
            s = lerp(1.25, 0.3, shrink) * km
            n2(c, mx + (px + jx) * km, my + (py + jy) * km, a0 + 0.3 * math.sin(t + i), s, o2=o2)
        c.restore()
        circle(c, mx, my, r_); fill_stroke(c, None, INK, 6)
        circle(c, mx, my, r_ - 10); c.set_source_rgba(1, 1, 1, 0.08); c.set_line_width(8); c.stroke()
        if km > 0.9 and shrink < 0.3:
            callout(c, "N₂", mx + MOLS2[0][0], my + MOLS2[0][1], 150, 1080, t, wt("paso2", "moléculas") + 0.1, LAV)
            callout(c, "O₂", mx + MOLS2[4][0], my + MOLS2[4][1], 930, 1080, t, wt("paso2", "aire") - 0.1, ORANGE)
        t_peq = wt("paso2", "pequeñas") - 0.2
        if shrink > 0.95:
            # ruler over one wavelength
            t_ond = wt("paso2", "onda") - 0.3
            k1 = ramp(t, t_ond, t_ond + 0.4)
            # crests of sin(2pi (x - x0)/lam) with x0 = mx - r_: x = x0 + lam/4 + n lam
            xa_ = mx - r_ + lam_big / 4; xb_ = xa_ + lam_big * ease(k1)
            yr = my - 150
            if k1 > 0:
                line(c, [(xa_, my - 100), (xa_, yr)], alpha(CREAM, 0.6), 3); line(c, [(xa_ + lam_big, my - 100), (xa_ + lam_big, yr)], alpha(CREAM, 0.6 * k1), 3)
                line(c, [(xa_, yr), (xb_, yr)], CREAM, 6)
                if k1 > 0.6: text(c, "UNA ONDA", (xa_ + xa_ + lam_big) / 2, yr - 20, 36, CREAM, SLAB, False, outline=INK, olw=8)
            mol = MOLS2[1]
            callout(c, "UNA MOLÉCULA", mx + mol[0] * 1.0, my + mol[1] * 1.0, 540, 1655, t, t_peq, LAV)


# ---------------------------------------------------------------- paso 3: scattering, blue ~5.8x more than red
P3_M = (540, 950)
P3_ANG = [i * 2 * math.pi / 10 + 0.31 for i in range(10)]

def scatter_rays(c, t, mx, my, kw, kb, kr, Lmax=300, white=False):
    ph = tfast(t) * 9
    for i, a in enumerate(P3_ANG):
        if abs(math.cos(a) + 1) < 0.05: continue
        if white:
            ray(c, mx + 55 * math.cos(a), my + 55 * math.sin(a), a, Lmax * kw, 50, 8, ph + i, alpha(WHITE, 0.85), 6, 0.8)
            continue
        if kb > 0: ray(c, mx + 55 * math.cos(a), my + 55 * math.sin(a), a, Lmax * kb, 40, 9, ph + i, BL, 7, 0.75)
        if kr > 0:
            a2 = a + 0.31
            ray(c, mx + 55 * math.cos(a2), my + 55 * math.sin(a2), a2, Lmax / 5.8 * kr, 62, 7, ph * 0.64 + i, alpha(RL, 0.9), 6, 0.3)

def scene_paso3(c, t):
    background(c, t, COLD)
    b = B("paso3")
    mx, my = P3_M
    t_az = wt("paso3", "azul") - 0.3
    my += 150 * (1 - ease(ramp(t, t_az - 0.6, t_az)))
    c.save(); cam(c, 1.0 + 0.04 * ease(ramp(t, b["start"], b["end"])), W / 2, 1000)
    t_des = wt("paso3", "desvían") - 0.2
    t_col = wt("paso3", "colores") - 0.2
    split = ease(ramp(t, t_col, t_col + 0.6))
    kw = ease(ramp(t, t_des, t_des + 0.9)) * (1 - split)
    kb = ease(ramp(t, t_col + 0.3, t_col + 1.2))
    kr = kb
    pump = 1 + 0.15 * pulse_at(t, wt("paso3", "rebota") - 0.1, 0.8) + 0.15 * pulse_at(t, wt("paso3", "rebota", 1) - 0.1, 0.8)
    glow(c, mx, my, 360, mix(WHITE, BL, split), 0.22)
    # incoming light
    ph = tfast(t) * 9
    x0 = 40
    if split < 1: ray(c, x0, my, 0, mx - 60 - x0, 50, 14, ph, alpha(WHITE, 1 - split), 9)
    if split > 0:
        ray(c, x0, my - 26, 0, mx - 60 - x0, 62, 14, ph * 0.64, alpha(RL, split), 8)
        ray(c, x0, my + 26, 0, mx - 60 - x0, 40, 14, ph, alpha(BL, split), 8)
    scatter_rays(c, t, mx, my, kw, kb * pump, kr, 300, white=(split < 0.5 and kw > 0))
    # transmitted: red keeps going (almost all of it), blue a bit weaker
    if split > 0:
        ray(c, mx + 60, my - 26 + 4, 0, 1040 - mx - 60, 62, 14, ph * 0.64, alpha(RL, split), 9)
        ray(c, mx + 60, my + 26, 0, 1040 - mx - 60, 40, 14, ph, alpha(BL, 0.45 * split), 6)
    elif kw > 0:
        ray(c, mx + 60, my, 0, 1040 - mx - 60, 50, 14, ph, alpha(WHITE, 0.8), 8)
    glow(c, mx, my, 120, WHITE, 0.3)
    n2(c, mx, my, 0.5 + 0.12 * math.sin(t * 3), 2.4)
    c.restore()
    callout(c, "MOLÉCULA", mx + 30, my - 30, 820, my - 300, t, wt("paso3", "moléculas") - 0.2, LAV)
    callout(c, "MÁS CORTA = MÁS REBOTE", mx - 260, my + 26, 330, my + 300, t, wt("paso3", "corta") - 0.1, BL)
    # bar chart
    kp = eob(ramp(t, t_az, t_az + 0.4))
    if kp > 0.02:
        c.save(); c.translate(540, 1505); c.scale(kp, kp); c.translate(-540, -1505)
        rrect(c, 80, 1340, 920, 330, 26); fill_stroke(c, CREAM, INK, 6)
        text(c, "CUÁNTO REBOTA", 540, 1392, 32, INK, SLAB, False)
        unit = 100
        t6 = wt("paso3", "seis") - 0.25
        g6 = ease(ramp(t, t6 - 0.4, t6 + 0.5))
        vb = lerp(1.0, 5.8, g6)
        for j, (lab, col, val, yy) in enumerate([("AZUL", BL, vb, 1460), ("ROJO", RL, 1.0, 1580)]):
            text(c, lab, 228, yy + 14, 40, INK, SANS, True, "r")
            kk = ease(ramp(t, t_az + 0.2, t_az + 0.6))
            bw = val * unit * kk
            rrect(c, 250, yy - 36, max(bw, 12), 72, 12); fill_stroke(c, col, INK, 5)
            s = "×" + (f"{val:.1f}".replace(".", ",") if val > 1.04 else "1")
            if j == 0 and bw > 160: text(c, s, 250 + bw - 18, yy + 17, 46, WHITE, SLAB, False, "r", outline=INK, olw=6)
            else: text(c, s, 250 + bw + 20, yy + 17, 46, INK, SLAB, False, "l")
        if g6 > 0.9:
            text(c, "CASI 6", 900, 1470, 36, RED, SLAB, False) if False else None
        c.restore()


# ---------------------------------------------------------------- paso 4: blue from everywhere, red almost straight
P4W = (80, 630, 920, 1020)
_r = random.Random(3)
MOLS4 = []
while len(MOLS4) < 16:
    px, py = _r.uniform(140, 950), _r.uniform(730, 1300)
    if all(math.dist((px, py), m) > 150 for m in MOLS4) and math.dist((px, py), (210, 740)) > 170:
        MOLS4.append((px, py))
BOUNCE = [(240, 760)]
_left = MOLS4[:]
_cur = BOUNCE[0]
for _ in range(6):
    _n = min(_left, key=lambda m: abs(math.dist(m, _cur) - 280) + (0 if m[0] > _cur[0] - 50 else 200))
    BOUNCE.append(_n); _left.remove(_n); _cur = _n

def partial(pts, frac):
    L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; d = frac * sum(L); out = [pts[0]]
    for i, l in enumerate(L):
        if d >= l: out.append(pts[i + 1]); d -= l
        else:
            a, b_ = pts[i], pts[i + 1]; out.append((a[0] + (b_[0] - a[0]) * d / l, a[1] + (b_[1] - a[1]) * d / l)); break
    return out

def wavy_path(c, pts, col, lw, lam, amp, ph):
    for i in range(len(pts) - 1):
        a, b_ = pts[i], pts[i + 1]
        L = math.dist(a, b_)
        if L < 2: continue
        ray(c, a[0], a[1], math.atan2(b_[1] - a[1], b_[0] - a[0]), L, lam, amp, ph, col, lw)

def scene_paso4(c, t):
    background(c, t, COLD)
    b = B("paso4")
    x, y, w, h = P4W
    t_mir = wt("paso4", "mires") - 0.2
    t_tod = wt("paso4", "todas") - 0.3
    sat = 0.15 + 0.85 * ease(ramp(t, t_mir, t_tod + 0.4))
    look = -math.pi / 2 + 0.6 * math.sin((t - t_mir) * 2.2) * ramp(t, t_mir, t_mir + 0.4) * (1 - ramp(t, t_tod, t_tod + 0.4))
    ph = tfast(t) * 8
    holder = {}

    def inner(c):
        sx, sy = 210, 740
        for i, (px, py) in enumerate(MOLS4):
            n2(c, px, py, i + 0.3 * math.sin(t + i), 0.7)
        # red: almost straight
        t_r = wt("paso4", "rojo") - 0.3
        kr = ease(ramp(t, t_r, t_r + 0.9))
        if kr > 0:
            x1 = lerp(sx, 1010, kr); y1 = lerp(sy, 890, kr)
            ray(c, sx + 40, sy + 6, math.atan2(890 - sy, 1010 - sx), math.dist((sx + 40, sy + 6), (x1, y1)), 62, 10, ph * 0.64, RL, 8)
        # blue: from molecule to molecule
        t_b = wt("paso4", "rebotando") - 0.3
        kb = ramp(t, t_b, wt("paso4", "cielo", end=True))
        if kb > 0:
            pts = partial(BOUNCE, ease(kb))
            wavy_path(c, pts, BL, 7, 36, 7, ph)
            for p in BOUNCE[1:len(pts)]: glow(c, p[0], p[1], 60, BL, 0.6)
        # person + blue arriving from everywhere
        ex, ey = person(c, 540, y + h - 50, 1.15, look)
        holder["eye"] = (ex, ey)
        if t >= t_mir - 0.3:
            for i, (px, py) in enumerate(MOLS4):
                k = ramp(t, t_mir - 0.3 + i * 0.09, t_mir + 0.5 + i * 0.09)
                if k <= 0: continue
                a = math.atan2(ey - py, ex - px); L = math.dist((px, py), (ex, ey)) - 50
                ray(c, px, py, a, L * ease(k), 36, 6, ph + i, alpha(BL, 0.85), 5)
                glow(c, px, py, 50, BL, 0.4)
        sun(c, sx, sy, 58, t, rays=True)

    window(c, x, y, w, h, t, r=70, inner=inner, sat=sat, sun_pos=(2.0, 2.0), clouds=False, hz=0.80)
    callout(c, "ROJO: CASI RECTO", 930, 878, 740, 680, t, wt("paso4", "recto") - 0.2, RL)
    callout(c, "DE MOLÉCULA EN MOLÉCULA", BOUNCE[3][0], BOUNCE[3][1], 430, 1220, t, wt("paso4", "molécula") - 0.1, BL)
    if "eye" in holder:
        ex, ey = holder["eye"]
        callout(c, "DE TODAS PARTES", ex + 20, ey - 10, 780, 1500, t, t_tod + 0.1, BL)


# ---------------------------------------------------------------- paso 5: violet? less from the sun, weaker in the eye
P5 = dict(x0=150, x1=930, yb=1210, yt=720)

def lx(l): return P5["x0"] + (l - 380) / 320 * (P5["x1"] - P5["x0"])
def ly(v): return P5["yb"] - v * (P5["yb"] - P5["yt"])
def f_scat(l): return (380 / l) ** 4
SOLAR = [(380, 0.58), (400, 0.8), (420, 0.88), (440, 0.96), (460, 1.0), (480, 1.0), (500, 0.98), (540, 0.95), (580, 0.92), (620, 0.87), (660, 0.81), (700, 0.75)]
def f_sun(l):
    for (a, va), (b_, vb) in zip(SOLAR, SOLAR[1:]):
        if a <= l <= b_: return lerp(va, vb, (l - a) / (b_ - a))
    return SOLAR[-1][1]
def _g(l, m, s): return math.exp(-((l - m) / s) ** 2 / 2)
_EYE_MAX = max(_g(l, 440, 26) * 0.75 + _g(l, 535, 42) + _g(l, 565, 46) for l in range(380, 701))
def f_eye(l): return (_g(l, 440, 26) * 0.75 + _g(l, 535, 42) + _g(l, 565, 46)) / _EYE_MAX

def curve(c, f, k, col, lw=9):
    if k <= 0: return
    l1 = 380 + 320 * ease(k)
    pts = [(lx(l), ly(f(l) * 0.92)) for l in [380 + i * 2 for i in range(161)] if l <= l1]
    if len(pts) > 1:
        line(c, pts, INK, lw + 8); line(c, pts, col, lw)

def tag(c, s, x, y, col, k, fg=INK, size=30):
    if k <= 0.02: return
    c.save(); c.translate(x, y); c.scale(k, k)
    font(c, SANS, size, True); bw = c.text_extents(s).x_advance + 30
    rrect(c, -bw / 2, -size * 0.85, bw, size * 1.7, 12); fill_stroke(c, col, INK, 4)
    text(c, s, 0, size * 0.36, size, fg, SANS, True)
    c.restore()

def scene_paso5(c, t):
    background(c, t, VI)
    b = B("paso5")
    t_vi = wt("paso5", "violeta") - 0.3
    kp = eob(ramp(t, b["start"] - 0.1, b["start"] + 0.35))
    c.save(); c.translate(540, 1000); c.scale(kp, kp); c.translate(-540, -1000)
    rrect(c, 80, 650, 920, 760, 26); fill_stroke(c, alpha(NIGHT, 0.95), INK, 6)
    # axes
    line(c, [(P5["x0"] - 10, P5["yt"] - 20), (P5["x0"] - 10, P5["yb"])], alpha(CREAM, 0.5), 4)
    # violet zone highlight
    kv = ease(ramp(t, t_vi, t_vi + 0.5))
    if kv > 0:
        rrect(c, lx(380), P5["yt"] - 20, lx(430) - lx(380), P5["yb"] - P5["yt"] + 20, 10)
        c.set_source_rgba(*alpha(VI, 0.22 * kv)); c.fill()
    # spectrum bar
    yb = P5["yb"] + 18
    for i in range(160):
        l = 380 + i * 2
        c.new_path(); c.rectangle(lx(l), yb, lx(l + 2) - lx(l) + 1, 54); c.set_source_rgba(*wl_rgb(l)); c.fill()
    rrect(c, lx(380), yb, lx(700) - lx(380), 54, 6); fill_stroke(c, None, INK, 5)
    for l, s in [(405, "VIOLETA"), (470, "AZUL"), (530, "VERDE"), (665, "ROJO")]:
        text(c, s, lx(l), yb + 98, 28, CREAM, SANS, True)
    # curves
    t_reb = wt("paso5", "rebota") - 0.2
    curve(c, f_scat, ramp(t, t_reb, t_reb + 0.9), hx("#B9D9FF"))
    tag(c, "REBOTE", lx(424) + 30, ly(f_scat(424) * 0.92) + 8, hx("#B9D9FF"), eob(ramp(t, t_reb + 0.4, t_reb + 0.7)))
    t_sol = wt("paso5", "sol") - 0.2
    curve(c, f_sun, ramp(t, t_sol, t_sol + 0.9), YEL)
    tag(c, "LO QUE MANDA EL SOL", lx(475), ly(f_sun(475) * 0.92) - 58, YEL, eob(ramp(t, t_sol + 0.4, t_sol + 0.7)))
    t_ojo = wt("paso5", "ojos") - 0.2
    curve(c, lambda l: f_eye(l) * 0.82, ramp(t, t_ojo, t_ojo + 0.9), hx("#7CFC9A"))
    tag(c, "LO QUE CAPTA TU OJO", lx(618), ly(f_eye(618) * 0.82 * 0.92) + 62, hx("#7CFC9A"), eob(ramp(t, t_ojo + 0.4, t_ojo + 0.7)))
    # "menos" / "peor": arrows down in the violet zone
    for w0, f, dx in [("menos", f_sun, 0), ("peor", f_eye, 0)]:
        tw = wt("paso5", w0) - 0.1
        k = ramp(t, tw, tw + 0.3)
        if k > 0:
            l = 400 if w0 == "menos" else 405
            yy = ly(f(l) * 0.92 * (0.82 if w0 == "peor" else 1))
            xx = lx(l) + (0 if w0 == "menos" else 0)
            if w0 == "menos": arrow(c, xx - 10, yy - 110, xx - 10, yy - 110 + 80 * ease(k), YEL, 9, 26)
            else: arrow(c, xx + 22, yy - 100, xx + 22, yy - 100 + 70 * ease(k), hx("#7CFC9A"), 9, 26)
    c.restore()
    # brain says AZUL
    t_cer = wt("paso5", "cerebro") - 0.2
    kb = eob(ramp(t, t_cer, t_cer + 0.4))
    if kb > 0.02:
        brain(c, 320, 1560, 1.0 * kb)
        t_mez = wt("paso5", "mezcla") - 0.1
        for i, l in enumerate([410, 450, 480]):  # the colours flow into the brain and get mixed
            k = ramp(t, t_mez + i * 0.12, t_mez + 0.6 + i * 0.12)
            if 0 < k < 1:
                px, py = lerp(lx(l), 320, ease(k)), lerp(1290, 1530, ease(k))
                circle(c, px, py, 16 * (1 - 0.5 * k)); fill_stroke(c, wl_rgb(l), INK, 3)
        t_az = wt("paso5", "azul") - 0.15
        k2 = eob(ramp(t, t_az, t_az + 0.35))
        if k2 > 0.02:
            c.save(); c.translate(700, 1540); c.scale(k2, k2)
            c.new_path(); c.move_to(-200, 30); c.line_to(-250, 70); c.line_to(-180, 50)
            rrect(c, -210, -80, 420, 160, 40); fill_stroke(c, CREAM, INK, 6)
            c.new_path(); c.move_to(-196, 20); c.line_to(-260, 64); c.line_to(-170, 52); c.close_path(); fill_stroke(c, CREAM, INK, 6)
            rrect(c, -207, -77, 414, 154, 38); c.set_source_rgba(*CREAM); c.fill()
            text(c, "¡AZUL!", 0, 30, 84, BL, SLAB, False, outline=INK, olw=10)
            c.restore()


# ---------------------------------------------------------------- junto + acelerón
J = dict(cx=540, cy=1500 + 1600, R=1600, th=230)
J_SUN = (170, 770)
J_HIT = (560, 1360)
J_P = 790
_r = random.Random(11)
MOLSJ = []
while len(MOLSJ) < 22:
    a = _r.uniform(-math.pi / 2 - 0.36, -math.pi / 2 + 0.36); rr = J["R"] + _r.uniform(40, J["th"] - 40)
    p = (J["cx"] + rr * math.cos(a), J["cy"] + rr * math.sin(a))
    if all(math.dist(p, m) > 85 for m in MOLSJ) and 40 < p[0] < 1040: MOLSJ.append(p)

def scene_junto(c, t):
    b = B("junto")
    fast = ease(ramp(t, T_REAL + 0.2, B("remate")["start"] - 0.4))
    background(c, tfast(t) * 0.3 if fast > 0 else t, COLD)
    tw = {k: wt("junto", k) - 0.1 for k in ["sol", "colores", "aire", "rebote", "azul", "ojos"]}
    shake = 7 * fast
    c.save(); cam(c, 1.0 + 0.05 * ease(ramp(t, b["start"], B("remate")["start"])), W / 2, 1150)
    c.translate(shake * math.sin(t * 61), shake * math.cos(t * 53))
    k_air = ease(ramp(t, tw["aire"], tw["aire"] + 0.4)); k_az = ease(ramp(t, tw["azul"], tw["azul"] + 0.5))
    atmo(c, t, J["cx"], J["cy"], J["R"], J["th"], 0.25 + 0.75 * k_az)
    if k_air > 0:
        glow(c, 540, 1380, 520, XRAY, 0.15 * pulse_at(t, tw["aire"], 0.8))
    for i, (px, py) in enumerate(MOLSJ):
        n2(c, px, py, i + 0.4 * math.sin(tfast(t) + i), 0.5 + 0.12 * pulse_at(t, tw["aire"] + i * 0.02, 0.6))
    ph = tfast(t) * 9
    sx, sy = J_SUN; hx_, hy_ = J_HIT
    ang = math.atan2(hy_ - sy, hx_ - sx); Lb = math.dist(J_SUN, J_HIT)
    k_col = ease(ramp(t, tw["colores"], tw["colores"] + 0.5))
    line(c, [(sx, sy), J_HIT], alpha(WHITE, 0.2), 36)
    if k_col < 1: line(c, [(sx, sy), J_HIT], alpha(WHITE, 1 - k_col), 12)
    if k_col > 0:
        for i, col in enumerate(RAINBOW):
            off = (i - 3) * 8 * k_col
            ray(c, sx - math.sin(ang) * off, sy + math.cos(ang) * off, ang, Lb, 30 + i * 6 * 0 + (6 - i) * 5, 4, ph * (1.5 - i * 0.07), alpha(col, k_col), 4)
    # rebote: blue scattered from the molecules near the beam
    k_reb = ease(ramp(t, tw["rebote"], tw["rebote"] + 0.6))
    if k_reb > 0:
        for j, m in enumerate(MOLSJ):
            if math.dist(m, J_HIT) > 330: continue
            for q in range(5):
                a = q * 2 * math.pi / 5 + j
                ray(c, m[0], m[1], a, 85 * k_reb, 24, 4, ph + j, alpha(BL, 0.9), 4, 0.7)
    ex, ey = person(c, J_P, surf(J["cx"], J["cy"], J["R"], J_P) + 4, 0.55, -math.pi / 2 - 0.5)
    k_ojo = ease(ramp(t, tw["ojos"], tw["ojos"] + 0.5))
    if k_ojo > 0:
        for j, m in enumerate(MOLSJ):
            if m[1] > ey - 20 or math.dist(m, (ex, ey)) > 520: continue
            a = math.atan2(ey - m[1], ex - m[0]); L = math.dist(m, (ex, ey)) - 14
            ray(c, m[0], m[1], a, L * k_ojo, 24, 4, ph + j, alpha(BL, 0.8), 4)
        glow(c, ex, ey, 60, BL, 0.7 * k_ojo)
    sun(c, sx, sy, 80 * (1 + 0.15 * pulse_at(t, tw["sol"], 0.6)), tfast(t))
    if fast > 0:  # light streaking at full speed
        for i in range(26):
            u = ((i * 0.137 + tfast(t) * 0.9) % 1.0)
            off = ((i * 53) % 260) - 130
            px = sx + math.cos(ang) * (Lb * u) - math.sin(ang) * off * 1.8
            py = sy + math.sin(ang) * (Lb * u) + math.cos(ang) * off * 1.8
            L = 180 * fast
            line(c, [(px, py), (px - math.cos(ang) * L, py - math.sin(ang) * L)], alpha(RAINBOW[i % 7] if i % 3 else WHITE, 0.7 * fast), 5)
        for i in range(24):
            r0 = 350 + (i * 97 + t * 2400) % 900
            a = i * 0.26
            line(c, [(540 + math.cos(a) * r0, 1150 + math.sin(a) * r0), (540 + math.cos(a) * (r0 + 130 * fast), 1150 + math.sin(a) * (r0 + 130 * fast))],
                 alpha(WHITE, 0.3 * fast), 5)
    c.restore()
    if fast < 0.3:
        callout(c, "SOL", sx + 60, sy - 50, 400, 660, t, tw["sol"], YEL)
        callout(c, "COLORES", lerp(sx, hx_, 0.45) + 8, lerp(sy, hy_, 0.45), 640, 860, t, tw["colores"], YEL)
        callout(c, "AIRE", 150, 1440, 200, 1200, t, tw["aire"], XRAY)
        callout(c, "REBOTE", MOLSJ[0][0] if False else hx_ + 80, hy_ - 40, 860, 1080, t, tw["rebote"], BL)
        callout(c, "AZUL", 330, 1420, 260, 1650, t, tw["azul"], BL)
        callout(c, "OJOS", ex, ey, 880, 1640, t, tw["ojos"], CREAM)
    flash = ramp(t, B("remate")["start"] - 0.45, B("remate")["start"] - 0.3) * (1 - ramp(t, B("remate")["start"] - 0.3, B("remate")["start"] - 0.1))
    if flash > 0: c.set_source_rgba(1, 1, 1, 0.85 * flash); c.paint()


# ---------------------------------------------------------------- remate: sunset, long path through the air
RW = (130, 640, 820, 470)
RE = dict(cx=540, cy=2370, R=800, th=150)

def scene_remate(c, t):
    b = B("remate")
    background(c, t, ORANGE)
    t_at = wt("remate", "atardecer") - 0.2
    t_cru = wt("remate", "cruza") - 0.2
    t_mas = wt("remate", "mucho") - 0.1
    t_az = wt("remate", "azul") - 0.2
    t_sol = wt("remate", "solo") - 0.2
    t_roj = wt("remate", "rojo", 0) - 0.1
    sunset = ease(ramp(t, t_at, t_roj + 0.3))
    c.save(); cam(c, 1.0 + 0.04 * ramp(t, b["start"], T_LOOP), W / 2, 1100)
    x, y, w, h = RW
    sp = (lerp(0.74, 0.30, sunset), lerp(0.22, 0.74, sunset))
    window(c, x, y, w, h, t, r=56, sunset=sunset, sat=1.0, sun_pos=sp, hz=0.76)
    kd = eob(ramp(t, b["start"] + 0.1, b["start"] + 0.5))
    cx, cy, R, th = RE["cx"], RE["cy"], RE["R"], RE["th"]
    py = cy - R
    eye = [540, py - 60]
    if kd > 0.02:
        c.save(); c.translate(540, 1560); c.scale(kd, kd); c.translate(-540, -1560)
        atmo(c, t, cx, cy, R, th, 0.5)
        turn = ease(ramp(t, t_cru + 0.4, t_cru + 0.8))
        ex, ey = person(c, 540, py + 3, 0.5, lerp(-math.pi / 2, -math.pi + 0.05, turn))
        eye[:] = [ex, ey]
        ph = t * 9
        y_top = py - th
        # noon: the sun overhead, short path through the air
        kn = ease(ramp(t, t_cru, t_cru + 0.4))
        if kn > 0:
            sun(c, 540, 1235, 34, t, rays=False)
            line(c, [(540, 1272), (540, lerp(1272, ey - 16, kn))], alpha(WHITE, 0.8), 6)
            if kn > 0.9:
                bx = 600
                line(c, [(bx, y_top), (bx, ey)], YEL, 6); line(c, [(bx - 10, y_top), (bx + 10, y_top)], YEL, 5); line(c, [(bx - 10, ey), (bx + 10, ey)], YEL, 5)
                text(c, "MEDIODÍA:", 760, 1240, 32, YEL, SLAB, False, outline=INK, olw=7)
                text(c, "POCO AIRE", 760, 1282, 32, YEL, SLAB, False, outline=INK, olw=7)
        # sunset: the sun on the horizon, a long path almost tangent to the ground
        ks = ease(ramp(t, t_cru + 0.3, t_mas + 0.6))
        if ks > 0:
            x_in = cx - math.sqrt((R + th) ** 2 - (cy - ey) ** 2)
            sun(c, 100, ey, 40, t, rays=False, col=hx("#FF8A3A"))
            x0 = 145; x1 = ex - 14
            x_end = lerp(x0, x1, ks)
            lost = ease(ramp(t, t_az, t_sol + 0.4))
            n = 30
            for i in range(n):
                xa_, xb_ = lerp(x0, x1, i / n), lerp(x0, x1, (i + 1) / n)
                if xa_ > x_end: break
                xb_ = min(xb_, x_end)
                inside = clamp((xa_ - x_in) / (x1 - x_in))
                col = mix(WHITE, mix(hx("#FFB347"), RL, inside), lost * clamp(inside * 1.5 + 0.15))
                line(c, [(xa_, ey), (xb_ + 1, ey)], col, 9)
            if ks > 0.95:
                yb = ey + 34
                line(c, [(x_in, yb), (x1, yb)], YEL, 6)
                line(c, [(x_in, yb - 10), (x_in, yb + 10)], YEL, 5); line(c, [(x1, yb - 10), (x1, yb + 10)], YEL, 5)
                text(c, "ATARDECER: MUCHO AIRE", (x_in + x1) / 2 - 20, yb + 46, 30, YEL, SLAB, False, outline=INK, olw=7)
            if lost > 0:  # blue scattered out of the beam along the way
                for i in range(6):
                    px = lerp(x_in + 20, x1 - 50, (i + 0.5) / 6)
                    for q, a in enumerate((-2.2, -1.35)):
                        k = ramp(t, t_az + i * 0.13 + q * 0.05, t_az + 0.6 + i * 0.13 + q * 0.05)
                        a2 = a + 0.25 * math.sin(i * 2.3 + q)
                        ray(c, px, ey - 4, a2, 95 * ease(k), 22, 4, ph + i, alpha(BL, 0.95 * k), 4, 0.6)
            if t >= t_sol:
                glow(c, ex, ey, 70, RL, 0.85 * ramp(t, t_sol, t_sol + 0.3))
        c.restore()
    c.restore()
    callout(c, "EL AZUL SE PIERDE", 320, eye[1] - 90, 270, 1250, t, t_az + 0.4, BL)
    callout(c, "SOLO LLEGA EL ROJO", eye[0], eye[1], 720, 1660, t, t_roj - 0.2, RL)


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
    ps = [wt("gancho", "seis") - 0.15]
    ps += [wt("imposible", w) - 0.15 for w in ("transparente", "pintura", "vaso")]
    ps += [wt("imposible", "cabeza") - 0.2]
    ps += [wt("paso1", "blanca") - 0.1, wt("paso1", "roja") - 0.15, wt("paso1", "azul") - 0.15, wt("paso1", "tranquila") - 0.1, wt("paso1", "nerviosa") - 0.1]
    ps += [wt("paso2", "atmósfera") - 0.1, wt("paso2", "muchísimas") - 0.3, wt("paso2", "moléculas") + 0.1, wt("paso2", "aire") - 0.1, wt("paso2", "pequeñas") - 0.2]
    ps += [wt("paso3", "moléculas") - 0.2, wt("paso3", "corta") - 0.1, wt("paso3", "azul") - 0.3]
    ps += [wt("paso4", "recto") - 0.2, wt("paso4", "molécula") - 0.1, wt("paso4", "todas") - 0.2]
    ps += [wt("paso5", "rebota") + 0.2, wt("paso5", "sol") + 0.2, wt("paso5", "ojos") + 0.2, wt("paso5", "cerebro") - 0.2, wt("paso5", "azul") - 0.15]
    ps += [wt("junto", k) - 0.1 for k in ["sol", "colores", "aire", "rebote", "azul", "ojos"]]
    ps += [wt("remate", "azul") + 0.1, wt("remate", "rojo") - 0.2]
    return ps


def SFX(put, L):
    np_ = __import__("numpy")
    def airy(d, fc=1800, g=1.0):
        n = int(d * L["SR"]); x = L["noise"](d, fc); tt = L["t_"](n)
        return x * np_.sin(np_.pi * tt / d) ** 2 * g
    for tt_, d in [(wt("paso1", "luz") - 0.2, 1.0), (wt("paso2", "entrar") - 0.3, 1.0), (wt("paso3", "desvían") - 0.2, 0.9),
                   (wt("paso4", "rojo") - 0.3, 0.9), (wt("paso4", "rebotando") - 0.3, 1.4), (wt("remate", "cruza") - 0.1, 1.2)]:
        put(airy(d), tt_, 0.35)
    for tt_ in [wt("paso1", "colores") - 0.1, wt("paso1", "azul") - 0.1, wt("paso3", "colores"), wt("paso3", "seis") - 0.2,
                wt("paso4", "llega"), wt("paso5", "azul") - 0.1, wt("junto", "azul") - 0.1, wt("imposible", "todo")]:
        put(L["shimmer"](), tt_, 0.35)
    put(airy(4.0, 2500, 1.0), T_REAL + 0.2, 0.3)


# ---------------------------------------------------------------- thumbnails
def _thumb_window(c, x, y, w, h, r=60):
    shadow(c, lambda: rrect(c, x - 26, y - 26, w + 52, h + 52, r + 22), 14, 20, 0.45)
    rrect(c, x - 26, y - 26, w + 52, h + 52, r + 22); fill_stroke(c, GOLD, INK, 8)
    for half, ss in [(0, 0.0), (1, 1.0)]:
        c.save(); rrect(c, x, y, w, h, r); c.clip()
        c.new_path(); c.rectangle(x + half * w / 2, y, w / 2, h); c.clip()
        landscape(c, x, y, w, h, 4.0, sunset=ss, sun_pos=(0.25, 0.22) if half == 0 else (0.78, 0.70), hz=0.78, clouds=True)
        c.restore()
    line(c, [(x + w / 2, y), (x + w / 2, y + h)], INK, 10)
    rrect(c, x, y, w, h, r); fill_stroke(c, None, INK, 7)

def _thumb_mol(c, x, y, s):
    glow(c, x, y, 260 * s, BL, 0.55)
    for i in range(12):
        a = i * math.pi / 6 + 0.2
        args = (x + 60 * s * math.cos(a), y + 60 * s * math.sin(a), a, 240 * s, 44 * s, 11 * s, i)
        ray(c, *args, INK, 20 * s); ray(c, *args, hx("#6FB4FF"), 11 * s)
    n2(c, x, y, 0.5, 3.4 * s)

def THUMB_V(c):
    background(c, 3.0, COLD)
    _thumb_window(c, 90, 760, 900, 860)
    _thumb_mol(c, 540, 1160, 1.15)
    for i, ln in enumerate(["CERO", "PINTURA"]):
        sz = fit_size(c, ln, SLAB, 200, 960)
        text(c, ln, 540, 330 + i * 210, sz, YEL if i else WHITE, SLAB, False, outline=INK, olw=22)

def THUMB_H(c):
    g = cairo.LinearGradient(0, 0, 0, 720); g.add_color_stop_rgba(0, *BG_TOP); g.add_color_stop_rgba(1, *BG_BOT); c.set_source(g); c.paint()
    glow(c, 960, 360, 420, BL, 0.35)
    _thumb_window(c, 700, 90, 520, 540, 44)
    _thumb_mol(c, 960, 360, 0.75)
    for i, ln in enumerate(["CERO", "PINTURA"]):
        sz = fit_size(c, ln, SLAB, 150, 600)
        text(c, ln, 340, 320 + i * 170, sz, YEL if i else WHITE, SLAB, False, outline=INK, olw=20)
