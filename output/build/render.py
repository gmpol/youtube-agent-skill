"""Frame renderer for the microwave short. Everything is drawn with pycairo (no third-party footage).
Timing comes from beats_timed.json + words.json (whisper on the real narration).

  python3 render.py --still 12.5 out.png     # one frame
  python3 render.py --video out.mp4 [--jobs 4]
"""
import argparse, json, math, os, random, re, subprocess, sys, unicodedata
import cairo

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
BEATS = {b["id"]: b for b in json.load(open(os.path.join(HERE, "beats_timed.json")))}
WORDS = json.load(open(os.path.join(HERE, "words.json")))

# ---------------------------------------------------------------- palette (guia_de_estilo.md §5)
def hx(s, a=1.0):
    s = s.lstrip("#"); return (int(s[0:2], 16) / 255, int(s[2:4], 16) / 255, int(s[4:6], 16) / 255, a)
BG_TOP, BG_BOT = hx("#282336"), hx("#17161D")
INK = hx("#1B1925"); CREAM = hx("#FFEEE0"); CREAM2 = hx("#F3EAD1"); RED = hx("#BC3A38"); GOLD = hx("#A6613A")
ORANGE = hx("#E27E56"); ORANGE2 = hx("#CC7B3E"); RUST = hx("#BF5B45"); YEL = hx("#F2C94C"); STEEL = hx("#526DA9")
LAV = hx("#A1ABC9"); WHITE = hx("#FFFFFF"); COLD = hx("#5B8DEF"); HOT = hx("#FF5A3C"); XRAY = hx("#9FD3FF")
SLAB = "Alfa Slab One"; SANS = "Inter"


# ---------------------------------------------------------------- timing helpers
def _bare(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))

def wt(beat, sub, nth=0, end=False):
    """Start (or end) time of the nth word in `beat` whose text contains `sub`."""
    hits = [w for w in WORDS if w["beat"] == beat and _bare(sub) in _bare(w["word"])]
    w = hits[min(nth, len(hits) - 1)]
    return w["end"] if end else w["start"]

B = lambda k: BEATS[k]
T_LENTO = wt("freno", "lento", end=True)
T_REAL = wt("acelera", "real", end=True)
T_LOOP = wt("remate", "porque")
DUR = round(B("remate")["end"] + 0.45, 2)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ramp(t, t0, t1): return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t0)
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eob(x):  # ease-out-back (pop)
    x = clamp(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, k): return a + (b - a) * k
def mix(c1, c2, k): return tuple(lerp(a, b, k) for a, b in zip(c1, c2))
def alpha(c, a): return (c[0], c[1], c[2], c[3] * a)


# ---------------------------------------------------------------- drawing primitives
def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()

def fill_stroke(c, fill, stroke=INK, lw=6):
    if fill: c.set_source_rgba(*fill); c.fill_preserve() if stroke else c.fill()
    if stroke: c.set_source_rgba(*stroke); c.set_line_width(lw); c.stroke()
    else: c.new_path()

def shadow(c, path_fn, dx=10, dy=14, a=0.35):
    c.save(); c.translate(dx, dy); path_fn(); c.set_source_rgba(0, 0, 0, a); c.fill(); c.restore()

def font(c, fam, size, bold=False):
    c.select_font_face(fam, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)

def text(c, s, x, y, size, color=WHITE, fam=SANS, bold=True, align="c", outline=None, olw=8):
    font(c, fam, size, bold); e = c.text_extents(s)
    dx = {"c": -e.x_advance / 2, "l": 0, "r": -e.x_advance}[align]
    c.move_to(x + dx, y)
    if outline:
        c.text_path(s); c.set_source_rgba(*outline); c.set_line_width(olw); c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.stroke_preserve(); c.set_source_rgba(*color); c.fill()
    else:
        c.set_source_rgba(*color); c.show_text(s)
    return e.x_advance

def fit_size(c, s, fam, size, maxw, bold=False):
    font(c, fam, size, bold)
    w = c.text_extents(s).x_advance
    return size * min(1.0, maxw / w) if w else size

def line(c, pts, color, lw, cap=cairo.LINE_CAP_ROUND):
    c.move_to(*pts[0])
    for p in pts[1:]: c.line_to(*p)
    c.set_source_rgba(*color); c.set_line_width(lw); c.set_line_cap(cap); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()

def glow(c, x, y, r, color, a=0.6):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, color[0], color[1], color[2], a); g.add_color_stop_rgba(1, color[0], color[1], color[2], 0)
    c.set_source(g); c.arc(x, y, r, 0, 2 * math.pi); c.fill()

def callout(c, label, ax, ay, lx, ly, t, t0, color=CREAM, size=34):
    """Label with a leader line, popping in at t0 (like ref1/ref2 'MOTOR', 'SHAFT')."""
    k = ramp(t, t0, t0 + 0.35)
    if k <= 0: return
    p = eob(k)
    # leader line draws itself
    mx, my = lerp(ax, lx, ease(k)), lerp(ay, ly, ease(k))
    line(c, [(ax, ay), (mx, my)], alpha(WHITE, 0.9), 4)
    c.set_source_rgba(*WHITE); c.arc(ax, ay, 9 * p, 0, 2 * math.pi); c.fill()
    font(c, SANS, size, True); e = c.text_extents(label)
    bw, bh = e.x_advance + 30, size + 22
    c.save(); c.translate(lx, ly); c.scale(p, p)
    rrect(c, -bw / 2, -bh / 2, bw, bh, 10); fill_stroke(c, INK if color != INK else CREAM, alpha(WHITE, 0.95), 3)
    text(c, label, 0, size * 0.36, size, color if color != INK else INK, SANS, True)
    c.restore()

def xmark(c, x, y, s, t, t0, lw=16):
    k = ramp(t, t0, t0 + 0.25)
    if k <= 0: return
    line(c, [(x - s, y - s), (lerp(x - s, x + s, ease(k)), lerp(y - s, y + s, ease(k)))], RED, lw)
    k2 = ramp(t, t0 + 0.12, t0 + 0.37)
    if k2 > 0: line(c, [(x + s, y - s), (lerp(x + s, x - s, ease(k2)), lerp(y - s, y + s, ease(k2)))], RED, lw)


# ---------------------------------------------------------------- background & HUD
STARS = [(random.Random(i).uniform(0, W), random.Random(i + 99).uniform(560, 1700), random.Random(i + 7).uniform(1.5, 3.5))
         for i in range(60)]

def background(c, t, tint=None):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, *BG_TOP); g.add_color_stop_rgba(1, *BG_BOT)
    c.set_source(g); c.paint()
    if tint: glow(c, W / 2, 1100, 900, tint, 0.18)
    for i, (x, y, r) in enumerate(STARS):  # faint dust, slowly drifting (the camera is never still)
        a = 0.10 + 0.08 * math.sin(t * 1.3 + i)
        c.set_source_rgba(1, 1, 1, a); c.arc((x + t * 6) % W, y, r, 0, 2 * math.pi); c.fill()
    v = cairo.RadialGradient(W / 2, H / 2, 500, W / 2, H / 2, 1250)
    v.add_color_stop_rgba(0, 0, 0, 0, 0); v.add_color_stop_rgba(1, 0, 0, 0, 0.55)
    c.set_source(v); c.paint()


def slow_log(t):
    """log10 of the slow-motion factor shown in the HUD (0 = real speed, 9 = 1.000.000.000x slower)."""
    if t < wt("freno", "vamos"): return 0.0
    if t < T_LENTO + 0.3: return 9 * ease(ramp(t, wt("freno", "vamos"), T_LENTO + 0.3))
    if t < T_REAL + 0.2: return 9.0
    if t < B("remate")["start"] - 0.4: return 9 * (1 - ease(ramp(t, T_REAL + 0.2, B("remate")["start"] - 0.4)) ** 0.7)
    return 0.0

def dots(n): return f"{int(round(n)):,}".replace(",", ".")

def hud(c, t):
    L = slow_log(t)
    y0 = 96
    # speed label box (ref2: "64x SLOWER")
    step = int(round(L / 3) * 3) if L > 0.05 else 0
    lab = "VELOCIDAD REAL" if step == 0 else f"{dots(10 ** step)}x MÁS LENTO"
    sz = fit_size(c, lab, SLAB, 34, 400)
    shadow(c, lambda: rrect(c, 40, y0, 430, 78, 12), 6, 8, 0.4)
    rrect(c, 40, y0, 430, 78, 12); fill_stroke(c, CREAM, INK, 5)
    text(c, lab, 255, y0 + 39 + sz * 0.36, sz, RED if step else INK, SLAB, False)
    # gauge
    gx, gy, gr = 560, y0 + 72, 62
    rrect(c, gx - 80, y0 - 6, 160, 90, 14); fill_stroke(c, CREAM, INK, 5)
    for i in range(30):
        a0 = math.pi + math.pi * i / 30; a1 = math.pi + math.pi * (i + 0.8) / 30
        col = mix(hx("#4CAF50"), YEL, i / 15) if i < 15 else mix(YEL, HOT, (i - 15) / 15)
        c.arc(gx, gy, gr, a0, a1); c.set_source_rgba(*col); c.set_line_width(14); c.stroke()
    ang = math.pi + math.pi * (0.06 + 0.88 * (1 - L / 9)) + 0.03 * math.sin(t * 40) * (L < 0.5)
    line(c, [(gx, gy), (gx + math.cos(ang) * (gr - 6), gy + math.sin(ang) * (gr - 6))], INK, 6)
    c.set_source_rgba(*INK); c.arc(gx, gy, 9, 0, 2 * math.pi); c.fill()
    # counter (ref2: "STROKES A MINUTE 7680")
    v = 2.45e9 / 10 ** L
    val = dots(v) if v >= 1000 else (f"{v:.2f}".replace(".", ",") if v < 100 else f"{v:.0f}")
    shadow(c, lambda: rrect(c, 660, y0, 380, 78, 12), 6, 8, 0.4)
    rrect(c, 660, y0, 380, 78, 12); fill_stroke(c, CREAM, INK, 5)
    text(c, "SACUDIDAS", 676, y0 + 32, 20, INK, SANS, True, "l"); text(c, "POR SEG.", 676, y0 + 58, 20, INK, SANS, True, "l")
    rrect(c, 800, y0 + 12, 226, 54, 8); fill_stroke(c, hx("#1E3A2A"), INK, 3)
    vs = fit_size(c, val, "JetBrains Mono", 34, 206, True)
    text(c, val, 1016, y0 + 39 + vs * 0.36, vs, hx("#7CFC9A"), "JetBrains Mono", True, "r")


CARDS = {  # beat -> (number, title, subtitle)
    "gancho": (None, ["¿CÓMO CALIENTA", "UN MICROONDAS?"], "2.450.000.000 VECES POR SEGUNDO"),
    "paso1": (1, ["¿DE DÓNDE SALE?"], "UN MAGNETRÓN"),
    "paso2": (2, ["¿A DÓNDE VA?"], "REBOTA EN EL METAL"),
    "paso3": (3, ["¿QUÉ LE HACE AL AGUA?"], "LA HACE GIRAR"),
    "paso4": (4, ["¿POR QUÉ GIRA EL PLATO?"], "PUNTOS CALIENTES Y FRÍOS"),
    "paso5": (5, ["¿POR QUÉ NO TE COCINA?"], "LA REJILLA DE LA PUERTA"),
    "junto": (None, ["TODO JUNTO"], "DEL ENCHUFE AL CALOR"),
    "acelera": (None, ["A VELOCIDAD REAL"], "2.450.000.000 POR SEGUNDO"),
    "remate": (None, ["Y OJO:"], "SOLO ENTRA UNOS CENTÍMETROS"),
}

def card_windows():
    wins = []
    for k in CARDS:
        b = B(k)
        t0 = 0.0 if k == "gancho" else b["start"] - 0.15
        t1 = {"gancho": B("freno")["start"] - 0.1, "acelera": B("remate")["start"] - 0.35,
              "remate": T_LOOP - 0.1}.get(k, b["end"] + b["pause"] - 0.05)
        wins.append((k, t0, t1))
    wins.append(("gancho", T_LOOP + 0.05, DUR + 1))  # the loop: same card as frame 0
    return wins
CARD_WINS = card_windows()

def draw_card(c, key, k_in, k_out):
    num, title, sub = CARDS[key]
    s = eob(k_in) * (1 - ease(k_out))
    if s <= 0.01: return
    cx, top = W / 2, 232
    tsz = min(fit_size(c, ln, SLAB, 62, 740 if num else 820) for ln in title)
    ssz = fit_size(c, sub, SLAB, 32, 760)
    h = 36 + len(title) * tsz * 1.08 + ssz + 22
    w = 900
    c.save(); c.translate(cx, top + h / 2); c.scale(s, s); c.translate(-cx, -(top + h / 2))
    shadow(c, lambda: rrect(c, cx - w / 2, top, w, h, 14), 10, 14, 0.45)
    rrect(c, cx - w / 2 - 10, top - 10, w + 20, h + 20, 18); fill_stroke(c, GOLD, INK, 6)
    rrect(c, cx - w / 2, top, w, h, 12); fill_stroke(c, CREAM, INK, 4)
    for side in (-1, 1):  # barber-pole ends (ref1)
        px = cx + side * (w / 2 - 22)
        c.save(); rrect(c, px - 14, top + 10, 28, h - 20, 8); c.clip()
        c.set_source_rgba(*WHITE); c.paint()
        for j in range(-4, int(h / 22) + 4):
            c.move_to(px - 20, top + j * 22); c.line_to(px + 20, top + j * 22 + 20); c.line_to(px + 20, top + j * 22 + 31); c.line_to(px - 20, top + j * 22 + 11)
            c.close_path(); c.set_source_rgba(*(RED if j % 2 else STEEL)); c.fill()
        c.restore(); rrect(c, px - 14, top + 10, 28, h - 20, 8); fill_stroke(c, None, INK, 3)
    y = top + 24 + tsz * 0.82
    for ln in title:
        text(c, ln, cx, y, tsz, INK, SLAB, False); y += tsz * 1.08
    text(c, sub, cx, y + ssz * 0.15, ssz, RED, SLAB, False)
    if num:
        bx, by = cx - w / 2 + 8, top + 6
        c.new_path(); c.set_source_rgba(*RED); c.arc(bx, by, 36, 0, 2 * math.pi); c.fill_preserve()
        c.set_source_rgba(*INK); c.set_line_width(5); c.stroke()
        text(c, str(num), bx, by + 15, 42, WHITE, SLAB, False)
    c.restore()

def cards(c, t):
    for key, t0, t1 in CARD_WINS:
        if t0 - 0.01 <= t <= t1 + 0.3:
            k_in = 1.0 if t0 <= 0.0 or key == "gancho" and t0 > 1 and False else ramp(t, t0, t0 + 0.4)
            if key == "gancho" and t0 == 0.0: k_in = 1.0
            draw_card(c, key, k_in, ramp(t, t1, t1 + 0.25))


# ---------------------------------------------------------------- illustration pieces
def soup_bowl(c, x, y, s, t, heat=0.0, bubbles=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    # bowl
    c.move_to(-120, -20); c.curve_to(-115, 90, 115, 90, 120, -20); c.close_path()
    fill_stroke(c, CREAM2, INK, 6)
    c.save(); c.scale(1, 0.28); c.arc(0, -70, 120, 0, 2 * math.pi); c.restore()
    fill_stroke(c, mix(ORANGE2, HOT, heat * 0.6), INK, 6)
    for i in range(int(6 * bubbles)):
        bx = -80 + (i * 37) % 160; by = -22 + 6 * math.sin(t * 9 + i)
        r = 6 + 4 * abs(math.sin(t * 7 + i * 1.7))
        c.set_source_rgba(1, 0.85, 0.6, 0.85); c.arc(bx, by, r, 0, 2 * math.pi); c.fill()
    c.restore()

def steam(c, x, y, s, t, amount):
    if amount <= 0: return
    for i in range(3):
        ph = (t * 0.6 + i / 3) % 1
        a = amount * math.sin(ph * math.pi) * 0.8
        pts = [(x + (i - 1) * 50 * s + 18 * s * math.sin(ph * 8 + j * 0.9 + i), y - ph * 160 * s - j * 26 * s) for j in range(7)]
        line(c, pts, (1, 1, 1, a), 10 * s)

def microwave_front(c, t, running=1.0, heat=0.0, bubbles=0.0, xray=0.0):
    """Front view, body centred at (540, 1080). xray>0 fades to the see-through version."""
    X, Y, BW, BH = 110, 820, 860, 520
    # counter + wall tiles
    c.set_source_rgba(*hx("#3B364B")); c.rectangle(0, Y + BH + 30, W, 30); c.fill()
    c.set_source_rgba(*hx("#55404D")); c.rectangle(0, Y + BH + 60, W, 400); c.fill()
    for i in range(8):
        c.set_source_rgba(1, 1, 1, 0.04); c.rectangle(0, Y + BH + 90 + i * 46, W, 4); c.fill()
    if xray < 1:
        c.push_group()
        shadow(c, lambda: rrect(c, X, Y, BW, BH, 40), 18, 24, 0.45)
        rrect(c, X, Y, BW, BH, 40); fill_stroke(c, RUST, INK, 8)
        rrect(c, X + 18, Y + 18, BW - 36, 26, 13); c.set_source_rgba(1, 1, 1, 0.12); c.fill()
        # window
        wx, wy, ww, wh = X + 50, Y + 60, 540, BH - 120
        rrect(c, wx, wy, ww, wh, 26); fill_stroke(c, hx("#1E1B2E"), INK, 7)
        c.save(); rrect(c, wx, wy, ww, wh, 26); c.clip()
        glow(c, wx + ww / 2, wy + wh / 2, 360, YEL, 0.55 * running)
        c.set_source_rgba(*alpha(YEL, 0.10 * running)); c.paint()
        # plate + bowl (bowl turns: its highlight slides)
        c.save(); c.translate(wx + ww / 2, wy + wh - 70); c.scale(1, 0.22); c.arc(0, 0, 210, 0, 2 * math.pi); c.restore()
        fill_stroke(c, alpha(LAV, 0.6), INK, 4)
        soup_bowl(c, wx + ww / 2, wy + wh - 140, 1.0, t, heat, bubbles)
        for i in range(0, ww, 22):  # door mesh dots
            for j in range(0, wh, 22):
                c.set_source_rgba(0, 0, 0, 0.22); c.arc(wx + i + 11, wy + j + 11, 4, 0, 2 * math.pi); c.fill()
        c.move_to(wx + 30, wy + 20); c.line_to(wx + 130, wy + 20); c.line_to(wx + 40, wy + 200); c.close_path()
        c.set_source_rgba(1, 1, 1, 0.08); c.fill()
        c.restore()
        # control panel
        px = X + 620
        rrect(c, px, wy, 200, wh, 18); fill_stroke(c, hx("#2C293C"), INK, 6)
        rrect(c, px + 22, wy + 24, 156, 70, 10); fill_stroke(c, hx("#10100F"), INK, 4)
        secs = max(0, 30 - int(t)) if running else 30
        text(c, f"0:{secs:02d}", px + 100, wy + 74, 44, alpha(ORANGE, 0.5 + 0.5 * running), "JetBrains Mono", True)
        for i, (kx, ky) in enumerate([(px + 100, wy + 170), (px + 100, wy + 290)]):
            c.set_source_rgba(*CREAM2); c.arc(kx, ky, 46, 0, 2 * math.pi); c.fill_preserve(); c.set_source_rgba(*INK); c.set_line_width(5); c.stroke()
            a = t * (0.8 if i == 0 else 0) * running + i
            line(c, [(kx, ky), (kx + 34 * math.cos(a), ky + 34 * math.sin(a))], INK, 7)
        rrect(c, px + 40, wy + 360, 120, 18, 9); fill_stroke(c, INK, None)
        for fx in (X + 80, X + BW - 120):
            rrect(c, fx, Y + BH - 4, 40, 26, 6); fill_stroke(c, INK, None)
        c.pop_group_to_source(); c.paint_with_alpha(1 - xray)
    if xray > 0:
        c.push_group(); microwave_xray(c, t, heat=heat); c.pop_group_to_source(); c.paint_with_alpha(xray)

MW = dict(X=110, Y=820, BW=860, BH=520)
def mw_parts():
    X, Y, BW, BH = MW["X"], MW["Y"], MW["BW"], MW["BH"]
    return dict(cav=(X + 50, Y + 60, 540, BH - 120), panel=(X + 620, Y + 60, 200, BH - 120),
                mag=(X + 720, Y + 150), trafo=(X + 720, Y + 330), plug=(X + BW - 90, Y + BH + 120),
                guide=[(X + 680, Y + 150), (X + 600, Y + 150), (X + 600, Y + 110), (X + 560, Y + 110)])

def microwave_xray(c, t, heat=0.0, hl=None, wave=0.0, spark=None, steam_amt=0.0, fast=0.0):
    """See-through microwave: blueprint lines over the dark background. hl = set of highlighted parts."""
    hl = hl or set()
    X, Y, BW, BH = MW["X"], MW["Y"], MW["BW"], MW["BH"]; P = mw_parts()
    def pcol(name): return YEL if name in hl else XRAY
    rrect(c, X, Y, BW, BH, 40); c.set_source_rgba(*alpha(STEEL, 0.18)); c.fill_preserve()
    c.set_source_rgba(*alpha(XRAY, 0.9)); c.set_line_width(5); c.stroke()
    cx, cy, cw, ch = P["cav"]
    rrect(c, cx, cy, cw, ch, 20); c.set_source_rgba(*alpha(XRAY, 0.10)); c.fill_preserve()
    c.set_source_rgba(*alpha(pcol("cav"), 0.9)); c.set_line_width(4); c.stroke()
    # bowl
    c.save(); c.translate(cx + cw / 2, cy + ch - 70); c.scale(1, 0.22); c.arc(0, 0, 210, 0, 2 * math.pi); c.restore()
    c.set_source_rgba(*alpha(XRAY, 0.5)); c.set_line_width(3); c.stroke()
    soup_bowl(c, cx + cw / 2, cy + ch - 140, 1.0, t, heat, heat)
    steam(c, cx + cw / 2, cy + ch - 200, 1.0, t, steam_amt)
    # magnetron (cylinder with cooling fins)
    mx, my = P["mag"]
    c.set_source_rgba(*alpha(pcol("mag"), 0.25)); rrect(c, mx - 60, my - 70, 120, 140, 16); c.fill_preserve()
    c.set_source_rgba(*pcol("mag")); c.set_line_width(5); c.stroke()
    for i in range(6):
        line(c, [(mx - 75, my - 55 + i * 22), (mx + 75, my - 55 + i * 22)], alpha(pcol("mag"), 0.8), 4)
    c.set_source_rgba(*pcol("mag")); c.arc(mx, my, 22, 0, 2 * math.pi); c.fill()
    # transformer
    tx, ty = P["trafo"]
    rrect(c, tx - 70, ty - 55, 140, 110, 10); c.set_source_rgba(*alpha(pcol("trafo"), 0.22)); c.fill_preserve()
    c.set_source_rgba(*pcol("trafo")); c.set_line_width(5); c.stroke()
    for i in range(7):
        line(c, [(tx - 50 + i * 16, ty - 40), (tx - 50 + i * 16, ty + 40)], alpha(ORANGE, 0.9), 6)
    # wires + plug
    plx, ply = P["plug"]
    wire = [(plx + 20, ply - 30), (plx + 20, Y + BH - 30), (tx + 70, Y + BH - 30), (tx + 70, ty), (tx, ty - 55), (mx, my + 70)]
    line(c, wire, alpha(pcol("plug"), 0.8), 5)
    rrect(c, plx - 10, ply - 30, 60, 60, 10); c.set_source_rgba(*alpha(pcol("plug"), 0.3)); c.fill_preserve()
    c.set_source_rgba(*pcol("plug")); c.set_line_width(5); c.stroke()
    line(c, [(plx + 6, ply + 30), (plx + 6, ply + 60)], pcol("plug"), 7); line(c, [(plx + 34, ply + 30), (plx + 34, ply + 60)], pcol("plug"), 7)
    if spark is not None and 0 < spark < 1:  # electricity travelling plug -> magnetron
        segs = [(wire[i], wire[i + 1]) for i in range(len(wire) - 1)]
        L = [math.dist(a, b) for a, b in segs]; d = spark * sum(L)
        for (a, b), l in zip(segs, L):
            if d <= l:
                px, py = a[0] + (b[0] - a[0]) * d / l, a[1] + (b[1] - a[1]) * d / l
                glow(c, px, py, 70, YEL, 0.9); c.set_source_rgba(1, 1, 1, 1); c.arc(px, py, 12, 0, 2 * math.pi); c.fill(); break
            d -= l
    # waveguide
    line(c, P["guide"], alpha(pcol("guide"), 0.9), 26, cairo.LINE_CAP_BUTT)
    line(c, P["guide"], hx("#17161D"), 14, cairo.LINE_CAP_BUTT)
    if wave > 0:  # microwaves entering the cavity
        c.save(); rrect(c, cx, cy, cw, ch, 20); c.clip()
        speed = 1 + fast * 30
        for k in range(3):
            pts = []
            for i in range(0, 120):
                u = i / 119
                x = cx + cw - 40 - u * (cw - 80); y = cy + 60 + u * (ch - 160) * (0.3 + 0.35 * k)
                amp = 26 * wave * (1 - 0.3 * k)
                yy = y + amp * math.sin(u * 22 - t * 5 * speed + k)
                pts.append((x, yy))
            line(c, pts, alpha(YEL, 0.75 * wave * (1 - 0.25 * k)), 6)
        c.restore()
    rrect(c, X + 18, Y + 18, BW - 36, 26, 13); c.set_source_rgba(1, 1, 1, 0.06); c.fill()


def water_molecule(c, x, y, ang, s=1.0, heat=0.0, labels=False):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    for sgn in (-1, 1):  # two H at ±52° from the dipole axis
        hx_, hy_ = 58 * math.cos(math.radians(52) * sgn), 58 * math.sin(math.radians(52) * sgn)
        line(c, [(0, 0), (hx_, hy_)], INK, 10)
        c.new_path(); c.arc(hx_, hy_, 22, 0, 2 * math.pi); fill_stroke(c, mix(WHITE, hx("#FFD0B0"), heat), INK, 5)
        if labels: text(c, "+", hx_, hy_ + 11, 32, INK, SANS, True)
    c.new_path(); c.arc(0, 0, 36, 0, 2 * math.pi); fill_stroke(c, mix(RUST, HOT, heat), INK, 6)
    if labels: text(c, "−", 0, 12, 40, WHITE, SANS, True)
    c.restore()


# ---------------------------------------------------------------- scenes
def cam(c, s, cx=W / 2, cy=1100):
    c.translate(cx, cy); c.scale(s, s); c.translate(-cx, -cy)

def scene_front(c, t, frozen=None):
    tt = 0.0 if frozen is not None else t
    background(c, tt, YEL)
    b = B("imposible")
    push = 1.0 + 0.04 * ease(ramp(tt, 0, b["start"]))
    t_hierve = wt("imposible", "hierve")
    t_zoom0 = wt("freno", "vamos")
    z = ease(ramp(tt, t_zoom0, T_LENTO + 0.2))
    up = ease(ramp(tt, wt("imposible", "llama") - 0.3, wt("imposible", "llama")))
    up *= 1 - z
    c.save()
    cam(c, push * (1 + 0.18 * z), W / 2, 1080)
    c.translate(0, -170 * up)
    heat = ease(ramp(tt, wt("imposible", "minuto"), t_hierve + 0.6))
    microwave_front(c, tt, 1.0, heat, heat, xray=ease(ramp(tt, T_LENTO - 0.5, T_LENTO + 0.3)))
    steam(c, 380, 1050 - 170 * up, 1.0, tt, heat)
    c.restore()
    # "no tiene llama / resistencia / nada se pone rojo" icons (ref3: crossed-out icons)
    if frozen is None and up > 0.01:
        ia = up
        icons = [("llama", 250), ("resistencia", 540), ("rojo", 830)]
        for name, x in icons:
            t0 = wt("imposible", name) - 0.15
            k = eob(ramp(tt, t0, t0 + 0.3)) * ia
            if k <= 0: continue
            y = 1500
            c.save(); c.translate(x, y); c.scale(k, k)
            c.arc(0, 0, 105, 0, 2 * math.pi); fill_stroke(c, CREAM, INK, 6)
            if name == "llama":
                c.move_to(0, -70); c.curve_to(55, -10, 55, 55, 0, 62); c.curve_to(-55, 55, -55, -10, 0, -70)
                fill_stroke(c, ORANGE, INK, 5)
                c.move_to(0, -10); c.curve_to(25, 20, 25, 50, 0, 55); c.curve_to(-25, 50, -25, 20, 0, -10); fill_stroke(c, YEL, None)
            elif name == "resistencia":
                pts = [(-70 + i * 14, (-28 if i % 2 else 28)) for i in range(11)]
                line(c, pts, HOT, 12)
            else:
                for i, (bx, by) in enumerate([(-30, 20), (25, 25), (0, -20)]):
                    c.arc(bx, by, 32, 0, 2 * math.pi); fill_stroke(c, mix(RUST, HOT, 0.6), INK, 5)
            c.restore()
            if k > 0.3: xmark(c, x, y, 70 * k, tt, t0 + 0.35)
            if k > 0.3: text(c, {"llama": "LLAMA", "resistencia": "RESISTENCIA", "rojo": "BRASAS"}[name], x, y + 150, 30, alpha(CREAM, clamp(k)), SANS, True)

def scene_xray_steps(c, t):
    """Paso 1: magnetrón, voltios, microondas, wifi."""
    background(c, t)
    b = B("paso1")
    c.save(); cam(c, 1.0 + 0.04 * ease(ramp(t, b["start"], b["end"])), W / 2, 1080)
    t_mag = wt("paso1", "magnetrón"); t_volt = wt("paso1", "voltios"); t_mw = wt("paso1", "escupe")
    hl = set()
    if t >= wt("paso1", "pared") - 0.1: hl.add("panel")
    if t >= t_mag: hl.add("mag")
    if t_volt - 0.6 <= t < t_mw: hl |= {"trafo", "plug"}
    spark = ramp(t, t_volt - 0.6, t_mw) if t < t_mw + 0.05 else None
    wave = ease(ramp(t, t_mw, t_mw + 0.6)) * (1 + 0.6 * ease(ramp(t, wt("paso1", "fuertes") - 0.3, wt("paso1", "fuertes"))))
    microwave_xray(c, t, heat=0.0, hl=hl, wave=wave, spark=spark)
    if "panel" in hl:  # pulse on the panel wall ("detrás de esa pared")
        px, py, pw, ph = mw_parts()["panel"]
        a = 0.5 * (1 - ramp(t, wt("paso1", "pared"), wt("paso1", "pared") + 1.0))
        rrect(c, px, py, pw, ph, 18); c.set_source_rgba(*alpha(YEL, a)); c.set_line_width(10); c.stroke()
    c.restore()
    P = mw_parts()
    def sc(p): return (W / 2 + (p[0] - W / 2) * 1.02, 1080 + (p[1] - 1080) * 1.02)
    mx, my = sc(P["mag"]); tx, ty = sc(P["trafo"])
    callout(c, "MAGNETRÓN", mx, my, 800, 690, t, t_mag)
    callout(c, "MILES DE VOLTIOS", tx, ty, 760, 1560, t, t_volt - 0.2)
    callout(c, "MICROONDAS", 420, 960, 300, 690, t, t_mw + 0.2, YEL)
    t_wifi = wt("paso1", "wifi") - 0.2
    k = eob(ramp(t, t_wifi, t_wifi + 0.35))
    if k > 0:  # same band as wifi
        x0, y0 = 290, 1560
        c.save(); c.translate(x0, y0); c.scale(k, k)
        rrect(c, -190, -80, 380, 160, 20); fill_stroke(c, CREAM, INK, 6)
        for r in (30, 55, 80):
            c.arc(-120, 30, r, -math.pi * 0.75, -math.pi * 0.25); c.set_source_rgba(*STEEL); c.set_line_width(10); c.stroke()
        c.set_source_rgba(*STEEL); c.arc(-120, 30, 10, 0, 2 * math.pi); c.fill()
        text(c, "WIFI", 60, -8, 44, INK, SLAB, False); text(c, "2,4 GHz", 60, 46, 38, RED, SLAB, False)
        c.restore()

def bounce_path(x0, y0, w, h, ang, n):
    pts = [(x0 + w * 0.85, y0 + 30)]; x, y = pts[0]; dx, dy = -math.cos(ang), math.sin(ang)
    for _ in range(n):
        tx = ((x0 - x) / dx if dx < 0 else (x0 + w - x) / dx); ty = ((y0 - y) / dy if dy < 0 else (y0 + h - y) / dy)
        s = min(tx, ty); x, y = x + dx * s, y + dy * s; pts.append((x, y))
        if s == tx: dx = -dx
        else: dy = -dy
    return pts

def draw_partial(c, pts, frac, color, lw, wiggle=0.0, t=0.0, fade=True):
    L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(L); d = frac * tot; acc = 0
    for i, l in enumerate(L):
        if acc > d: break
        a, b = pts[i], pts[i + 1]; seg = min(l, d - acc); n = max(2, int(seg / 6))
        nx, ny = -(b[1] - a[1]) / l, (b[0] - a[0]) / l
        q = []
        for j in range(n + 1):
            u = seg * j / n; s_ = (acc + u)
            w_ = wiggle * math.sin(s_ / 22 - t * 6)
            q.append((a[0] + (b[0] - a[0]) * u / l + nx * w_, a[1] + (b[1] - a[1]) * u / l + ny * w_))
        al = 0.25 + 0.75 * (i + 1) / len(L) if fade else 1
        line(c, q, alpha(color, al), lw); acc += l
    return

def scene_cavity(c, t):
    background(c, t, YEL)
    b = B("paso2")
    c.save(); cam(c, 1.0 + 0.05 * ramp(t, b["start"], b["end"]))
    x0, y0, w, h = 120, 640, 840, 940
    shadow(c, lambda: rrect(c, x0 - 30, y0 - 30, w + 60, h + 60, 30), 14, 18, 0.45)
    rrect(c, x0 - 30, y0 - 30, w + 60, h + 60, 30); fill_stroke(c, hx("#8A93A6"), INK, 8)
    for i in range(0, 12):
        line(c, [(x0 - 20 + i * 76, y0 - 22), (x0 - 50 + i * 76, y0 + h + 22)], (1, 1, 1, 0.12), 6)
    rrect(c, x0, y0, w, h, 18); fill_stroke(c, hx("#211E30"), INK, 6)
    glow(c, x0 + w / 2, y0 + h / 2, 600, YEL, 0.18)
    c.save(); c.translate(x0 + w / 2, y0 + h - 120); c.scale(1, 0.25); c.arc(0, 0, 300, 0, 2 * math.pi); c.restore()
    fill_stroke(c, alpha(LAV, 0.5), INK, 4)
    soup_bowl(c, x0 + w / 2, y0 + h - 220, 1.5, t, 0.2, 0)
    c.save(); rrect(c, x0, y0, w, h, 18); c.clip()
    t_reb = wt("paso2", "rebotan") - 0.3
    for k, ang in enumerate((0.95, 0.62, 1.22)):
        start = t_reb + k * 0.9 if k else t_reb
        if k and t < wt("paso2", "una"): continue
        frac = ramp(t, start, start + 3.2)
        if frac > 0:
            pts = bounce_path(x0, y0, w, h, ang + k * 0.13, 9)
            draw_partial(c, pts, frac, YEL, 8, 14, t)
    c.restore()
    c.restore()
    callout(c, "PAREDES DE METAL", x0 - 10, y0 + 300, 360, 600, t, wt("paso2", "metal") - 0.2)
    callout(c, "REBOTAN", 820, 1100, 820, 1650, t, t_reb + 0.3, YEL)

MOLS = [(random.Random(i * 3).uniform(220, 860), random.Random(i * 3 + 1).uniform(720, 1520), random.Random(i * 3 + 2).uniform(0, 6.28))
        for i in range(40)]
MOLS = [(540, 1120, 0.4)] + [m for i, m in enumerate(MOLS) if math.dist(m[:2], (540, 1120)) > 230 and all(math.dist(m[:2], n[:2]) > 150 for n in MOLS[:i])][:11]

def scene_molecules(c, t):
    b = B("paso3")
    heat = ease(ramp(t, wt("paso3", "roza"), wt("paso3", "calor", end=True) + 0.5))
    background(c, t, mix(STEEL, HOT, heat))
    c.save(); cam(c, 1.0 + 0.06 * ramp(t, b["start"], b["end"]))
    # magnifier into the soup
    R = 420; cx, cy = 540, 1120
    shadow(c, lambda: c.arc(cx, cy, R + 24, 0, 2 * math.pi), 14, 18, 0.45)
    c.arc(cx, cy, R + 24, 0, 2 * math.pi); fill_stroke(c, GOLD, INK, 8)
    c.save(); c.arc(cx, cy, R, 0, 2 * math.pi); c.clip()
    g = cairo.RadialGradient(cx, cy, 50, cx, cy, R)
    base = mix(hx("#7A3B22"), hx("#B8502E"), heat)
    g.add_color_stop_rgba(0, *mix(base, ORANGE, 0.3)); g.add_color_stop_rgba(1, *base); c.set_source(g); c.paint()
    t_iman = wt("paso3", "imán"); t_flip = wt("paso3", "cambia"); t_choca = wt("paso3", "choca")
    follow = ease(ramp(t, t_flip, t_flip + 1.2))
    # field flips at 2.45 Hz in this 1.000.000.000x slow motion (2.45 GHz / 1e9)
    field = math.sin(2 * math.pi * 2.45 * (t - t_flip)) if t > t_flip else 1.0
    target = -math.pi / 2 if field >= 0 else math.pi / 2
    smooth = -math.pi / 2 * field  # continuous version for the rotation
    jit = 0.35 * ease(ramp(t, t_choca, t_choca + 0.5))
    for i, (x, y, a0) in enumerate(MOLS):
        a = lerp(a0 + 0.15 * math.sin(t * 2 + i), smooth + 0.25 * math.sin(i * 1.7) + jit * math.sin(t * 23 + i * 3), follow)
        dx = jit * 14 * math.sin(t * 17 + i * 2.1); dy = jit * 14 * math.cos(t * 19 + i)
        water_molecule(c, x + dx, y + dy, a, 1.6 if i == 0 else 0.95, heat, labels=(i == 0 and t >= t_iman))
        if heat > 0.05: glow(c, x, y, 110, HOT, 0.25 * heat)
    c.restore()
    c.restore()
    # field arrow (left) once the wave starts flipping
    k = ramp(t, t_flip - 0.3, t_flip)
    if k > 0:
        x = 90; y = 1120; d = 1 if field >= 0 else -1
        L_ = 220 * k
        line(c, [(x, y + L_ * d), (x, y - L_ * d)], YEL, 18)
        c.move_to(x, y - L_ * d - 40 * d); c.line_to(x - 34, y - L_ * d + 10 * d); c.line_to(x + 34, y - L_ * d + 10 * d); c.close_path()
        c.set_source_rgba(*YEL); c.fill()
        c.save(); c.translate(x - 50, y); c.rotate(-math.pi / 2); text(c, "ONDA", 0, 0, 30, YEL, SANS, True); c.restore()
    m0 = MOLS[0]
    callout(c, "POSITIVO (+)", m0[0] + 70, m0[1] - 60, 800, 660, t, wt("paso3", "positivo"))
    callout(c, "NEGATIVO (−)", m0[0] - 20, m0[1] + 20, 300, 1640, t, wt("paso3", "negativo"))
    # thermometer (right)
    k = ramp(t, wt("paso3", "roza") - 0.5, wt("paso3", "roza"))
    if k > 0:
        x, y0, y1 = 1000, 780, 1420
        rrect(c, x - 26, y0, 52, y1 - y0, 26); fill_stroke(c, CREAM, INK, 6)
        c.arc(x, y1 + 20, 46, 0, 2 * math.pi); fill_stroke(c, mix(COLD, HOT, heat), INK, 6)
        lv = lerp(y1 - 40, y0 + 40, heat)
        rrect(c, x - 12, lv, 24, y1 - lv + 10, 12); c.set_source_rgba(*mix(COLD, HOT, heat)); c.fill()
    if heat > 0.6:
        text(c, "CALOR", 540, 1650, 70, HOT, SLAB, False, outline=INK, olw=10)

def scene_plate(c, t):
    b = B("paso4")
    background(c, t)
    c.save(); cam(c, 1.0 + 0.05 * ramp(t, b["start"], b["end"]))
    cx, cy, R = 540, 1120, 400
    t_rot = wt("paso4", "gira") - 0.2
    rot = 0.9 * max(0, t - t_rot) ** 1.0
    shadow(c, lambda: c.arc(cx, cy, R + 20, 0, 2 * math.pi), 14, 18, 0.45)
    c.arc(cx, cy, R + 20, 0, 2 * math.pi); fill_stroke(c, alpha(LAV, 0.75), INK, 8)
    c.arc(cx, cy, R - 30, 0, 2 * math.pi); c.set_source_rgba(1, 1, 1, 0.15); c.set_line_width(6); c.stroke()
    even = ease(ramp(t, t_rot + 1.5, b["end"] + 0.5))
    # pizza on the plate (rotates with it)
    c.save(); c.translate(cx, cy); c.rotate(rot)
    c.arc(0, 0, 300, 0, 2 * math.pi); fill_stroke(c, hx("#E9B76A"), INK, 7)
    c.arc(0, 0, 262, 0, 2 * math.pi); fill_stroke(c, mix(RUST, HOT, 0.4 * even), None)
    for i in range(14):
        a = i * 2.4; r = 60 + (i * 47) % 180
        c.arc(r * math.cos(a), r * math.sin(a), 28, 0, 2 * math.pi); fill_stroke(c, hx("#8E2F2A"), INK, 4)
    for i in range(9):
        a = i * 1.3 + 0.5; r = 90 + (i * 61) % 150
        c.arc(r * math.cos(a), r * math.sin(a), 18, 0, 2 * math.pi); fill_stroke(c, YEL, None)
    for i in range(8):
        line(c, [(0, 0), (300 * math.cos(i * math.pi / 4), 300 * math.sin(i * math.pi / 4))], alpha(INK, 0.35), 3)
    c.restore()
    # standing-wave hot/cold spots: fixed in space, ~6 cm apart (half of 12.2 cm)
    t_hot = wt("paso4", "queman") - 0.2; t_cold = wt("paso4", "frías") - 0.2
    sp = 190
    c.save(); c.arc(cx, cy, 300, 0, 2 * math.pi); c.clip()
    for i in range(-2, 3):
        for j in range(-2, 3):
            x, y = cx + i * sp, cy + j * sp
            hot = (i + j) % 2 == 0
            k = ramp(t, t_hot, t_hot + 0.5) if hot else ramp(t, t_cold, t_cold + 0.5)
            k *= 1 - 0.65 * even
            if k > 0: glow(c, x, y, 120, HOT if hot else COLD, 0.85 * k)
    c.restore()
    t6 = wt("paso4", "seis") - 0.2
    k = ramp(t, t6, t6 + 0.4)
    if k > 0:
        x0, x1, y = cx, cx + sp, cy - sp - 0
        y = cy + sp + 0
        line(c, [(x0, cy), (x0, cy + 330)], alpha(WHITE, 0.6 * k), 3); line(c, [(x1, cy - sp), (x1, cy + 330)], alpha(WHITE, 0.6 * k), 3)
        line(c, [(x0, cy + 330), (lerp(x0, x1, ease(k)), cy + 330)], YEL, 8)
        text(c, "6 cm", (x0 + x1) / 2, cy + 395, 52, YEL, SLAB, False, outline=INK, olw=10)
    c.restore()
    callout(c, "ZONA QUE QUEMA", cx, cy, 300, 650, t, t_hot + 0.1, HOT)
    callout(c, "ZONA FRÍA", cx + sp, cy, 820, 650, t, t_cold + 0.1, COLD)
    if t >= t_rot:  # rotation arrow
        c.arc(cx, cy, R + 55, -2.6 + rot % 6.28, -1.4 + rot % 6.28); c.set_source_rgba(*YEL); c.set_line_width(12); c.stroke()

def scene_mesh(c, t):
    b = B("paso5")
    background(c, t)
    c.save(); cam(c, 1.0 + 0.05 * ramp(t, b["start"], b["end"]))
    mx = 640
    # door (metal sheet with holes) seen from the side
    rrect(c, mx - 22, 600, 44, 1050, 10); fill_stroke(c, hx("#8A93A6"), INK, 6)
    for i in range(30):
        c.set_source_rgba(*hx("#17161D")); c.rectangle(mx - 22, 620 + i * 35, 44, 10); c.fill()
    lam = 380  # 12 cm drawn as 380 px
    t_onda = wt("paso5", "onda"); t_luz = wt("paso5", "luz"); t_no = wt("paso5", "no", 2)
    k = ease(ramp(t, t_onda - 0.3, t_onda + 0.3))
    if k > 0:  # big microwave hitting the door and reflecting (standing wave on the inside)
        pts = []
        for i in range(0, 520):
            x = 60 + i
            y = 1120 + 150 * k * math.sin(2 * math.pi * (x - mx) / lam) * math.cos(t * 3.2)
            pts.append((x, y))
        line(c, pts, YEL, 12)
        # ruler: one wavelength
        x1 = mx - 20 - lam * 1.25 + 40; x2 = x1 + lam
        k2 = ramp(t, wt("paso5", "doce") - 0.3, wt("paso5", "doce"))
        if k2 > 0:
            line(c, [(x1, 880), (lerp(x1, x2, ease(k2)), 880)], CREAM, 6)
            line(c, [(x1, 860), (x1, 900)], CREAM, 6); line(c, [(x2, 860), (x2, 900)], alpha(CREAM, k2), 6)
            text(c, "12 cm", (x1 + x2) / 2, 840, 54, CREAM, SLAB, False, outline=INK, olw=10)
    t_agu = wt("paso5", "agujeros") - 0.2
    kk = eob(ramp(t, t_agu, t_agu + 0.4))
    if kk > 0:  # magnified holes
        c.save(); c.translate(860, 760); c.scale(kk, kk)
        c.arc(0, 0, 150, 0, 2 * math.pi); fill_stroke(c, hx("#8A93A6"), INK, 7)
        c.save(); c.arc(0, 0, 150, 0, 2 * math.pi); c.clip()
        for i in range(-4, 5):
            for j in range(-4, 5):
                c.arc(i * 36 + (j % 2) * 18, j * 32, 11, 0, 2 * math.pi); c.set_source_rgba(*hx("#17161D")); c.fill()
        c.restore(); c.restore()
        line(c, [(mx + 22, 860), (860 - 150 * kk * 0.7, 760 + 150 * kk * 0.7)], alpha(WHITE, 0.7), 3)
        if kk > 0.9: text(c, "AGUJEROS DIMINUTOS", 860, 960, 30, CREAM, SANS, True)
    kl = ramp(t, t_luz - 0.3, t_luz)
    if kl > 0:  # little light waves pass through
        for n in range(4):
            ph = ((t - t_luz) * 0.5 + n / 4) % 1
            x0 = 300 + ph * 720
            y0 = 1380 + n * 40
            pts = [(x0 + i * 3, y0 + 10 * math.sin(i * 0.9 - t * 12)) for i in range(40)]
            line(c, pts, alpha(YEL, kl * 0.9), 4)
        # eye
        ex, ey = 960, 1430
        c.save(); c.translate(ex, ey); c.scale(1, 0.6); c.arc(0, 0, 60, 0, 2 * math.pi); c.restore(); fill_stroke(c, WHITE, INK, 6)
        c.arc(ex - 10, ey, 22, 0, 2 * math.pi); fill_stroke(c, STEEL, INK, 4)
        text(c, "LA LUZ PASA", 830, 1560, 40, YEL, SLAB, False, outline=INK, olw=8)
    kn = ramp(t, t_no - 0.1, t_no + 0.2)
    if kn > 0:
        xmark(c, mx + 120, 1120, 70, t, t_no - 0.1, 20)
        text(c, "MICROONDAS: NO", 360, 1300, 44, HOT, SLAB, False, outline=INK, olw=8)
    c.restore()

def scene_all(c, t):
    """Todo junto + acelerón: full x-ray, labels light up in order, then real speed."""
    background(c, t, YEL)
    b = B("junto")
    fast = ease(ramp(t, T_REAL + 0.2, B("remate")["start"] - 0.4))
    shake = 6 * fast
    c.save(); cam(c, 1.0 + 0.05 * ease(ramp(t, b["start"], B("remate")["start"])), W / 2, 1080)
    c.translate(shake * math.sin(t * 60), shake * math.cos(t * 53))
    order = [("enchufe", "plug"), ("magnetrón", "mag"), ("ondas", "guide"), ("agua", "cav"), ("calor", "cav")]
    hl = {p for w, p in order if t >= wt("junto", w) - 0.1}
    heat = ramp(t, wt("junto", "calor"), T_REAL) * 0.5 + 0.5 * fast
    microwave_xray(c, t, heat=heat, hl=hl, wave=1.0 if t >= wt("junto", "ondas") else 0.0, steam_amt=heat, fast=fast,
                   spark=((t - wt("junto", "enchufe")) % 1.0) if t < wt("junto", "ondas") + 0.2 else None)
    c.restore()
    P = mw_parts()
    def sc(p): return (W / 2 + (p[0] - W / 2) * 1.03, 1080 + (p[1] - 1080) * 1.03)
    if fast < 0.3:
        callout(c, "ENCHUFE", *sc(P["plug"]), 880, 1600, t, wt("junto", "enchufe"))
        callout(c, "MAGNETRÓN", *sc(P["mag"]), 820, 680, t, wt("junto", "magnetrón"))
        callout(c, "ONDAS", *sc((560, 900)), 330, 680, t, wt("junto", "ondas"), YEL)
        callout(c, "AGUA", *sc((430, 1150)), 220, 1560, t, wt("junto", "agua"))
        callout(c, "CALOR", *sc((430, 1100)), 520, 1680, t, wt("junto", "calor"), HOT)
    if fast > 0:  # speed lines
        for i in range(24):
            r0 = 300 + (i * 97 + t * 2400) % 900
            a = i * 0.26
            line(c, [(540 + math.cos(a) * r0, 1080 + math.sin(a) * r0), (540 + math.cos(a) * (r0 + 120 * fast), 1080 + math.sin(a) * (r0 + 120 * fast))],
                 alpha(WHITE, 0.35 * fast), 5)
    flash = ramp(t, B("remate")["start"] - 0.45, B("remate")["start"] - 0.3) * (1 - ramp(t, B("remate")["start"] - 0.3, B("remate")["start"] - 0.1))
    if flash > 0: c.set_source_rgba(1, 1, 1, 0.8 * flash); c.paint()

def scene_lasagna(c, t):
    b = B("remate")
    background(c, t)
    c.save(); cam(c, 1.0 + 0.06 * ramp(t, b["start"], T_LOOP))
    x0, y0, w, h = 150, 830, 780, 520
    shadow(c, lambda: rrect(c, x0, y0, w, h, 26), 14, 20, 0.45)
    layers = [hx("#F3D9A0"), hx("#BF5B45"), hx("#F2C94C"), hx("#F3D9A0"), hx("#BF5B45"), hx("#F2C94C"), hx("#F3D9A0")]
    c.save(); rrect(c, x0, y0, w, h, 26); c.clip()
    lh = h / len(layers)
    for i, col in enumerate(layers):
        c.set_source_rgba(*col); c.rectangle(x0, y0 + i * lh, w, lh + 1); c.fill()
        line(c, [(x0 + 20 * k, y0 + i * lh + 6 * math.sin(k)) for k in range(0, 40)], alpha(INK, 0.25), 3)
    # heat map: only the outer few cm get hot, centre stays frozen
    t_cm = wt("remate", "centímetros") - 0.4; t_con = wt("remate", "contagio") - 0.3; t_hel = wt("remate", "helada") - 0.2
    kh = ease(ramp(t, t_cm, t_cm + 0.6))
    spread = ease(ramp(t, t_con, t_con + 1.5))
    depth = 110 + 50 * spread
    if kh > 0:
        for side in range(4):
            if side == 0: g = cairo.LinearGradient(x0, 0, x0 + depth, 0)
            elif side == 1: g = cairo.LinearGradient(x0 + w, 0, x0 + w - depth, 0)
            elif side == 2: g = cairo.LinearGradient(0, y0, 0, y0 + depth)
            else: g = cairo.LinearGradient(0, y0 + h, 0, y0 + h - depth)
            g.add_color_stop_rgba(0, *alpha(HOT, 0.75 * kh)); g.add_color_stop_rgba(1, *alpha(HOT, 0)); c.set_source(g); c.paint()
        glow(c, x0 + w / 2, y0 + h / 2, 260 - 40 * spread, COLD, 0.85 * kh)
    c.restore()
    rrect(c, x0, y0, w, h, 26); fill_stroke(c, None, INK, 8)
    if kh > 0:
        for side, (ax, ay, dx, dy) in enumerate([(x0 - 70, y0 + h / 2, 1, 0), (x0 + w + 70, y0 + h / 2, -1, 0), (x0 + w / 2, y0 - 70, 0, 1)]):
            line(c, [(ax, ay), (ax + dx * 110 * kh, ay + dy * 110 * kh)], HOT, 14)
        text(c, "UNOS CM", x0 + 150, y0 - 110, 44, HOT, SLAB, False, outline=INK, olw=8)
    if spread > 0:  # conduction arrows creeping inwards
        for i in range(6):
            a = i * math.pi / 3 + 0.3
            r1 = 280 - 120 * spread
            line(c, [(540 + math.cos(a) * 300 * 0.9, 1090 + math.sin(a) * 190), (540 + math.cos(a) * r1 * 0.9, 1090 + math.sin(a) * r1 * 0.6)], alpha(ORANGE, 0.9 * spread), 7)
    kf = ramp(t, t_hel, t_hel + 0.4)
    if kf > 0:  # frost sparkles in the middle
        for i in range(10):
            a = i * 2.39; r = 30 + (i * 23) % 110
            x, y = 540 + math.cos(a) * r * 1.6, 1090 + math.sin(a) * r * 0.8
            s = 16 * kf * (0.7 + 0.3 * math.sin(t * 6 + i))
            line(c, [(x - s, y), (x + s, y)], WHITE, 4); line(c, [(x, y - s), (x, y + s)], WHITE, 4)
        text(c, "HELADA", 540, 1470, 76, COLD, SLAB, False, outline=INK, olw=10)
    c.restore()


# ---------------------------------------------------------------- timeline
X = 0.35  # crossfade
SCENES = [
    ("front", 0.0, T_LENTO + 0.5),
    ("xray", T_LENTO + 0.5, B("paso2")["start"] - 0.25),
    ("cavity", B("paso2")["start"] - 0.25, B("paso3")["start"] - 0.25),
    ("molecules", B("paso3")["start"] - 0.25, B("paso4")["start"] - 0.25),
    ("plate", B("paso4")["start"] - 0.25, B("paso5")["start"] - 0.25),
    ("mesh", B("paso5")["start"] - 0.25, B("junto")["start"] - 0.25),
    ("all", B("junto")["start"] - 0.25, B("remate")["start"] - 0.1),
    ("lasagna", B("remate")["start"] - 0.1, T_LOOP + 0.15),
    ("loop", T_LOOP + 0.15, DUR + 1),
]
FN = {"front": scene_front, "xray": scene_xray_steps, "cavity": scene_cavity, "molecules": scene_molecules,
      "plate": scene_plate, "mesh": scene_mesh, "all": scene_all, "lasagna": scene_lasagna,
      "loop": lambda c, t: scene_front(c, t, frozen=True)}
XF = {"lasagna": 0.08, "loop": 0.6}  # flash cut into the lasagna; slow dissolve back to frame 0

def draw_scene(c, name, t):
    c.save(); FN[name](c, t); c.restore()

def frame(t):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_antialias(cairo.ANTIALIAS_GOOD)
    cur = [i for i, (n, a, b) in enumerate(SCENES) if a <= t < b] or [len(SCENES) - 1]
    i = cur[0]; name, a, b = SCENES[i]
    draw_scene(c, name, t)
    xf = XF.get(name, X)
    if i > 0 and t < a + xf:  # dissolve in from the previous scene
        prev = SCENES[i - 1][0]
        c.push_group(); draw_scene(c, prev, t); c.pop_group_to_source()
        c.paint_with_alpha(1 - ease((t - a) / xf))
    if name == "loop":  # the last frame is exactly frame 0 (HUD and card included)
        c.save(); hud(c, 0.0); cards(c, 0.0); c.restore()
    else:
        hud(c, t); cards(c, t)
    return s


def render_range(f0, f1, out):
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", out],
                           stdin=subprocess.PIPE)
    for f in range(f0, f1):
        s = frame(f / FPS); s.flush(); enc.stdin.write(bytes(s.get_data()))
    enc.stdin.close(); enc.wait()
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", nargs=2); ap.add_argument("--sheet", nargs="+"); ap.add_argument("--video")
    ap.add_argument("--jobs", type=int, default=os.cpu_count())
    a = ap.parse_args()
    if a.still:
        frame(float(a.still[0])).write_to_png(a.still[1])
    elif a.sheet:  # contact sheet: --sheet out.png t1 t2 ...
        out, ts = a.sheet[0], [float(x) for x in a.sheet[1:]]
        cols = min(len(ts), 6); rows = math.ceil(len(ts) / cols); sw, sh = W // 3, H // 3
        S = cairo.ImageSurface(cairo.FORMAT_ARGB32, sw * cols, sh * rows); c = cairo.Context(S)
        for k, t in enumerate(ts):
            c.save(); c.translate((k % cols) * sw, (k // cols) * sh); c.scale(1 / 3, 1 / 3)
            c.set_source_surface(frame(t), 0, 0); c.paint(); c.restore()
            text(c, f"{t:.1f}s", (k % cols) * sw + 8, (k // cols) * sh + 30, 26, YEL, SANS, True, "l")
        S.write_to_png(out)
    elif a.video:
        from multiprocessing import Pool
        n = int(DUR * FPS); J = a.jobs; step = math.ceil(n / J)
        parts = [(i * step, min(n, (i + 1) * step), os.path.join(HERE, f"part{i}.mp4")) for i in range(J)]
        with Pool(J) as p: p.starmap(render_range, parts)
        lst = os.path.join(HERE, "parts.txt"); open(lst, "w").write("".join(f"file '{x[2]}'\n" for x in parts))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", a.video], check=True)
        for x in parts: os.remove(x[2])
        print("video", a.video, n, "frames", DUR, "s")
