"""Shared engine for the animated explainer shorts (style: output/guia_de_estilo.md).

A project is a folder (env PROJ, or set before import) holding:
  project.json   voice/rate, HUD, cards, caption keywords, music
  beats.json     the script, one entry per beat (ids: gancho, imposible, freno, paso1..pasoN, junto, acelera, remate)
  scenes.py      the illustrations: SCENES list + scene functions + POPS/SFX/THUMB (does `from core import *`)
Generated: beats_timed.json, words.json (whisper), subs.ass, narration.wav, mix.wav, ...
"""
import json, math, os, random, re, unicodedata
import cairo

W, H, FPS = 1080, 1920, 30
PROJ = os.path.abspath(os.environ.get("PROJ", "."))
CFG = json.load(open(os.path.join(PROJ, "project.json")))
_bt = os.path.join(PROJ, "beats_timed.json"); _wd = os.path.join(PROJ, "words.json")
BEATS = {b["id"]: b for b in json.load(open(_bt))} if os.path.exists(_bt) else {}
WORDS = json.load(open(_wd)) if os.path.exists(_wd) else []

# ---------------------------------------------------------------- palette (guia_de_estilo.md §5)
def hx(s, a=1.0):
    s = s.lstrip("#"); return (int(s[0:2], 16) / 255, int(s[2:4], 16) / 255, int(s[4:6], 16) / 255, a)
BG_TOP, BG_BOT = hx("#282336"), hx("#17161D")
INK = hx("#1B1925"); CREAM = hx("#FFEEE0"); CREAM2 = hx("#F3EAD1"); RED = hx("#BC3A38"); GOLD = hx("#A6613A")
ORANGE = hx("#E27E56"); ORANGE2 = hx("#CC7B3E"); RUST = hx("#BF5B45"); YEL = hx("#F2C94C"); STEEL = hx("#526DA9")
LAV = hx("#A1ABC9"); WHITE = hx("#FFFFFF"); COLD = hx("#5B8DEF"); HOT = hx("#FF5A3C"); XRAY = hx("#9FD3FF")
GREEN = hx("#4CAF50"); METAL = hx("#8A93A6"); DARK = hx("#2C293C"); NIGHT = hx("#1E1B2E")
SLAB = "Alfa Slab One"; SANS = "Inter"; MONO = "JetBrains Mono"

# ---------------------------------------------------------------- timing helpers
def bare(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))

def wt(beat, sub, nth=0, end=False):
    """Start (or end) time of the nth word in `beat` whose text contains `sub` (accent/case-insensitive)."""
    hits = [w for w in WORDS if w["beat"] == beat and bare(sub) in bare(w["word"])]
    if not hits: raise KeyError(f"word '{sub}' not found in beat '{beat}'")
    w = hits[min(nth, len(hits) - 1)]
    return w["end"] if end else w["start"]

def B(k): return BEATS[k]
if BEATS:
    T_SLOW = BEATS["freno"]["end"]                      # slow motion fully reached
    T_REAL = BEATS["acelera"]["end"]                    # "a velocidad real" said
    T_LOOP = wt("remate", CFG["loop_word"])             # loop dissolve starts here
    DUR = round(BEATS["remate"]["end"] + 0.45, 2)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ramp(t, t0, t1): return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t0)
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eob(x):  # ease-out-back: pop
    x = clamp(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, k): return a + (b - a) * k
def mix(c1, c2, k): return tuple(lerp(a, b, k) for a, b in zip(c1, c2))
def alpha(c, a): return (c[0], c[1], c[2], c[3] * a)
def pulse_at(t, t0, d=0.6): return math.sin(math.pi * ramp(t, t0, t0 + d)) if t0 <= t <= t0 + d else 0.0

# ---------------------------------------------------------------- drawing primitives
def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()

def circle(c, x, y, r):
    c.new_sub_path(); c.arc(x, y, r, 0, 2 * math.pi)

def fill_stroke(c, fill, stroke=INK, lw=6):
    """Fill then stroke the current path (cartoon look: thick dark outline)."""
    if fill:
        c.set_source_rgba(*fill)
        c.fill_preserve() if stroke else c.fill()
    if stroke: c.set_source_rgba(*stroke); c.set_line_width(lw); c.stroke()
    else: c.new_path()

def shadow(c, path_fn, dx=10, dy=14, a=0.35):
    c.save(); c.new_path(); c.translate(dx, dy); path_fn(); c.set_source_rgba(0, 0, 0, a); c.fill(); c.restore()

def font(c, fam, size, bold=False):
    c.select_font_face(fam, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)

def text(c, s, x, y, size, color=WHITE, fam=SANS, bold=True, align="c", outline=None, olw=8):
    """Draw text with baseline at y. align: c/l/r. Leaves no current point behind."""
    c.new_path(); font(c, fam, size, bold); e = c.text_extents(s)
    dx = {"c": -e.x_advance / 2, "l": 0, "r": -e.x_advance}[align]
    c.move_to(x + dx, y)
    if outline:
        c.text_path(s); c.set_source_rgba(*outline); c.set_line_width(olw); c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.stroke_preserve(); c.set_source_rgba(*color); c.fill()
    else:
        c.set_source_rgba(*color); c.show_text(s)
    c.new_path()
    return e.x_advance

def fit_size(c, s, fam, size, maxw, bold=False):
    font(c, fam, size, bold); w = c.text_extents(s).x_advance
    return size * min(1.0, maxw / w) if w else size

def line(c, pts, color, lw, cap=cairo.LINE_CAP_ROUND):
    c.new_path(); c.move_to(*pts[0])
    for p in pts[1:]: c.line_to(*p)
    c.set_source_rgba(*color); c.set_line_width(lw); c.set_line_cap(cap); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()

def arrow(c, x0, y0, x1, y1, color, lw=12, head=34):
    a = math.atan2(y1 - y0, x1 - x0)
    line(c, [(x0, y0), (x1 - math.cos(a) * head * 0.6, y1 - math.sin(a) * head * 0.6)], color, lw)
    c.new_path(); c.move_to(x1, y1)
    c.line_to(x1 - head * math.cos(a - 0.45), y1 - head * math.sin(a - 0.45))
    c.line_to(x1 - head * math.cos(a + 0.45), y1 - head * math.sin(a + 0.45)); c.close_path()
    c.set_source_rgba(*color); c.fill()

def glow(c, x, y, r, color, a=0.6):
    c.new_path()
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, color[0], color[1], color[2], a); g.add_color_stop_rgba(1, color[0], color[1], color[2], 0)
    c.set_source(g); c.arc(x, y, r, 0, 2 * math.pi); c.fill()

def wave(c, x0, x1, y, amp, wavelength, phase, color, lw=8):
    """Horizontal sine from x0 to x1."""
    n = max(2, int(abs(x1 - x0) / 4))
    pts = [(x0 + (x1 - x0) * i / n, y + amp * math.sin(2 * math.pi * ((x1 - x0) * i / n) / wavelength + phase)) for i in range(n + 1)]
    line(c, pts, color, lw)

def callout(c, label, ax, ay, lx, ly, t, t0, color=CREAM, size=34):
    """Label with a leader line popping in at t0 (ref1/ref2 'MOTOR', 'SHAFT'). (ax,ay)=thing, (lx,ly)=label centre."""
    k = ramp(t, t0, t0 + 0.35)
    if k <= 0: return
    p = eob(k)
    mx, my = lerp(ax, lx, ease(k)), lerp(ay, ly, ease(k))
    line(c, [(ax, ay), (mx, my)], alpha(WHITE, 0.9), 4)
    circle(c, ax, ay, 9 * p); c.set_source_rgba(*WHITE); c.fill()
    font(c, SANS, size, True); e = c.text_extents(label)
    bw, bh = e.x_advance + 30, size + 22
    c.save(); c.translate(lx, ly); c.scale(p, p)
    rrect(c, -bw / 2, -bh / 2, bw, bh, 10); fill_stroke(c, INK, alpha(WHITE, 0.95), 3)
    text(c, label, 0, size * 0.36, size, color, SANS, True)
    c.restore()

def xmark(c, x, y, s, t, t0, lw=16):
    k = ramp(t, t0, t0 + 0.25)
    if k <= 0 or s < 8: return
    line(c, [(x - s, y - s), (lerp(x - s, x + s, ease(k)), lerp(y - s, y + s, ease(k)))], RED, lw)
    k2 = ramp(t, t0 + 0.12, t0 + 0.37)
    if k2 > 0: line(c, [(x + s, y - s), (lerp(x + s, x - s, ease(k2)), lerp(y - s, y + s, ease(k2)))], RED, lw)

def icon_badge(c, x, y, k, label, draw_fn, t=0.0, crossed_at=None, r=105):
    """Round cream badge with an icon (draw_fn(c) draws around 0,0 in a ~140px box), label below, optional red X.
    k = 0..1 pop scale."""
    if k <= 0.02: return
    c.save(); c.translate(x, y); c.scale(k, k)
    circle(c, 0, 0, r); fill_stroke(c, CREAM, INK, 6)
    c.save(); draw_fn(c); c.restore()
    c.restore()
    if crossed_at is not None and k > 0.3: xmark(c, x, y, 70 * k, t, crossed_at)
    if k > 0.3: text(c, label, x, y + r + 45, 30, alpha(CREAM, clamp(k)), SANS, True)

def cam(c, s, cx=W / 2, cy=1100):
    """Zoom the camera by s around (cx, cy). Call inside c.save()/c.restore()."""
    c.translate(cx, cy); c.scale(s, s); c.translate(-cx, -cy)

# ---------------------------------------------------------------- background
STARS = [(random.Random(i).uniform(0, W), random.Random(i + 99).uniform(560, 1700), random.Random(i + 7).uniform(1.5, 3.5)) for i in range(60)]

def background(c, t, tint=None):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, *BG_TOP); g.add_color_stop_rgba(1, *BG_BOT)
    c.set_source(g); c.paint()
    if tint: glow(c, W / 2, 1100, 900, tint, 0.18)
    for i, (x, y, r) in enumerate(STARS):  # drifting dust: the camera is never still
        c.set_source_rgba(1, 1, 1, 0.10 + 0.08 * math.sin(t * 1.3 + i)); circle(c, (x + t * 6) % W, y, r); c.fill()
    v = cairo.RadialGradient(W / 2, H / 2, 500, W / 2, H / 2, 1250)
    v.add_color_stop_rgba(0, 0, 0, 0, 0); v.add_color_stop_rgba(1, 0, 0, 0, 0.55)
    c.set_source(v); c.paint()

# ---------------------------------------------------------------- HUD (ref2: "64x SLOWER" | gauge | counter)
def dots(n): return f"{int(round(n)):,}".replace(",", ".")

def slow_log(t):
    """log10 of the slow-motion factor: 0 = real speed, HUD.max_log = fully slowed."""
    M = CFG["hud"]["max_log"]
    t0 = B("freno")["start"]
    if t < t0: return 0.0
    if t < T_SLOW + 0.3: return M * ease(ramp(t, t0, T_SLOW + 0.3))
    if t < T_REAL + 0.2: return float(M)
    t2 = B("remate")["start"] - 0.4
    if t < t2: return M * (1 - ease(ramp(t, T_REAL + 0.2, t2)) ** 0.7)
    return 0.0

def speed_fraction(t):
    """1 at real speed, 0 fully slowed (handy for animation speed)."""
    return 1 - slow_log(t) / CFG["hud"]["max_log"]

_AT = {}
def anim_time(t):
    """'Physical' time: advances 10**-slow_log slower than the video clock. Use it for anything that oscillates at
    its real frequency f: phase = 2*pi*f*anim_time(t). At full slow motion it advances 10**-max_log per second."""
    k = round(t, 3)
    if k not in _AT:
        acc, x = 0.0, 0.0
        while x < t:
            dx = min(0.02, t - x); acc += dx * 10 ** (-slow_log(x)); x += dx
        _AT[k] = acc
    return _AT[k]

def fmt_val(v):
    if v >= 1000: return dots(v)
    if v >= 100: return f"{v:.0f}"
    if v >= 10: return f"{v:.1f}".replace(".", ",")
    if v >= 0.01: return f"{v:.2f}".replace(".", ",")
    return f"{v:.4f}".replace(".", ",")

def hud(c, t):
    h = CFG["hud"]; L = slow_log(t); y0 = 96
    step = h.get("step", 1)
    e = int(round(L / step) * step) if L > 0.05 else 0
    lab = "VELOCIDAD REAL" if e == 0 else f"{dots(10 ** e)}x MÁS LENTO"
    sz = fit_size(c, lab, SLAB, 34, 400)
    shadow(c, lambda: rrect(c, 40, y0, 430, 78, 12), 6, 8, 0.4)
    rrect(c, 40, y0, 430, 78, 12); fill_stroke(c, CREAM, INK, 5)
    text(c, lab, 255, y0 + 39 + sz * 0.36, sz, RED if e else INK, SLAB, False)
    gx, gy, gr = 560, y0 + 72, 62
    rrect(c, gx - 80, y0 - 6, 160, 90, 14); fill_stroke(c, CREAM, INK, 5)
    for i in range(30):
        a0 = math.pi + math.pi * i / 30; a1 = math.pi + math.pi * (i + 0.8) / 30
        col = mix(GREEN, YEL, i / 15) if i < 15 else mix(YEL, HOT, (i - 15) / 15)
        c.new_path(); c.arc(gx, gy, gr, a0, a1); c.set_source_rgba(*col); c.set_line_width(14); c.stroke()
    ang = math.pi + math.pi * (0.06 + 0.88 * (1 - L / h["max_log"])) + 0.03 * math.sin(t * 40) * (L < 0.5)
    line(c, [(gx, gy), (gx + math.cos(ang) * (gr - 6), gy + math.sin(ang) * (gr - 6))], INK, 6)
    circle(c, gx, gy, 9); c.set_source_rgba(*INK); c.fill()
    v = h["base"] / 10 ** L
    val = fmt_val(v) + h.get("suffix", "")
    shadow(c, lambda: rrect(c, 660, y0, 380, 78, 12), 6, 8, 0.4)
    rrect(c, 660, y0, 380, 78, 12); fill_stroke(c, CREAM, INK, 5)
    us = min(20, *(fit_size(c, u, SANS, 20, 116, True) for u in h["unit"]))
    text(c, h["unit"][0], 676, y0 + 32, us, INK, SANS, True, "l"); text(c, h["unit"][1], 676, y0 + 58, us, INK, SANS, True, "l")
    rrect(c, 800, y0 + 12, 226, 54, 8); fill_stroke(c, hx("#1E3A2A"), INK, 3)
    vs = fit_size(c, val, MONO, 34, 206, True)
    text(c, val, 1016, y0 + 39 + vs * 0.36, vs, hx("#7CFC9A"), MONO, True, "r")

# ---------------------------------------------------------------- step cards (ref1: barber-shop sign, numbered)
def card_windows():
    wins = []
    for k, v in CFG["cards"].items():
        b = B(k)
        t0 = 0.0 if k == "gancho" else b["start"] - 0.15
        t1 = {"gancho": B("freno")["start"] - 0.1, "acelera": B("remate")["start"] - 0.35, "remate": T_LOOP - 0.1}.get(k, b["end"] + b["pause"] - 0.05)
        wins.append((k, t0, t1))
    wins.append(("gancho", T_LOOP + 0.05, DUR + 1))  # loop: same card as frame 0
    return wins

def draw_card(c, key, k_in, k_out):
    num, title, sub = CFG["cards"][key]
    s = eob(k_in) * (1 - ease(k_out))
    if s <= 0.01: return
    cx, top = W / 2, 232
    tsz = min(fit_size(c, ln, SLAB, 62, 740 if num else 820) for ln in title)
    ssz = fit_size(c, sub, SLAB, 32, 760)
    h = 36 + len(title) * tsz * 1.08 + ssz + 22; w = 900
    c.save(); c.translate(cx, top + h / 2); c.scale(s, s); c.translate(-cx, -(top + h / 2))
    shadow(c, lambda: rrect(c, cx - w / 2, top, w, h, 14), 10, 14, 0.45)
    rrect(c, cx - w / 2 - 10, top - 10, w + 20, h + 20, 18); fill_stroke(c, GOLD, INK, 6)
    rrect(c, cx - w / 2, top, w, h, 12); fill_stroke(c, CREAM, INK, 4)
    for side in (-1, 1):
        px = cx + side * (w / 2 - 22)
        c.save(); rrect(c, px - 14, top + 10, 28, h - 20, 8); c.clip()
        c.set_source_rgba(*WHITE); c.paint()
        for j in range(-4, int(h / 22) + 4):
            c.new_path(); c.move_to(px - 20, top + j * 22); c.line_to(px + 20, top + j * 22 + 20); c.line_to(px + 20, top + j * 22 + 31); c.line_to(px - 20, top + j * 22 + 11)
            c.close_path(); c.set_source_rgba(*(RED if j % 2 else STEEL)); c.fill()
        c.restore(); rrect(c, px - 14, top + 10, 28, h - 20, 8); fill_stroke(c, None, INK, 3)
    y = top + 24 + tsz * 0.82
    for ln in title: text(c, ln, cx, y, tsz, INK, SLAB, False); y += tsz * 1.08
    text(c, sub, cx, y + ssz * 0.15, ssz, RED, SLAB, False)
    if num:
        bx, by = cx - w / 2 + 8, top + 6
        circle(c, bx, by, 36); fill_stroke(c, RED, INK, 5)
        text(c, str(num), bx, by + 15, 42, WHITE, SLAB, False)
    c.restore()

def cards(c, t):
    for key, t0, t1 in CARD_WINS:
        if t0 - 0.01 <= t <= t1 + 0.3:
            k_in = 1.0 if key == "gancho" else ramp(t, t0, t0 + 0.4)
            draw_card(c, key, k_in, ramp(t, t1, t1 + 0.25))

CARD_WINS = card_windows() if BEATS else []
