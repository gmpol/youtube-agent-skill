"""¿Cómo funciona el motor de un coche?  (motor de gasolina de 4 tiempos, 4 cilindros, 3.000 rpm)
Illustrations for the engine (output/engine/SCENES_GUIDE.md). Everything drawn with pycairo."""
from core import *  # noqa
import cairo, math, random

# ---------------------------------------------------------------- timing
def cut(beat): return B(beat)["start"] - 0.3
def ws(beat, w, nth=0):  # word start, never before the beat really starts (whisper stretches words after pauses)
    return max(wt(beat, w, nth), B(beat)["start"] - 0.05) if nth == 0 else wt(beat, w, nth)

RPS = 50.0                     # 3.000 rpm = 50 vueltas/s -> 25 explosiones/s por cilindro, 100 con 4
_G0 = None
def G_of(t):
    """Crank angle (degrees) of the real engine at video time t (slowed by the HUD factor)."""
    global _G0
    if _G0 is None:
        g = 360 * RPS * anim_time(ws("junto", "chispa") + 0.05)
        _G0 = -(g % 180)       # a cylinder fires right on "chispa" in the junto line
    return 360 * RPS * anim_time(t) + _G0

# ---------------------------------------------------------------- cylinder geometry (local units, origin = crank centre)
R_CR, L_ROD = 70, 230
HEAD_Y, HEAD_TOP = -400, -495
BORE, WALL = 85, 26
LIFT, VX = 30, 48
BLOCK_BOT = -170

PISTON = hx("#E9DCC2"); ROD = hx("#B9C0D3"); BLOCK = RUST; HEAD = ORANGE2; CAVE = hx("#14121C"); CRANK = hx("#D9A441")
AIRC = hx("#6FA8FF"); FUEL = hx("#FFB84C"); SMOKE = hx("#9A97A6")

def pin_y(th): return -(R_CR * math.cos(th) + math.sqrt(L_ROD ** 2 - (R_CR * math.sin(th)) ** 2))
def crown_y(phi): return pin_y(math.radians(phi % 360)) - 55
def lift_in(phi):
    p = phi % 720; return math.sin(math.pi * p / 180) if p < 180 else 0.0
def lift_ex(phi):
    p = phi % 720; return math.sin(math.pi * (p - 540) / 180) if p >= 540 else 0.0

def gas_state(phi):
    """What is in the chamber at cycle angle phi (0 = TDC, start of intake; 360 = TDC firing)."""
    p = phi % 720
    if p < 180:
        k = p / 180; return dict(col=AIRC, a=0.15 + 0.45 * k, drops=k, fire=0.0, smoke=0.0, press=0.0)
    if p < 360:
        k = (p - 180) / 180; return dict(col=mix(AIRC, hx("#8FB6FF"), k), a=0.6 + 0.3 * k, drops=1.0, fire=0.0, smoke=0.0, press=k)
    if p < 540:
        k = (p - 360) / 180
        return dict(col=mix(YEL, HOT, ease(k / 0.4)) if k < 0.4 else mix(HOT, SMOKE, ease((k - 0.4) / 0.6)),
                    a=0.95 - 0.3 * k, drops=0.0, fire=clamp(1 - k / 0.55), smoke=ease(k), press=0.0)
    k = (p - 540) / 180; return dict(col=SMOKE, a=0.65 * (1 - k) + 0.08, drops=0.0, fire=0.0, smoke=1.0, press=0.0)

def spark_k(phi, w=24):
    p = phi % 720
    return math.sin(math.pi * (p - (360 - w * 0.35)) / w) if 360 - w * 0.35 <= p <= 360 + w * 0.65 else 0.0

DROPS = [(random.Random(i).uniform(-75, 75), random.Random(i + 50).uniform(0, 1), random.Random(i + 9).uniform(3, 7)) for i in range(26)]

def spark_draw(c, x, y, k, t, s=1.0):
    if k <= 0: return
    glow(c, x, y, 120 * s * k, YEL, 0.9 * k)
    glow(c, x, y, 50 * s * k, WHITE, 0.9 * k)
    rnd = random.Random(int(t * 30))
    for j in range(5):
        a = math.pi / 2 + (j - 2) * 0.55 + rnd.uniform(-0.2, 0.2)
        pts = [(x, y)]; r = 0
        for m in range(4):
            r += 14 * s * k
            pts.append((x + math.cos(a) * r + rnd.uniform(-7, 7) * s, y + math.sin(a) * r + rnd.uniform(-5, 5) * s))
        line(c, pts, alpha(YEL, k), 6 * s)
        line(c, pts, alpha(WHITE, k), 2.5 * s)

def flame_blob(c, cx, cy, rx, ry, k, t):
    """Wobbly orange explosion (yellow core) inside the chamber."""
    if k <= 0: return
    for layer, (col, sc) in enumerate([(HOT, 1.0), (ORANGE, 0.78), (YEL, 0.5), (WHITE, 0.22)]):
        c.new_path(); n = 28
        for i in range(n + 1):
            a = 2 * math.pi * i / n
            r = sc * k * (1 + 0.14 * math.sin(a * 5 + t * 9 + layer) + 0.08 * math.sin(a * 9 - t * 13))
            x, y = cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r
            c.line_to(x, y) if i else c.move_to(x, y)
        c.close_path(); c.set_source_rgba(*alpha(col, 0.95)); c.fill()

def chamber_gas(c, phi, t, st, x0=-BORE, x1=BORE):
    yc = crown_y(phi)
    if yc <= HEAD_Y + 2: return
    c.save(); c.rectangle(x0, HEAD_Y, x1 - x0, yc - HEAD_Y); c.clip()
    c.set_source_rgba(*alpha(st["col"], st["a"])); c.paint()
    if st.get("drops", 0) > 0:  # tiny petrol droplets mixed in the air
        n = int(len(DROPS) * st["drops"])
        for i, (dx, v, r) in enumerate(DROPS[:n]):
            y = lerp(HEAD_Y + 10, yc - 8, v)
            circle(c, dx + 4 * math.sin(t * 3 + i), y, r); c.set_source_rgba(*alpha(FUEL, 0.95)); c.fill()
    if st.get("fire", 0) > 0:
        flame_blob(c, 0, (HEAD_Y + yc) / 2, 110, max(40, (yc - HEAD_Y) * 0.75), 0.4 + 0.75 * st["fire"], t)
    c.restore()

def draw_valve(c, x, lift, col=ROD, top=HEAD_TOP - 10):
    y = HEAD_Y + lift * LIFT
    line(c, [(x, y - 4), (x, top + lift * LIFT)], INK, 14); line(c, [(x, y - 4), (x, top + lift * LIFT)], col, 7)
    c.new_path(); c.move_to(x - 7, y - 14); c.line_to(x + 7, y - 14); c.line_to(x + 27, y); c.line_to(x + 27, y + 7)
    c.line_to(x - 27, y + 7); c.line_to(x - 27, y); c.close_path(); fill_stroke(c, col, INK, 4)
    rrect(c, x - 14, top - 8 + lift * LIFT, 28, 12, 4); fill_stroke(c, col, INK, 3)

def draw_plug(c, fired=0.0):
    rrect(c, -14, -470, 28, 62, 4); fill_stroke(c, METAL, INK, 4)
    for j in range(5): line(c, [(-14, -462 + j * 11), (14, -456 + j * 11)], alpha(INK, 0.5), 2)
    rrect(c, -22, -500, 44, 32, 5); fill_stroke(c, hx("#5A5F70"), INK, 4)
    rrect(c, -12, -568, 24, 70, 8); fill_stroke(c, WHITE, INK, 4)
    for j in range(3): line(c, [(-12, -550 + j * 16), (12, -550 + j * 16)], alpha(INK, 0.35), 3)
    rrect(c, -7, -588, 14, 22, 4); fill_stroke(c, METAL, INK, 3)
    line(c, [(0, -408), (0, -398)], INK, 7)
    line(c, [(-10, -394), (8, -394), (8, -402)], INK, 5)

def draw_injector(c, spray=0.0, t=0.0):
    rrect(c, -16, -472, 32, 70, 6); fill_stroke(c, METAL, INK, 4)
    rrect(c, -24, -560, 48, 92, 8); fill_stroke(c, STEEL, INK, 4)
    rrect(c, -8, -590, 16, 32, 4); fill_stroke(c, METAL, INK, 3)
    c.new_path(); c.move_to(-8, -404); c.line_to(8, -404); c.line_to(0, -394); c.close_path(); fill_stroke(c, METAL, INK, 3)

def crank_side(c, th):
    """Crank seen along its axis (side view): counterweight + web + pin."""
    px, py = R_CR * math.sin(th), -R_CR * math.cos(th)
    c.save(); c.rotate(th)
    c.new_path(); c.arc(0, 0, 112, math.radians(90 - 70) , math.radians(90 + 70)); c.line_to(0, 0); c.close_path()
    fill_stroke(c, mix(CRANK, INK, 0.25), INK, 5)
    rrect(c, -40, -R_CR - 36, 80, R_CR + 76, 36); fill_stroke(c, CRANK, INK, 5)
    c.restore()
    circle(c, 0, 0, 26); fill_stroke(c, hx("#7A6A4A"), INK, 4)
    return px, py

def rod_draw(c, x0, y0, x1, y1):
    line(c, [(x0, y0), (x1, y1)], INK, 40); line(c, [(x0, y0), (x1, y1)], ROD, 28)
    line(c, [(x0, y0), (x1, y1)], alpha(WHITE, 0.35), 6)
    circle(c, x0, y0, 22); fill_stroke(c, ROD, INK, 5); circle(c, x0, y0, 8); fill_stroke(c, INK, None)

def piston_draw(c, phi, push=0.0):
    yc = crown_y(phi)
    rrect(c, -BORE + 3, yc, 2 * BORE - 6, 110, 10); fill_stroke(c, PISTON, INK, 6)
    for j in range(2): line(c, [(-BORE + 4, yc + 18 + j * 14), (BORE - 4, yc + 18 + j * 14)], alpha(INK, 0.55), 4)
    rrect(c, -BORE + 14, yc + 8, 26, 90, 8); c.set_source_rgba(1, 1, 1, 0.25); c.fill()
    circle(c, 0, yc + 55, 16); fill_stroke(c, METAL, INK, 4)

def hatch(c, x, y, w, h, a=0.12):
    c.save(); c.rectangle(x, y, w, h); c.clip()
    for i in range(-int(h), int(w), 22): line(c, [(x + i, y + h), (x + i + h, y)], (1, 1, 1, a), 3)
    c.restore()

def engine_side(c, phi, t, diesel=False, st=None, spark=None, inject=0.0, hot=0.0, port_flow=True, crank=True):
    """One cylinder, side cut-away, local coords (origin = crank centre). phi = cycle angle."""
    st = st or gas_state(phi)
    th = math.radians(phi % 360)
    # crankcase
    c.new_path(); c.move_to(-118, BLOCK_BOT); c.line_to(118, BLOCK_BOT); c.curve_to(190, -80, 190, 150, 0, 160)
    c.curve_to(-190, 150, -190, -80, -118, BLOCK_BOT); c.close_path(); fill_stroke(c, BLOCK, INK, 7)
    c.new_path(); c.move_to(-96, BLOCK_BOT + 8); c.line_to(96, BLOCK_BOT + 8); c.curve_to(160, -70, 160, 130, 0, 138)
    c.curve_to(-160, 130, -160, -70, -96, BLOCK_BOT + 8); c.close_path(); fill_stroke(c, CAVE, INK, 4)
    # bore
    c.rectangle(-BORE, HEAD_Y, 2 * BORE, BLOCK_BOT - HEAD_Y + 10); c.set_source_rgba(*CAVE); c.fill()
    if hot > 0: c.rectangle(-BORE, HEAD_Y, 2 * BORE, crown_y(phi) - HEAD_Y); c.set_source_rgba(*alpha(HOT, 0.0)); c.fill()
    chamber_gas(c, phi, t, st)
    if crank:
        px, py = crank_side(c, th)
        piston_draw(c, phi); rod_draw(c, px, py, 0, pin_y(th))
        circle(c, 0, pin_y(th), 14); fill_stroke(c, METAL, INK, 4)
    else:
        piston_draw(c, phi)
    # walls
    for x in (-BORE - WALL, BORE):
        c.rectangle(x, HEAD_Y, WALL, BLOCK_BOT - HEAD_Y); fill_stroke(c, BLOCK, INK, 5); hatch(c, x, HEAD_Y, WALL, BLOCK_BOT - HEAD_Y)
    # head with ports
    rrect(c, -135, HEAD_TOP, 270, HEAD_Y - HEAD_TOP + 6, 14); fill_stroke(c, HEAD, INK, 6)
    hatch(c, -135, HEAD_TOP, 270, HEAD_Y - HEAD_TOP)
    li, le = lift_in(phi), lift_ex(phi)
    for sx, lf, col in ((-1, li, AIRC), (1, le, SMOKE)):
        pts = [(sx * VX, HEAD_Y + 4), (sx * VX, HEAD_Y - 34), (sx * 150, HEAD_Y - 62)]
        line(c, pts, INK, 52, cairo.LINE_CAP_BUTT); line(c, pts, CAVE, 40, cairo.LINE_CAP_BUTT)
        if lf > 0.05 and port_flow:
            line(c, pts, alpha(col, 0.55 * lf), 40, cairo.LINE_CAP_BUTT)
    draw_valve(c, -VX, li); draw_valve(c, VX, le)
    if diesel: draw_injector(c, inject, t)
    else: draw_plug(c)
    # spark / ignition
    k = spark_k(phi) if spark is None else spark
    if k > 0 and not diesel: spark_draw(c, 0, HEAD_Y + 6, k, t)
    if st.get("fire", 0) > 0.6: glow(c, 0, (HEAD_Y + crown_y(phi)) / 2, 260, ORANGE, 0.5 * (st["fire"] - 0.6) / 0.4)

def callout_a(c, a, *args, **kw):
    if a <= 0.01: return
    c.push_group(); callout(c, *args, **kw); c.pop_group_to_source(); c.paint_with_alpha(clamp(a))

# ---------------------------------------------------------------- 4-cylinder in-line block (front cut-away)
ROW_X = [250, 440, 630, 820]; ROW_Y = 1520; ROW_S = 0.95
FIRE = {0: 0, 2: 180, 3: 360, 1: 540}           # firing order 1-3-4-2 (cylinder index -> crank angle at firing)
def cyl_phi(i, G): return (G + 360 - FIRE[i]) % 720
def row_pt(i, x, y): return ROW_X[i] + x * ROW_S, ROW_Y + y * ROW_S

def engine_row(c, G, t, hl=None, dim=1.0, num=0.0, gas=True):
    hl = hl or {}
    S = ROW_S
    x0, x1 = ROW_X[0] - 125 * S, ROW_X[3] + 125 * S
    def Y(y): return ROW_Y + y * S
    # flywheel (left end) + shaft
    th = math.radians(G)
    shadow(c, lambda: rrect(c, x0 - 10, Y(HEAD_TOP), x1 - x0 + 20, Y(160) - Y(HEAD_TOP), 30), 14, 18, 0.45)
    c.save(); c.translate(x0 - 36, ROW_Y); c.scale(0.3, 1)
    circle(c, 0, 0, 118); c.restore(); fill_stroke(c, mix(CRANK, INK, 0.2), INK, 6)
    mx, my = x0 - 36 + 28 * math.sin(th), ROW_Y - 96 * math.cos(th)
    circle(c, mx, my, 11); fill_stroke(c, YEL if math.cos(th) > -0.2 else alpha(YEL, 0.4), INK, 3)
    # crankcase
    rrect(c, x0 + 6, Y(BLOCK_BOT) - 10, x1 - x0 - 12, Y(150) - Y(BLOCK_BOT) + 10, 40); fill_stroke(c, BLOCK, INK, 7)
    rrect(c, x0 + 24, Y(BLOCK_BOT) + 4, x1 - x0 - 48, Y(128) - Y(BLOCK_BOT) - 4, 30); fill_stroke(c, CAVE, INK, 4)
    line(c, [(x0 - 30, ROW_Y), (x1 + 4, ROW_Y)], INK, 34); line(c, [(x0 - 30, ROW_Y), (x1 + 4, ROW_Y)], mix(CRANK, INK, 0.15), 22)
    # cylinder block body
    c.rectangle(x0 + 6, Y(HEAD_Y), x1 - x0 - 12, Y(BLOCK_BOT) - Y(HEAD_Y)); fill_stroke(c, BLOCK, INK, 7)
    hatch(c, x0 + 6, Y(HEAD_Y), x1 - x0 - 12, Y(BLOCK_BOT) - Y(HEAD_Y))
    for i in range(4):
        phi = cyl_phi(i, G); thi = math.radians(phi % 360)
        c.save(); c.translate(ROW_X[i], ROW_Y); c.scale(S, S)
        c.rectangle(-BORE, HEAD_Y, 2 * BORE, BLOCK_BOT - HEAD_Y + 4); fill_stroke(c, CAVE, INK, 4)
        if gas: chamber_gas(c, phi, t, gas_state(phi))
        # crank throw (projected: the pin only moves up and down in this view)
        pyy = -R_CR * math.cos(thi)
        rrect(c, -50, min(0, pyy) - 22, 24, abs(pyy) + 44, 10); fill_stroke(c, CRANK, INK, 4)
        rrect(c, 26, min(0, pyy) - 22, 24, abs(pyy) + 44, 10); fill_stroke(c, CRANK, INK, 4)
        rrect(c, -68, -pyy * 0.9 - 30, 136, 60, 26); fill_stroke(c, mix(CRANK, INK, 0.25), INK, 4)
        rod_draw(c, 0, pyy, 0, pin_y(thi))
        piston_draw(c, phi)
        circle(c, 0, pin_y(thi), 14); fill_stroke(c, METAL, INK, 4)
        c.restore()
    # head
    rrect(c, x0, Y(HEAD_TOP), x1 - x0, Y(HEAD_Y) - Y(HEAD_TOP) + 6, 14); fill_stroke(c, HEAD, INK, 7)
    hatch(c, x0, Y(HEAD_TOP), x1 - x0, Y(HEAD_Y) - Y(HEAD_TOP))
    for i in range(4):
        phi = cyl_phi(i, G)
        c.save(); c.translate(ROW_X[i], ROW_Y); c.scale(S, S)
        li, le = lift_in(phi), lift_ex(phi)
        for sx, lf, col in ((-1, li, AIRC), (1, le, SMOKE)):
            pts = [(sx * VX, HEAD_Y + 4), (sx * VX, HEAD_TOP - 40)]
            line(c, pts, INK, 50, cairo.LINE_CAP_BUTT); line(c, pts, CAVE, 38, cairo.LINE_CAP_BUTT)
            if lf > 0.05: line(c, pts, alpha(col, 0.7 * lf), 38, cairo.LINE_CAP_BUTT)
            rrect(c, sx * VX - 30, HEAD_TOP - 52, 60, 18, 6); fill_stroke(c, col if lf > 0.05 else mix(col, INK, 0.5), INK, 4)
        draw_valve(c, -VX, li, top=HEAD_TOP - 16); draw_valve(c, VX, le, top=HEAD_TOP - 16)
        draw_plug(c)
        k = spark_k(phi, 34)
        st = gas_state(phi)
        if st["fire"] > 0.5: glow(c, 0, HEAD_Y + 60, 200, ORANGE, 0.55 * (st["fire"] - 0.5) * 2)
        if k > 0: spark_draw(c, 0, HEAD_Y + 6, k, t, 1.2)
        if i in hl and hl[i] > 0:
            rrect(c, -BORE - WALL - 6, HEAD_TOP - 60, 2 * (BORE + WALL) + 12, 160 - HEAD_TOP + 70, 20)
            c.set_source_rgba(*alpha(YEL, 0.9 * hl[i])); c.set_line_width(8); c.stroke()
        c.restore()
        if num > 0:
            k2 = eob(clamp(num * 4 - i * 0.6))
            if k2 > 0:
                x, y = row_pt(i, 0, 60)
                c.save(); c.translate(x, ROW_Y - 330 * S + 0); c.scale(k2, k2)
                circle(c, 0, 0, 30); fill_stroke(c, YEL, INK, 5); text(c, str(i + 1), 0, 13, 36, INK, SLAB, False)
                c.restore()

def engine_row_blur(c, t, extra=None):
    """Averages several crank positions inside one frame's exposure -> real motion blur at real speed."""
    G = G_of(t)
    dG = 360 * RPS * (anim_time(t + 1 / 30) - anim_time(t))
    n = int(clamp(math.ceil(dG / 25), 1, 10))
    for k in range(n):
        g = G - dG * k / n
        if k == 0: engine_row(c, g, t, **(extra or {}))
        else:
            c.push_group(); engine_row(c, g, t, **(extra or {})); c.pop_group_to_source(); c.paint_with_alpha(1 / (k + 1))
    return G, dG

# ---------------------------------------------------------------- the car (side view, facing right)
CAR_RED = RUST
def car(c, t, wheel_ang=0.0, puff=0.0, beam=1.0, hood_glow=0.0, bounce=0.0):
    """Car centred at (0,0); wheels at y=+80. Length ~740."""
    c.save(); c.translate(0, bounce)
    # headlight beam
    if beam > 0:
        g = cairo.LinearGradient(350, 0, 900, 0)
        g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.55 * beam); g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)
        c.new_path(); c.move_to(340, -18); c.line_to(900, -120); c.line_to(900, 170); c.line_to(340, 14); c.close_path()
        c.set_source(g); c.fill()
    def body():
        c.new_path(); c.move_to(-360, 60); c.line_to(-370, -10); c.curve_to(-360, -60, -300, -70, -250, -72)
        c.curve_to(-200, -190, -120, -200, -10, -200); c.curve_to(100, -200, 160, -180, 215, -78)
        c.curve_to(300, -74, 365, -60, 372, -6); c.line_to(368, 60); c.close_path()
    shadow(c, body, 12, 16, 0.4)
    body(); fill_stroke(c, CAR_RED, INK, 8)
    # cream roof band + windows
    c.new_path(); c.move_to(-238, -80); c.curve_to(-190, -182, -120, -190, -10, -190); c.curve_to(95, -190, 150, -172, 200, -84); c.close_path()
    fill_stroke(c, CREAM, INK, 6)
    for (a, b) in ((-215, -30), (-10, 182)):
        c.new_path()
        if a < 0 and b < 0:
            c.move_to(-205, -90); c.curve_to(-170, -160, -110, -168, -30, -168); c.line_to(-30, -90); c.close_path()
        else:
            c.move_to(-10, -168); c.curve_to(80, -168, 128, -152, 168, -90); c.line_to(-10, -90); c.close_path()
        fill_stroke(c, hx("#2E3A5C"), INK, 5)
    c.new_path(); c.move_to(-160, -150); c.line_to(-120, -150); c.line_to(-150, -100); c.line_to(-185, -100); c.close_path(); c.set_source_rgba(1, 1, 1, 0.18); c.fill()
    c.new_path(); c.move_to(30, -160); c.line_to(70, -160); c.line_to(45, -100); c.line_to(8, -100); c.close_path(); c.set_source_rgba(1, 1, 1, 0.18); c.fill()
    # cream stripe, door, handle
    rrect(c, -362, -14, 732, 22, 10); fill_stroke(c, CREAM2, INK, 4)
    line(c, [(-20, -90), (-20, 52)], alpha(INK, 0.8), 4); line(c, [(185, -78), (190, 52)], alpha(INK, 0.6), 4)
    rrect(c, 18, -46, 44, 12, 6); fill_stroke(c, CREAM2, INK, 3)
    # hood glow (engine)
    if hood_glow > 0: glow(c, 285, -40, 140, ORANGE, 0.7 * hood_glow)
    # lights
    circle(c, 336, -42, 26); fill_stroke(c, hx("#FFF2B0"), INK, 5); glow(c, 340, -42, 70, YEL, 0.5 * beam)
    rrect(c, -372, -52, 22, 34, 8); fill_stroke(c, RED, INK, 4); glow(c, -368, -36, 50, RED, 0.35)
    # bumpers
    rrect(c, 340, 30, 50, 22, 10); fill_stroke(c, METAL, INK, 4); rrect(c, -388, 30, 48, 22, 10); fill_stroke(c, METAL, INK, 4)
    # exhaust
    rrect(c, -404, 56, 60, 16, 6); fill_stroke(c, hx("#5A5F70"), INK, 4)
    # wheels
    for wx in (-225, 225):
        c.new_path(); c.arc(wx, 40, 100, math.pi, 2 * math.pi); c.close_path(); c.set_source_rgba(*alpha(INK, 0.85)); c.fill()
        circle(c, wx, 80, 74); fill_stroke(c, hx("#24212F"), INK, 6)
        circle(c, wx, 80, 40); fill_stroke(c, CREAM2, INK, 5)
        for j in range(5):
            a = wheel_ang + j * 2 * math.pi / 5
            line(c, [(wx, 80), (wx + 34 * math.cos(a), 80 + 34 * math.sin(a))], alpha(INK, 0.7), 5)
        circle(c, wx, 80, 9); fill_stroke(c, RED, INK, 3)
    c.restore()

def puffs(c, x, y, ph, k=1.0):
    """Exhaust puffs drifting backwards; ph = continuous puff counter."""
    for j in range(4):
        u = (ph - math.floor(ph)) + j
        if u > 3.2: continue
        a = k * (1 - u / 3.2) * 0.85
        r = 14 + 16 * u
        circle(c, x - 25 - u * 32, y - 10 - u * 48 + 6 * math.sin(u * 3), r); fill_stroke(c, alpha(hx("#B9B6C6"), a), alpha(INK, a * 0.6), 3)

def night_world(c, t, roll, moon=1.0):
    # moon + skyline + road
    if moon > 0:
        glow(c, 820, 720, 160, CREAM, 0.25 * moon); circle(c, 820, 720, 58); fill_stroke(c, alpha(CREAM2, moon), None)
        circle(c, 840, 708, 50); c.set_source_rgba(*alpha(BG_TOP, 0.9 * moon)); c.fill()
    c.set_source_rgba(*hx("#221F31"))
    rnd = random.Random(5); x = -40
    while x < W + 40:
        w = rnd.uniform(70, 150); h = rnd.uniform(90, 300); xx = (x - roll * 0.15) % (W + 200) - 100
        c.rectangle(xx, 1300 - h, w, h + 10); c.fill(); x += w + rnd.uniform(5, 30)
    rnd = random.Random(8)
    for i in range(40):
        xx = (rnd.uniform(0, W + 200) - roll * 0.15) % (W + 200) - 100; yy = 1300 - rnd.uniform(30, 260)
        c.set_source_rgba(*alpha(YEL, 0.35)); c.rectangle(xx, yy, 10, 14); c.fill()
    c.set_source_rgba(*hx("#2B2838")); c.rectangle(0, 1300, W, 260); c.fill()
    line(c, [(0, 1302), (W, 1302)], INK, 6)
    for i in range(-1, 9):
        xx = (i * 180 - roll) % (W + 180) - 90
        rrect(c, xx, 1440, 100, 14, 7); c.set_source_rgba(*alpha(CREAM, 0.5)); c.fill()
    c.set_source_rgba(*hx("#1C1A27")); c.rectangle(-200, 1560, W + 400, H); c.fill()

# ---------------------------------------------------------------- icons for the "imposible" badges
def ic_horse(c):
    c.new_path(); c.move_to(-48, 62); c.curve_to(-50, 10, -40, -30, -10, -55); c.line_to(-4, -78); c.line_to(10, -58)
    c.curve_to(30, -50, 50, -30, 62, -2); c.curve_to(68, 12, 56, 24, 42, 16); c.curve_to(26, 8, 14, 8, 8, 20)
    c.curve_to(0, 36, 8, 52, 14, 62); c.close_path(); fill_stroke(c, GOLD, INK, 5)
    c.new_path(); c.move_to(-10, -55); c.curve_to(-40, -40, -56, -5, -54, 40); c.line_to(-46, 40); c.curve_to(-46, 0, -32, -30, -8, -45); c.close_path()
    fill_stroke(c, hx("#5A3424"), INK, 3)
    circle(c, 24, -24, 6); fill_stroke(c, INK, None)

def ic_pedals(c):
    circle(c, 0, 0, 44); fill_stroke(c, METAL, INK, 5)
    for j in range(12):
        a = j * math.pi / 6; line(c, [(40 * math.cos(a), 40 * math.sin(a)), (52 * math.cos(a), 52 * math.sin(a))], INK, 6)
    circle(c, 0, 0, 14); fill_stroke(c, INK, None)
    for sgn in (1, -1):
        line(c, [(0, 0), (sgn * 52, sgn * 40)], INK, 12)
        rrect(c, sgn * 52 - 26, sgn * 40 - 9, 52, 18, 5); fill_stroke(c, RED, INK, 4)

def ic_push(c):
    rrect(c, 8, -50, 64, 96, 8); fill_stroke(c, GOLD, INK, 5)
    circle(c, -38, -50, 15); fill_stroke(c, CREAM2, INK, 4)
    line(c, [(-40, -32), (-16, 14)], INK, 11)
    line(c, [(-32, -22), (6, -18)], INK, 9); line(c, [(-26, -10), (6, 0)], INK, 9)
    line(c, [(-16, 14), (-36, 40), (-50, 60)], INK, 10); line(c, [(-16, 14), (0, 40), (-4, 62)], INK, 10)

def ic_plug(c):
    c.save(); c.rotate(0.6); c.scale(0.45, 0.45); c.translate(0, 490)
    draw_plug(c); c.restore()

def weight_icon(c, x, y, k):
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(k, k)
    c.new_path(); c.arc(0, -70, 30, math.pi, 2 * math.pi); c.set_source_rgba(*INK); c.set_line_width(16); c.stroke()
    c.new_path(); c.move_to(-90, 70); c.line_to(-62, -52); c.line_to(62, -52); c.line_to(90, 70); c.close_path()
    shadow(c, lambda: (c.move_to(-90, 70), c.line_to(-62, -52), c.line_to(62, -52), c.line_to(90, 70), c.close_path()), 8, 10, 0.4)
    c.new_path(); c.move_to(-90, 70); c.line_to(-62, -52); c.line_to(62, -52); c.line_to(90, 70); c.close_path()
    fill_stroke(c, hx("#4A4658"), INK, 6)
    text(c, "1.000", 0, 10, 40, CREAM, SLAB, False); text(c, "kg", 0, 54, 34, YEL, SLAB, False)
    c.restore()

BADGES = [("caballos", 250, ic_horse, "CABALLOS"), ("pedales", 540, ic_pedals, "PEDALES"), ("empujando", 830, ic_push, "EMPUJAR")]

# ---------------------------------------------------------------- scene: front (gancho + imposible + freno)
CAR_X, CAR_Y = 540, 1210
def puff_phase(t): return 3.2 * anim_time(t)

def scene_front(c, t):
    background(c, t, ORANGE)
    t_up0 = ws("imposible", "caballos") - 0.4
    t_zoom = ws("freno", "vamos")
    z = ease(ramp(t, t_zoom, T_SLOW + 0.1))
    up = ease(ramp(t, t_up0, t_up0 + 0.4)) * (1 - z)
    push = 1.0 + 0.05 * ease(ramp(t, 0, t_up0))
    sp = speed_fraction(t)
    roll = 420 * anim_time(t)                                  # road scrolls; slows with the HUD
    wheel = roll / 74
    hood = (CAR_X + 285, CAR_Y - 40)
    xr = ease(ramp(t, T_SLOW - 0.8, T_SLOW + 0.3))
    c.save()
    fx, fy = lerp(W / 2, hood[0], z), 1150
    c.translate(lerp(W / 2, 540, z), lerp(1150, 1220, z)); c.scale(push * (1 + 1.4 * z), push * (1 + 1.4 * z)); c.translate(-fx, -fy)
    c.translate(0, -150 * up)
    night_world(c, t, roll, 1 - z)
    # explosions hinted inside the hood on "explosiones"
    t_ex = ws("gancho", "explosiones")
    hg = 0.0
    if t_ex - 0.1 < t < t_ex + 1.6: hg = 0.5 + 0.5 * math.sin((t - t_ex) * 30)
    c.save(); c.translate(CAR_X, CAR_Y)
    puffs(c, -404, 64, puff_phase(t), 1.0)
    car(c, t, wheel, beam=1.0, hood_glow=max(hg, z), bounce=2.5 * math.sin(t * 40) * sp)
    c.restore()
    if hg > 0:
        for j in range(3):
            u = ramp(t, t_ex + j * 0.3, t_ex + j * 0.3 + 0.45)
            if 0 < u < 1:
                bx, by = CAR_X + 250 + j * 40, CAR_Y - 110 - j * 20
                for m in range(8):
                    a = m * math.pi / 4 + j
                    line(c, [(bx + math.cos(a) * 20 * u, by + math.sin(a) * 20 * u), (bx + math.cos(a) * 60 * u, by + math.sin(a) * 60 * u)], alpha(YEL, 1 - u), 7)
    c.restore()
    # --- gancho infographics: tachometer, then 25 x 4 = 100
    t_mil = ws("gancho", "tres"); t_25 = ws("gancho", "veinticinco"); t_4 = ws("gancho", "cuatro"); t_100 = ws("gancho", "cien")
    k = eob(ramp(t, t_mil - 0.15, t_mil + 0.2)) * (1 - ease(ramp(t, t_25 - 0.5, t_25 - 0.2)))
    if k > 0.02:
        c.save(); c.translate(540, 790); c.scale(k, k)
        rrect(c, -170, -130, 340, 230, 30); fill_stroke(c, CREAM, INK, 6)
        for i in range(9):
            a = math.pi * (1.0 + i / 8)
            line(c, [(105 * math.cos(a), 30 + 105 * math.sin(a)), (125 * math.cos(a), 30 + 125 * math.sin(a))], RED if i >= 6 else INK, 6)
        need = math.pi * (1.0 + 0.5 * ease(ramp(t, t_mil, t_mil + 0.6))) + 0.03 * math.sin(t * 50)
        line(c, [(0, 30), (95 * math.cos(need), 30 + 95 * math.sin(need))], RED, 8)
        circle(c, 0, 30, 12); fill_stroke(c, INK, None)
        text(c, "3.000 RPM", 0, 86, 40, INK, SLAB, False)
        c.restore()
    ky = 820
    parts = [(t_25, "25", WHITE, 250), (t_25 + 0.4, "/s", CREAM, 345), (t_4, "× 4", WHITE, 540), (t_100, "= 100", YEL, 800)]
    fade = 1 - ease(ramp(t, t_up0 - 0.2, t_up0 + 0.2))
    for t0, s, col, x in parts:
        k = eob(ramp(t, t0 - 0.1, t0 + 0.2)) * fade
        if k <= 0.02: continue
        c.save(); c.translate(x, ky); c.scale(k, k)
        text(c, s, 0, 0, 96 if s != "/s" else 56, col, SLAB, False, outline=INK, olw=14)
        c.restore()
    if fade > 0 and t > t_25:
        k = ease(ramp(t, t_25, t_25 + 0.3)) * fade
        text(c, "EXPLOSIONES POR CILINDRO", 300, 880, 26, alpha(CREAM, k), SANS, True)
    if t > t_100:
        k = ease(ramp(t, t_100, t_100 + 0.3)) * fade
        text(c, "POR SEGUNDO", 800, 880, 26, alpha(YEL, k), SANS, True)
    # --- imposible: crossed badges + 1.000 kg
    if up > 0.01:
        for w, x, fn, lab in BADGES:
            t0 = ws("imposible", w) - 0.15
            k = eob(ramp(t, t0, t0 + 0.3)) * up
            icon_badge(c, x, 1490, k, lab, fn, t, t0 + 0.35)
        t_ton = ws("imposible", "tonelada") - 0.15
        kw = eob(ramp(t, t_ton, t_ton + 0.35)) * up
        weight_icon(c, 540, 760, kw)
        if kw > 0.5:
            text(c, "Y MUEVE MÁS DE", 540, 650, 34, alpha(CREAM, kw), SANS, True)
    # --- freno: engine cut-away grows out of the hood
    if xr > 0:
        c.save()
        s = lerp(0.35, 1.0, ease(xr))
        cxp = 540; cyp = lerp(1220, ROW_Y - 200, ease(xr))
        c.translate(cxp, cyp); c.scale(s, s); c.translate(-540, -(ROW_Y - 200))
        c.push_group(); background(c, t); engine_row(c, G_of(t), t); c.pop_group_to_source(); c.paint_with_alpha(xr)
        c.restore()

# ---------------------------------------------------------------- paso1: the 4-cylinder block
def syringe(c, x, y, k, plunge):
    """Vertical syringe, needle down, at (x, y) = top; plunge 0..1 (plunger position like the piston)."""
    if k <= 0.02: return
    c.save(); c.translate(x, y); c.scale(k, k)
    rrect(c, -40, 60, 80, 230, 12); fill_stroke(c, alpha(XRAY, 0.35), INK, 6)
    for j in range(5): line(c, [(-40, 100 + j * 36), (-16, 100 + j * 36)], alpha(INK, 0.7), 3)
    py = 80 + 140 * plunge
    rrect(c, -36, py, 72, 22, 6); fill_stroke(c, RED, INK, 4)
    c.rectangle(-36, py + 22, 72, 288 - py - 22); c.set_source_rgba(*alpha(AIRC, 0.5)); c.fill()
    line(c, [(0, py), (0, 20)], INK, 14); line(c, [(0, py), (0, 20)], CREAM2, 7)
    rrect(c, -46, 6, 92, 18, 8); fill_stroke(c, CREAM2, INK, 4)
    rrect(c, -60, 54, 120, 14, 6); fill_stroke(c, CREAM2, INK, 4)
    c.new_path(); c.move_to(-14, 290); c.line_to(14, 290); c.line_to(0, 318); c.close_path(); fill_stroke(c, CREAM2, INK, 4)
    line(c, [(0, 316), (0, 380)], METAL, 5)
    c.restore()

def scene_paso1(c, t):
    background(c, t, ORANGE)
    b = B("paso1")
    G = G_of(t)
    t_cil = ws("paso1", "cilindros"); t_4 = ws("paso1", "cuatro"); t_pis = ws("paso1", "pistón"); t_sube = ws("paso1", "sube")
    t_jer = ws("paso1", "jeringa") - 0.1
    hl = {}
    if t >= t_pis - 0.1: hl[0] = ease(ramp(t, t_pis - 0.1, t_pis + 0.2))
    c.save(); cam(c, 1.0 + 0.04 * ease(ramp(t, b["start"], b["end"])), W / 2, 1300)
    engine_row(c, G, t, hl=hl, num=ramp(t, t_4 - 0.1, t_4 + 0.5))
    c.restore()
    def sc(p): s = 1.0 + 0.04 * ease(ramp(t, b["start"], b["end"])); return (W / 2 + (p[0] - W / 2) * s, 1300 + (p[1] - 1300) * s)
    # CILINDROS: one label, four leader lines
    k = ramp(t, t_cil - 0.1, t_cil + 0.3) * (1 - ramp(t, t_pis - 0.6, t_pis - 0.3))
    if k > 0:
        lx, ly = 540, 700
        for i in range(4):
            ax, ay = sc(row_pt(i, -BORE - WALL / 2, HEAD_Y + 60))
            line(c, [(lx, ly + 30), (lerp(lx, ax, ease(k)), lerp(ly + 30, ay, ease(k)))], alpha(WHITE, 0.9 * k), 4)
            circle(c, ax, ay, 9 * k); c.set_source_rgba(*alpha(WHITE, k)); c.fill()
        c.save(); c.translate(lx, ly); c.scale(eob(k), eob(k))
        rrect(c, -150, -36, 300, 72, 12); fill_stroke(c, INK, alpha(WHITE, 0.95), 3)
        text(c, "CILINDROS", 0, 16, 44, YEL, SANS, True); c.restore()
    # PISTÓN on cylinder 1 + up/down arrow
    px, py = sc(row_pt(0, 0, crown_y(cyl_phi(0, G)) + 50))
    callout(c, "PISTÓN", px, py, 250, 720, t, t_pis)
    ka = ease(ramp(t, t_sube - 0.2, t_sube + 0.2)) * (1 - ramp(t, t_jer - 0.4, t_jer))
    if ka > 0:
        x0 = 105; ym = sc(row_pt(0, 0, -290))[1]
        line(c, [(x0, ym - 90 * ka), (x0, ym + 90 * ka)], YEL, 12)
        arrow(c, x0, ym, x0, ym - 110 * ka, YEL, 12, 36); arrow(c, x0, ym, x0, ym + 110 * ka, YEL, 12, 36)
    # syringe: plunger in step with piston 4
    ks = eob(ramp(t, t_jer, t_jer + 0.35))
    if ks > 0:
        p4 = (crown_y(cyl_phi(3, G)) - crown_y(0)) / (crown_y(180) - crown_y(0))
        syringe(c, 800, 600, ks, p4)
        if ks > 0.6: text(c, "JERINGA", 650, 760, 34, alpha(CREAM, ks), SANS, True)

# ---------------------------------------------------------------- paso2..4: single cylinder close-up
SX, SY, SS = 520, 1530, 1.35
def sp(x, y): return SX + x * SS, SY + y * SS

def flow_dots(c, pts, t, col, k, speed=1.0, n=14, r=9):
    if k <= 0: return
    L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(L)
    for j in range(n):
        d = ((j / n + t * 0.45 * speed) % 1) * tot; acc = 0
        for i, l in enumerate(L):
            if d <= acc + l:
                u = (d - acc) / l; x = lerp(pts[i][0], pts[i + 1][0], u); y = lerp(pts[i][1], pts[i + 1][1], u)
                circle(c, x, y + 6 * math.sin(j * 2.1 + t * 4), r); c.set_source_rgba(*alpha(col, 0.9 * k)); c.fill(); break
            acc += l

def intake_pipe(c, flow, t, fuel=0.0):
    """Intake pipe from the left edge to the intake port, with port fuel injector."""
    x1, y1 = sp(-150, HEAD_Y - 62)
    rrect(c, 50, y1 - 34, x1 - 50 + 4, 68, 16); fill_stroke(c, METAL, INK, 6)
    c.rectangle(56, y1 - 18, x1 - 56, 36); c.set_source_rgba(*CAVE); c.fill()
    if flow > 0:
        c.rectangle(56, y1 - 18, x1 - 56, 36); c.set_source_rgba(*alpha(AIRC, 0.4 * flow)); c.fill()
        for j in range(4):
            u = (t * 0.9 + j / 4) % 1
            x = lerp(70, x1 - 20, u)
            arrow(c, x - 30, y1, x + 20, y1, alpha(WHITE, 0.9 * flow * math.sin(math.pi * u)), 6, 20)
    # injector
    ix = x1 - 70
    rrect(c, ix - 16, y1 - 120, 32, 90, 8); fill_stroke(c, STEEL, INK, 5)
    rrect(c, ix - 8, y1 - 140, 16, 24, 4); fill_stroke(c, METAL, INK, 3)
    if fuel > 0:
        for j in range(10):
            u = (t * 1.6 + j / 10) % 1
            x = ix + u * 55 + 10 * math.sin(j * 3); y = y1 - 28 + u * 30 + 8 * math.cos(j * 5)
            circle(c, x, y, 5 + 2 * (j % 2)); c.set_source_rgba(*alpha(FUEL, fuel * (1 - u * 0.5))); c.fill()
    return ix, y1

def exhaust_pipe(c, flow, t):
    x0, y0 = sp(150, HEAD_Y - 62)
    rrect(c, x0 - 4, y0 - 34, 905 - x0, 68, 16); fill_stroke(c, METAL, INK, 6)
    c.rectangle(x0, y0 - 18, 905 - x0 - 10, 36); c.set_source_rgba(*CAVE); c.fill()
    if flow > 0:
        c.rectangle(x0, y0 - 18, 895 - x0, 36); c.set_source_rgba(*alpha(SMOKE, 0.6 * flow)); c.fill()
        for j in range(4):
            u = (t * 0.9 + j / 4) % 1; x = lerp(x0 + 10, 880, u)
            arrow(c, x - 20, y0, x + 30, y0, alpha(WHITE, 0.8 * flow * math.sin(math.pi * u)), 6, 20)
    return x0, y0

def smoke_out(c, x, y, t, k):
    if k <= 0: return
    for j in range(5):
        u = (t * 0.5 + j / 5) % 1
        r = 18 + 50 * u
        circle(c, x + 10 + u * 40 + 10 * math.sin(j), y - u * 260, r)
        fill_stroke(c, alpha(SMOKE, k * 0.8 * (1 - u)), alpha(INK, k * 0.5 * (1 - u)), 3)

def single(c, phi, t, **kw):
    c.save(); c.translate(SX, SY); c.scale(SS, SS); engine_side(c, phi, t, **kw); c.restore()

def phi_paso2(t):
    a0, a1 = ws("paso2", "baja"), ws("paso2", "gasolina", ) + 0.5
    b0, b1 = ws("paso2", "sube"), ws("paso2", "diminuto") + 0.3
    if t < b0: return 180 * ease(ramp(t, a0, a1))
    return 180 + 180 * ease(ramp(t, b0, b1))

def scene_paso2(c, t):
    background(c, t, COLD)
    b = B("paso2")
    phi = phi_paso2(t)
    c.save(); cam(c, 1.0 + 0.04 * ramp(t, b["start"], b["end"]), W / 2, 1200)
    t_asp = ws("paso2", "aspira"); t_air = ws("paso2", "aire"); t_gas = ws("paso2", "gasolina")
    t_apr = ws("paso2", "aprieta"); t_dim = ws("paso2", "diminuto")
    li = lift_in(phi)
    intake_pipe(c, li, t, fuel=li * ramp(t, t_gas - 0.3, t_gas))
    exhaust_pipe(c, 0, t)
    single(c, phi, t, spark=0.0)
    if li > 0.05:  # air + droplets pulled through the open valve
        flow_dots(c, [sp(-150, HEAD_Y - 62), sp(-VX, HEAD_Y - 40), sp(-VX, HEAD_Y + 30), sp(-20, HEAD_Y + 90)], t, AIRC, li, 1.5, 10, 8)
    c.restore()
    s = 1.0 + 0.04 * ramp(t, b["start"], b["end"])
    def sc(p): return (W / 2 + (p[0] - W / 2) * s, 1200 + (p[1] - 1200) * s)
    # piston down arrow on "baja"
    kd = ramp(t, ws("paso2", "baja") - 0.1, ws("paso2", "baja") + 0.2) * (1 - ramp(t, t_gas + 0.4, t_gas + 0.7))
    if kd > 0:
        x, y = sc(sp(0, crown_y(phi) + 55)); arrow(c, x, y - 30, x, y + 110, alpha(YEL, kd), 16, 46)
    callout(c, "VÁLVULA ABIERTA", *sc(sp(-VX - 20, HEAD_Y + 10)), 210, 1240, t, t_asp - 0.1) if t < ws("paso2", "sube") else None
    callout(c, "AIRE", *sc((150, sp(0, HEAD_Y - 62)[1])), 160, 700, t, t_air, XRAY)
    ix, iy = sp(-150, HEAD_Y - 62)
    callout(c, "GASOLINA", *sc((ix - 70, iy - 140)), 420, 690, t, t_gas, FUEL)
    # compression: both valves closed + squeeze arrows + tiny space
    if t >= t_apr - 0.2:
        k = ease(ramp(t, t_apr - 0.2, t_apr + 0.2))
        yc = crown_y(phi)
        for sx in (-1, 1):
            x, y = sc(sp(sx * (BORE + 70), (HEAD_Y + yc) / 2))
            arrow(c, x, y, x - sx * 40 * k, y, alpha(HOT, k), 10, 28)
        lab = "VÁLVULAS CERRADAS"
        callout(c, lab, *sc(sp(VX, HEAD_Y + 4)), 760, 1660, t, t_apr - 0.1)
    if t >= t_dim - 0.2:
        k = ease(ramp(t, t_dim - 0.2, t_dim + 0.2))
        x = sc(sp(BORE + WALL + 40, 0))[0]
        y0 = sc(sp(0, HEAD_Y))[1]; y1 = sc(sp(0, crown_y(phi)))[1]
        line(c, [(x, y0), (x, y1)], alpha(YEL, k), 6)
        line(c, [(x - 16, y0), (x + 16, y0)], alpha(YEL, k), 6); line(c, [(x - 16, y1), (x + 16, y1)], alpha(YEL, k), 6)
        line(c, [(x + 20, (y0 + y1) / 2), (x + 70, 760)], alpha(WHITE, 0.8 * k), 3)
        c.save(); c.translate(820, 740); c.scale(eob(k), eob(k))
        rrect(c, -120, -34, 240, 68, 12); fill_stroke(c, INK, alpha(WHITE, 0.95), 3)
        text(c, "DIMINUTO", 0, 13, 36, YEL, SANS, True); c.restore()
    # stroke name
    nm, col = ("ADMISIÓN", XRAY) if t < ws("paso2", "sube") - 0.2 else ("COMPRESIÓN", AIRC)
    ks = ramp(t, ws("paso2", "baja") - 0.2, ws("paso2", "baja") + 0.2)
    if ks > 0: text(c, nm, 540, 640, 56, alpha(col, ks), SLAB, False, outline=INK, olw=10)

def phi_paso3(t):
    return 360 + 180 * ease(ramp(t, ws("paso3", "empuja") - 0.1, ws("paso3", "fuerza") + 0.2))

def scene_paso3(c, t):
    t_ch = ws("paso3", "chispa"); t_ex = ws("paso3", "explota"); t_emp = ws("paso3", "empuja"); t_fu = ws("paso3", "fuerza")
    kb = ease(ramp(t, t_ex - 0.1, t_ex + 0.25))
    background(c, t, mix(COLD, HOT, kb))
    b = B("paso3")
    phi = phi_paso3(t)
    shake = 10 * pulse_at(t, t_ex - 0.05, 0.5)
    c.save(); cam(c, 1.0 + 0.04 * ramp(t, b["start"], b["end"]), W / 2, 1200)
    c.translate(shake * math.sin(t * 70), shake * math.cos(t * 61))
    intake_pipe(c, 0, t); exhaust_pipe(c, 0, t)
    # spark: crackles on "chispa" (a couple of flashes), explosion from "explota"
    sk = 0.0
    for j, dt in enumerate((0.0, 0.18, 0.42)):
        sk = max(sk, pulse_at(t, t_ch - 0.05 + dt, 0.22))
    if t_ex - 0.12 < t < t_ex + 0.05: sk = max(sk, 1.0)
    u = ramp(t, t_ex - 0.05, t_fu + 0.6)
    if t < t_ex - 0.05:
        st = dict(col=hx("#8FB6FF"), a=0.9, drops=1.0, fire=0.0, smoke=0.0, press=1.0)
    else:
        fire = clamp(1.15 - 0.6 * u) * ease(ramp(t, t_ex - 0.05, t_ex + 0.15))
        st = dict(col=mix(YEL, HOT, ease(u * 2)), a=0.95, drops=0.0, fire=fire, smoke=0.0)
    single(c, phi, t, st=st, spark=sk)
    if t >= t_ex - 0.05:  # glow spilling out of the chamber
        k = clamp(1.2 - u) * ease(ramp(t, t_ex - 0.05, t_ex + 0.15))
        glow(c, *sp(0, (HEAD_Y + crown_y(phi)) / 2), 420, ORANGE, 0.55 * k)
        rr = 1 - ramp(t, t_ex, t_ex + 0.6)
        if rr > 0:
            x, y = sp(0, HEAD_Y + 60)
            for m in range(12):
                a = m * math.pi / 6
                r0, r1 = 230 + 160 * (1 - rr), 290 + 220 * (1 - rr)
                line(c, [(x + math.cos(a) * r0, y + math.sin(a) * r0 * 0.8), (x + math.cos(a) * r1, y + math.sin(a) * r1 * 0.8)], alpha(YEL, rr), 10)
    c.restore()
    s = 1.0 + 0.04 * ramp(t, b["start"], b["end"])
    def sc(p): return (W / 2 + (p[0] - W / 2) * s, 1200 + (p[1] - 1200) * s)
    fo = 1 - ramp(t, t_ex - 0.15, t_ex + 0.05)
    callout_a(c, fo, "BUJÍA", *sc(sp(0, -540)), 300, 700, t, ws("paso3", "bujía") - 0.1)
    callout_a(c, fo, "CHISPA", *sc(sp(10, HEAD_Y + 6)), 800, 700, t, t_ch, YEL)
    ke = eob(ramp(t, t_ex - 0.05, t_ex + 0.3)) * (1 - ramp(t, t_emp - 0.2, t_emp + 0.1))
    if ke > 0:
        c.save(); c.translate(540, 680); c.scale(ke, ke); c.rotate(-0.06)
        text(c, "¡BUM!", 0, 30, 110, YEL, SLAB, False, outline=INK, olw=16); c.restore()
    kf = ease(ramp(t, t_emp - 0.15, t_emp + 0.25))
    if kf > 0:  # big force arrow pushing the piston down
        x, y = sc(sp(0, crown_y(phi)))
        L = 200 * kf + 60 * pulse_at(t, t_fu - 0.1, 0.5)
        arrow(c, x, y - 60, x, y + 20 + L, INK, 58, 110)
        arrow(c, x, y - 58, x, y + 6 + L, YEL, 38, 90)
    if t >= t_fu - 0.2:
        k = eob(ramp(t, t_fu - 0.2, t_fu + 0.15))
        x, y = sc(sp(0, crown_y(phi)))
        c.save(); c.translate(810, 1250); c.scale(k, k)
        text(c, "¡FUERZA!", 0, 20, 64, YEL, SLAB, False, outline=INK, olw=12); c.restore()
    nm_k = ramp(t, t_ex - 0.1, t_ex + 0.2)
    if nm_k > 0 and t > t_emp - 0.2:
        text(c, "EXPLOSIÓN", 540, 640, 56, alpha(ORANGE, ramp(t, t_emp - 0.2, t_emp + 0.1)), SLAB, False, outline=INK, olw=10)

# ---- paso4: exhaust stroke, then the 4-stroke cycle grid
def phi_paso4(t): return 540 + 180 * ease(ramp(t, ws("paso4", "subir") - 0.4, ws("paso4", "escape") + 0.3))
GRID = [("ADMISIÓN", 90, XRAY, 0), ("COMPRESIÓN", 270, AIRC, 1), ("EXPLOSIÓN", 390, ORANGE, 3), ("ESCAPE", 630, SMOKE, 2)]
GPOS = [(300, 900), (760, 900), (300, 1400), (760, 1400)]   # slot index -> centre

def scene_paso4(c, t):
    background(c, t, SMOKE)
    b = B("paso4")
    t_grid = ws("paso4", "admisión") - 0.45
    g = ease(ramp(t, t_grid, t_grid + 0.45))
    phi = phi_paso4(t)
    t_q = ws("paso4", "quemados"); t_esc = ws("paso4", "escape")
    if g < 1:
        c.push_group()
        c.save(); cam(c, 1.0 + 0.04 * ramp(t, b["start"], t_grid), W / 2, 1200)
        intake_pipe(c, 0, t)
        le = lift_ex(phi)
        x0, y0 = exhaust_pipe(c, le, t)
        smoke_out(c, 905, y0 - 30, t, le)
        single(c, phi, t, st=dict(col=SMOKE, a=0.75, drops=0, fire=0, smoke=1))
        if le > 0.05:
            flow_dots(c, [sp(20, HEAD_Y + 80), sp(VX, HEAD_Y + 20), sp(VX, HEAD_Y - 40), sp(150, HEAD_Y - 62), (880, y0)], t, SMOKE, le, 1.5, 12, 10)
        kd = ramp(t, ws("paso4", "subir") - 0.4, ws("paso4", "subir")) * (1 - ramp(t, t_esc, t_esc + 0.3))
        if kd > 0:
            x, y = sp(0, crown_y(phi) + 60); arrow(c, x, y + 60, x, y - 80, alpha(YEL, kd), 16, 46)
        c.restore()
        s = 1.0 + 0.04 * ramp(t, b["start"], t_grid)
        def sc(p): return (W / 2 + (p[0] - W / 2) * s, 1200 + (p[1] - 1200) * s)
        callout(c, "GASES QUEMADOS", *sc(sp(-30, HEAD_Y + 60)), 300, 700, t, t_q - 0.1, CREAM)
        callout(c, "TUBO DE ESCAPE", *sc((760, y0)), 740, 1660, t, ws("paso4", "tubo") - 0.1, CREAM)
        callout(c, "VÁLVULA DE ESCAPE", *sc(sp(VX + 20, HEAD_Y + 20)), 780, 700, t, ws("paso4", "echa") - 0.1, CREAM, 30) if t < t_q - 0.1 else None
        ks = ramp(t, ws("paso4", "subir") - 0.4, ws("paso4", "subir"))
        if ks > 0: text(c, "ESCAPE", 540, 640, 56, alpha(LAV, ks), SLAB, False, outline=INK, olw=10)
        c.pop_group_to_source(); c.paint_with_alpha(1 - g)
    if g > 0:
        c.push_group()
        words = [ws("paso4", "admisión"), ws("paso4", "compresión"), ws("paso4", "explosión"), wt("paso4", "escape", 1)]
        t_v = ws("paso4", "vuelta") - 0.1
        cur = max([i for i, w in enumerate(words) if t >= w - 0.15] or [-1])
        if t >= t_v: cur = 0 if (t - t_v) < 0.6 else -1
        # arrows between panels (clockwise cycle)
        arrs = [((450, 900), (610, 900)), ((760, 1110), (760, 1190)), ((610, 1400), (450, 1400)), ((300, 1190), (300, 1110))]
        for j, (p0, p1) in enumerate(arrs):
            on = t >= words[(j + 1) % 4] - 0.15 if j < 3 else t >= t_v
            arrow(c, *p0, *p1, YEL if on else alpha(CREAM, 0.35), 12, 34)
        for i, (name, ph0, col, slot) in enumerate(GRID):
            x, y = GPOS[slot]
            k = eob(ramp(t, t_grid + 0.08 * i, t_grid + 0.08 * i + 0.4))
            active = (i == cur)
            c.save(); c.translate(x, y); c.scale(k * (1.06 if active else 1.0), k * (1.06 if active else 1.0))
            rrect(c, -190, -230, 380, 460, 26); fill_stroke(c, alpha(DARK, 0.95), YEL if active else INK, 8 if active else 5)
            # mini cylinder: animate its own stroke while active
            if active and i < 4:
                w0 = words[i] if not (t >= t_v and i == 0) else t_v
                ph = ph0 - 90 + 180 * ease(ramp(t, w0 - 0.1, w0 + 0.55))
            else: ph = ph0
            st = gas_state(ph)
            if name == "EXPLOSIÓN": st = dict(col=ORANGE, a=0.95, drops=0, fire=0.9, smoke=0)
            c.save(); c.translate(0, 150); c.scale(0.5, 0.5)
            engine_side(c, ph, t, st=st, spark=(1.0 if name == "EXPLOSIÓN" and active and math.sin(t * 40) > 0 else 0.0))
            c.restore()
            if not active: rrect(c, -190, -230, 380, 460, 26); c.set_source_rgba(0, 0, 0, 0.35); c.fill()
            sz = fit_size(c, name, SLAB, 40, 330)
            text(c, name, 0, -175, sz, col if active else alpha(CREAM, 0.7), SLAB, False, outline=INK, olw=8)
            text(c, str(i + 1), -160, 212, 30, alpha(CREAM, 0.6), SLAB, False)
            c.restore()
        if t >= t_v:
            k = eob(ramp(t, t_v, t_v + 0.35))
            c.save(); c.translate(530, 1150); c.scale(k, k)
            circle(c, 0, 0, 62); fill_stroke(c, YEL, INK, 6)
            c.new_path(); c.arc(0, 0, 36, 0.3, 5.6); c.set_source_rgba(*INK); c.set_line_width(10); c.stroke()
            arrow(c, 36 * math.cos(5.3), 36 * math.sin(5.3), 36 * math.cos(5.9) + 6, 36 * math.sin(5.9) + 10, INK, 8, 24)
            c.restore()
        c.pop_group_to_source(); c.paint_with_alpha(g)

# ---------------------------------------------------------------- paso5: crankshaft = pedals
P5X, P5Y, P5S = 330, 1530, 1.1
def leg_and_pedal(c, th, k, t):
    """Cartoon leg pushing a bike pedal crank; th = crank angle (same convention as the engine)."""
    if k <= 0.02: return
    cx, cy = 790, 1500; r = 70
    hipx, hipy = 760, 1150
    px, py = cx + r * math.sin(th), cy - r * math.cos(th)
    c.save(); c.translate(cx, cy); c.scale(k, k); c.translate(-cx, -cy)
    # chainring + crank arms
    circle(c, cx, cy, 52); fill_stroke(c, METAL, INK, 5)
    for j in range(16):
        a = j * math.pi / 8; line(c, [(cx + 50 * math.cos(a), cy + 50 * math.sin(a)), (cx + 60 * math.cos(a), cy + 60 * math.sin(a))], INK, 5)
    ox, oy = cx - r * math.sin(th), cy + r * math.cos(th)
    line(c, [(cx, cy), (ox, oy)], alpha(INK, 0.6), 14)
    # bike frame: seat post from the saddle down to the crank, saddle under the hip
    line(c, [(hipx - 10, hipy + 40), (cx, cy)], INK, 26); line(c, [(hipx - 10, hipy + 40), (cx, cy)], RED, 16)
    line(c, [(cx, cy), (cx + 170, cy - 20)], INK, 22); line(c, [(cx, cy), (cx + 170, cy - 20)], RED, 12)
    rrect(c, hipx - 70, hipy + 18, 120, 30, 14); fill_stroke(c, INK, None)
    shx, shy = 860, 900
    line(c, [(shx, shy), (930, 1040)], INK, 34); line(c, [(shx, shy), (930, 1040)], hx("#F2B48E"), 22)
    line(c, [(930, 1040), (cx + 170, cy - 20)], INK, 14)
    c.new_path(); c.move_to(hipx - 30, hipy + 10); c.line_to(hipx + 30, hipy + 20); c.line_to(shx + 30, shy + 10); c.line_to(shx - 30, shy - 20); c.close_path()
    fill_stroke(c, YEL, INK, 5)
    circle(c, shx + 20, shy - 75, 48); fill_stroke(c, hx("#F2B48E"), INK, 5)
    c.new_path(); c.arc(shx + 20, shy - 85, 52, math.pi, 2 * math.pi); c.close_path(); fill_stroke(c, RED, INK, 5)
    # leg (2-link IK)
    l1, l2 = 220, 220
    d = min(math.dist((hipx, hipy), (px, py)), l1 + l2 - 1)
    a0 = math.atan2(py - hipy, px - hipx)
    aa = math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1))
    kx, ky = hipx + l1 * math.cos(a0 - aa), hipy + l1 * math.sin(a0 - aa)
    line(c, [(hipx, hipy), (kx, ky)], INK, 64); line(c, [(hipx, hipy), (kx, ky)], STEEL, 50)
    line(c, [(kx, ky), (px - 10, py - 20)], INK, 50); line(c, [(kx, ky), (px - 10, py - 20)], hx("#F2B48E"), 38)
    circle(c, kx, ky, 26); fill_stroke(c, STEEL, INK, 5)
    circle(c, hipx, hipy, 40); fill_stroke(c, STEEL, INK, 5)
    rrect(c, px - 50, py - 36, 80, 30, 12); fill_stroke(c, RED, INK, 5)   # shoe
    line(c, [(cx, cy), (px, py)], INK, 26); line(c, [(cx, cy), (px, py)], CRANK, 16)
    rrect(c, px - 34, py - 8, 68, 16, 5); fill_stroke(c, INK, None)
    circle(c, cx, cy, 14); fill_stroke(c, INK, None)
    c.restore()

def wheel(c, x, y, r, ang, k):
    if k <= 0.02: return
    c.save(); c.translate(x, y); c.scale(k, k)
    circle(c, 0, 0, r); fill_stroke(c, hx("#24212F"), INK, 7)
    circle(c, 0, 0, r * 0.62); fill_stroke(c, CREAM2, INK, 5)
    for j in range(5):
        a = ang + j * 2 * math.pi / 5; line(c, [(0, 0), (r * 0.55 * math.cos(a), r * 0.55 * math.sin(a))], alpha(INK, 0.75), 7)
    circle(c, 0, 0, 12); fill_stroke(c, RED, INK, 4)
    c.restore()

def scene_paso5(c, t):
    background(c, t, ORANGE)
    b = B("paso5")
    G = G_of(t) + 90
    phi = G % 720; th = math.radians(phi % 360)
    t_pis = ws("paso5", "pistones"); t_rue = ws("paso5", "ruedas"); t_gir = ws("paso5", "giran"); t_cig = ws("paso5", "cigüeñal")
    t_conv = ws("paso5", "convierte"); t_vue = ws("paso5", "vueltas"); t_pie = ws("paso5", "piernas"); t_ped = ws("paso5", "pedales")
    c.save(); c.translate(P5X, P5Y); c.scale(P5S, P5S)
    engine_side(c, phi, t)
    if t >= t_cig - 0.1:  # crank highlight ring
        k = ease(ramp(t, t_cig - 0.1, t_cig + 0.3))
        c.new_path(); c.arc(0, 0, 135, 0, 2 * math.pi); c.set_source_rgba(*alpha(YEL, 0.8 * k)); c.set_line_width(8); c.stroke()
    c.restore()
    # up/down arrow next to the piston
    ka = ease(ramp(t, t_pis - 0.1, t_pis + 0.3))
    if ka > 0:
        x0 = P5X - 235; ym = P5Y + (-290) * P5S
        arrow(c, x0, ym, x0, ym - 100 * ka, YEL, 12, 36); arrow(c, x0, ym, x0, ym + 100 * ka, YEL, 12, 36)
        text(c, "SUBE", x0, ym - 125, 28, alpha(YEL, ka), SANS, True); text(c, "BAJA", x0, ym + 150, 28, alpha(YEL, ka), SANS, True)
    # rotation arrow around the crank
    kr = ease(ramp(t, t_conv - 0.1, t_conv + 0.3))
    if kr > 0:
        r = 165 * P5S; a0 = th - 0.2
        c.new_path(); c.arc(P5X, P5Y, r, a0 - 1.6 * kr - math.pi / 2, a0 - math.pi / 2); c.set_source_rgba(*YEL); c.set_line_width(12); c.stroke()
        ae = a0 - math.pi / 2
        ex, ey = P5X + r * math.cos(ae), P5Y + r * math.sin(ae)
        arrow(c, ex - 30 * math.cos(ae + math.pi / 2), ey - 30 * math.sin(ae + math.pi / 2), ex + 8 * math.cos(ae + math.pi / 2), ey + 8 * math.sin(ae + math.pi / 2), YEL, 12, 36)
    callout(c, "CIGÜEÑAL", P5X + 60, P5Y + 40, 220, 1690, t, t_cig)
    # wheel (turns with the crank, through the gearbox)
    kw = eob(ramp(t, t_rue - 0.1, t_rue + 0.3)) * (1 - ease(ramp(t, t_pie - 0.5, t_pie - 0.1)))
    if kw > 0.02:
        wheel(c, 780, 1000, 160, math.radians(G) * 0.5 if t > t_gir else 0, kw)
        if t > t_gir:
            c.new_path(); c.arc(780, 1000, 190, -2.4, -0.6); c.set_source_rgba(*alpha(YEL, kw)); c.set_line_width(12); c.stroke()
            arrow(c, 780 + 190 * math.cos(-0.9), 1000 + 190 * math.sin(-0.9), 780 + 190 * math.cos(-0.5), 1000 + 190 * math.sin(-0.5), alpha(YEL, kw), 12, 36)
        text(c, "RUEDA", 780, 1220, 36, alpha(CREAM, kw), SANS, True)
        if t > t_vue - 0.1:
            k = ease(ramp(t, t_vue - 0.1, t_vue + 0.3)) * kw
            line(c, [(P5X + 150, P5Y), (600, P5Y), (600, 1130)], alpha(CRANK, k), 14)
            text(c, "VUELTAS", 780, 750, 46, alpha(YEL, k), SLAB, False, outline=INK, olw=8)
    # leg + pedals, crank in step with the engine's crank
    kl = eob(ramp(t, t_pie - 0.2, t_pie + 0.3))
    leg_and_pedal(c, th, kl, t)
    if kl > 0.5:
        k = ease(ramp(t, t_ped - 0.1, t_ped + 0.3))
        text(c, "=", 560, 1530, 110, alpha(YEL, k), SLAB, False, outline=INK, olw=10)
        text(c, "PEDALES", 790, 1660, 40, alpha(CREAM, k), SLAB, False, outline=INK, olw=8)
        text(c, "DE UNA BICI", 790, 1700 - 0, 26, alpha(CREAM, k), SANS, True) if False else None

# ---------------------------------------------------------------- junto + acelera
JUNTO = [("aire", "AIRE", XRAY), ("gasolina", "GASOLINA", FUEL), ("compresión", "COMPRESIÓN", AIRC),
         ("chispa", "CHISPA", YEL), ("explosión", "EXPLOSIÓN", ORANGE), ("vuelta", "VUELTA", CREAM)]
JPOS = {"aire": (170, 690), "gasolina": (470, 690), "compresión": (790, 690), "chispa": (200, 820), "explosión": (530, 820), "vuelta": (330, 1690)}

def junto_anchor(word):
    """Pick the cylinder that is in the matching stroke when the word is said."""
    t0 = ws("junto", word); G = G_of(t0)
    want = {"aire": (0, 180), "gasolina": (0, 180), "compresión": (180, 360), "chispa": (330, 400), "explosión": (360, 540)}
    if word == "vuelta": return (ROW_X[0] - 125 * ROW_S - 36, ROW_Y - 60)
    lo, hi = want[word]
    best = min(range(4), key=lambda i: 0 if lo <= cyl_phi(i, G) < hi else min(abs(cyl_phi(i, G) - lo), abs(cyl_phi(i, G) - hi)))
    if word == "aire": return row_pt(best, -VX, HEAD_TOP - 50)
    if word == "chispa": return row_pt(best, 0, HEAD_Y + 6)
    if word == "gasolina": return row_pt(best, 20, HEAD_Y + 40)
    return row_pt(best, 0, (HEAD_Y + crown_y(cyl_phi(best, G))) / 2 + 10)
_JA = {}

def scene_all(c, t):
    b = B("junto")
    t_end = B("remate")["start"]
    fast = ease(ramp(t, T_REAL + 0.2, t_end - 0.4))
    background(c, t, mix(ORANGE, HOT, fast))
    shake = 7 * fast
    zc = 1.0 + 0.05 * ease(ramp(t, b["start"], t_end))
    c.save(); cam(c, zc, W / 2, 1300)
    c.translate(shake * math.sin(t * 60), shake * math.cos(t * 53))
    G, dG = engine_row_blur(c, t)
    if fast > 0.05:  # flickering sparks at real speed
        rnd = random.Random(int(t * 30))
        for i in range(4):
            if rnd.random() < 0.45 + 0.4 * fast:
                c.save(); c.translate(ROW_X[i], ROW_Y); c.scale(ROW_S, ROW_S)
                spark_draw(c, 0, HEAD_Y + 6, 0.8, t, 1.2); glow(c, 0, HEAD_Y + 60, 160, ORANGE, 0.5 * fast)
                c.restore()
    c.restore()
    def sc(p): return (W / 2 + (p[0] - W / 2) * zc, 1300 + (p[1] - 1300) * zc)
    la = 1 - ramp(t, T_REAL - 0.6, T_REAL + 0.2)
    if la > 0:
        c.push_group()
        for w, lab, col in JUNTO:
            if w not in _JA: _JA[w] = junto_anchor(w)
            callout(c, lab, *sc(_JA[w]), *JPOS[w], t, ws("junto", w) - 0.05, col)
        if t > ws("junto", "vuelta") - 0.1:  # rotation arrow round the flywheel
            k = ease(ramp(t, ws("junto", "vuelta") - 0.1, ws("junto", "vuelta") + 0.3))
            x, y = sc((ROW_X[0] - 125 * ROW_S - 36, ROW_Y))
            c.save(); c.translate(x, y); c.scale(0.45, 1)
            c.new_path(); c.arc(0, 0, 150, -math.pi * 0.9, -math.pi * 0.9 + 4.2 * k); c.restore()
            c.set_source_rgba(*YEL); c.set_line_width(9); c.stroke()
        c.pop_group_to_source(); c.paint_with_alpha(la)
    if fast > 0:  # speed lines
        for i in range(26):
            r0 = 320 + (i * 97 + t * 2600) % 900; a = i * 0.24
            line(c, [(540 + math.cos(a) * r0, 1250 + math.sin(a) * r0), (540 + math.cos(a) * (r0 + 140 * fast), 1250 + math.sin(a) * (r0 + 140 * fast))],
                 alpha(WHITE, 0.35 * fast), 5)
    if t > T_REAL - 0.2:
        k = ease(ramp(t, T_REAL - 0.2, T_REAL + 0.3))
        rpm = 3000 * (1 - slow_log(t) / CFG["hud"]["max_log"]) + 30 * (1 - fast)
        rps = 360 * RPS * (anim_time(t + 0.05) - anim_time(t)) / 0.05 / 360 * 60
        c.save(); c.translate(540, 760); c.scale(k, k)
        rrect(c, -230, -70, 460, 120, 20); fill_stroke(c, alpha(INK, 0.9), alpha(WHITE, 0.9), 3)
        text(c, f"{dots(rps)} RPM", 0, 22, 64, YEL, MONO, True)
        c.restore()
    flash = ramp(t, t_end - 0.45, t_end - 0.3) * (1 - ramp(t, t_end - 0.3, t_end - 0.1))
    if flash > 0: c.set_source_rgba(1, 1, 1, 0.85 * flash); c.paint()

# ---------------------------------------------------------------- remate: diesel, no spark plug
RX, RY, RS = 470, 1560, 1.2
def phi_remate(t):
    a0 = ws("remate", "aprietan") - 0.1; a1 = ws("remate", "calienta") + 0.2
    e0 = ws("remate", "enciende")
    return 180 + 180 * ease(ramp(t, a0, a1)) + 150 * ease(ramp(t, e0, e0 + 1.4))

def scene_remate(c, t):
    b = B("remate")
    t_bu = ws("remate", "bujía"); t_ap = ws("remate", "aprietan"); t_ca = ws("remate", "calienta")
    t_co = ws("remate", "combustible"); t_en = ws("remate", "enciende")
    heat = ease(ramp(t, t_ca - 0.2, t_ca + 0.8))
    fire = ease(ramp(t, t_en - 0.05, t_en + 0.2)) * (1 - 0.5 * ramp(t, t_en + 0.4, t_en + 1.5))
    background(c, t, mix(STEEL, HOT, max(heat * 0.6, fire)))
    phi = phi_remate(t)
    c.save(); cam(c, 1.0 + 0.05 * ramp(t, b["start"], T_LOOP), W / 2, 1200)
    sh = 9 * pulse_at(t, t_en, 0.5); c.translate(sh * math.sin(t * 70), sh * math.cos(t * 50))
    if fire > 0:
        st = dict(col=ORANGE, a=0.95, drops=0, fire=fire, smoke=0)
    else:
        st = dict(col=mix(AIRC, HOT, heat), a=0.35 + 0.5 * ramp(t, t_ap, t_ca) + 0.1 * heat, drops=0, fire=0, smoke=0)
    c.save(); c.translate(RX, RY); c.scale(RS, RS)
    engine_side(c, phi, t, diesel=True, st=st, spark=0.0)
    # hot glow of the squeezed air
    yc = crown_y(phi)
    if heat > 0 and fire <= 0:
        c.save(); c.rectangle(-BORE, HEAD_Y, 2 * BORE, yc - HEAD_Y); c.clip()
        glow(c, 0, (HEAD_Y + yc) / 2, 160, HOT, 0.9 * heat); glow(c, 0, (HEAD_Y + yc) / 2, 70, YEL, 0.7 * heat)
        c.restore()
    # fuel spray from the injector
    ksp = ramp(t, t_co - 0.1, t_co + 0.2) * (1 - ramp(t, t_en + 0.3, t_en + 0.6))
    if ksp > 0:
        c.save(); c.rectangle(-BORE, HEAD_Y, 2 * BORE, yc - HEAD_Y); c.clip()
        rnd = random.Random(int(t * 30))
        for j in range(26):
            a = math.pi / 2 + rnd.uniform(-0.7, 0.7); r = rnd.uniform(8, 120) * ksp
            circle(c, math.cos(a) * r, HEAD_Y + 6 + math.sin(a) * r, rnd.uniform(3, 6)); c.set_source_rgba(*alpha(FUEL, 0.95)); c.fill()
        c.restore()
    if fire > 0.3: glow(c, 0, (HEAD_Y + yc) / 2, 330, ORANGE, 0.6 * fire)
    c.restore()
    c.restore()
    # crossed spark-plug badge
    kb = eob(ramp(t, t_bu - 0.15, t_bu + 0.2))
    icon_badge(c, 830, 890, kb, "SIN BUJÍA", ic_plug, t, t_bu + 0.2, 95)
    # thermometer
    kt = ramp(t, t_ca - 0.5, t_ca)
    if kt > 0:
        x, y0, y1 = 860, 1100, 1460
        c.save(); c.translate(x, y1); c.scale(kt, kt); c.translate(-x, -y1)
        rrect(c, x - 26, y0, 52, y1 - y0, 26); fill_stroke(c, CREAM, INK, 6)
        circle(c, x, y1 + 20, 46); fill_stroke(c, mix(COLD, HOT, heat), INK, 6)
        lv = lerp(y1 - 40, y0 + 30, heat)
        rrect(c, x - 12, lv, 24, y1 - lv + 10, 12); c.set_source_rgba(*mix(COLD, HOT, heat)); c.fill()
        c.restore()
        if heat > 0.3: text(c, "+500 °C", 860, 1580, 44, alpha(HOT, heat), SLAB, False, outline=INK, olw=8)
    callout_a(c, 1 - ramp(t, t_en - 0.3, t_en), "AIRE APRETADO", RX + 0, RY + (HEAD_Y + 40) * RS, 250, 680, t, t_ap)
    kd = ramp(t, ws("remate", "diésel") - 0.1, ws("remate", "diésel") + 0.2) * (1 - ramp(t, t_ap - 0.3, t_ap))
    if kd > 0: text(c, "MOTOR DIÉSEL", 540, 700, 64, alpha(CREAM, kd), SLAB, False, outline=INK, olw=10)
    callout(c, "INYECTOR", RX, RY - 520 * RS, 470, 640, t, t_co - 0.1) if t < t_en - 0.3 else None
    ke = eob(ramp(t, t_en - 0.05, t_en + 0.3))
    if ke > 0:
        c.save(); c.translate(540, 690); c.scale(ke, ke); c.rotate(-0.04)
        sz = fit_size(c, "¡SE ENCIENDE SOLO!", SLAB, 84, 880)
        text(c, "¡SE ENCIENDE SOLO!", 0, 30, sz, YEL, SLAB, False, outline=INK, olw=14); c.restore()

# ---------------------------------------------------------------- timeline
SCENES = [
    ("front", 0.0, cut("paso1"), scene_front),
    ("paso1", cut("paso1"), cut("paso2"), scene_paso1),
    ("paso2", cut("paso2"), cut("paso3"), scene_paso2),
    ("paso3", cut("paso3"), cut("paso4"), scene_paso3),
    ("paso4", cut("paso4"), cut("paso5"), scene_paso4),
    ("paso5", cut("paso5"), cut("junto"), scene_paso5),
    ("all", cut("junto"), B("remate")["start"] - 0.1, scene_all),
    ("remate", B("remate")["start"] - 0.1, T_LOOP + 0.15, scene_remate),
]
LOOP_FN = scene_front
XF = {"remate": 0.08}

def POPS():
    p = [ws("imposible", w) - 0.15 for w, *_ in BADGES] + [ws("imposible", "tonelada") - 0.15]
    p += [ws("gancho", w) for w in ("tres", "veinticinco", "cuatro", "cien")]
    p += [ws("paso1", w) for w in ("cilindros", "cuatro", "pistón", "jeringa")]
    p += [ws("paso2", w) for w in ("aspira", "aire", "gasolina", "aprieta", "diminuto")]
    p += [ws("paso3", w) for w in ("bujía", "explota", "fuerza")]
    p += [ws("paso4", w) for w in ("echa", "quemados", "tubo", "admisión", "compresión", "explosión", "vuelta")] + [wt("paso4", "escape", 1)]
    p += [ws("paso5", w) for w in ("pistones", "ruedas", "cigüeñal", "convierte", "piernas")]
    p += [ws("junto", w) - 0.05 for w, *_ in JUNTO]
    p += [ws("remate", w) for w in ("bujía", "aprietan", "calienta", "combustible")]
    return sorted(p)

def SFX(put, L):
    import numpy as np
    SR = L["SR"]
    def putt(g, d=0.09, fc=260):
        n = int(d * SR); x = L["lp"](np.random.default_rng(len(_used)).standard_normal(n), fc) * L["env"](n, 0.002, d * 0.35)
        _used.append(1); return x * 3.0
    _used = []
    # physical clock, integrated finely
    ts = np.arange(0, DUR, 0.002)
    dt = 0.002 * 10 ** (-np.array([slow_log(x) for x in ts]))
    at = np.cumsum(dt)
    G0 = G_of(0.0) - 0.0
    def crossings(phase, step):
        k = np.floor(phase / step); idx = np.nonzero(np.diff(k) > 0)[0]
        return ts[idx + 1]
    # front: idle putts in step with the exhaust puffs
    for x in crossings(3.2 * at, 1.0):
        if x < cut("paso1"): put(putt(1, 0.11, 220), x, 0.55)
    # paso1 + paso5 + junto + acelera: a putt on every firing of the real crank (1 per s slowed -> 100 per s)
    G = 360 * RPS * at + _G0
    for x in crossings(G, 180.0):
        if cut("paso1") <= x < cut("paso2"): put(putt(1), x, 0.35)
        elif cut("junto") <= x < B("remate")["start"] - 0.3:
            sfr = 1 - slow_log(x) / CFG["hud"]["max_log"]
            put(putt(1, 0.09 if sfr < 0.4 else 0.05, 260 + 200 * sfr), x, 0.5 - 0.3 * sfr)
    for x in crossings(G + 90, 360.0):  # single cylinder of paso5 fires every 720°
        pass
    for x in crossings(G + 90 - 360, 720.0):
        if cut("paso5") <= x < cut("junto"): put(putt(1, 0.12), x, 0.45)
    # paso3: spark clicks + the explosion
    t_ch = ws("paso3", "chispa")
    for dt_ in (0.0, 0.18, 0.42): put(L["click"](), t_ch - 0.05 + dt_, 0.9); put(L["zap"](0.12), t_ch - 0.05 + dt_, 0.08)
    put(L["click"](), ws("paso3", "explota") - 0.1, 0.9)
    put(L["boom"](), ws("paso3", "explota") - 0.05, 0.5); put(putt(1, 0.25, 400), ws("paso3", "explota") - 0.05, 0.6)
    # paso2 intake hiss, paso4 exhaust hiss
    put(L["noise"](1.2, 1800) * np.sin(np.linspace(0, np.pi, int(1.2 * SR))), ws("paso2", "aspira") - 0.4, 0.08)
    put(L["noise"](1.6, 900) * np.sin(np.linspace(0, np.pi, int(1.6 * SR))), ws("paso4", "echa") - 0.2, 0.12)
    for w in ("admisión", "compresión", "explosión"): put(L["click"](), ws("paso4", w), 0.5)
    put(putt(1, 0.2, 400), ws("paso4", "explosión"), 0.5)
    # remate: diesel self-ignition
    put(L["noise"](0.5, 2500) * np.linspace(1, 0, int(0.5 * SR)), ws("remate", "combustible"), 0.08)
    put(L["boom"](), ws("remate", "enciende") - 0.05, 0.5); put(putt(1, 0.25, 350), ws("remate", "enciende") - 0.05, 0.6)
    # front: the imposible crosses
    for w, *_ in BADGES: put(L["scratch"](), ws("imposible", w) + 0.2, 0.25)
    put(L["boom"](), ws("imposible", "tonelada"), 0.25)

# ---------------------------------------------------------------- thumbnails
def _thumb_cyl(c):
    ph = 425; yc = crown_y(ph); ym = (HEAD_Y + yc) / 2
    glow(c, 0, ym, 520, HOT, 0.55)
    st = dict(col=ORANGE, a=0.95, drops=0, fire=1.0, smoke=0)
    engine_side(c, ph, 1.3, st=st, spark=0.0)
    c.save(); c.rectangle(-BORE, HEAD_Y, 2 * BORE, yc - HEAD_Y); c.clip()
    flame_blob(c, 0, ym, 120, 90, 1.1, 0.7); c.restore()
    for m in range(12):
        a = m * math.pi / 6
        line(c, [(math.cos(a) * 200, ym + math.sin(a) * 170), (math.cos(a) * 300, ym + math.sin(a) * 250)], YEL, 12)
    arrow(c, 0, yc - 20, 0, yc + 150, INK, 60, 120); arrow(c, 0, yc - 18, 0, yc + 136, YEL, 40, 96)

def THUMB_V(c):
    background(c, 3.0, HOT)
    glow(c, 540, 1150, 600, HOT, 0.35)
    c.save(); c.translate(540, 1720); c.scale(1.75, 1.75); _thumb_cyl(c); c.restore()
    for i, (ln, col) in enumerate([("PURA", WHITE), ("EXPLOSIÓN", YEL)]):
        sz = fit_size(c, ln, SLAB, 210, 980)
        text(c, ln, 540, 330 + i * 210, sz, col, SLAB, False, outline=INK, olw=24)

def THUMB_H(c):
    g = cairo.LinearGradient(0, 0, 0, 720); g.add_color_stop_rgba(0, *BG_TOP); g.add_color_stop_rgba(1, *BG_BOT); c.set_source(g); c.paint()
    glow(c, 980, 380, 420, HOT, 0.45)
    c.save(); c.translate(980, 640); c.scale(0.78, 0.78); _thumb_cyl(c); c.restore()
    for i, (ln, col) in enumerate([("PURA", WHITE), ("EXPLOSIÓN", YEL)]):
        sz = fit_size(c, ln, SLAB, 150, 700)
        text(c, ln, 380, 320 + i * 180, sz, col, SLAB, False, outline=INK, olw=20)
