"""¿Cómo 'piensa' tu móvil?  (transistores = interruptores, reglas lógicas, reloj)
Illustrations for the engine (output/engine/SCENES_GUIDE.md). Everything drawn with pycairo."""
from core import *  # noqa
import cairo, math, random


def fw(beat): return min(B(beat)["start"], min(w["start"] for w in WORDS if w["beat"] == beat))
def cut(beat): return fw(beat) - 0.25

HZ = 3.0  # 3 GHz shown 1.000.000.000x slower = 3 ticks per second
def clock_ph(t): return HZ * anim_time(t)
def tickn(t): return int(math.floor(clock_ph(t)))

def hsh(*a):
    h = 2166136261
    for v in a:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    h ^= h >> 13; h = (h * 0x5bd1e995) & 0xffffffff; h ^= h >> 15
    return h / 0xffffffff

def pill(c, s, x, y, size, color=CREAM, fill=INK, k=1.0, fam=SLAB, bold=False, edge=WHITE):
    if k <= 0.02: return
    font(c, fam, size, bold); e = c.text_extents(s)
    bw, bh = e.x_advance + 44, size + 30
    c.save(); c.translate(x, y); c.scale(k, k)
    shadow(c, lambda: rrect(c, -bw / 2, -bh / 2, bw, bh, 14), 6, 8, 0.4)
    rrect(c, -bw / 2, -bh / 2, bw, bh, 14); fill_stroke(c, fill, alpha(edge, 0.95), 4)
    text(c, s, 0, size * 0.36, size, color, fam, bold)
    c.restore()

def popk(t, t0, d=0.35): return eob(ramp(t, t0, t0 + d))

# ================================================================ chip die (local coords -380..380)
DIE_BG = hx("#2A2638"); DIE_IN = hx("#3B3552"); MODEM = hx("#7B6FA8"); CLKC = hx("#C9A23A")
DIE_BLOCKS = [
    (-330, -330, 130, 130, ORANGE2, "core"), (-185, -330, 130, 130, ORANGE2, "core"),
    (-330, -185, 130, 130, ORANGE2, "core"), (-185, -185, 130, 130, ORANGE2, "core"),
    (-35, -330, 365, 275, RUST, "gpu"),
    (-330, -35, 390, 175, STEEL, "mem"),
    (80, -35, 250, 175, GOLD, "npu"),
    (-330, 160, 250, 170, MODEM, "modem"),
    (-60, 160, 180, 170, ORANGE, "io"),
    (140, 160, 190, 170, CLKC, "clk"),
]

def _buildings():
    out = []
    for bi, (x, y, w, h, col, kind) in enumerate(DIE_BLOCKS):
        rnd = random.Random(bi * 7 + 1)
        cell = 18 if kind == "mem" else 26
        nx, ny = int((w - 14) // cell), int((h - 14) // cell)
        ox = x + (w - nx * cell) / 2; oy = y + (h - ny * cell) / 2
        for i in range(nx):
            for j in range(ny):
                if kind == "clk" and j < 3: continue
                if kind == "io" and 2 <= j <= 4: continue
                if kind == "mem":
                    out.append((ox + i * cell + 2, oy + j * cell + 2, cell - 4, cell - 4, mix(col, CREAM, 0.22 + 0.1 * ((i + j) % 2))))
                    continue
                if rnd.random() < 0.12: continue
                ww = cell - 4 - rnd.randint(0, 8); hh = cell - 4 - rnd.randint(0, 8)
                shade = mix(col, INK, 0.12 + 0.35 * rnd.random()) if rnd.random() < 0.6 else mix(col, CREAM, 0.12 + 0.25 * rnd.random())
                out.append((ox + i * cell + 2, oy + j * cell + 2, ww, hh, shade))
    return out
BUILD = _buildings()
LIGHTS = []
for bi, (x, y, w, h, col, kind) in enumerate(DIE_BLOCKS):
    rnd = random.Random(bi * 13 + 5)
    for k in range(7 if kind != "mem" else 10):
        LIGHTS.append((bi, x + 14 + rnd.random() * (w - 28), y + 14 + rnd.random() * (h - 28)))
BIT1, BIT0 = (-10, 255), (70, 255)       # the "1" and "0" bit lights in the io block
CLK_C = (235, 205)

def die0(c, n, bits=False, flick=0.0, heat=0.0):
    rrect(c, -380, -380, 760, 760, 30); fill_stroke(c, DIE_BG, INK, 10)
    c.new_path()
    for i in range(13):
        p = -330 + i * 55
        for (x, y) in ((p, -371), (p, 353), (-371, p), (353, p)):
            c.rectangle(x - 1, y, 18, 18) if False else c.rectangle(x, y, 18, 18)
    c.set_source_rgba(*GOLD); c.fill()
    rrect(c, -348, -348, 696, 696, 10); fill_stroke(c, DIE_IN, INK, 5)
    for (x, y, w, h, col, kind) in DIE_BLOCKS:
        rrect(c, x, y, w, h, 6); fill_stroke(c, mix(col, INK, 0.25), INK, 4)
    for (x, y, w, h, col) in BUILD:
        c.rectangle(x, y, w, h); c.set_source_rgba(*col); c.fill()
    # clock glyph
    x, y = 160, 175
    line(c, [(x, y + 40), (x + 25, y + 40), (x + 25, y), (x + 60, y), (x + 60, y + 40), (x + 95, y + 40), (x + 95, y), (x + 130, y), (x + 130, y + 40), (x + 150, y + 40)], CREAM, 7)
    for i, (bi, lx, ly) in enumerate(LIGHTS):
        on = hsh(i, n) > 0.5
        if flick > 0: on = hsh(i, n, 77) > 0.5
        if on:
            col = mix(YEL, HOT, heat)
            c.rectangle(lx - 6, ly - 6, 12, 12); c.set_source_rgba(*col); c.fill()
            glow(c, lx, ly, 26, col, 0.55)
        else:
            c.rectangle(lx - 5, ly - 5, 10, 10); c.set_source_rgba(*alpha(INK, 0.6)); c.fill()
    if bits:
        for (bx, by), v in ((BIT1, 1), (BIT0, 0)):
            if v: glow(c, bx, by, 60, YEL, 0.7)
            rrect(c, bx - 26, by - 26, 52, 52, 8); fill_stroke(c, YEL if v else DARK, INK, 4)
            text(c, str(v), bx, by + 15, 40, INK if v else LAV, SLAB, False)

# ---------------------------------------------------------------- deeper zoom levels
def _cells():
    rnd = random.Random(42); out = []
    for r in range(10):
        y = -380 + r * 76; x = -380
        while x < 380:
            w = rnd.choice([34, 46, 58, 76, 96, 120])
            col = rnd.choice([ORANGE2, mix(ORANGE2, RUST, 0.5), GOLD, mix(ORANGE2, CREAM, 0.25)])
            out.append((x + 3, y + 10, w - 6, 56, col)); x += w
    return out
CELLS = _cells()
WIRES = [(random.Random(i).uniform(-370, 370), random.Random(i + 50).randint(0, 9), random.Random(i + 90).randint(1, 4)) for i in range(26)]

def cells1(c, n, on=False):
    c.set_source_rgba(*DIE_IN); c.paint()
    for (x, y, w, h, col) in CELLS:
        rrect(c, x, y, w, h, 5); fill_stroke(c, col, INK, 3)
    for r in range(11):
        line(c, [(-380, -380 + r * 76 + 3), (380, -380 + r * 76 + 3)], alpha(LAV, 0.85), 7, cairo.LINE_CAP_BUTT)
    for i, (x, r0, ln) in enumerate(WIRES):
        y0 = -380 + r0 * 76 + 20
        line(c, [(x, y0), (x, y0 + ln * 76)], alpha(XRAY, 0.55), 5)
        circle(c, x, y0, 6); c.set_source_rgba(*alpha(XRAY, 0.8)); c.fill()

def array2(c, n, on=False):
    c.set_source_rgba(*hx("#2E2A44")); c.paint()
    for k in range(-5, 6):
        c.rectangle(-380, 76 * k - 13, 760, 26); c.set_source_rgba(*STEEL); c.fill()
    for k in range(-5, 6):
        lit = hsh(k, n, 3) > 0.5
        c.rectangle(76 * k - 13, -380, 26, 760)
        fill_stroke(c, mix(ORANGE2, YEL, 0.8) if lit else ORANGE2, INK, 3)
    for k in range(-5, 5):
        for m in range(-5, 6):
            if (k + m) % 2 == 0:
                c.rectangle(76 * k + 38 - 9, 76 * m - 9, 18, 18); c.set_source_rgba(*GOLD); c.fill()

def tr3(c, n, on=False, labels=0.0):
    c.set_source_rgba(*hx("#2E2A44")); c.paint()
    for gx in (-570, 570):  # neighbouring gates, cut by the frame
        c.rectangle(gx - 130, -380, 260, 760); fill_stroke(c, ORANGE2, INK, 6)
    c.rectangle(-400, -130, 800, 260); fill_stroke(c, STEEL, INK, 6)
    for sx in (-255, 255):
        rrect(c, sx - 75, -90, 150, 180, 14); fill_stroke(c, GOLD, INK, 6)
    if on: glow(c, 0, 0, 260, YEL, 0.6)
    c.rectangle(-130, -380, 260, 760); fill_stroke(c, YEL if on else ORANGE2, INK, 7)
    if on:
        c.rectangle(-130, -130, 260, 260); c.set_source_rgba(1, 1, 1, 0.35); c.fill()
    if labels > 0:
        text(c, "FUENTE", -255, 18, 40, alpha(INK, labels), SANS, True)
        text(c, "DRENADOR", 255, 18, 36, alpha(INK, labels), SANS, True)

LEVELS = [lambda c, n, on: die0(c, n), cells1, array2, tr3]
OFFS = [(-265, -265), (150, 114), (0, 0)]
ZLAB = ["×10", "×1.000", "×100.000", "×1.000.000"]

def zoom_view(c, u, n, on=False):
    if u >= 3:
        LEVELS[3](c, n, on); return
    k = int(u); f = u - k
    z = 10 ** ease(f); e = (z - 1) / 9
    ox, oy = OFFS[k]
    c.save(); c.scale(z, z); c.translate(-ox * e, -oy * e)
    LEVELS[k](c, n, on)
    a = ease(ramp(f, 0.3, 0.85))
    if a > 0:
        c.save(); c.translate(ox, oy); c.scale(0.1, 0.1)
        c.push_group()
        c.save(); rrect(c, -380, -380, 760, 760, 24); c.clip(); LEVELS[k + 1](c, n, on); c.restore()
        rrect(c, -380, -380, 760, 760, 24); fill_stroke(c, None, INK, 14)
        c.pop_group_to_source(); c.paint_with_alpha(a)
        c.restore()
    if a < 1 and f > 0.05:  # little target square on the bit we zoom into
        rrect(c, ox - 40, oy - 40, 80, 80, 6); fill_stroke(c, None, alpha(WHITE, 0.9 * (1 - a)), 3 / z * 2)
    c.restore()

def die_panel(c, cx, cy, s, draw):
    c.save(); c.translate(cx, cy); c.scale(s, s)
    shadow(c, lambda: rrect(c, -380, -380, 760, 760, 30), 14, 18, 0.45)
    c.save(); rrect(c, -380, -380, 760, 760, 30); c.clip(); draw(c); c.restore()
    rrect(c, -380, -380, 760, 760, 30); fill_stroke(c, None, INK, 10)
    c.restore()

# ================================================================ phone (front view)
PX, PY, PW, PH = 540, 1110, 460, 920
SX, SY, SW, SH = PX - PW / 2 + 22, PY - PH / 2 + 22, PW - 44, PH - 44
CHX, CHY, CHS = 540, 990, 150
APPCOL = [ORANGE, YEL, RED, CREAM2, ORANGE2, STEEL, GREEN, RUST, LAV, GOLD, COLD, HOT]

def wallpaper(c, k=1.0):
    g = cairo.LinearGradient(0, SY, 0, SY + SH)
    g.add_color_stop_rgba(0, *hx("#2E2A5C")); g.add_color_stop_rgba(0.62, *hx("#6B3A6B")); g.add_color_stop_rgba(1, *hx("#E27E56"))
    c.set_source(g); c.paint()
    glow(c, PX, SY + SH - 80, 460, YEL, 0.45 * k)
    text(c, "12:00", PX, SY + 140, 84, alpha(WHITE, 0.92), SANS, True)
    text(c, "JUEVES 26", PX, SY + 190, 28, alpha(WHITE, 0.7), SANS, True)

def draw_apps(c, k):
    for r in range(4):
        for q in range(4):
            i = r * 4 + q
            kk = eob(clamp(k * 1.6 - i * 0.04))
            if kk <= 0.02: continue
            x = SX + 60 + q * 99; y = 1150 + r * 112 if r < 3 else 1478
            c.save(); c.translate(x, y); c.scale(kk, kk)
            rrect(c, -36, -36, 72, 72, 18); fill_stroke(c, APPCOL[(i * 5) % len(APPCOL)], INK, 4)
            g = i % 5; c.new_path()
            if g == 0: circle(c, 0, 0, 15); c.set_source_rgba(*alpha(INK, 0.8)); c.set_line_width(6); c.stroke()
            elif g == 1: c.move_to(-9, -14); c.line_to(14, 0); c.line_to(-9, 14); c.close_path(); c.set_source_rgba(*alpha(INK, 0.8)); c.fill()
            elif g == 2: rrect(c, -16, -10, 32, 22, 5); c.set_source_rgba(*alpha(INK, 0.8)); c.fill()
            elif g == 3:
                for j in range(3): rrect(c, -15 + j * 11, 6 - j * 8, 8, 10 + j * 8, 2)
                c.set_source_rgba(*alpha(INK, 0.8)); c.fill()
            else: circle(c, 0, 0, 7); c.set_source_rgba(*alpha(WHITE, 0.9)); c.fill()
            c.restore()

def xray_chip(c, n, a, heat=0.0, flash=0.0):
    if a <= 0.01: return
    c.push_group()
    glow(c, CHX, CHY, 190, mix(XRAY, HOT, heat), 0.45)
    rrect(c, CHX - 100, CHY - 100, 200, 200, 22); c.set_source_rgba(*alpha(NIGHT, 0.75)); c.fill()
    for i in range(10):
        line(c, [(CHX - 96, CHY - 90 + i * 20), (CHX + 96, CHY - 90 + i * 20)], alpha(XRAY, 0.10), 2)
    c.new_path()
    for i in range(7):  # pins
        p = -60 + i * 20
        for (x, y, w, h) in ((p - 4, -94, 8, 14), (p - 4, 80, 8, 14), (-94, p - 4, 14, 8), (80, p - 4, 14, 8)):
            c.rectangle(CHX + x, CHY + y, w, h)
    c.set_source_rgba(*alpha(XRAY, 0.85)); c.fill()
    c.save(); c.translate(CHX, CHY); c.scale(CHS / 760, CHS / 760); die0(c, n, heat=heat); c.restore()
    if flash > 0:
        rrect(c, CHX - 75, CHY - 75, 150, 150, 6); c.set_source_rgba(1, 1, 1, 0.7 * flash); c.fill()
    rrect(c, CHX - 100, CHY - 100, 200, 200, 22); fill_stroke(c, None, alpha(XRAY, 0.9), 4)
    c.pop_group_to_source(); c.paint_with_alpha(a)

def phone(c, t, n, xray=0.85, apps=0.0, wall=1.0, dim=0.0, heat=0.0, content=None, chipflash=0.0, sparks=None):
    shadow(c, lambda: rrect(c, PX - PW / 2, PY - PH / 2, PW, PH, 64), 16, 22, 0.45)
    for (x, y, w, h) in ((PX + PW / 2 - 6, 860, 16, 100), (PX + PW / 2 - 6, 990, 16, 64), (PX - PW / 2 - 10, 880, 16, 80)):
        rrect(c, x, y, w, h, 6); fill_stroke(c, GOLD, INK, 4)
    rrect(c, PX - PW / 2, PY - PH / 2, PW, PH, 64); fill_stroke(c, RUST, INK, 8)
    rrect(c, PX - PW / 2 + 14, PY - PH / 2 + 14, PW - 28, 18, 9); c.set_source_rgba(1, 1, 1, 0.14); c.fill()
    rrect(c, PX - PW / 2 + 12, PY - PH / 2 + 12, PW - 24, PH - 24, 54); fill_stroke(c, INK, None)
    c.save(); rrect(c, SX, SY, SW, SH, 44); c.clip()
    if content: content(c)
    else: wallpaper(c, wall)
    if apps > 0: draw_apps(c, apps)
    if dim > 0: c.set_source_rgba(*alpha(NIGHT, dim)); c.paint()
    if heat > 0:
        r = 170 + 420 * heat
        g = cairo.RadialGradient(CHX, CHY, 20, CHX, CHY, r)
        g.add_color_stop_rgba(0, *alpha(mix(ORANGE, HOT, heat), 0.85 * min(1, heat * 2)))
        g.add_color_stop_rgba(0.45, *alpha(mix(COLD, ORANGE, heat), 0.55 * min(1, heat * 2)))
        g.add_color_stop_rgba(1, *alpha(COLD, 0.0))
        c.set_source(g); c.paint()
        if heat > 0.05: c.set_source_rgba(*alpha(COLD, 0.25 * (1 - heat) * min(1, heat * 6))); c.paint()
    xray_chip(c, n, xray, heat, chipflash)
    if sparks: sparks(c)
    c.move_to(SX + 30, SY + 30); c.line_to(SX + 150, SY + 30); c.line_to(SX + 30, SY + 260); c.close_path()
    c.set_source_rgba(1, 1, 1, 0.06); c.fill()
    c.restore()
    rrect(c, PX - 60, SY + 16, 120, 30, 15); fill_stroke(c, INK, None)
    circle(c, PX + 38, SY + 31, 7); c.set_source_rgba(*alpha(STEEL, 0.8)); c.fill()

# ---------------------------------------------------------------- icons
def ic_gear(c):
    c.new_path(); n = 9; w = math.pi / n
    for i in range(n):
        a = 2 * math.pi * i / n
        for (aa, r) in ((a - w * 0.95, 44), (a - w * 0.5, 62), (a + w * 0.5, 62), (a + w * 0.95, 44)):
            c.line_to(r * math.cos(aa), r * math.sin(aa))
    c.close_path(); fill_stroke(c, ORANGE2, INK, 5)
    circle(c, 0, 0, 18); fill_stroke(c, CREAM, INK, 5)

def ic_spring(c):
    pts = [(0, -54)] + [((-30 if i % 2 else 30), -44 + i * 10) for i in range(10)] + [(0, 52)]
    line(c, pts, STEEL, 9)
    for y in (-66, 54):
        rrect(c, -40, y, 80, 14, 5); fill_stroke(c, METAL, INK, 4)
    for s in (-1, 1):
        line(c, [(s * 56, -30), (s * 56, 30)], alpha(INK, 0.7), 5)

def ic_bubble(c):
    c.new_path(); c.move_to(-26, 22); c.line_to(-44, 62); c.line_to(6, 26); c.close_path(); fill_stroke(c, WHITE, INK, 5)
    rrect(c, -64, -50, 128, 84, 24); fill_stroke(c, WHITE, INK, 5)
    c.move_to(-26, 18); c.line_to(4, 18); c.set_source_rgba(*WHITE); c.set_line_width(10); c.stroke()
    text(c, "ABC", 0, 4, 38, INK, SLAB, False)

def switch_icon(c, on, s=1.0, glowk=1.0):
    c.save(); c.scale(s, s)
    if on and glowk > 0: glow(c, 0, -20, 90, YEL, 0.6 * glowk)
    rrect(c, -52, -76, 104, 152, 16); fill_stroke(c, CREAM2, INK, 6)
    rrect(c, -24, -50, 48, 100, 12); fill_stroke(c, INK, None)
    ky = -46 if on else 6
    rrect(c, -19, ky, 38, 40, 9); fill_stroke(c, YEL if on else METAL, INK, 4)
    text(c, "ON", 0, -56, 17, RED if on else alpha(INK, 0.5), SANS, True)
    text(c, "OFF", 0, 70, 17, alpha(INK, 0.5) if on else RED, SANS, True)
    c.restore()

def ic_switch_fn(on):
    return lambda c: switch_icon(c, on, 0.8)

def spark(c, x, y, s, a=1.0, col=YEL):
    if s <= 0.5 or a <= 0.02: return
    glow(c, x, y, s * 2.2, col, 0.5 * a)
    c.new_path()
    for i in range(4):
        ang = i * math.pi / 2
        c.move_to(x + math.cos(ang) * s, y + math.sin(ang) * s)
        c.line_to(x + math.cos(ang + math.pi / 4) * s * 0.28, y + math.sin(ang + math.pi / 4) * s * 0.28)
        c.line_to(x + math.cos(ang + math.pi / 2) * s, y + math.sin(ang + math.pi / 2) * s)
    c.close_path(); c.set_source_rgba(*alpha(WHITE, a)); c.fill_preserve(); c.set_source_rgba(*alpha(col, a)); c.set_line_width(3); c.stroke()

def thermo(c, x, y0, y1, lv, k=1.0):
    if k <= 0.02: return
    c.save(); c.translate(x, y1); c.scale(k, k); c.translate(-x, -y1)
    col = mix(COLD, HOT, lv)
    rrect(c, x - 28, y0, 56, y1 - y0, 28); fill_stroke(c, CREAM, INK, 6)
    for i in range(6): line(c, [(x + 6, y0 + 50 + i * (y1 - y0 - 90) / 5), (x + 22, y0 + 50 + i * (y1 - y0 - 90) / 5)], alpha(INK, 0.5), 3)
    circle(c, x, y1 + 22, 48); fill_stroke(c, col, INK, 6)
    top = lerp(y1 - 30, y0 + 34, lv)
    rrect(c, x - 13, top, 26, y1 - top + 20, 13); c.set_source_rgba(*col); c.fill()
    c.restore()

# ================================================================ scene: front (gancho + imposible + freno)
BADGES = [("engranajes", "ENGRANAJES", ic_gear, 250), ("mueva", "PIEZAS MÓVILES", ic_spring, 540), ("palabra", "PALABRAS", ic_bubble, 830)]

def scene_front(c, t):
    background(c, t, YEL)
    t_up = wt("imposible", "engranajes") - 0.45
    up = ease(ramp(t, t_up, t_up + 0.5))
    push = 1.0 + 0.04 * ease(ramp(t, 0, t_up))
    sp = push * lerp(1, 0.74, up); pyc = lerp(PY, 1000, up)
    t_z0 = wt("freno", "vamos") + 0.1
    ze = ease(ramp(t, t_z0, T_SLOW + 0.1))
    n = int(t * 7) if t < t_z0 else int(t_z0 * 7)
    t_app = wt("imposible", "pantalla") - 0.1
    apps = ramp(t, t_app, t_app + 0.6) * (1 - ze)
    xr = lerp(0.85, 1.0, ze)
    # gancho side gags
    gk = 1 - ease(ramp(t, t_up - 0.4, t_up))
    t_sw = wt("gancho", "enciende")
    fl = 0.0
    if t >= t_sw: fl = 0.35 * min(1, (t - t_sw) / 2)
    c.save()
    chs = (540, pyc + sp * (CHY - PY))
    Z = (760 / (sp * CHS)) ** ze
    c.translate(lerp(chs[0], 540, ze), lerp(chs[1], 1130, ze)); c.scale(Z, Z); c.translate(-chs[0], -chs[1])
    c.translate(540, pyc); c.scale(sp, sp); c.translate(-PX, PY * 0 - PY)
    phone(c, t, n, xray=xr, apps=apps)
    if t >= t_sw and gk > 0 and ze <= 0:  # the chip's lights flickering hard: on/off
        glow(c, CHX, CHY, 150, YEL, 0.25 * gk * (0.5 + 0.5 * math.sin(t * 40)))
    c.restore()
    kd = ease(ramp(t, T_SLOW - 0.6, T_SLOW + 0.1))
    if kd > 0:
        c.push_group(); die_panel(c, 540, 1130, 1.0, lambda c: die0(c, n)); c.pop_group_to_source(); c.paint_with_alpha(kd)
    if gk > 0 and ze <= 0:
        callout(c, "CHIP", 540 + 75 * push, PY + (CHY - PY) * push - 60 * push, 860, 760, t, wt("gancho", "chip"), YEL)
        # "no piensa": thought cloud crossed out
        k = popk(t, wt("gancho", "no") - 0.1) * gk
        if k > 0.02:
            c.save(); c.translate(175, 840); c.scale(k, k)
            for (bx, by, r) in ((-40, 10, 50), (10, -20, 60), (55, 15, 46), (5, 35, 50)):
                circle(c, bx, by, r); fill_stroke(c, CREAM, INK, 6)
            for (bx, by, r) in ((-40, 10, 44), (10, -20, 54), (55, 15, 40), (5, 35, 44)):
                circle(c, bx, by, r); fill_stroke(c, CREAM, None)
            for (bx, by, r) in ((-50, 95, 14), (-70, 125, 9)):
                circle(c, bx, by, r); fill_stroke(c, CREAM, INK, 4)
            text(c, "?", 8, 40, 92, INK, SLAB, False)
            c.restore()
            xmark(c, 180, 840, 62 * k, t, wt("gancho", "piensa") + 0.05, 14)
        # on/off switch flipping, faster and faster
        k = popk(t, t_sw - 0.1) * gk
        if k > 0.02:
            ph = 0.0 if t < t_sw else (t - t_sw) * (2.2 + 5 * ramp(t, wt("gancho", "tres"), wt("gancho", "segundo")))
            on = int(ph * 2) % 2 == 0 if t < wt("gancho", "tres") else hsh(int(t * 30)) > 0.5
            c.save(); c.translate(175, 1400); c.scale(k, k); switch_icon(c, on, 1.05); c.restore()
    # imposible badges
    if up > 0.01:
        ia = up * (1 - ze)
        for w, lab, fn, x in BADGES:
            t0 = wt("imposible", w) - 0.15
            k = eob(ramp(t, t0, t0 + 0.3)) * ia
            icon_badge(c, x, 1480, k, lab, fn, t, t0 + 0.35)

# ================================================================ scene: paso1 (die -> transistor)
def scene_paso1(c, t):
    background(c, t, ORANGE)
    b0 = fw("paso1")
    tz0 = wt("paso1", "transistores") + 0.15
    t_int = wt("paso1", "interruptor")
    tz1 = t_int - 0.2
    u = 0.0 if t < tz0 else min(3.0, 3 * (t - tz0) / (tz1 - tz0))
    ks = ease(ramp(t, t_int - 0.05, t_int + 0.45))
    push = 1 + 0.03 * ease(ramp(t, b0, tz0))
    cx, cy, s = lerp(540, 320, ks), lerp(1130, 1050, ks), lerp(push, 0.52, ks)
    n = tickn(t)
    on = False
    if t >= t_int: on = int((t - t_int) / 0.7) % 2 == 0
    lab = ease(ramp(t, t_int + 0.2, t_int + 0.6))
    die_panel(c, cx, cy, s, lambda c: tr3(c, n, on, lab) if u >= 3 else zoom_view(c, u, n, on))
    # ruler: about 1 cm
    kr = ease(ramp(t, wt("paso1", "chip") - 0.1, wt("paso1", "chip") + 0.3)) * (1 - ease(ramp(t, tz0 - 0.2, tz0 + 0.1)))
    if kr > 0:
        x0, x1, y = 540 - 380 * push, 540 + 380 * push, 1560
        line(c, [(x0, y), (lerp(x0, x1, kr), y)], CREAM, 6)
        line(c, [(x0, y - 18), (x0, y + 18)], CREAM, 6); line(c, [(x1, y - 18), (x1, y + 18)], alpha(CREAM, kr), 6)
        text(c, "≈ 1 cm", 540, y + 70, 48, alpha(CREAM, kr), SLAB, False, outline=INK, olw=8)
    # zoom level pill
    kz = ease(ramp(t, tz0 - 0.2, tz0 + 0.1)) * (1 - ks)
    if kz > 0:
        idx = min(3, int(u + 0.55))
        pill(c, "ZOOM " + ZLAB[idx], 540, 1600, 44, YEL, INK, kz)
    # >10.000 millones
    t10 = wt("paso1", "diez") - 0.1
    k = popk(t, t10) * (1 - ease(ramp(t, t_int - 0.3, t_int)))
    if k > 0.02:
        c.save(); c.translate(540, 680); c.scale(k, k)
        text(c, "> 10.000 MILLONES", 0, 22, 66, YEL, SLAB, False, outline=INK, olw=12)
        c.restore()
    if ks > 0:
        text(c, "=", 575, 1080, 90, alpha(CREAM, ks), SLAB, False, outline=INK, olw=10)
        text(c, "TRANSISTOR", 320, 1340, 40, alpha(CREAM, ks), SLAB, False, outline=INK, olw=8)
    kk = popk(t, t_int)
    if kk > 0.02:
        icon_badge(c, 790, 1050, kk, "", lambda c: switch_icon(c, on, 0.85), t, None, 120)
        text(c, "INTERRUPTOR", 790, 1340, 40, alpha(YEL, clamp(kk)), SLAB, False, outline=INK, olw=8)
    t_sin = wt("paso1", "sin")
    k = popk(t, t_sin)
    if k > 0.02:
        pill(c, "NINGUNA PIEZA SE MUEVE", 540, 1520, 42, CREAM, INK, k)
        xg = 540
    # tiny gear crossed next to it
    if k > 0.3:
        c.save(); c.translate(540, 1640); c.scale(0.55 * k, 0.55 * k); ic_gear(c); c.restore()
        xmark(c, 540, 1640, 40 * k, t, t_sin + 0.3, 10)

# ================================================================ scene: paso2 (cross-section)
SUBY = 1120
DOTS_PATH = [(300, 800), (300, 1136), (780, 1136), (780, 826)]
def path_pt(pts, s):
    for a, b in zip(pts, pts[1:]):
        l = math.dist(a, b)
        if s <= l: return (a[0] + (b[0] - a[0]) * s / l, a[1] + (b[1] - a[1]) * s / l)
        s -= l
    return pts[-1]
PATH_L = sum(math.dist(a, b) for a, b in zip(DOTS_PATH, DOTS_PATH[1:]))
S_CH = math.dist(DOTS_PATH[0], DOTS_PATH[1]) + 120   # start of the channel

def bulb(c, x, y, on, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    if on > 0: glow(c, 0, -6, 150, YEL, 0.8 * on)
    circle(c, 0, -10, 40); fill_stroke(c, mix(alpha(CREAM2, 1), YEL, on), INK, 6)
    rrect(c, -20, 26, 40, 26, 5); fill_stroke(c, METAL, INK, 5)
    line(c, [(-12, 0), (-4, -16), (4, 0), (12, -16)], alpha(ORANGE2 if on else INK, 0.9), 4)
    c.restore()

def scene_paso2(c, t):
    background(c, t, STEEL)
    b0 = fw("paso2")
    c.save(); cam(c, 1.0 + 0.04 * ease(ramp(t, b0, B("paso2")["end"])), 540, 1150)
    t_tr = wt("paso2", "transistor"); t_pu = wt("paso2", "puerta"); t_el = wt("paso2", "electricidad")
    t_pa = wt("paso2", "deja"); t_co = wt("paso2", "corriente"); t_en = wt("paso2", "encendido"); t_uno = wt("paso2", "uno")
    t_si2 = wt("paso2", "si", 1); t_ap = wt("paso2", "apagado"); t_cero = wt("paso2", "cero")
    t_off = t_si2 + 0.3
    k0 = popk(t, b0 - 0.1, 0.45)
    gv = ease(ramp(t, t_el + 0.35, t_el + 0.6)) * (1 - ease(ramp(t, t_off, t_off + 0.25)))
    chan = ease(ramp(t, t_pa - 0.1, t_pa + 0.4)) * (1 - ease(ramp(t, t_off + 0.2, t_off + 0.6)))
    def flow_at(x): return ease(ramp(x, t_co - 0.1, t_co + 0.3)) * (1 - ease(ramp(x, t_off + 0.2, t_off + 0.5)))
    flow = flow_at(t)
    c.save(); c.translate(540, 1260); c.scale(k0, k0); c.translate(-540, -1260)
    # wires
    for pts in ([(300, 1120), (300, 800)], [(780, 1120), (780, 826)], [(540, 985), (540, 820)]):
        line(c, pts, INK, 16); line(c, pts, METAL, 8)
    circle(c, 300, 790, 22); fill_stroke(c, GOLD, INK, 5)
    # substrate + regions
    shadow(c, lambda: rrect(c, 150, SUBY, 780, 290, 18), 12, 16, 0.45)
    rrect(c, 150, SUBY, 780, 290, 18); fill_stroke(c, hx("#6E5F8F"), INK, 7)
    text(c, "SILICIO", 540, SUBY + 260, 30, alpha(CREAM, 0.55), SANS, True)
    for x in (190, 660):
        rrect(c, x, SUBY, 230, 115, 14); fill_stroke(c, ORANGE2, INK, 5)
    kl = ease(ramp(t, t_tr, t_tr + 0.4))
    text(c, "FUENTE", 305, SUBY + 80, 34, alpha(INK, kl), SANS, True)
    text(c, "DRENADOR", 775, SUBY + 80, 34, alpha(INK, kl), SANS, True)
    if chan > 0:
        glow(c, 540, SUBY + 16, 200, YEL, 0.5 * chan)
        c.rectangle(420, SUBY + 2, 240, 30); c.set_source_rgba(*alpha(YEL, 0.95 * chan)); c.fill()
    c.rectangle(400, SUBY - 20, 280, 20); fill_stroke(c, CREAM2, INK, 4)
    pk = pulse_at(t, t_pu - 0.1, 0.6)
    gcol = mix(METAL, YEL, gv)
    if gv > 0: glow(c, 540, 1040, 230, YEL, 0.5 * gv)
    c.save(); c.translate(540, 1040); c.scale(1 + 0.08 * pk, 1 + 0.08 * pk)
    rrect(c, -130, -55, 260, 115, 12); fill_stroke(c, gcol, INK, 7)
    kp = ease(ramp(t, t_pu - 0.1, t_pu + 0.2))
    text(c, "PUERTA", 0, 18, 46, alpha(INK, kp), SLAB, False)
    c.restore()
    # gate input: electricity badge
    ke = ease(ramp(t, t_el - 0.1, t_el + 0.2)) * (1 - ease(ramp(t, t_off - 0.1, t_off + 0.1)))
    circle(c, 540, 770, 52); fill_stroke(c, mix(DARK, YEL, ke), INK, 6)
    c.new_path(); c.move_to(552, 728); c.line_to(522, 776); c.line_to(542, 776); c.line_to(528, 812); c.line_to(560, 760); c.line_to(540, 760); c.close_path()
    fill_stroke(c, mix(LAV, WHITE, ke), INK, 4)
    if t_el <= t <= t_el + 0.45:
        y = lerp(822, 985, ramp(t, t_el, t_el + 0.4)); glow(c, 540, y, 70, YEL, 0.9); circle(c, 540, y, 12); c.set_source_rgba(1, 1, 1, 1); c.fill()
    # electrons
    if t > t_co - 0.2:
        off = 0.0; x = t_co - 0.2
        while x < t: off += 190 * flow_at(x) * 0.03; x += 0.03
    else: off = 0.0
    gone = ease(ramp(t, t_off + 0.4, t_off + 0.8))
    for i in range(int(PATH_L // 46) + 1):
        s = (off + i * 46) % PATH_L
        if s > S_CH and (t < t_co - 0.1 or gone > 0):
            a = (1 - gone) if t >= t_co else 0.0
        else: a = 1.0
        if s < 12: a *= s / 12
        if a <= 0.02: continue
        x, y = path_pt(DOTS_PATH, s)
        circle(c, x, y, 11); fill_stroke(c, alpha(CREAM, a), alpha(INK, a), 3)
    bulb(c, 780, 780, flow)
    c.restore()
    c.restore()
    callout(c, "CORRIENTE", 780, 990, 655, 900, t, t_co + 0.2, YEL, 30)
    # state labels + big digit
    k1 = popk(t, t_en) * (1 - ease(ramp(t, t_off, t_off + 0.3)))
    if k1 > 0.02:
        c.save(); c.translate(540, 1480); c.scale(k1, k1); text(c, "ENCENDIDO", 0, 16, 46, YEL, SLAB, False, outline=INK, olw=8); c.restore()
    kd1 = popk(t, t_uno - 0.05, 0.4) * (1 - ease(ramp(t, t_off, t_off + 0.3)))
    if kd1 > 0.02:
        c.save(); c.translate(540, 1600); c.scale(kd1, kd1)
        glow(c, 0, 0, 140, YEL, 0.5)
        text(c, "1", 0, 62, 170, YEL, SLAB, False, outline=INK, olw=14); c.restore()
    k0_ = popk(t, t_ap)
    if k0_ > 0.02:
        c.save(); c.translate(540, 1480); c.scale(k0_, k0_); text(c, "APAGADO", 0, 16, 46, LAV, SLAB, False, outline=INK, olw=8); c.restore()
    kd0 = popk(t, t_cero - 0.05, 0.4)
    if kd0 > 0.02:
        c.save(); c.translate(540, 1600); c.scale(kd0, kd0)
        text(c, "0", 0, 62, 170, LAV, SLAB, False, outline=INK, olw=14); c.restore()

# ================================================================ scene: paso3 (AND rule)
XA, XB, YW = 360, 620, 900
ROWS = [(0, 0), (0, 1), (1, 0), (1, 1)]

def mini_tr(c, x, val, lab, k):
    if k <= 0.02: return
    c.save(); c.translate(x, YW); c.scale(k, k); c.translate(-x, -YW)
    line(c, [(x, YW - 70), (x, YW - 150)], INK, 12); line(c, [(x, YW - 70), (x, YW - 150)], mix(METAL, YEL, val), 6)
    rrect(c, x - 100, YW - 30, 200, 84, 10); fill_stroke(c, hx("#6E5F8F"), INK, 5)
    for sx in (x - 100, x + 34):
        rrect(c, sx, YW - 30, 66, 50, 8); fill_stroke(c, ORANGE2, INK, 4)
    if val:
        c.rectangle(x - 34, YW - 28, 68, 16); c.set_source_rgba(*YEL); c.fill()
    c.rectangle(x - 40, YW - 38, 80, 8); fill_stroke(c, CREAM2, INK, 3)
    if val: glow(c, x, YW - 55, 80, YEL, 0.5)
    rrect(c, x - 38, YW - 76, 76, 40, 6); fill_stroke(c, YEL if val else METAL, INK, 4)
    if val: glow(c, x, YW - 190, 70, YEL, 0.6)
    circle(c, x, YW - 190, 40); fill_stroke(c, YEL if val else DARK, INK, 5)
    text(c, str(val), x, YW - 174, 46, INK if val else LAV, SLAB, False)
    text(c, lab, x - 78, YW - 172, 48, CREAM, SLAB, False, outline=INK, olw=8)
    c.restore()

def scene_paso3(c, t):
    background(c, t, GOLD)
    b0 = fw("paso3")
    t_tr = wt("paso3", "transistores"); t_re = wt("paso3", "reglas"); t_dos = wt("paso3", "dos"); t_sale = wt("paso3", "sale")
    t_con = wt("paso3", "con"); t_su = wt("paso3", "suma"); t_cm = wt("paso3", "compara"); t_de = wt("paso3", "decide")
    rev = [t_re + 0.25, t_re + 0.7, t_re + 1.15, t_dos - 0.05]
    st = 0
    for i, r in enumerate(rev):
        if t >= r: st = i
    if t >= t_con: st = int((t - t_con) / 0.55) % 4
    a, b = ROWS[st]
    out = a & b
    c.save(); cam(c, 1.0 + 0.03 * ease(ramp(t, b0, B("paso3")["end"])), 540, 1100)
    kc = ease(ramp(t, b0, b0 + 0.4))
    # wire + supply + bulb
    if kc > 0:
        x1 = lerp(170, 830, kc)
        line(c, [(170, YW + 8), (x1, YW + 8)], INK, 14); line(c, [(170, YW + 8), (x1, YW + 8)], METAL, 6)
        circle(c, 150, YW + 8, 34); fill_stroke(c, GOLD, INK, 5)
        text(c, "+", 150, YW + 26, 48, INK, SLAB, False)
    mini_tr(c, XA, a, "A", popk(t, t_tr - 0.15))
    mini_tr(c, XB, b, "B", popk(t, t_tr + 0.1))
    if kc > 0.5:
        # electrons: blocked at the first closed channel
        block = 1e9
        if not a: block = XA - 36
        elif not b: block = XB - 36
        flowing = a and b
        off = (t * 160) % 44 if flowing else 0
        x = 180 + off
        while x < 830:
            if x < block: circle(c, x, YW + 8, 9); fill_stroke(c, CREAM, INK, 3)
            x += 44
        bulb(c, 870, YW + 40, 1.0 if out else 0.0, 0.9)
        line(c, [(870, YW - 20), (870, YW - 150)], alpha(WHITE, 0.6), 3)
        circle(c, 870, YW - 190, 40); fill_stroke(c, YEL if out else DARK, INK, 5)
        text(c, str(out), 870, YW - 174, 46, INK if out else LAV, SLAB, False)
        text(c, "SALIDA", 870, YW - 250, 28, CREAM, SANS, True)
    c.restore()
    # rule label + truth table
    kr = popk(t, t_re - 0.05)
    pill(c, "REGLA «Y»", 540, 1040, 38, YEL, INK, kr)
    kt = ease(ramp(t, t_re, t_re + 0.3))
    if kt > 0:
        X0, X1, Y0, RH = 250, 830, 1110, 64
        cols = [(345, "A"), (500, "B"), (690, "SALIDA")]
        c.save(); c.translate(540, Y0); c.scale(kt, kt); c.translate(-540, -Y0)
        nrow = sum(1 for r in rev if t >= r)
        hgt = 66 + RH * nrow
        shadow(c, lambda: rrect(c, X0, Y0, X1 - X0, hgt, 14), 8, 10, 0.4)
        rrect(c, X0, Y0, X1 - X0, hgt, 14); fill_stroke(c, CREAM, INK, 6)
        for x, h in cols: text(c, h, x, Y0 + 46, 34, RED, SLAB, False)
        line(c, [(X0, Y0 + 66), (X1, Y0 + 66)], INK, 4)
        line(c, [(580, Y0 + 8), (580, Y0 + hgt - 8)], alpha(INK, 0.4), 3)
        for i, (ra, rb) in enumerate(ROWS):
            kk = ease(ramp(t, rev[i], rev[i] + 0.25))
            if kk <= 0: continue
            y = Y0 + 66 + i * RH
            if i == st:
                rrect(c, X0 + 8, y + 5, X1 - X0 - 16, RH - 10, 10); c.set_source_rgba(*alpha(YEL, 0.55 * kk)); c.fill()
            for (x, _), v in zip(cols, (ra, rb, ra & rb)):
                text(c, str(v), x, y + 46, 42, alpha(INK, kk), MONO, True)
        # "sale un uno": output of the last row
        ko = pulse_at(t, t_sale, 0.8)
        if t >= t_sale - 0.05 and nrow == 4:
            y = Y0 + 66 + 3 * RH
            circle(c, 690, y + 32, 30 + 6 * ko); fill_stroke(c, None, RED, 6)
        c.restore()
    k = popk(t, t_sale) * (1 - ease(ramp(t, t_con - 0.2, t_con + 0.1)))
    if k > 0.02:
        c.save(); c.translate(540, 1560); c.scale(k, k)
        text(c, "1 Y 1 → 1", 0, 24, 76, YEL, SLAB, False, outline=INK, olw=12); c.restore()
    # suma / compara / decide
    def ic_plus(c):
        line(c, [(-45, 0), (45, 0)], RED, 22); line(c, [(0, -45), (0, 45)], RED, 22)
    def ic_cmp(c):
        line(c, [(-55, -20), (55, -20)], INK, 8); line(c, [(0, -50), (0, 50)], INK, 8)
        for s in (-1, 1):
            c.new_path(); c.arc(s * 40, 0, 22, 0, math.pi); c.set_source_rgba(*(STEEL if s < 0 else ORANGE2)); c.fill()
            line(c, [(s * 55, -20), (s * 40, 0)], INK, 4); line(c, [(s * 25, -20), (s * 40, 0)], INK, 4)
        rrect(c, -30, 46, 60, 12, 4); fill_stroke(c, INK, None)
    def ic_fork(c):
        line(c, [(0, 55), (0, 5)], INK, 12)
        arrow(c, 0, 8, -42, -42, GREEN, 12, 34); arrow(c, 0, 8, 42, -42, RED, 12, 34)
    for (w, tw, fn, x) in (("SUMA", t_su, ic_plus, 270), ("COMPARA", t_cm, ic_cmp, 540), ("DECIDE", t_de, ic_fork, 810)):
        kk = popk(t, tw - 0.1)
        if kk > 0.02:
            c.save(); c.translate(x, 1550); c.scale(kk * 0.66, kk * 0.66)
            circle(c, 0, 0, 105); fill_stroke(c, CREAM, INK, 8); fn(c); c.restore()
            text(c, w, x, 1665, 32, alpha(CREAM, clamp(kk)), SANS, True)

# ================================================================ scene: paso4 (clock)
GX, GY, GNX, GNY, GSP = 540, 1270, 12, 8, 64
def sq(ph): return 1 if (ph % 1.0) < 0.5 else 0

def clock_strip(c, t, ph, k=1.0, x0=130, x1=900, yh=700, yl=820, P=170):
    pts = []; xp = x1
    phx = lambda x: ph - (x1 - x) / P
    x = x0; pts.append((x, yh if sq(phx(x)) else yl))
    # walk edges
    e = math.floor(phx(x0) * 2) / 2 + 0.5
    while True:
        xe = x1 - (ph - e) * P
        if xe >= x1: break
        v_before = sq(e - 0.01); v_after = sq(e + 0.01)
        pts.append((xe, yh if v_before else yl)); pts.append((xe, yh if v_after else yl))
        e += 0.5
    pts.append((x1, yh if sq(ph) else yl))
    line(c, pts, alpha(YEL, k), 9)
    # rising edges = ticks
    e = math.ceil(phx(x0))
    while e <= ph:
        xe = x1 - (ph - e) * P
        circle(c, xe, yh, 7); c.set_source_rgba(*alpha(WHITE, 0.8 * k)); c.fill()
        e += 1

def scene_paso4(c, t):
    background(c, t, STEEL)
    b0 = fw("paso4")
    t_re = wt("paso4", "reloj"); t_tic = wt("paso4", "tic"); t_int = wt("paso4", "interruptores"); t_vez = wt("paso4", "vez")
    t_tres = wt("paso4", "tres")
    ph = clock_ph(t)
    c.save(); cam(c, 1.0 + 0.03 * ease(ramp(t, b0, B("paso4")["end"])), 540, 1150)
    kc = popk(t, b0 - 0.1, 0.4)
    c.save(); c.translate(540, 760); c.scale(kc, kc); c.translate(-540, -760)
    shadow(c, lambda: rrect(c, 110, 650, 860, 220, 18), 10, 14, 0.45)
    rrect(c, 110, 650, 860, 220, 18); fill_stroke(c, hx("#14201A"), INK, 7)
    for i in range(1, 9): line(c, [(110 + i * 96, 660), (110 + i * 96, 860)], alpha(GREEN, 0.15), 2)
    line(c, [(120, 760), (960, 760)], alpha(GREEN, 0.15), 2)
    c.save(); rrect(c, 110, 650, 860, 220, 18); c.clip()
    clock_strip(c, t, ph, 1.0, 120, 900)
    pulse = math.exp(-(ph % 1.0) * 9)
    line(c, [(900, 668), (900, 852)], alpha(WHITE, 0.4 + 0.5 * pulse), 4)
    glow(c, 900, 700, 60, YEL, 0.8 * pulse)
    c.restore()
    c.restore()
    k = popk(t, t_re - 0.05)
    if k > 0.02: pill(c, "RELOJ INTERNO", 290, 650, 30, YEL, INK, k, SANS, True)
    # switch field
    kg = popk(t, b0 + 0.25, 0.45)
    flipping = t >= t_tic - 0.05
    nn = tickn(t) if flipping else tickn(t_tic - 0.05)
    fr = (ph % 1.0) if flipping else 1.0
    c.save(); c.translate(GX, GY); c.scale(kg, kg); c.translate(-GX, -GY)
    w, h = GNX * GSP + 40, GNY * GSP + 40
    shadow(c, lambda: rrect(c, GX - w / 2, GY - h / 2, w, h, 20), 12, 16, 0.45)
    rrect(c, GX - w / 2, GY - h / 2, w, h, 20); fill_stroke(c, DIE_IN, INK, 7)
    for i in range(GNX):
        for j in range(GNY):
            x = GX + (i - (GNX - 1) / 2) * GSP; y = GY + (j - (GNY - 1) / 2) * GSP
            on = hsh(i, j, nn) > 0.5
            was = hsh(i, j, nn - 1) > 0.5
            if on: glow(c, x, y, 44, YEL, 0.4)
            rrect(c, x - 23, y - 23, 46, 46, 9); fill_stroke(c, YEL if on else DARK, INK, 4)
            if flipping and on != was and fr < 0.35:
                rrect(c, x - 27, y - 27, 54, 54, 11); fill_stroke(c, None, alpha(WHITE, 1 - fr / 0.35), 4)
    c.restore()
    c.restore()
    k = popk(t, t_int - 0.05)
    if k > 0.02: pill(c, "INTERRUPTORES", 330, GY - (GNY * GSP + 40) / 2, 30, CREAM, INK, k, SANS, True)
    # TIC pops on each rising edge (first one on the word)
    if t >= t_tic - 0.05 and t < t_tres - 0.3:
        kk = eob(ramp(fr, 0, 0.18)) * (1 - ease(ramp(fr, 0.55, 0.9)))
        big = 1.0 + 0.5 * (1 - ramp(t, t_tic, t_tic + 0.4))
        if kk > 0.02:
            c.save(); c.translate(800, 915); c.scale(kk * big, kk * big)
            text(c, "¡TIC!", 0, 22, 66, YEL, SLAB, False, outline=INK, olw=10); c.restore()
    k = popk(t, t_vez - 0.1) * (1 - ease(ramp(t, t_tres - 0.5, t_tres - 0.2)))
    if k > 0.02: pill(c, "TODOS A LA VEZ", 540, 1620, 44, YEL, INK, k)
    k = popk(t, t_tres - 0.1)
    if k > 0.02:
        pill(c, "3.000.000.000 TICS / SEG", 540, 1620, 44, YEL, INK, k)
        text(c, "(3 GHz)", 540, 935, 40, alpha(CREAM, clamp(k)), SLAB, False, outline=INK, olw=8)

# ================================================================ scene: paso5 (photo -> pixels -> bits)
NXP, NYP = 24, 50
PXW, PXH = SW / NXP, SH / NYP
SUNC = (16, 14)
def photo_col(i, j):
    u, v = (i + 0.5) / NXP, (j + 0.5) / NYP
    d = math.hypot(i - SUNC[0], (j - SUNC[1]))
    if d <= 2.3: return YEL
    sky = mix(hx("#3D3A7A"), hx("#E9A06A"), clamp(v / 0.5))
    if d < 4.2: sky = mix(YEL, sky, (d - 2.3) / 1.9 * 0.8 + 0.2)
    h1 = 0.56 + 0.05 * math.sin(u * 7 + 1)
    h2 = 0.68 + 0.04 * math.sin(u * 11 + 3)
    if v > h2: return mix(hx("#3E6B3A"), hx("#24402A"), clamp((v - h2) / 0.3))
    if v > h1: return mix(RUST, hx("#7A3B2E"), clamp((v - h1) / 0.12))
    return sky

PCOLS = [[photo_col(i, j) for j in range(NYP)] for i in range(NXP)]

def photo(c):
    c.set_source_rgba(*INK); c.paint()
    for i in range(NXP):
        for j in range(NYP):
            c.rectangle(SX + i * PXW + 0.5, SY + j * PXH + 0.5, PXW - 1.0, PXH - 1.0)
            c.set_source_rgba(*PCOLS[i][j]); c.fill()

def chat(c):
    c.set_source_rgba(*hx("#2E2A44")); c.paint()
    for k, (x, y, w, mine) in enumerate([(SX + 30, 760, 250, 0), (SX + SW - 30 - 220, 880, 220, 1), (SX + 30, 1000, 300, 0), (SX + SW - 30 - 180, 1120, 180, 1), (SX + 30, 1240, 230, 0)]):
        rrect(c, x, y, w, 80, 24); fill_stroke(c, ORANGE if mine else CREAM2, INK, 4)
        for q in range(2): rrect(c, x + 22, y + 22 + q * 22, w - 60 - q * 50, 10, 5); c.set_source_rgba(*alpha(INK, 0.4)); c.fill()

def video(c):
    photo(c)
    c.set_source_rgba(0, 0, 0, 0.3); c.paint()
    circle(c, PX, PY, 70); fill_stroke(c, alpha(WHITE, 0.85), INK, 5)
    c.new_path(); c.move_to(PX - 22, PY - 34); c.line_to(PX + 36, PY); c.line_to(PX - 22, PY + 34); c.close_path(); fill_stroke(c, RED, None)
    rrect(c, SX + 30, SY + SH - 70, SW - 60, 12, 6); c.set_source_rgba(1, 1, 1, 0.4); c.fill()
    rrect(c, SX + 30, SY + SH - 70, (SW - 60) * 0.35, 12, 6); c.set_source_rgba(*RED); c.fill()

RGB = [("R", 242, hx("#FF6B5A")), ("G", 201, hx("#6FD36F")), ("B", 76, hx("#6FA8FF"))]

def scene_paso5(c, t):
    background(c, t, YEL)
    b0 = fw("paso5")
    t_fo = wt("paso5", "foto"); t_me = wt("paso5", "mensaje"); t_vi = wt("paso5", "vídeo"); t_ch = wt("paso5", "chip")
    t_to = wt("paso5", "todo"); t_pu = wt("paso5", "punto"); t_pa = wt("paso5", "pantalla"); t_nu = wt("paso5", "número")
    t_cn = wt("paso5", "número", 1); t_in = wt("paso5", "interruptores")
    content = photo
    if t_me - 0.1 <= t < t_vi - 0.1: content = chat
    elif t_vi - 0.1 <= t < t_ch: content = video
    kz = ease(ramp(t, t_pu - 0.2, t_pu + 0.7))
    sun = (SX + (SUNC[0] + 0.5) * PXW, SY + (SUNC[1] + 0.5) * PXH)
    s0 = 0.82 * (1 + 0.03 * ease(ramp(t, b0, t_pu)))
    S = s0 * ((90 / PXW) / s0) ** kz
    T0 = (540 + s0 * (sun[0] - 540), 1110 + s0 * (sun[1] - 1110))
    k_in = popk(t, b0 - 0.1, 0.45)
    c.save()
    c.translate(lerp(T0[0], 540, kz), lerp(T0[1], 960, kz)); c.scale(S * k_in, S * k_in); c.translate(-sun[0], -sun[1])
    phone(c, t, 0, xray=0.0, content=content)
    # "todo son unos y ceros": binary over the screen
    kb = ease(ramp(t, t_to - 0.1, t_to + 0.4)) * (1 - ease(ramp(t, t_pu - 0.5, t_pu)))
    if kb > 0:
        c.save(); rrect(c, SX, SY, SW, SH, 44); c.clip()
        c.set_source_rgba(*alpha(INK, 0.55 * kb)); c.paint()
        for j in range(22):
            for i in range(9):
                ch = "1" if hsh(i, j, int(t * 6)) > 0.5 else "0"
                text(c, ch, SX + 30 + i * 45, SY + 40 + j * 40, 34, alpha(GREEN if ch == "1" else XRAY, kb * 0.9), MONO, True)
        c.restore()
    c.restore()
    # content tags under the phone
    for (lab, t0, t1) in (("FOTO", t_fo, t_me), ("MENSAJE", t_me, t_vi), ("VÍDEO", t_vi, t_to)):
        k = popk(t, t0 - 0.1, 0.3) * (1 - ease(ramp(t, t1 - 0.15, t1)))
        if k > 0.02 and kz <= 0: pill(c, lab, 540, 1590, 44, YEL, INK, k)
    k = popk(t, t_to) * (1 - ease(ramp(t, t_pu - 0.4, t_pu - 0.1)))
    if k > 0.02: pill(c, "SOLO UNOS Y CEROS", 540, 1590, 44, GREEN, INK, k)
    # highlighted pixel
    kp = ease(ramp(t, t_pa - 0.1, t_pa + 0.2))
    if kp > 0:
        rrect(c, 540 - 48, 960 - 48, 96, 96, 6); fill_stroke(c, None, alpha(WHITE, kp), 8)
        callout(c, "1 PUNTO (PÍXEL)", 540 + 48, 960 - 48, 760, 700, t, t_pa - 0.05, CREAM, 32)
    # number card
    kc = popk(t, t_nu - 0.1, 0.4)
    if kc > 0.02:
        line(c, [(540, 1008), (540, lerp(1008, 1300, kc))], alpha(WHITE, 0.8), 4)
        c.save(); c.translate(540, 1480); c.scale(kc, kc); c.translate(-540, -1480)
        shadow(c, lambda: rrect(c, 130, 1300, 820, 360, 22), 10, 14, 0.45)
        rrect(c, 130, 1300, 820, 360, 22); fill_stroke(c, alpha(INK, 0.95), alpha(WHITE, 0.9), 4)
        for r, (ch, v, col) in enumerate(RGB):
            y = 1395 + r * 100
            kr = ease(ramp(t, t_nu + r * 0.1, t_nu + r * 0.1 + 0.2))
            text(c, ch, 190, y, 56, alpha(col, kr), SLAB, False)
            text(c, str(v), 375, y, 58, alpha(CREAM, kr), MONO, True, "r")
            bits = format(v, "08b")
            for q, bt in enumerate(bits):
                x = 450 + q * 60
                kb = ease(ramp(t, t_cn + r * 0.12 + q * 0.04, t_cn + r * 0.12 + q * 0.04 + 0.15))
                ks = ease(ramp(t, t_in - 0.1 + r * 0.1 + q * 0.03, t_in + r * 0.1 + q * 0.03 + 0.2))
                if kb > 0 and ks < 1:
                    text(c, bt, x, y, 54, alpha(YEL if bt == "1" else LAV, kb * (1 - ks)), MONO, True)
                if ks > 0:
                    c.save(); c.translate(x, y - 20); c.scale(ks * 0.42, ks * 0.42); switch_icon(c, bt == "1", 1.0, 0.6); c.restore()
        c.restore()

# ================================================================ scene: junto + acelerón
DS = 640 / 760
DCX, DCY = 540, 1100
def dpt(p): return (DCX + p[0] * DS, DCY + p[1] * DS)
PAD = (-362, 150)
JUNTO = [("electricidad", "ELECTRICIDAD", PAD, (240, 1630), YEL), ("puerta", "PUERTA", (147, -192), (780, 690), CREAM),
         ("uno", "UNO", BIT1, (420, 1520), YEL), ("cero", "CERO", BIT0, (650, 1520), LAV),
         ("reglas", "REGLAS", (-265, -265), (300, 690), CREAM), ("tic", "TIC", CLK_C, (860, 1520), YEL)]

def scene_junto(c, t):
    b = B("junto")
    rs = B("remate")["start"]
    fast = ease(ramp(t, T_REAL + 0.2, rs - 0.4))
    background(c, t, mix(YEL, HOT, fast))
    fi = int(t * FPS)
    if fast > 0:  # binary rain behind
        for col in range(14):
            x = 70 + col * 68
            for r in range(16):
                y = 600 + ((r * 90 + col * 37 + t * 2600 * fast) % 1440)
                ch = "1" if hsh(col, r, fi) > 0.5 else "0"
                text(c, ch, x, y, 34, alpha(GREEN if hsh(col, r) > 0.5 else XRAY, 0.5 * fast), MONO, True)
    shake = 7 * fast
    c.save(); cam(c, 1.0 + 0.05 * ease(ramp(t, b["start"], rs)), 540, 1100)
    c.translate(shake * math.sin(t * 61), shake * math.cos(t * 53))
    n = tickn(t) if fast < 0.05 else fi * 7919
    t_el = wt("junto", "electricidad")
    def draw(c):
        die0(c, n, bits=True, flick=fast)
        if t_el - 0.1 <= t < rs:  # electricity entering from the pad
            ph = ((t - t_el) * (1.2 + 10 * fast)) % 1.0
            pts = [PAD, (-300, 150), (-300, 140), (-120, 140), (-120, 60)]
            p = path_pt(pts, ph * sum(math.dist(a, b_) for a, b_ in zip(pts, pts[1:])))
            line(c, pts, alpha(YEL, 0.6), 6)
            glow(c, p[0], p[1], 50, YEL, 0.9); circle(c, p[0], p[1], 10); c.set_source_rgba(1, 1, 1, 1); c.fill()
        if fast > 0:
            c.set_source_rgba(1, 1, 1, 0.12 * fast * hsh(fi)); c.paint()
    die_panel(c, DCX, DCY, DS, draw)
    c.restore()
    if fast < 0.3:
        fa = 1 - fast / 0.3
        for w, lab, p, (lx, ly), col in JUNTO:
            ax, ay = dpt(p)
            c.push_group(); callout(c, lab, ax, ay, lx, ly, t, wt("junto", w) - 0.05, col, 36); c.pop_group_to_source(); c.paint_with_alpha(fa)
            tw = wt("junto", w)
            if tw <= t < tw + 0.6 and w != "electricidad":
                r = 30 + 60 * ramp(t, tw, tw + 0.6)
                circle(c, ax, ay, r); c.set_source_rgba(*alpha(WHITE, 0.8 * (1 - ramp(t, tw, tw + 0.6)) * fa)); c.set_line_width(5); c.stroke()
    if fast > 0:  # speed lines
        for i in range(28):
            r0 = 280 + (i * 97 + t * 2600) % 900
            a = i * 0.2244
            line(c, [(540 + math.cos(a) * r0, 1100 + math.sin(a) * r0), (540 + math.cos(a) * (r0 + 160 * fast), 1100 + math.sin(a) * (r0 + 160 * fast))],
                 alpha(WHITE, 0.4 * fast), 5)
    flash = ramp(t, rs - 0.45, rs - 0.3) * (1 - ramp(t, rs - 0.3, rs - 0.1))
    if flash > 0: c.set_source_rgba(1, 1, 1, 0.85 * flash); c.paint()

# ================================================================ scene: remate (heat)
SPARKS = []
_r = random.Random(5)
for i in range(150):
    if i < 14: SPARKS.append((CHX + _r.uniform(-70, 70), CHY + _r.uniform(-70, 70)))
    else:
        rr = 90 + 330 * (i / 150) ** 0.6; a = _r.uniform(0, 6.283)
        SPARKS.append((CHX + math.cos(a) * rr * 0.55, CHY + 60 + math.sin(a) * rr))

def scene_remate(c, t):
    rs = B("remate")["start"]
    background(c, t, mix(COLD, HOT, ramp(t, rs, T_LOOP)))
    t_ca = wt("remate", "calienta"); t_int = wt("remate", "interruptor"); t_en = wt("remate", "energía")
    t_mul = wt("remate", "multiplícalo"); t_mi = wt("remate", "miles"); t_tic = wt("remate", "tic")
    heat = 0.55 * ease(ramp(t, t_ca - 0.4, t_ca + 0.9)) + 0.45 * ease(ramp(t, t_mul, t_tic + 0.4))
    nsp = 0
    if t >= t_int: nsp = 1
    if t >= t_en - 0.3: nsp = 4
    nsp += int(136 * ease(ramp(t, t_mul, t_mi + 0.7)) ** 1.5)
    tf = pulse_at(t, t_tic - 0.05, 0.5)
    def sparks(c):
        for i in range(min(nsp, len(SPARKS))):
            x, y = SPARKS[i]
            ph = ((t * 1.6) + hsh(i, 9)) % 1.0
            s = (22 if i < 4 else 14) * math.sin(math.pi * ph) ** 2 + 20 * tf
            spark(c, x, y, s, 1.0)
    push = 1.0 + 0.04 * ease(ramp(t, rs, T_LOOP))
    c.save(); cam(c, push, 540, 1110)
    phone(c, t, int(t * 6), xray=1.0, dim=0.35 * ease(ramp(t, rs, t_ca)), heat=heat, chipflash=tf, sparks=sparks)
    c.restore()
    # thermometer on "se calienta"
    kt = popk(t, t_ca - 0.3, 0.4)
    thermo(c, 890, 760, 1300, 0.12 + 0.85 * heat, kt)
    # one switch, magnified: each flip costs a bit of energy
    ki = popk(t, t_int - 0.1, 0.4)
    if ki > 0.02:
        cx, cy = 190, 1440
        line(c, [(cx + 80 * ki, cy - 80 * ki), (CHX - 50, CHY + 40)], alpha(WHITE, 0.8 * clamp(ki)), 4)
        c.save(); c.translate(cx, cy); c.scale(ki, ki)
        circle(c, 0, 0, 120); fill_stroke(c, NIGHT, GOLD, 10)
        flip = (t - t_int) / 0.6
        on = int(flip) % 2 == 0
        switch_icon(c, on, 0.75, 0.8)
        fr = flip % 1.0
        if t > t_int: spark(c, 46, -50, 26 * (1 - fr) ** 2, 1.0)
        c.restore()
    k = popk(t, t_en - 0.1)
    if k > 0.02: pill(c, "+ ENERGÍA = CALOR", 300, 1640, 38, HOT, INK, k)
    k = popk(t, t_mi - 0.05)
    if k > 0.02:
        c.save(); c.translate(540, 1340); c.scale(k, k)
        text(c, "× MILES DE MILLONES", 0, 18, 54, YEL, SLAB, False, outline=INK, olw=10); c.restore()

# ================================================================ timeline
SCENES = [
    ("front", 0.0, cut("paso1"), scene_front),
    ("paso1", cut("paso1"), cut("paso2"), scene_paso1),
    ("paso2", cut("paso2"), cut("paso3"), scene_paso2),
    ("paso3", cut("paso3"), cut("paso4"), scene_paso3),
    ("paso4", cut("paso4"), cut("paso5"), scene_paso4),
    ("paso5", cut("paso5"), cut("junto"), scene_paso5),
    ("junto", cut("junto"), B("remate")["start"] - 0.1, scene_junto),
    ("remate", B("remate")["start"] - 0.1, T_LOOP + 0.15, scene_remate),
]
LOOP_FN = scene_front
XF = {"remate": 0.08}

def POPS():
    p = [wt("gancho", "chip"), wt("gancho", "no") - 0.1, wt("gancho", "enciende") - 0.1]
    p += [wt("imposible", w) - 0.15 for w, *_ in BADGES]
    p += [wt("imposible", "pantalla")]
    p += [wt("paso1", "diez") - 0.1, wt("paso1", "interruptor"), wt("paso1", "sin")]
    p += [wt("paso2", "puerta"), wt("paso2", "encendido"), wt("paso2", "uno"), wt("paso2", "apagado"), wt("paso2", "cero")]
    p += [wt("paso3", "transistores") - 0.15, wt("paso3", "reglas"), wt("paso3", "sale"), wt("paso3", "suma") - 0.1,
          wt("paso3", "compara") - 0.1, wt("paso3", "decide") - 0.1]
    p += [wt("paso4", "reloj"), wt("paso4", "interruptores"), wt("paso4", "vez") - 0.1, wt("paso4", "tres") - 0.1]
    p += [wt("paso5", w) - 0.1 for w in ("foto", "mensaje", "vídeo")] + [wt("paso5", "todo"), wt("paso5", "pantalla"), wt("paso5", "número") - 0.1]
    p += [wt("junto", w) - 0.05 for w, *_ in JUNTO]
    p += [wt("remate", "calienta") - 0.3, wt("remate", "interruptor") - 0.1, wt("remate", "energía") - 0.1, wt("remate", "miles")]
    return sorted(p)

def SFX(put, L):
    import numpy as np
    SR = L["SR"]
    t_sw = wt("gancho", "enciende")
    for k in range(5): put(L["click"](), t_sw + k * 0.23, 0.55)
    for w in ("engranajes", "mueva", "palabra"): put(L["scratch"](), wt("imposible", w) + 0.2, 0.25)
    put(L["click"](), wt("paso1", "interruptor"), 0.6)
    put(L["zap"](0.5), wt("paso2", "electricidad"), 0.14)
    put(L["ding"](), wt("paso2", "uno"), 0.22)
    put(L["tone"](330, 0.25, 0.005, 0.12), wt("paso2", "cero"), 0.25)
    put(L["ding"](2093), wt("paso3", "sale"), 0.2)
    # soft digital blips on every clock tick while slowed (clock visible: paso4, junto, acelera)
    blip = L["tone"](2350, 0.05, 0.002, 0.02) + 0.5 * L["tone"](4700, 0.05, 0.002, 0.012)
    for (a, b) in ((cut("paso4") + 0.2, cut("paso5")), (cut("junto"), T_REAL + 0.2)):
        ph = clock_ph(a); tt = a + (math.ceil(ph) - ph) / HZ
        while tt < b:
            put(blip, tt, 0.09); tt += 1 / HZ
    # bits -> switches
    for k in range(6): put(L["click"](), wt("paso5", "interruptores") + k * 0.07, 0.3)
    # acelerón: rising digital chirp
    d = max(0.5, B("remate")["start"] - 0.4 - (T_REAL + 0.2))
    n = int(d * SR); tg = np.arange(n) / SR; u = tg / d
    f = 300 * 2 ** (5 * u ** 1.4)
    sig = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (0.15 + 0.85 * u ** 2)
    sig = L["lp"](sig, 5000) * np.minimum(1, (d - tg) / 0.05)
    put(sig, T_REAL + 0.2, 0.16)
    # remate: crackles as the sparks multiply, a zap on "tic"
    for k in range(12): put(L["click"](), wt("remate", "miles") + k * 0.09, 0.25)
    put(L["zap"](0.4), wt("remate", "tic"), 0.12)

# ================================================================ thumbnails
def _thumb_scene(c):
    glow(c, CHX, CHY, 420, YEL, 0.55)
    phone(c, 3.0, 11, xray=1.0, wall=1.2, chipflash=0.0)
    glow(c, CHX, CHY, 230, YEL, 0.5)
    for i, (x, y) in enumerate(SPARKS[:10]): spark(c, x, y, 18 + 6 * (i % 3), 1.0)

def THUMB_V(c):
    background(c, 3.0, YEL)
    c.save(); c.translate(-90, 360); cam(c, 1.0, 540, 1110); _thumb_scene(c); c.restore()
    c.save(); c.translate(810, 1450); c.rotate(0.12); switch_icon(c, True, 2.4); c.restore()
    for i, (ln, col) in enumerate([("NO PIENSA", WHITE), ("NADA", YEL)]):
        sz = fit_size(c, ln, SLAB, 210, 980)
        text(c, ln, 540, 340 + i * 220, sz, col, SLAB, False, outline=INK, olw=24)

def THUMB_H(c):
    g = cairo.LinearGradient(0, 0, 0, 720); g.add_color_stop_rgba(0, *BG_TOP); g.add_color_stop_rgba(1, *BG_BOT); c.set_source(g); c.paint()
    glow(c, 960, 380, 420, YEL, 0.35)
    c.save(); c.translate(920, 360); c.scale(0.62, 0.62); c.translate(-540, -1060); _thumb_scene(c); c.restore()
    c.save(); c.translate(1150, 520); c.rotate(0.12); switch_icon(c, True, 1.25); c.restore()
    for i, (ln, col) in enumerate([("NO PIENSA", WHITE), ("NADA", YEL)]):
        sz = fit_size(c, ln, SLAB, 150, 680)
        text(c, ln, 380, 310 + i * 180, sz, col, SLAB, False, outline=INK, olw=20)
