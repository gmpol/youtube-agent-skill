"""¿Cómo sabe tu pantalla táctil dónde la tocas?  (pantalla capacitiva proyectada)
Illustrations for the engine (output/engine/SCENES_GUIDE.md). Everything drawn with pycairo."""
from core import *  # noqa
import cairo, math, random

# ---------------------------------------------------------------- geometry
PX, PY, PW, PH = 540, 1130, 540, 1040                 # phone body (front view)
SX0, SY0 = PX - PW / 2 + 24, PY - PH / 2 + 24         # screen
SW, SH = PW - 48, PH - 48
NC, NR = 10, 20                                       # electrode grid: 200 crossings ("cientos")
def gx(i): return SX0 + (i + 0.5) * SW / NC
def gy(j): return SY0 + (j + 0.5) * SH / NR

SKIN = hx("#F2B48E"); SKIN2 = hx("#D98C69"); NAIL = hx("#FFE1D2")
WOOL = hx("#C2463F"); WOOL2 = hx("#8E2F2A"); SCREEN_BG = hx("#2A2140")

def fw(beat): return min(B(beat)["start"], min(w["start"] for w in WORDS if w["beat"] == beat))
def cut(beat): return fw(beat) - 0.25

# ---------------------------------------------------------------- app icons
ICOL = [ORANGE, YEL, RED, CREAM2, ORANGE2, STEEL, GREEN, RUST, LAV, GOLD]
ICONS = []
for r in range(5):
    for k in range(4):
        ICONS.append((SX0 + 35 + 42 + k * 114, SY0 + 120 + 42 + r * 132, ICOL[(r * 4 + k * 3) % len(ICOL)], (r * 4 + k) % 7))
for k in range(4):
    ICONS.append((SX0 + 35 + 42 + k * 114, SY0 + SH - 92, [RED, YEL, GREEN, ORANGE][k], [5, 0, 6, 2][k]))

def glyph(c, g, s=1.0):
    col = alpha(INK, 0.85)
    c.save(); c.scale(s, s); c.new_path()
    if g == 0: circle(c, 0, 0, 20); c.set_source_rgba(*col); c.set_line_width(7); c.stroke()
    elif g == 1:
        for i in range(3): rrect(c, -20 + i * 15, 8 - i * 12, 10, 14 + i * 12, 3)
        c.set_source_rgba(*col); c.fill()
    elif g == 2:
        c.move_to(-12, -18); c.line_to(18, 0); c.line_to(-12, 18); c.close_path(); c.set_source_rgba(*col); c.fill()
    elif g == 3:
        rrect(c, -22, -14, 44, 30, 6); c.set_source_rgba(*col); c.fill(); circle(c, 0, 1, 9); c.set_source_rgba(1, 1, 1, 0.8); c.fill()
    elif g == 4:
        c.move_to(0, 18); c.curve_to(-30, -2, -14, -26, 0, -9); c.curve_to(14, -26, 30, -2, 0, 18); c.close_path()
        c.set_source_rgba(*col); c.fill()
    elif g == 5:
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5; r = 22 if i % 2 == 0 else 9
            (c.move_to if i == 0 else c.line_to)(r * math.cos(a), r * math.sin(a))
        c.close_path(); c.set_source_rgba(*col); c.fill()
    else:
        rrect(c, -22, -16, 44, 28, 10); c.move_to(-10, 10); c.line_to(-16, 22); c.line_to(2, 10); c.close_path()
        c.set_source_rgba(*col); c.fill()
    c.restore(); c.new_path()

def draw_icon(c, x, y, col, g, press=0.0):
    s = 1 - 0.12 * press
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -42, -42, 84, 84, 22); fill_stroke(c, mix(col, WHITE, 0.35 * press), INK, 4)
    rrect(c, -34, -36, 68, 14, 7); c.set_source_rgba(1, 1, 1, 0.18); c.fill()
    glyph(c, g)
    c.restore()

# ---------------------------------------------------------------- phone
def body_path(c): rrect(c, PX - PW / 2, PY - PH / 2, PW, PH, 74)

def phone_display(c, t, press=None, dim=0.0, shade=True, body=True, flicker=0.0):
    press = press or {}
    if body:
        if shade: shadow(c, lambda: body_path(c), 18, 26, 0.45)
        rrect(c, PX + PW / 2 - 6, PY - 330, 16, 130, 7); fill_stroke(c, RUST, INK, 5)
        rrect(c, PX - PW / 2 - 10, PY - 380, 16, 90, 7); fill_stroke(c, RUST, INK, 5)
        rrect(c, PX - PW / 2 - 10, PY - 260, 16, 90, 7); fill_stroke(c, RUST, INK, 5)
        body_path(c); fill_stroke(c, ORANGE, INK, 8)
        rrect(c, PX - PW / 2 + 14, PY - PH / 2 + 8, PW - 28, 18, 9); c.set_source_rgba(1, 1, 1, 0.18); c.fill()
        rrect(c, PX - PW / 2 + 12, PY - PH / 2 + 12, PW - 24, PH - 24, 64); fill_stroke(c, INK, None)
    c.save(); rrect(c, SX0, SY0, SW, SH, 54); c.clip()
    g = cairo.LinearGradient(0, SY0, 0, SY0 + SH)
    g.add_color_stop_rgba(0, *hx("#2B2546")); g.add_color_stop_rgba(1, *hx("#4A2E3E")); c.set_source(g); c.paint()
    glow(c, SX0 + 60, SY0 + SH - 160, 420, ORANGE, 0.35); glow(c, SX0 + SW - 40, SY0 + 160, 320, STEEL, 0.35)
    text(c, "9:41", SX0 + 52, SY0 + 52, 26, CREAM, SANS, True, "l")
    for i in range(3): rrect(c, SX0 + SW - 92 + i * 12, SY0 + 40 - i * 5, 8, 12 + i * 5, 2); c.set_source_rgba(*CREAM); c.fill()
    rrect(c, SX0 + SW - 50, SY0 + 32, 30, 18, 4); fill_stroke(c, None, CREAM, 2.5)
    rrect(c, PX - 62, SY0 + 20, 124, 38, 19); c.set_source_rgba(*INK); c.fill()
    rrect(c, SX0 + 18, SY0 + SH - 150, SW - 36, 118, 38); c.set_source_rgba(1, 1, 1, 0.12); c.fill()
    for i, (x, y, col, gg) in enumerate(ICONS):
        draw_icon(c, x, y, col, gg, press.get(i, 0.0))
    if flicker > 0:  # the controller scanning at real speed: a blur of row flashes
        rnd = random.Random(int(t * 30))
        for _ in range(5):
            j = rnd.randrange(NR); c.set_source_rgba(*alpha(YEL, 0.18 * flicker)); c.rectangle(SX0, gy(j) - 3, SW, 6); c.fill()
    if dim > 0: c.set_source_rgba(0.05, 0.04, 0.09, dim); c.paint()
    c.restore()
    # glass sheen
    c.save(); rrect(c, SX0, SY0, SW, SH, 54); c.clip()
    c.move_to(SX0 + SW * 0.55, SY0); c.line_to(SX0 + SW * 0.78, SY0); c.line_to(SX0, SY0 + SH * 0.62); c.line_to(SX0, SY0 + SH * 0.40); c.close_path()
    c.set_source_rgba(1, 1, 1, 0.05); c.fill(); c.restore()

def grid_lines(c, rows_a, cols_a, lw=3.0, rows_k=1.0, cols_k=1.0, hl_row=None, hl_col=None, hl_a=0.0):
    for j in range(NR):
        L = SW * clamp(rows_k * 1.6 - j * 0.6 / NR)
        if L > 1 and rows_a > 0: line(c, [(SX0, gy(j)), (SX0 + L, gy(j))], alpha(ORANGE, rows_a), lw)
    for i in range(NC):
        L = SH * clamp(cols_k * 1.6 - i * 0.6 / NC)
        if L > 1 and cols_a > 0: line(c, [(gx(i), SY0), (gx(i), SY0 + L)], alpha(YEL, cols_a), lw)
    if hl_row is not None and hl_a > 0: line(c, [(SX0, gy(hl_row)), (SX0 + SW, gy(hl_row))], alpha(ORANGE, hl_a), lw * 2.6)
    if hl_col is not None and hl_a > 0: line(c, [(gx(hl_col), SY0), (gx(hl_col), SY0 + SH)], alpha(YEL, hl_a), lw * 2.6)

def node(c, x, y, r, q, lw=3, plus=True, ring=None):
    """A crossing = a tiny store of charge. q = how full (0..1)."""
    if q > 0.03: glow(c, x, y, r * 3.4, YEL, 0.55 * q)
    circle(c, x, y, r); fill_stroke(c, mix(hx("#3A3350"), YEL, q), INK, lw)
    if plus and q > 0.3: text(c, "+", x, y + r * 0.45, r * 1.35, alpha(INK, min(1, q * 1.3)), SANS, True)
    if ring: circle(c, x, y, r * 1.6); fill_stroke(c, None, ring, lw * 1.2)

# ---------------------------------------------------------------- exploded stack (tilt 0 = front view, 1 = tilted)
GAP = 190
def layer_tf(c, tilt, k, ex):
    """k = layer index -1.5 (glass, top) .. +1.5 (display, bottom)."""
    c.translate(PX - 20 * tilt, PY + k * GAP * ex + 20 * tilt)
    c.scale(1, 1 - 0.52 * tilt); c.rotate(-0.62 * tilt); c.scale(lerp(1, 0.64, tilt), lerp(1, 0.64, tilt))
    c.translate(-PX, -PY)

def to_dev(c, tilt, k, ex, x, y):
    c.save(); layer_tf(c, tilt, k, ex); p = c.user_to_device(x, y); c.restore(); return p

def sheet(c, tilt, k, ex, fill, stroke, lw=4, thick=0.0):
    if thick > 0:
        c.save(); c.translate(0, thick); layer_tf(c, tilt, k, ex); rrect(c, SX0 - 4, SY0 - 4, SW + 8, SH + 8, 56); c.restore()
        c.set_source_rgba(*alpha(stroke, 0.35)); c.fill()
    c.save(); layer_tf(c, tilt, k, ex); rrect(c, SX0 - 4, SY0 - 4, SW + 8, SH + 8, 56); c.restore()
    fill_stroke(c, fill, stroke, lw)

def phone_stack(c, t, tilt, ex, rows_a=0.0, cols_a=0.0, rows_k=1.0, cols_k=1.0, glass_hl=0.0, rows_hl=0.0, cols_hl=0.0,
                disp_hl=0.0, press=None, sweep=None):
    # display (with the phone body)
    c.save(); layer_tf(c, tilt, 1.5, ex); phone_display(c, t, press, shade=tilt < 0.5); c.restore()
    if disp_hl > 0:
        c.save(); layer_tf(c, tilt, 1.5, ex); rrect(c, SX0, SY0, SW, SH, 54); c.restore(); fill_stroke(c, None, alpha(YEL, disp_hl), 7)
    sep = ease(ramp(ex, 0.05, 0.5))
    # columns layer
    if sep > 0: sheet(c, tilt, 0.5, ex, alpha(WHITE, 0.05 * sep), alpha(mix(LAV, YEL, cols_hl), 0.8 * sep), 4 + 3 * cols_hl, 10 * tilt)
    c.save(); layer_tf(c, tilt, 0.5, ex)
    for i in range(NC):
        L = SH * clamp(cols_k * 1.6 - i * 0.6 / NC)
        if L > 1 and cols_a > 0:
            c.new_path(); c.move_to(gx(i), SY0); c.line_to(gx(i), SY0 + L)
            c.save(); c.identity_matrix(); c.set_source_rgba(*alpha(YEL, cols_a)); c.set_line_width(3.5 + 2 * cols_hl); c.stroke(); c.restore()
    c.restore()
    # rows layer
    if sep > 0: sheet(c, tilt, -0.5, ex, alpha(WHITE, 0.05 * sep), alpha(mix(LAV, ORANGE, rows_hl), 0.8 * sep), 4 + 3 * rows_hl, 10 * tilt)
    c.save(); layer_tf(c, tilt, -0.5, ex)
    for j in range(NR):
        L = SW * clamp(rows_k * 1.6 - j * 0.6 / NR)
        if L > 1 and rows_a > 0:
            c.new_path(); c.move_to(SX0, gy(j)); c.line_to(SX0 + L, gy(j))
            c.save(); c.identity_matrix(); c.set_source_rgba(*alpha(ORANGE, rows_a)); c.set_line_width(3.5 + 2 * rows_hl); c.stroke(); c.restore()
    c.restore()
    if sweep is not None and 0 < sweep < 1:  # light sweep over the whole screen ("cubren toda la pantalla")
        c.save(); layer_tf(c, tilt, -0.5, ex); rrect(c, SX0, SY0, SW, SH, 54); c.clip()
        y = SY0 + SH * sweep
        g = cairo.LinearGradient(0, y - 160, 0, y)
        g.add_color_stop_rgba(0, *alpha(YEL, 0)); g.add_color_stop_rgba(1, *alpha(YEL, 0.35)); c.set_source(g); c.rectangle(SX0, y - 160, SW, 160); c.fill()
        c.restore()
    # glass
    if sep > 0:
        sheet(c, tilt, -1.5, ex, alpha(XRAY, 0.10 + 0.10 * glass_hl), alpha(mix(XRAY, YEL, glass_hl), 0.9 * sep), 5 + 3 * glass_hl, 14 * tilt)
        c.save(); layer_tf(c, tilt, -1.5, ex)
        c.move_to(SX0 + SW * 0.6, SY0); c.line_to(SX0 + SW * 0.8, SY0); c.line_to(SX0, SY0 + SH * 0.6); c.line_to(SX0, SY0 + SH * 0.42); c.close_path()
        c.restore(); c.set_source_rgba(1, 1, 1, 0.10 * sep); c.fill()

# ---------------------------------------------------------------- hand / finger
def hand_shape(c, palm=True):
    rrect(c, -52, 0, 104, 470, 52)
    if palm: rrect(c, -95, 380, 350, 460, 140)

def hand(c, x, y, ang, lift=0.0, s=1.0, kind="skin", mirror=False, palm=True):
    """Index finger tip at (x, y); ang rotates the finger (0 = pointing up, base below). lift 0..1 = raised."""
    sc = s * (1 + 0.12 * lift)
    base = SKIN if kind == "skin" else WOOL
    dark = SKIN2 if kind == "skin" else WOOL2
    def tf(dx=0, dy=0):
        c.translate(x + dx, y + dy); c.rotate(ang); c.scale(-sc if mirror else sc, sc)
    c.save(); tf((10 + 40 * lift) * s, (16 + 56 * lift) * s); hand_shape(c, palm); c.restore()
    c.set_source_rgba(0, 0, 0, 0.30 - 0.1 * lift); c.fill()
    c.save(); tf()
    if palm:
        rrect(c, -95, 380, 350, 460, 140); fill_stroke(c, dark, INK, 7)
        for k in range(3):  # curled fingers
            rrect(c, 50, 400 + k * 80, 190, 84, 42); fill_stroke(c, base, INK, 6)
        c.save(); c.translate(-60, 520); c.rotate(-0.5); rrect(c, -46, -150, 92, 230, 46); c.restore(); fill_stroke(c, base, INK, 6)
    rrect(c, -52, 0, 104, 470, 52); fill_stroke(c, base, INK, 7)
    c.save(); rrect(c, -52, 0, 104, 470, 52); c.clip()
    if kind == "skin":
        rrect(c, -30, 12, 60, 84, 28); fill_stroke(c, NAIL, alpha(INK, 0.6), 4)
        for yy in (190, 330):
            c.new_path(); c.arc(0, yy - 40, 44, 0.9, math.pi - 0.9); c.set_source_rgba(*alpha(INK, 0.45)); c.set_line_width(4); c.stroke()
        rrect(c, 22, 30, 16, 380, 8); c.set_source_rgba(1, 1, 1, 0.18); c.fill()
    else:
        for yy in range(-8, 480, 28):
            for xx in range(-64, 64, 26):
                line(c, [(xx, yy), (xx + 13, yy + 13), (xx + 26, yy)], alpha(WOOL2, 0.9), 5)
        if kind == "touch":
            c.rectangle(-60, -5, 120, 118); c.set_source_rgba(*METAL); c.fill()
            for k in range(-6, 8):
                line(c, [(k * 16 - 40, -5), (k * 16 + 40, 115)], alpha(WHITE, 0.65), 3)
                line(c, [(k * 16 + 40, -5), (k * 16 - 40, 115)], alpha(CREAM2, 0.35), 2)
            line(c, [(-60, 113), (60, 113)], INK, 5)
    c.restore()
    rrect(c, -52, 0, 104, 470, 52); fill_stroke(c, None, INK, 7)
    c.restore()

def tip_of(x, y, ang, lift, s=1.0):
    return x, y

HOVER = (712, 1205, -0.42)
def finger_track(t, taps, hover=HOVER):
    """taps: [(t_touch, (x, y), hold)]. Returns x, y, lift."""
    x, y, _ = hover; lift = 1.0
    for tt, (tx, ty), hold in taps:
        a, b = tt - 0.3, tt + hold + 0.35
        if a <= t <= b:
            k = ease(ramp(t, a, tt)) if t < tt + hold else 1 - ease(ramp(t, tt + hold, b))
            x, y = lerp(hover[0], tx, k), lerp(hover[1], ty, k); lift = 1 - k
    return x, y, lift

def ripple(c, x, y, t, t0, col=CREAM, d=0.7, r0=20, r1=120):
    if t0 <= t < t0 + d:
        u = (t - t0) / d
        for k in (0, 0.3):
            v = clamp(u - k)
            if v > 0: circle(c, x, y, lerp(r0, r1, ease(v))); fill_stroke(c, None, alpha(col, (1 - v) * 0.9), 6)

def crosshair(c, x, y, k, col=GREEN, label=None, side=1, t=0.0):
    if k <= 0.01: return
    p = eob(k); r = 62 * p
    circle(c, x, y, r); fill_stroke(c, None, col, 6)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        line(c, [(x + dx * r * 0.55, y + dy * r * 0.55), (x + dx * r * 1.45, y + dy * r * 1.45)], col, 6)
    circle(c, x, y, 7 * p); c.set_source_rgba(*col); c.fill()
    if label and k > 0.5:
        font(c, MONO, 30, True); w = c.text_extents(label).x_advance + 26
        lx = x + side * (r * 1.45 + 14) + (0 if side > 0 else -w)
        rrect(c, lx, y - 62 - 46, w, 46, 8); fill_stroke(c, INK, col, 3)
        text(c, label, lx + w / 2, y - 62 - 13, 30, col, MONO, True)

def sparks_into(c, t, src, dst, n=6, rate=1.2, col=YEL, size=8, a=1.0, bend=0.0, seed=0):
    """Charge particles travelling from each point in src to dst (curved)."""
    if a <= 0: return
    for si, (sx, sy) in enumerate(src):
        for k in range(n):
            ph = (t * rate + k / n + 0.37 * si + seed * 0.13) % 1
            mx_, my_ = (sx + dst[0]) / 2 + bend * (1 if si % 2 else -1), (sy + dst[1]) / 2
            u = ease(ph)
            x = (1 - u) ** 2 * sx + 2 * (1 - u) * u * mx_ + u * u * dst[0]
            y = (1 - u) ** 2 * sy + 2 * (1 - u) * u * my_ + u * u * dst[1]
            al = a * math.sin(math.pi * ph)
            glow(c, x, y, size * 3, col, 0.6 * al)
            circle(c, x, y, size * (1 - 0.4 * ph)); c.set_source_rgba(*alpha(WHITE, al)); c.fill()

# ---------------------------------------------------------------- badges for "imposible"
def ic_boton(c):
    c.save(); c.scale(1, 0.5); circle(c, 0, 70, 70); c.restore(); fill_stroke(c, METAL, INK, 5)
    rrect(c, -50, -30, 100, 62, 14); fill_stroke(c, RED, INK, 5)
    c.save(); c.scale(1, 0.45); circle(c, 0, -66, 50); c.restore(); fill_stroke(c, hx("#E0574F"), INK, 5)

def ic_hunde(c):
    c.new_path(); c.move_to(-75, 40); c.line_to(-30, 40); c.curve_to(-20, 75, 20, 75, 30, 40); c.line_to(75, 40)
    c.set_source_rgba(*INK); c.set_line_width(9); c.stroke()
    arrow(c, 0, -70, 0, 30, STEEL, 16, 44)

def ic_aprieta(c):
    c.new_path(); c.arc(0, 30, 70, math.pi, 2 * math.pi); c.set_source_rgba(*INK); c.set_line_width(8); c.stroke()
    for i in range(7):
        a = math.pi + math.pi * (i + 0.5) / 7
        line(c, [(52 * math.cos(a), 30 + 52 * math.sin(a)), (66 * math.cos(a), 30 + 66 * math.sin(a))], mix(GREEN, HOT, i / 6), 7)
    line(c, [(0, 30), (60 * math.cos(-0.35), 30 + 60 * math.sin(-0.35))], RED, 8)
    circle(c, 0, 30, 10); c.set_source_rgba(*INK); c.fill()
    text(c, "kg", 0, 72, 30, INK, SANS, True)

# ---------------------------------------------------------------- scene: front (gancho + imposible + freno)
T_DEDO, T_ROBAS, T_COMPR = wt("gancho", "dedo"), wt("gancho", "robas"), wt("gancho", "comprueba")
T_EXACT = wt("imposible", "exactamente")
TAPS_FRONT = [(T_DEDO, ICONS[5][:2], 0.25), (T_ROBAS - 0.05, (500, 1050), 1.15), (T_EXACT, ICONS[10][:2], 1.3)]
BADGES = [("botones", "BOTONES", 250, ic_boton), ("hunde", "SE HUNDE", 540, ic_hunde), ("aprietes", "PRESIÓN", 830, ic_aprieta)]
T_FR0 = wt("freno", "vamos")

def scene_front(c, t):
    background(c, t, ORANGE)
    up = ease(ramp(t, wt("imposible", "botones") - 0.45, wt("imposible", "botones") - 0.05)) * (1 - ease(ramp(t, T_FR0 - 0.1, T_FR0 + 0.6)))
    tilt = ease(ramp(t, T_SLOW - 1.0, T_SLOW + 0.4)); ex = ease(ramp(t, T_SLOW - 0.8, T_SLOW + 0.5))
    push = 1.0 + 0.04 * ease(ramp(t, 0, B("imposible")["start"])) * (1 - tilt)
    zoom = 0.10 * math.sin(math.pi * ramp(t, T_FR0, T_SLOW + 0.4))   # push into the glass, then the layers come apart
    c.save()
    cam(c, push * (1 - 0.30 * up) + zoom, W / 2, 640 * up + 1130 * (1 - up))
    fx, fy, lift = finger_track(t, TAPS_FRONT)
    press = {}
    for tt, (tx, ty), hold in TAPS_FRONT:
        for i, ic in enumerate(ICONS):
            if (ic[0], ic[1]) == (tx, ty): press[i] = pulse_at(t, tt - 0.05, hold + 0.35)
    if tilt <= 0.001:
        phone_display(c, t, press, flicker=pulse_at(t, T_COMPR - 0.2, 2.0))
    else:
        phone_stack(c, t, tilt, ex, rows_a=0.75 * ex, cols_a=0.75 * ex)
    # "le robas electricidad": a lens shows the hidden grid and charge flowing into the finger
    kr = ramp(t, T_ROBAS - 0.15, T_ROBAS + 0.25) * (1 - ramp(t, T_ROBAS + 1.05, T_ROBAS + 1.35))
    if kr > 0:
        c.save(); circle(c, 500, 1050, 150 * ease(kr)); c.clip()
        c.set_source_rgba(0.05, 0.04, 0.1, 0.55); c.paint()
        grid_lines(c, 0.8, 0.8, 3)
        for i in range(NC):
            for j in range(NR):
                d = math.dist((gx(i), gy(j)), (500, 1050))
                if d < 160: node(c, gx(i), gy(j), 8, clamp(0.25 + d / 200), 2, False)
        c.restore()
        circle(c, 500, 1050, 150 * ease(kr)); fill_stroke(c, None, alpha(YEL, 0.9), 5)
        src = [(gx(i), gy(j)) for i in range(NC) for j in range(NR) if math.dist((gx(i), gy(j)), (500, 1050)) < 95]
        sparks_into(c, t, src[:8], (500, 1040), 3, 1.6, YEL, 6, kr, 30)
    for tt, (tx, ty), hold in TAPS_FRONT:
        ripple(c, tx, ty, t, tt)
    out = ease(ramp(t, T_FR0 + 0.2, T_FR0 + 1.1))
    out = max(out, ease(ramp(t, wt("imposible", "botones") - 0.6, wt("imposible", "botones"))) * (1 - ease(ramp(t, T_EXACT - 0.8, T_EXACT - 0.3))))
    if out < 1:
        hand(c, fx + 500 * out, fy + 700 * out, HOVER[2], lift)
    ke = ramp(t, wt("imposible", "dónde") - 0.1, wt("imposible", "dónde") + 0.25) * (1 - ramp(t, T_FR0, T_FR0 + 0.3))
    if ke > 0: crosshair(c, ICONS[10][0], ICONS[10][1], ke, GREEN, "X 7 · Y 9", -1)
    c.restore()
    # crossed-out badges
    if up > 0.01:
        for word, lab, x, fn in BADGES:
            t0 = wt("imposible", word) - 0.15
            k = eob(ramp(t, t0, t0 + 0.3)) * up
            k *= 1 - ease(ramp(t, T_EXACT - 0.7, T_EXACT - 0.2))
            icon_badge(c, x, 1460, k, lab, fn, t, t0 + 0.4, r=100)

# ---------------------------------------------------------------- scene: paso1 (exploded stack -> top view)
def scene_paso1(c, t):
    background(c, t, STEEL)
    b = B("paso1")
    T_CRI, T_REJ, T_FIL, T_COL = wt("paso1", "cristal"), wt("paso1", "rejilla"), wt("paso1", "filas"), wt("paso1", "columnas")
    T_FIN, T_VES, T_CUB = wt("paso1", "finos"), wt("paso1", "ves"), wt("paso1", "cubren")
    col = ease(ramp(t, T_FIN - 0.2, T_FIN + 1.1))          # collapse into the top view
    tilt, ex = 1 - col, 1 - col
    bob = 0.03 * math.sin(t * 1.4)
    rows_k = ease(ramp(t, T_REJ - 0.1, T_FIL + 0.2)); cols_k = ease(ramp(t, T_REJ + 0.3, T_COL + 0.2))
    fade = 1 - 0.8 * ease(ramp(t, T_VES - 0.5, T_VES + 0.2))   # "no los ves"
    sw = ramp(t, T_CUB - 0.1, T_CUB + 1.0)
    fade = max(fade, 0.2 + 0.7 * math.sin(math.pi * sw))
    c.save(); cam(c, 1.0 + 0.04 * ramp(t, b["start"], b["end"]), W / 2, 1100)
    phone_stack(c, t, tilt, ex + bob * ex, rows_a=0.85 * fade, cols_a=0.85 * fade, rows_k=rows_k, cols_k=cols_k,
                glass_hl=pulse_at(t, T_CRI - 0.1, 1.0), rows_hl=pulse_at(t, T_FIL - 0.1, 1.0), cols_hl=pulse_at(t, T_COL - 0.1, 1.0),
                sweep=sw)
    pts = {k: to_dev(c, tilt, k, ex + bob * ex, PX + PW / 2 - 30, PY - 120) for k in (-1.5, -0.5, 0.5, 1.5)}
    lft = {k: to_dev(c, tilt, k, ex + bob * ex, PX - PW / 2 + 40, PY + 200) for k in (-1.5, -0.5, 0.5, 1.5)}
    c.restore()
    if col < 0.3:
        a = 1 - col / 0.3
        c.push_group()
        callout(c, "CRISTAL", *pts[-1.5], 830, 700, t, T_CRI)
        callout(c, "FILAS", *lft[-0.5], 190, 930, t, T_FIL, ORANGE)
        callout(c, "COLUMNAS", *pts[0.5], 840, 1180, t, T_COL, YEL)
        callout(c, "PANTALLA", *lft[1.5], 220, 1560, t, wt("paso1", "debajo") + 0.2)
        c.pop_group_to_source(); c.paint_with_alpha(a)
    kt = ramp(t, T_REJ, T_REJ + 0.35) * (1 - ramp(t, T_FIN - 0.3, T_FIN))
    if kt > 0: text(c, "CABLES TRANSPARENTES", 540, 1690, 40, alpha(XRAY, kt), SLAB, False, outline=INK, olw=8)
    kv = ramp(t, T_VES - 0.2, T_VES + 0.2)
    if kv > 0 and sw <= 0: text(c, "MÁS FINOS QUE UN PELO", 540, 1700, 40, alpha(CREAM, kv), SLAB, False, outline=INK, olw=8)
    if sw > 0: text(c, "TODA LA PANTALLA", 540, 1700, 44, alpha(YEL, min(1, sw * 4)), SLAB, False, outline=INK, olw=8)

# ---------------------------------------------------------------- scene: paso2 (each crossing stores charge)
R0, C0 = 9, 4
def wcam(c, z, wx, wy, sx=540, sy=1140):
    c.translate(sx, sy); c.scale(z, z); c.translate(-wx, -wy)

def scene_paso2(c, t):
    background(c, t, YEL)
    T_FILA, T_CRU, T_COL = wt("paso2", "fila"), wt("paso2", "cruza"), wt("paso2", "columna")
    T_ALM, T_CAR, T_CIE, T_CIT = wt("paso2", "almacén"), wt("paso2", "carga"), wt("paso2", "cientos"), wt("paso2", "cargita")
    zin = ease(ramp(t, cut("paso2"), cut("paso2") + 1.1))
    zout = ease(ramp(t, T_CIE - 0.5, T_CIE + 1.0))
    z = lerp(lerp(1.0, 4.2, zin), 0.92, zout)
    wx, wy = lerp(gx(C0), PX, zout), lerp(gy(R0), PY, zout)
    sy = lerp(1140, 1120, zout)
    c.save(); rrect(c, 24, 600, W - 48, 1100, 40); c.clip()
    c.save(); wcam(c, z, wx, wy, 540, sy)
    phone_display(c, t, dim=lerp(0.4, 0.8, zin) * (1 - 0.6 * zout))
    hl = clamp(pulse_at(t, T_FILA - 0.1, 1.3) + ramp(t, T_COL, T_COL + 0.2) * 0)
    grid_lines(c, 0.55, 0.55, 2.6)
    kr = ramp(t, T_FILA - 0.1, T_FILA + 0.3) * (1 - 0.6 * zout)
    if kr > 0: line(c, [(SX0, gy(R0)), (SX0 + SW * ease(kr), gy(R0))], ORANGE, 7)
    kc = ramp(t, T_COL - 0.1, T_COL + 0.3) * (1 - 0.6 * zout)
    if kc > 0: line(c, [(gx(C0), SY0), (gx(C0), SY0 + SH * ease(kc))], YEL, 7)
    cx_, cy_ = gx(C0), gy(R0)
    kx = ramp(t, T_CRU, T_CRU + 0.4)
    # empty crossings first, then the charge appears
    for i in range(NC):
        for j in range(NR):
            x, y = gx(i), gy(j)
            if (i, j) == (C0, R0):
                q = ease(ramp(t, T_ALM - 0.1, T_CAR + 0.3))
                if kx > 0 or q > 0: node(c, x, y, 9 * max(eob(kx), 0.01), q, 2.5)
                continue
            d = math.dist((x, y), (cx_, cy_))
            k = ramp(t, T_CIE - 0.3 + d / 900, T_CIE + d / 900)
            if k > 0: node(c, x, y, 9 * eob(k), k * (0.85 + 0.15 * pulse_at(t, T_CIT - 0.1 + d / 2000, 0.6)), 2.5)
    pq = pulse_at(t, T_CIT - 0.1, 0.6)
    if pq > 0: glow(c, cx_, cy_, 30, WHITE, 0.4 * pq)
    if T_ALM <= t < T_CIE:  # the "+" charges arriving into the store
        for k in range(6):
            ph = ((t - T_ALM) * 0.9 + k / 6) % 1
            a = k * 1.047 + t * 0.4
            r = lerp(60, 10, ease(ph))
            text(c, "+", cx_ + r * math.cos(a), cy_ + r * math.sin(a) + 4, 11, alpha(YEL, math.sin(math.pi * ph)), SANS, True)
    c.restore(); c.restore()
    rrect(c, 24, 600, W - 48, 1100, 40); fill_stroke(c, None, alpha(LAV, 0.25 * (1 - zout)), 3)
    def dev(x, y): return (540 + (x - wx) * z, sy + (y - wy) * z)
    if zout < 0.2:
        a = 1 - zout / 0.2
        c.push_group()
        callout(c, "FILA", 170, 1140, 210, 880, t, T_FILA, ORANGE)
        callout(c, "COLUMNA", 540, 1420, 300, 1560, t, T_COL, YEL)
        callout(c, "CRUCE", *dev(cx_ + 7, cy_ - 7), 790, 860, t, T_CRU + 0.1)
        callout(c, "ALMACÉN DE CARGA", *dev(cx_ + 6, cy_ + 9), 720, 1480, t, T_CAR, YEL)
        c.pop_group_to_source(); c.paint_with_alpha(a)
    k = ramp(t, T_CIE, T_CIE + 0.4)
    if k > 0: callout(c, "CIENTOS DE CRUCES", 540 + (gx(8) - PX) * 0.92, 1120 + (gy(2) - PY) * 0.92, 790, 650, t, T_CIE + 0.2, YEL)

# ---------------------------------------------------------------- side view (paso3, paso5)
NODE_X = [120 + i * 105 for i in range(9)]; NODE_Y = 1305; GL_Y = 1190
def side_view(c, t, q, flow=0.0, labels=1.0):
    rrect(c, 40, GL_Y - 30, 1000, 330, 46); fill_stroke(c, ORANGE, INK, 8)
    rrect(c, 66, GL_Y - 6, 948, 280, 30); fill_stroke(c, INK, None)
    # display
    rrect(c, 80, 1360, 920, 70, 14); fill_stroke(c, hx("#2B2546"), alpha(LAV, 0.5), 3)
    for i in range(46):
        c.set_source_rgba(*alpha([RED, GREEN, COLD][i % 3], 0.6)); c.rectangle(92 + i * 19.6, 1378, 12, 34); c.fill()
    # electrode layer: one row seen along its length, columns as small squares
    line(c, [(90, NODE_Y + 26), (990, NODE_Y + 26)], ORANGE, 6)
    for i, x in enumerate(NODE_X):
        c.rectangle(x - 16, NODE_Y + 14, 32, 10); c.set_source_rgba(*YEL); c.fill()
    for i, x in enumerate(NODE_X):
        node(c, x, NODE_Y - 8, 20, q[i], 3)
    # glass
    rrect(c, 66, GL_Y - 6, 948, 64, 14); fill_stroke(c, alpha(XRAY, 0.28), XRAY, 4)
    line(c, [(110, GL_Y + 6), (360, GL_Y + 6)], alpha(WHITE, 0.6), 5)
    if labels > 0:
        text(c, "CRISTAL", 960, GL_Y + 38, 24, alpha(XRAY, labels), SANS, True, "r")
        text(c, "PANTALLA", 960, 1404, 24, alpha(CREAM, labels), SANS, True, "r")

def finger_down(c, tip_y, kind="skin", x=540, s=1.25):
    """Finger pointing down from the top, faded where it leaves the frame."""
    c.push_group()
    hand(c, x, tip_y, math.pi, 0.0, s, kind, mirror=True)
    c.pop_group_to_source()
    g = cairo.LinearGradient(0, 600, 0, 700); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 1)
    c.mask(g)

def flow_up(c, t, xs, tip, a, rate=0.9):
    """Charge leaving the crossings, crossing the glass, into the fingertip (field lines + particles)."""
    if a <= 0: return
    for x in xs:
        pts = []
        for i in range(21):
            u = i / 20
            px_ = lerp(x, tip[0] + (x - tip[0]) * 0.25, u); py_ = lerp(NODE_Y - 20, tip[1] + 10, u) - 40 * math.sin(math.pi * u) * (x - tip[0]) / 200
            pts.append((px_, py_))
        line(c, pts, alpha(YEL, 0.35 * a), 4)
    sparks_into(c, t, [(x, NODE_Y - 20) for x in xs], (tip[0], tip[1] + 6), 4, rate, YEL, 9, a, 0)

def check_mark(c, x, y, k):
    if k <= 0: return
    p = eob(k)
    c.save(); c.translate(x, y); c.scale(p, p)
    circle(c, 0, 0, 62); fill_stroke(c, GREEN, INK, 6)
    line(c, [(-28, 2), (-8, 24), (30, -22)], WHITE, 14)
    c.restore()

def scene_paso3(c, t):
    background(c, t, COLD)
    b = B("paso3")
    T_AG, T_SAL, T_CON = wt("paso3", "agua"), wt("paso3", "sal"), wt("paso3", "conduce")
    T_ACE, T_LLE, T_CAR, T_DEB = wt("paso3", "acercas"), wt("paso3", "llevas"), wt("paso3", "carga"), wt("paso3", "cruces")
    c.save(); cam(c, 1.0 + 0.05 * ramp(t, b["start"], b["end"]), W / 2, 1200)
    enter = ease(ramp(t, cut("paso3"), cut("paso3") + 0.9))
    down = ease(ramp(t, T_ACE - 0.1, T_ACE + 0.7))
    tip = lerp(lerp(560, 905, enter), GL_Y - 8, down)
    flow = ramp(t, T_LLE - 0.2, T_LLE + 0.3)
    drain = ease(ramp(t, T_LLE, T_CAR + 0.6))
    q = []
    for x in NODE_X:
        w_ = math.exp(-((x - 540) / 110) ** 2)
        q.append(1 - 0.75 * drain * w_ if w_ > 0.2 else 1.0)
    side_view(c, t, q)
    flow_up(c, t, [x for x in NODE_X if abs(x - 540) < 120], (540, tip), flow)
    finger_down(c, tip)
    kc = ramp(t, T_CON - 0.1, T_CON + 0.3)
    if kc > 0:  # conductor: electric shimmer along the finger outline
        for s_ in (-1, 1):
            pts = [(540 + s_ * (70 + 6 * math.sin(i * 1.7 + t * 9)), tip - 20 - i * 20) for i in range(18) if tip - 20 - i * 20 > 640]
            if len(pts) > 1: line(c, pts, alpha(XRAY, 0.8 * kc), 4)
    # window into the finger: salty water
    kw = ramp(t, T_AG - 0.15, T_AG + 0.3)
    if kw > 0:
        wx, wy, r = 540, tip - 215, 58 * eob(kw)
        c.save(); circle(c, wx, wy, r); c.clip()
        c.set_source_rgba(*hx("#2F6EA8")); c.paint()
        for i in range(7):
            a = i * 0.9 + t * 0.6; rr = 18 + (i * 13) % 34
            x, y = wx + rr * math.cos(a), wy + rr * math.sin(a * 1.3)
            if t >= T_SAL and i % 2 == 0:
                circle(c, x, y, 10); fill_stroke(c, YEL if i % 4 == 0 else CREAM, INK, 2)
                text(c, "+" if i % 4 == 0 else "−", x, y + 6, 16, INK, SANS, True)
            else:
                circle(c, x, y, 6); c.set_source_rgba(*alpha(XRAY, 0.9)); c.fill()
        c.restore()
        circle(c, wx, wy, r); fill_stroke(c, None, INK, 6)
        circle(c, wx, wy, r - 5); fill_stroke(c, None, alpha(WHITE, 0.4), 2)
    c.restore()
    callout(c, "AGUA CON SAL", 540 + 50, tip - 215 - 30, 800, 720, t, T_AG + 0.1, XRAY)
    callout(c, "CONDUCE", 540 - 72, tip - 110, 220, 900, t, T_CON, YEL)
    callout(c, "MENOS CARGA", 540 + 16, NODE_Y + 4, 720, 1600, t, T_DEB, YEL)
    callout(c, "TE LA LLEVAS", 540 - 40, GL_Y - 40, 230, 1110, t, T_CAR)

# ---------------------------------------------------------------- scan view (paso4, junto, acelera)
NC4, NR4 = 7, 8
XS = [190 + i * 100 for i in range(NC4)]; YS = [690 + j * 95 for j in range(NR4)]
F1 = (XS[4], YS[2]); F2 = (XS[1], YS[6])
CHIP = (490, 1575)

def scan_pos(t):
    return anim_time(t) * 120  # sweeps done (120 per real second)

def scan_view(c, t, f1=0.0, f2=0.0, hole=0.0, cross1=0.0, cross2=0.0, chip_k=1.0, scan_k=1.0, fast=0.0, hl=None, flow=0.0):
    hl = hl or set()
    # panel (glass seen from above)
    rrect(c, 120, 625, 740, 820, 34); fill_stroke(c, alpha(hx("#2B2546"), 0.9), alpha(XRAY, 0.7) if "rejilla" not in hl else YEL, 5)
    sp = scan_pos(t); row_f = (sp % 1) * NR4; row = int(row_f)
    def qn(x, y):
        q = 1.0
        for (fx, fy), a in ((F1, f1), (F2, f2)):
            if a > 0: q *= 1 - 0.78 * hole * a * math.exp(-(math.dist((x, y), (fx, fy)) / 75) ** 2)
        return q
    # wires to the chip
    wc = YEL if "chip" in hl else alpha(LAV, 0.55)
    line(c, [(150, YS[0]), (90, YS[0] + 30), (90, CHIP[1]), (CHIP[0] - 150, CHIP[1])], wc, 7)
    for j, y in enumerate(YS): line(c, [(150, y), (110, y)], alpha(ORANGE, 0.7), 4)
    for i, x in enumerate(XS):
        line(c, [(x, 1420), (x, 1440), (CHIP[0] - 90 + i * 30, CHIP[1] - 52)], wc, 4)
    # grid lines
    for j, y in enumerate(YS):
        line(c, [(150, y), (830, y)], alpha(ORANGE, 0.55 if "rejilla" not in hl else 0.95), 5)
    for i, x in enumerate(XS):
        line(c, [(x, 650), (x, 1420)], alpha(YEL, 0.5 if "rejilla" not in hl else 0.95), 5)
    # the active row being read
    if scan_k > 0:
        if fast > 0.3:  # real speed: a blur
            c.set_source_rgba(*alpha(CREAM, 0.20 * fast * scan_k)); c.rectangle(130, 650, 720, 770); c.fill()
        y = YS[row]
        glow(c, 150, y, 60, CREAM, 0.6 * scan_k)
        line(c, [(150, y), (830, y)], alpha(CREAM, 0.95 * scan_k), 9)
        line(c, [(110, y), (150, y)], alpha(CREAM, scan_k), 9)
    for j, y in enumerate(YS):
        for i, x in enumerate(XS):
            q = qn(x, y)
            ring = None
            if scan_k > 0 and j == row:
                ring = alpha(RED, scan_k) if q < 0.6 else alpha(GREEN, scan_k * 0.9)
            node(c, x, y, 17, q, 3, True, ring)
    # fingers (ghosted so the grid shows through)
    for (fx, fy), a, mir in ((F1, f1, False), (F2, f2, True)):
        if a > 0:
            c.push_group(); hand(c, fx, fy + 6, 0.42 if mir else -0.42, 0.25, 0.85, mirror=mir); c.pop_group_to_source()
            c.paint_with_alpha(0.5 * a)
            for j, y in enumerate(YS):
                for i, x in enumerate(XS):
                    q = qn(x, y)
                    if q < 0.7: node(c, x, y, 17, q, 3, True, alpha(RED, 0.9 * hole * a))
            if flow > 0:
                src = [(x, y) for x in XS for y in YS if 0 < math.dist((x, y), (fx, fy)) < 110]
                sparks_into(c, t, src, (fx, fy), 3, 1.3, YEL, 7, flow * a, 20)
    crosshair(c, *F1, cross1, GREEN, "X 5 · Y 3", 1)
    crosshair(c, *F2, cross2, GREEN, "X 2 · Y 7", 1)
    # chip
    if chip_k > 0:
        p = eob(chip_k); cx, cy = CHIP
        c.save(); c.translate(cx, cy); c.scale(p, p)
        if "chip" in hl: glow(c, 0, 0, 220, YEL, 0.5)
        for i in range(9):
            line(c, [(-120 + i * 30, -52), (-120 + i * 30, -66)], METAL, 6); line(c, [(-120 + i * 30, 52), (-120 + i * 30, 66)], METAL, 6)
        rrect(c, -150, -52, 300, 104, 14); fill_stroke(c, hx("#22202C"), INK if "chip" not in hl else YEL, 6)
        text(c, "CHIP", -70, 14, 40, CREAM, SLAB, False)
        rrect(c, 10, -30, 122, 60, 8); fill_stroke(c, hx("#1E3A2A"), INK, 3)
        n = max(0, int(sp - scan_pos(wt('paso4', 'revisa') - 0.1))) % 1000
        text(c, f"#{n:03d}", 71, 12, 28, hx("#7CFC9A"), MONO, True)
        c.restore()

def scene_paso4(c, t):
    background(c, t, STEEL)
    b = B("paso4")
    T_CHIP, T_REV, T_OTRA, T_120 = wt("paso4", "chip"), wt("paso4", "revisa"), wt("paso4", "otra"), wt("paso4", "ciento")
    T_FAL, T_AHI, T_DED, T_VAR, T_HUE = wt("paso4", "falta"), wt("paso4", "ahí"), wt("paso4", "dedo"), wt("paso4", "varios"), wt("paso4", "huecos")
    c.save(); cam(c, 1.0 + 0.04 * ramp(t, b["start"], b["end"]), W / 2, 1100)
    f1 = ease(ramp(t, T_FAL - 0.9, T_FAL - 0.2)); f2 = ease(ramp(t, T_VAR - 0.4, T_VAR + 0.2))
    scan_view(c, t, f1=f1, f2=f2, hole=1.0, cross1=ramp(t, T_AHI, T_AHI + 0.35), cross2=ramp(t, T_HUE - 0.1, T_HUE + 0.25),
              chip_k=ramp(t, T_CHIP - 0.3, T_CHIP + 0.1), scan_k=ramp(t, T_REV - 0.1, T_REV + 0.3))
    c.restore()
    def d(x, y): s = 1.0 + 0.04 * ramp(t, b["start"], b["end"]); return (540 + (x - 540) * s, 1100 + (y - 1100) * s)
    callout(c, "REVISA FILA A FILA", *d(830, YS[0]), 700, 650, t, T_REV + 0.15, CREAM, 30)
    k = eob(ramp(t, T_120 - 0.1, T_120 + 0.3))
    if k > 0:  # 120 vueltas por segundo
        c.save(); c.translate(*d(800, 1580)); c.scale(k, k)
        rrect(c, -95, -62, 190, 124, 18); fill_stroke(c, CREAM, INK, 6)
        text(c, "120", 0, 8, 58, RED, SLAB, False); text(c, "VECES / SEG", 0, 44, 22, INK, SANS, True)
        c.restore()
        line(c, [d(640, 1575), d(705, 1580)], alpha(WHITE, 0.8 * clamp(k)), 4)
    kf = ramp(t, T_FAL, T_FAL + 0.3) * (1 - ramp(t, T_VAR - 0.4, T_VAR))
    if kf > 0: text(c, "FALTA CARGA", 540, 1700, 46, alpha(HOT, kf), SLAB, False, outline=INK, olw=8)
    kv = ramp(t, T_HUE, T_HUE + 0.3)
    if kv > 0: text(c, "2 DEDOS = 2 HUECOS", 540, 1700, 46, alpha(GREEN, kv), SLAB, False, outline=INK, olw=8)

# ---------------------------------------------------------------- scene: paso5 (gloves)
def scene_paso5(c, t):
    background(c, t, RED)
    b = B("paso5")
    T_GU, T_LANA, T_NOC, T_NADA = wt("paso5", "guantes"), wt("paso5", "lana"), wt("paso5", "conduce"), wt("paso5", "nada")
    T_TAC, T_HILO, T_MET, T_PUN = wt("paso5", "táctiles"), wt("paso5", "hilo"), wt("paso5", "metal"), wt("paso5", "puntas")
    c.save(); cam(c, 1.0 + 0.05 * ramp(t, b["start"], b["end"]), W / 2, 1200)
    # wool glove: comes down, nothing happens, goes away
    d1 = ease(ramp(t, T_GU - 0.2, T_GU + 0.5)); u1 = ease(ramp(t, T_NADA + 0.5, T_NADA + 1.1))
    tip1 = lerp(lerp(lerp(420, 760, ease(ramp(t, cut('paso5'), cut('paso5') + 0.8))), GL_Y - 8, d1), 380, u1)
    d2 = ease(ramp(t, T_TAC - 0.5, T_HILO - 0.1))
    tip2 = lerp(420, GL_Y - 8, d2)
    flow = ramp(t, T_HILO + 0.1, T_MET + 0.3)
    drain = ease(ramp(t, T_HILO + 0.2, T_PUN))
    q = [1 - 0.75 * drain * math.exp(-((x - 540) / 110) ** 2) if abs(x - 540) < 120 else 1.0 for x in NODE_X]
    pulse = pulse_at(t, T_NADA - 0.1, 0.7)
    side_view(c, t, [min(1, v + 0.0) for v in q])
    if pulse > 0:
        for x in NODE_X: glow(c, x, NODE_Y - 8, 70, YEL, 0.5 * pulse)
    flow_up(c, t, [x for x in NODE_X if abs(x - 540) < 120], (540, tip2), flow)
    if u1 < 1: finger_down(c, tip1, "wool")
    if d2 > 0: finger_down(c, tip2, "touch")
    # wool: blocked
    if d1 > 0.9 and u1 < 0.3:
        kb = ramp(t, T_NOC - 0.2, T_NOC + 0.2)
        for x in (435, 540, 645):  # charges that stay put
            line(c, [(x, NODE_Y - 40), (x + (540 - x) * 0.3, GL_Y + 5)], alpha(LAV, 0.4 * kb), 4)
    c.restore()
    if u1 < 0.4:
        a = 1 - u1 / 0.4
        c.push_group()
        callout(c, "LANA", 560, GL_Y - 230, 820, 760, t, T_LANA, CREAM)
        k = ramp(t, T_NOC, T_NOC + 0.3)
        if k > 0:
            xmark(c, 790, 960, 60, t, T_NOC, 18)
            text(c, "NO CONDUCE", 790, 1100, 40, HOT, SLAB, False, outline=INK, olw=8)
        if t > T_NADA:
            text(c, "NO SE LLEVA NADA", 540, 1620, 44, alpha(CREAM, ramp(t, T_NADA, T_NADA + 0.3)), SLAB, False, outline=INK, olw=8)
        c.pop_group_to_source(); c.paint_with_alpha(a)
    if d2 > 0.5:
        callout(c, "HILO CON METAL", 540 + 50, GL_Y - 60, 800, 860, t, T_HILO + 0.05, YEL, 32)
        check_mark(c, 300, 960, ramp(t, T_MET + 0.2, T_MET + 0.5))
        if t > T_MET + 0.3:
            text(c, "SÍ FUNCIONA", 300, 1080, 40, alpha(hx("#7CFC9A"), ramp(t, T_MET + 0.3, T_MET + 0.6)), SLAB, False, outline=INK, olw=8)

# ---------------------------------------------------------------- scene: junto + acelerón
JUNTO = ["rejilla", "carga", "dedo", "robo", "chip", "posición"]
def scene_all(c, t):
    background(c, t, YEL)
    T_RS = cut("remate") + 0.1
    fast = ease(ramp(t, T_REAL + 0.2, T_RS - 0.4))
    tw = {w: wt("junto", w) for w in JUNTO}
    hl = {w for w in JUNTO if t >= tw[w] - 0.1}
    shake = 7 * fast
    c.save(); cam(c, 1.0 + 0.05 * ease(ramp(t, B("junto")["start"], T_RS)), W / 2, 1100)
    c.translate(shake * math.sin(t * 61), shake * math.cos(t * 53))
    scan_view(c, t, f1=1.0, hole=1.0, cross1=1.0 if "posición" not in hl else 1.0, fast=fast, hl=hl,
              flow=1.0 if "robo" in hl else 0.0)
    if "carga" in hl: glow(c, XS[1], YS[0], 90, YEL, 0.7 * (1 - fast))
    if "dedo" in hl: glow(c, F1[0] + 60, F1[1] + 160, 200, CREAM, 0.25 * (1 - fast))
    c.restore()
    s = 1.0 + 0.05 * ease(ramp(t, B("junto")["start"], T_RS))
    def d(x, y): return (540 + (x - 540) * s, 1100 + (y - 1100) * s)
    if fast < 0.3:
        c.push_group()
        callout(c, "REJILLA", *d(150, YS[7]), 190, 1665, t, tw["rejilla"], ORANGE)
        callout(c, "CARGA", *d(XS[1], YS[0]), 230, 648, t, tw["carga"], YEL)
        callout(c, "DEDO", *d(F1[0] + 120, F1[1] + 260), 870, 1300, t, tw["dedo"], CREAM)
        callout(c, "ROBO", *d(F1[0] - 30, F1[1] + 30), 470, 648, t, tw["robo"], HOT)
        callout(c, "CHIP", *d(CHIP[0] + 150, CHIP[1]), 800, 1640, t, tw["chip"], CREAM)
        callout(c, "POSICIÓN", *d(F1[0] + 40, F1[1] - 48), 730, 648, t, tw["posición"], GREEN)
        c.pop_group_to_source(); c.paint_with_alpha(1 - fast / 0.3)
    if fast > 0:  # speed lines
        for i in range(26):
            r0 = 300 + (i * 97 + t * 2600) % 900; a = i * 0.2417
            line(c, [(540 + math.cos(a) * r0, 1100 + math.sin(a) * r0), (540 + math.cos(a) * (r0 + 140 * fast), 1100 + math.sin(a) * (r0 + 140 * fast))],
                 alpha(WHITE, 0.35 * fast), 5)
    flash = ramp(t, T_RS - 0.45, T_RS - 0.3) * (1 - ramp(t, T_RS - 0.3, T_RS - 0.05))
    if flash > 0: c.set_source_rgba(1, 1, 1, 0.85 * flash); c.paint()

# ---------------------------------------------------------------- scene: remate (water drops = ghost touches)
DROPS = [(430, 900), (620, 1250), (380, 1390), (650, 760)]
def scene_remate(c, t):
    background(c, t, COLD)
    T_AG, T_GO, T_LOCA, T_TOCA, T_CUE = wt("remate", "agua"), wt("remate", "gotas"), wt("remate", "loca"), wt("remate", "toca"), wt("remate", "cuenta")
    lands = [T_AG + 0.1, T_GO, T_GO + 0.3, T_GO + 0.55]
    loca = ramp(t, T_LOCA - 0.1, T_LOCA + 0.2) * (1 - ramp(t, T_LOOP - 0.3, T_LOOP + 0.1))
    shake = 5 * loca
    c.save()
    c.translate(shake * math.sin(t * 47), shake * math.cos(t * 41))
    # ghost presses: every ~0.2 s one random icon or drop spot is "touched"
    press = {}; hits = []
    if loca > 0:
        for kk in range(int((T_LOCA - 0.1) / 0.2), int(t / 0.2) + 1):
            t0 = kk * 0.2
            if t0 < T_LOCA - 0.1 or t0 > T_LOOP - 0.3: continue
            rnd = random.Random(kk * 7 + 3)
            if rnd.random() < 0.5:
                i = rnd.randrange(len(ICONS)); press[i] = max(press.get(i, 0), pulse_at(t, t0, 0.35)); p = ICONS[i][:2]
            else:
                p = DROPS[rnd.randrange(4)]
            hits.append((t0, p))
    phone_display(c, t, press)
    for i, ((x, y), tl) in enumerate(zip(DROPS, lands)):
        if t < tl - 0.35: continue
        fall = ramp(t, tl - 0.35, tl)
        if fall < 1:
            yy = lerp(y - 380, y, fall ** 2)
            c.save(); c.translate(x, yy); c.new_path(); c.move_to(0, -40); c.curve_to(22, -6, 26, 26, 0, 30); c.curve_to(-26, 26, -22, -6, 0, -40)
            c.restore(); fill_stroke(c, alpha(XRAY, 0.85), INK, 4)
            continue
        ripple(c, x, y, t, tl, XRAY, 0.6, 20, 110)
        sparks_into(c, t, [(x + 90 * math.cos(a), y + 90 * math.sin(a)) for a in (0.3, 1.9, 3.5, 5.0)], (x, y), 2, 1.4, YEL, 6,
                    ramp(t, tl + 0.1, tl + 0.4) * (1 - ramp(t, T_LOOP - 0.3, T_LOOP + 0.1)))
        c.save(); c.translate(x, y); c.scale(1.25, 1.0); circle(c, 0, 0, 40); c.restore()
        fill_stroke(c, alpha(XRAY, 0.55), alpha(INK, 0.9), 4)
        circle(c, x - 12, y - 14, 10); c.set_source_rgba(1, 1, 1, 0.8); c.fill()
    for t0, (x, y) in hits:
        if t0 <= t < t0 + 0.45:
            ripple(c, x, y, t, t0, CREAM, 0.45, 15, 90)
            crosshair(c, x, y, ramp(t, t0, t0 + 0.12) * (1 - ramp(t, t0 + 0.3, t0 + 0.45)), HOT)
    hand(c, *HOVER[:2], HOVER[2], 1.0)
    c.restore()
    callout(c, "GOTA", DROPS[0][0] - 30, DROPS[0][1] - 20, 230, 700, t, lands[0] + 0.1, XRAY)
    if T_LOCA <= t < T_LOOP - 0.2:
        a = ramp(t, T_LOCA, T_LOCA + 0.2) * (1 - ramp(t, T_LOOP - 0.5, T_LOOP - 0.2))
        text(c, "¡TOCA SOLA!", 540, 1700, 48, alpha(HOT, a), SLAB, False, outline=INK, olw=9)

# ---------------------------------------------------------------- timeline
SCENES = [
    ("front", 0.0, cut("paso1") + 0.05, scene_front),
    ("paso1", cut("paso1") + 0.05, cut("paso2"), scene_paso1),
    ("paso2", cut("paso2"), cut("paso3"), scene_paso2),
    ("paso3", cut("paso3"), cut("paso4"), scene_paso3),
    ("paso4", cut("paso4"), cut("paso5"), scene_paso4),
    ("paso5", cut("paso5"), cut("junto"), scene_paso5),
    ("all", cut("junto"), cut("remate") + 0.1, scene_all),
    ("remate", cut("remate") + 0.1, T_LOOP + 0.15, scene_remate),
]
LOOP_FN = scene_front
XF = {"remate": 0.08}

def POPS():
    p = [wt("imposible", w) - 0.15 for w, *_ in BADGES]
    p += [wt("paso1", w) for w in ("cristal", "filas", "columnas", "debajo")]
    p += [wt("paso2", w) for w in ("fila", "columna", "cruza", "carga", "cientos")]
    p += [wt("paso3", w) for w in ("agua", "conduce", "cruces", "carga")]
    p += [wt("paso4", w) for w in ("chip", "ciento", "ahí", "huecos")]
    p += [wt("paso5", w) for w in ("lana", "hilo")]
    p += [wt("junto", w) for w in JUNTO]
    p += [wt("remate", "agua") + 0.2, wt("imposible", "dónde")]
    return sorted(p)

def SFX(put, L):
    for tt, _, _ in TAPS_FRONT: put(L["click"](), tt, 0.7)
    for w in ("botones", "hunde", "aprietes"): put(L["scratch"](), wt("imposible", w) + 0.25, 0.25)
    put(L["zap"](0.5), wt("gancho", "robas"), 0.12)
    put(L["click"](), wt("paso3", "acercas") + 0.6, 0.7)
    put(L["zap"](0.6), wt("paso3", "llevas"), 0.12)
    put(L["click"](), wt("paso5", "guantes") + 0.3, 0.6)
    put(L["scratch"](), wt("paso5", "conduce"), 0.35)
    put(L["click"](), wt("paso5", "hilo") - 0.1, 0.6)
    put(L["zap"](0.5), wt("paso5", "hilo") + 0.1, 0.12)
    put(L["ding"](), wt("paso5", "metal") + 0.2, 0.25)
    # scan ticks: one quiet tick per row read (slow motion), denser and denser in the acelerón
    t0, t1 = wt("paso4", "revisa") - 0.1, cut("remate") - 0.3
    last = None; t = t0
    while t < t1:
        r = int(scan_pos(t) * NR4)
        if last is not None and r != last:
            fast = ramp(t, T_REAL, t1)
            put(L["click"](), t, (0.10 if r % NR4 else 0.22) * (1 - 0.5 * fast))
        last = r; t += 1 / 60
    lands = [wt("remate", "agua") + 0.1, wt("remate", "gotas"), wt("remate", "gotas") + 0.3, wt("remate", "gotas") + 0.55]
    for tl in lands: put(L["tone"](1250, 0.12, 0.002, 0.04), tl, 0.25); put(L["tone"](700, 0.1, 0.002, 0.03), tl + 0.03, 0.2)
    k = int((wt("remate", "loca") - 0.1) / 0.2)
    while k * 0.2 < T_LOOP - 0.3:
        if k * 0.2 >= wt("remate", "loca") - 0.1: put(L["click"](), k * 0.2, 0.5)
        k += 1

# ---------------------------------------------------------------- thumbnails
def _thumb_scene(c, t=3.6):
    phone_display(c, t, {9: 0.6})
    c.save(); circle(c, 500, 1050, 170); c.clip()
    c.set_source_rgba(0.05, 0.04, 0.1, 0.6); c.paint()
    grid_lines(c, 0.9, 0.9, 4)
    for i in range(NC):
        for j in range(NR):
            d = math.dist((gx(i), gy(j)), (500, 1050))
            if d < 180: node(c, gx(i), gy(j), 9, clamp(0.2 + d / 220), 2, False)
    c.restore()
    circle(c, 500, 1050, 170); fill_stroke(c, None, YEL, 7)
    glow(c, 500, 1040, 200, YEL, 0.7)
    src = [(gx(i), gy(j)) for i in range(NC) for j in range(NR) if 20 < math.dist((gx(i), gy(j)), (500, 1050)) < 140]
    for k, (sx, sy) in enumerate(src):
        for u in (0.35, 0.7):
            x, y = lerp(sx, 500, u), lerp(sy, 1040, u)
            glow(c, x, y, 26, YEL, 0.8); circle(c, x, y, 7 * (1 - 0.4 * u)); c.set_source_rgba(1, 1, 1, 1); c.fill()
    for a in range(8):  # zaps
        an = a * 0.785 + 0.3
        pts = [(500 + math.cos(an) * r + 10 * math.sin(r), 1040 + math.sin(an) * r) for r in range(60, 200, 20)]
        line(c, pts, alpha(YEL, 0.9), 5)
    hand(c, 500, 1040, HOVER[2], 0.0)

def THUMB_V(c):
    background(c, 3.0, YEL)
    c.save(); c.translate(0, 170); _thumb_scene(c); c.restore()
    for i, (ln, col) in enumerate([("LE ROBAS", WHITE), ("ELECTRICIDAD", YEL)]):
        sz = fit_size(c, ln, SLAB, 190, 980)
        text(c, ln, 540, 330 + i * 210, sz, col, SLAB, False, outline=INK, olw=24)

def THUMB_H(c):
    g = cairo.LinearGradient(0, 0, 0, 720); g.add_color_stop_rgba(0, *BG_TOP); g.add_color_stop_rgba(1, *BG_BOT); c.set_source(g); c.paint()
    glow(c, 1000, 380, 420, YEL, 0.35)
    c.save(); c.translate(1000, 380); c.scale(0.6, 0.6); c.translate(-500, -1050); _thumb_scene(c); c.restore()
    for i, (ln, col) in enumerate([("LE ROBAS", WHITE), ("ELECTRICIDAD", YEL)]):
        sz = fit_size(c, ln, SLAB, 130, 700)
        text(c, ln, 390, 300 + i * 170, sz, col, SLAB, False, outline=INK, olw=20)
