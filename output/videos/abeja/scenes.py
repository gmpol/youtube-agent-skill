"""¿Cómo vuela una abeja?  Illustrations (pycairo only). Contract: output/engine/SCENES_GUIDE.md

Biology shown: honeybee (Apis mellifera), ~230 wingbeats/s, indirect asynchronous flight muscles.
  dorsoventral muscles contract -> roof (notum) pulled down -> wings UP (wing base is inside the pleural pivot)
  dorsal-longitudinal muscles contract -> thorax shortens, roof bulges up -> wings DOWN
  stretch activation: a stretched muscle contracts by itself; one nerve impulse -> many beats
  each stroke ends with the wing flipping over (pronation/supination); leading-edge vortex on top gives lift
  230 air pushes per second = a ~230 Hz tone (the buzz)
"""
from core import *  # noqa

# ---------------------------------------------------------------- colours of this video
FUR, FUR2 = hx("#D9A04A"), hx("#F3C977")
AMBER, BAND = hx("#F2B33D"), hx("#2A2230")
HEADC, EYEC = hx("#3A2E35"), hx("#14121C")
WINGC = (0.86, 0.94, 1.0, 0.42)
DVC, DLMC = hx("#E0544B"), hx("#5B8DEF")
PETAL, PETAL2 = hx("#F28FA8"), hx("#D9677F")
CHALK, BOARD = hx("#F4F1E6"), hx("#2E4638")

F = 230.0                                    # wingbeats per second (real)
BX, BY, BS = 600, 1050, 1.1                  # bee in the opening shot
ZX, ZY, ZS = 480, 1180, 1.75                 # same bee, zoomed (cut-away)
WMID, WAMP = -0.3, 0.7                       # side-view wing angle: mid, amplitude (rad)


def phase(t): return 2 * math.pi * F * anim_time(t)
def vis_hz(t): return F * 10 ** (-slow_log(t))          # flaps per second of VIDEO
def blurk(t): return ease(ramp(vis_hz(t), 5.0, 14.0))   # 0 sharp wing .. 1 blur
def wing_ang(u): return WMID - WAMP * u                 # u=+1 wings up, -1 down


def faded(c, a, fn):
    if a <= 0.003: return
    if a >= 0.997: fn(); return
    c.push_group(); fn(); c.pop_group_to_source(); c.paint_with_alpha(a)


def ellipse(c, x, y, rx, ry, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(rx, ry); c.new_sub_path(); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()


def fuzzy_circle(c, x, y, r, n=22, amp=5):
    c.new_path()
    for i in range(n * 4 + 1):
        a = 2 * math.pi * i / (n * 4); rr = r + amp * math.cos(n * a)
        p = (x + rr * math.cos(a), y + rr * math.sin(a))
        c.line_to(*p) if i else c.move_to(*p)
    c.close_path()


def bolt(c, x, y, s, col=YEL, lw=5):
    pts = [(12, -62), (-26, 6), (0, 6), (-14, 62), (30, -12), (4, -12), (20, -62)]
    c.new_path(); c.move_to(x + pts[0][0] * s, y + pts[0][1] * s)
    for p in pts[1:]: c.line_to(x + p[0] * s, y + p[1] * s)
    c.close_path(); fill_stroke(c, col, INK, lw)


def arrowhead_arc(c, cx, cy, r, a0, a1, col, lw):
    """Curved arrow along a circle from a0 to a1 (radians)."""
    n = 24; pts = [(cx + r * math.cos(lerp(a0, a1, i / n)), cy + r * math.sin(lerp(a0, a1, i / n))) for i in range(n + 1)]
    line(c, pts[:-2], col, lw)
    x1, y1 = pts[-1]; x0, y0 = pts[-3]
    arrow(c, x0, y0, x1, y1, col, lw, lw * 3)


# ---------------------------------------------------------------- wings
def wing_path(c, L, w):
    c.new_path(); c.move_to(0, -w * 0.12)
    c.curve_to(L * 0.25, -w * 0.8, L * 0.75, -w * 0.78, L, -w * 0.15)
    c.curve_to(L * 1.03, w * 0.22, L * 0.8, w * 0.55, L * 0.55, w * 0.45)
    c.curve_to(L * 0.3, w * 0.38, L * 0.1, w * 0.25, 0, w * 0.12)
    c.close_path()


def draw_wing(c, x, y, ang, L, w, a=1.0, fill=WINGC, edge=INK, veins=True, lw=4):
    if a <= 0.01: return
    c.save(); c.translate(x, y); c.rotate(ang)
    wing_path(c, L, w); c.set_source_rgba(*alpha(fill, a)); c.fill_preserve()
    c.set_source_rgba(*alpha(edge, 0.85 * a)); c.set_line_width(lw); c.stroke()
    if veins:
        for yy in (-0.3, 0.02, 0.28):
            line(c, [(L * 0.04, 0), (L * 0.42, w * yy), (L * 0.78, w * yy * 0.7)], alpha(edge, 0.3 * a), lw * 0.6)
    c.restore()


def wings_draw(c, u, bk, L, far=False, xr=False):
    """Fore + hind wing of one side. bk: 0 sharp at angle(u), 1 motion blur over the whole stroke."""
    fill = alpha(XRAY, 0.22) if xr else WINGC
    edge = XRAY if xr else INK
    fa = 0.45 if far else 1.0
    ox, oy = (16, -12) if far else (0, 0)
    for bx, by, l, w, da in [(22, -62, L * 0.64, L * 0.2, 0.13), (-10, -70, L, L * 0.27, 0.0)]:
        bx += ox; by += oy
        if bk < 0.99:
            draw_wing(c, bx, by, wing_ang(u) + da, l, w, fa * (1 - bk), fill, edge)
        if bk > 0.01:
            a_up, a_dn = wing_ang(1) + da, wing_ang(-1) + da
            c.new_path(); c.move_to(bx, by); c.arc(bx, by, l * 1.02, a_up - 0.12, a_dn + 0.12); c.close_path()
            g = cairo.RadialGradient(bx, by, 0, bx, by, l * 1.02)
            col = XRAY if xr else (0.92, 0.97, 1.0, 1)
            g.add_color_stop_rgba(0, col[0], col[1], col[2], 0.05 * bk * fa)
            g.add_color_stop_rgba(0.8, col[0], col[1], col[2], 0.3 * bk * fa)
            g.add_color_stop_rgba(1, col[0], col[1], col[2], 0.0)
            c.set_source(g); c.fill()
            for aa in (a_up, a_dn):
                draw_wing(c, bx, by, aa, l, w, 0.32 * bk * fa, fill, edge, veins=False, lw=3)


# ---------------------------------------------------------------- the bee (side view, facing left; origin = thorax centre)
LEGS = [[(-40, 60), (-62, 110), (-80, 150)], [(-5, 75), (-10, 125), (-25, 168)], [(35, 68), (70, 120), (62, 182)]]


def bee(c, ph, bk, chubby=False, L=None, xr=False, pollen=True):
    L = L or (180 if chubby else 260)
    u = math.sin(ph)
    wings_draw(c, u, bk, L, far=True, xr=xr)
    # legs: far side (lighter) then near side
    for off, a in (((14, -8), 0.55), ((0, 0), 1.0)):
        for leg in LEGS:
            pts = [(x + off[0], y + off[1]) for x, y in leg]
            if xr: line(c, pts, alpha(XRAY, 0.55 * a), 5)
            else:
                line(c, pts, alpha(INK, a), 12); line(c, pts, alpha(mix(HEADC, WHITE, 0.15 if a < 1 else 0), a), 6)
    if pollen and not chubby and not xr:
        circle(c, 68, 140, 17); fill_stroke(c, ORANGE2, INK, 4)
    # abdomen
    ax, ay, rx, ry, rot = (150, 25, 125, 108, 0.22) if chubby else (150, 30, 135, 90, 0.3)
    if not chubby and not xr:  # stinger
        ca, sa = math.cos(rot), math.sin(rot)
        tx, ty = ax + ca * rx, ay + sa * rx
        c.new_path(); c.move_to(tx - sa * 10, ty + ca * 10); c.line_to(tx + ca * 22, ty + sa * 22); c.line_to(tx + sa * 10, ty - ca * 10)
        c.close_path(); fill_stroke(c, BAND, INK, 3)
    c.new_path(); ellipse(c, ax, ay, rx, ry, rot)
    if xr:
        fill_stroke(c, alpha(STEEL, 0.22), alpha(XRAY, 0.9), 4)
    else:
        c.set_source_rgba(*(BAND if chubby else AMBER)); c.fill()
        c.save(); c.translate(ax, ay); c.rotate(rot); c.save(); c.scale(rx, ry); c.new_path(); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore(); c.clip()
        if chubby:
            c.set_source_rgba(*FUR2); c.rectangle(-75, -200, 48, 400); c.fill()
            c.set_source_rgba(*CREAM); c.rectangle(62, -200, 100, 400); c.fill()
        else:
            for x0 in (-42, 14, 66):
                c.set_source_rgba(*BAND); c.rectangle(x0, -200, 30, 400); c.fill()
            c.set_source_rgba(*BAND); c.rectangle(108, -200, 60, 400); c.fill()
        c.set_source_rgba(1, 1, 1, 0.18); ellipse(c, -10, -45, 90, 22); c.fill()
        c.restore()
        c.new_path(); ellipse(c, ax, ay, rx, ry, rot); fill_stroke(c, None, INK, 6)
    if xr:  # segment lines
        c.save(); c.translate(ax, ay); c.rotate(rot)
        for x0 in (-42, 14, 66, 108):
            yy = ry * math.sqrt(max(0, 1 - (x0 / rx) ** 2))
            line(c, [(x0, -yy + 4), (x0 + 6, yy - 4)], alpha(XRAY, 0.35), 3)
        c.restore()
    # thorax
    r = 95 if chubby else 85
    if xr:
        fuzzy_circle(c, 0, 0, r); fill_stroke(c, alpha(STEEL, 0.3), alpha(XRAY, 0.9), 4)
    else:
        fuzzy_circle(c, 0, 0, r)
        if chubby:
            c.set_source_rgba(*BAND); c.fill_preserve()
            c.save(); c.clip_preserve(); c.set_source_rgba(*FUR2); c.rectangle(-200, -200, 150, 400); c.fill(); c.restore()
        else:
            c.set_source_rgba(*FUR); c.fill_preserve()
        c.set_source_rgba(*INK); c.set_line_width(5); c.stroke()
        glow(c, -15, -25, r * 0.8, FUR2, 0.5)
        for i in range(14):  # fuzz strokes
            a = i * 2.39; rr = 20 + (i * 17) % 55
            x, y = rr * math.cos(a), rr * math.sin(a)
            line(c, [(x, y), (x + 6, y - 9)], alpha(WHITE, 0.22), 3)
    # head
    hxp, hyp, hr = (-128, 20, 60) if chubby else (-118, 14, 56)
    ant = [(hxp - 22, hyp - 46), (hxp - 42, hyp - 106), (hxp - 98, hyp - 124)]
    if xr: line(c, ant, alpha(XRAY, 0.8), 5)
    else: line(c, ant, INK, 12); line(c, ant, HEADC, 6)
    circle(c, ant[-1][0], ant[-1][1], 7); fill_stroke(c, alpha(XRAY, 0.3) if xr else HEADC, XRAY if xr else INK, 3)
    circle(c, hxp, hyp, hr)
    if xr:
        fill_stroke(c, alpha(STEEL, 0.22), alpha(XRAY, 0.9), 4)
        c.new_path(); ellipse(c, hxp + 8, hyp - 10, 24, 36, -0.15); fill_stroke(c, None, alpha(XRAY, 0.6), 3)
        return wings_draw(c, u, bk, L, far=False, xr=True)
    fill_stroke(c, BAND if chubby else HEADC, INK, 5)
    c.new_path(); ellipse(c, hxp + 8, hyp - 10, 25, 37, -0.15); fill_stroke(c, EYEC, INK, 3)
    circle(c, hxp + 0, hyp - 28, 9); c.set_source_rgba(*WHITE); c.fill()
    circle(c, hxp + 16, hyp - 2, 4.5); c.set_source_rgba(*WHITE); c.fill()
    circle(c, hxp - 24, hyp + 18, 10); c.set_source_rgba(0.95, 0.5, 0.55, 0.55); c.fill()
    c.new_path(); c.arc(hxp - 34, hyp + 22, 12, 0.6, 2.3); c.set_source_rgba(*CREAM); c.set_line_width(4); c.stroke()
    wings_draw(c, u, bk, L, far=False)


# ---------------------------------------------------------------- thorax cut-aways
def thorax_side(c, x, y, s, u, dv=1.0, dlm=1.0, hl_dv=0.0, hl_dlm=0.0, wing_a=None, wingL=300, interior=0.92):
    """Side (lateral) cut of the thorax: head to the left. u=+1: dorsoventral contracted (roof down, wings up);
    u=-1: longitudinal contracted (box shorter, roof bulges up, wings down)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    hw = 180 + 9 * u; top, bot = -140, 140
    def ry(xx): return top + 32 * u * (1 - (xx / hw) ** 2)
    pts = [(-hw + 2 * hw * i / 30, ry(-hw + 2 * hw * i / 30)) for i in range(31)]
    c.new_path(); c.move_to(*pts[0])
    for p in pts[1:]: c.line_to(*p)
    c.line_to(hw, bot); c.line_to(-hw, bot); c.close_path()
    c.set_source_rgba(*alpha(NIGHT, interior)); c.fill()
    # dorsal longitudinal muscles: front wall -> back wall
    if dlm > 0:
        if hl_dlm > 0: glow(c, 0, -30, 230, DLMC, 0.45 * hl_dlm)
        thk = 30 * (1 - 0.35 * u)
        for yy in (-74, -28, 18):
            x0, x1 = -hw + 14, hw - 14
            rrect(c, x0, yy - thk / 2, x1 - x0, thk, thk / 2)
            fill_stroke(c, alpha(mix(DLMC, WHITE, 0.3 * hl_dlm), dlm), alpha(INK, dlm), 3)
            for k in (-0.22, 0.22):
                line(c, [(x0 + 18, yy + thk * k), (x1 - 18, yy + thk * k)], alpha(WHITE, 0.25 * dlm), 2)
    # dorsoventral muscles: roof -> floor
    if dv > 0:
        wv = 34 * (1 + 0.45 * u)
        for xx in (-100, 100):
            if hl_dv > 0: glow(c, xx, 20, 120, DVC, 0.5 * hl_dv)
            y0 = ry(xx) + 12; y1 = bot - 12
            rrect(c, xx - wv / 2, y0, wv, y1 - y0, wv / 2)
            fill_stroke(c, alpha(mix(DVC, WHITE, 0.3 * hl_dv), 0.95 * dv), alpha(INK, dv), 3)
            for k in (-0.22, 0.22):
                line(c, [(xx + wv * k, y0 + 14), (xx + wv * k, y1 - 14)], alpha(WHITE, 0.25 * dv), 2)
    # cuticle walls
    c.new_path(); c.move_to(*pts[0])
    for p in pts[1:]: c.line_to(*p)
    c.line_to(hw, bot); c.line_to(-hw, bot); c.close_path()
    c.set_source_rgba(*INK); c.set_line_width(24); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
    c.set_source_rgba(*FUR); c.set_line_width(13); c.stroke()
    if wing_a is not None:
        bx = hw * 0.3; by = ry(bx) - 6
        draw_wing(c, bx, by, wing_a, wingL, wingL * 0.27, 1.0, alpha(WINGC, 0.8), INK, True, 5)
        circle(c, bx, by, 11); fill_stroke(c, CREAM, INK, 4)
    c.restore()


def thorax_side_pts(x, y, s, u):
    """World positions of useful points of thorax_side."""
    hw = 180 + 9 * u
    def ry(xx): return -140 + 32 * u * (1 - (xx / hw) ** 2)
    bx = hw * 0.3
    return dict(roof=(x, y + s * ry(0)), dv_l=(x - 100 * s, y + 40 * s), dv_r=(x + 100 * s, y + 40 * s),
                dlm=(x + 40 * s, y - 28 * s), dlm_r=(x + (hw - 20) * s, y - 28 * s), dlm_l=(x - (hw - 20) * s, y - 28 * s),
                wing=(x + bx * s, y + s * (ry(bx) - 6)), hw=hw * s, top=y - 140 * s, bot=y + 140 * s)


def thorax_front(c, x, y, s, u, hinge=0.0, wingL=300):
    """Front (transverse) cut: a box; each wing is a lever over the pleural pivot. Roof down -> wings up."""
    c.save(); c.translate(x, y); c.scale(s, s)
    hw, py, bot = 170, -128, 150
    ry = -130 + 30 * u
    c.new_path(); c.rectangle(-hw, py, 2 * hw, bot - py); c.set_source_rgba(*alpha(NIGHT, 0.92)); c.fill()
    for col, lw in ((INK, 24), (FUR, 13)):
        line(c, [(-hw, py), (-hw, bot), (hw, bot), (hw, py)], col, lw)
    for sg in (-1, 1):
        B_ = (sg * (hw - 30), ry); P = (sg * hw, py - 6)
        dx, dy = P[0] - B_[0], P[1] - B_[1]; a = math.atan2(dy, dx)
        draw_wing(c, P[0], P[1], a, wingL, wingL * 0.22, 1.0, alpha(WINGC, 0.85), INK, True, 5)
        for col, lw in ((INK, 20), (CREAM2, 10)): line(c, [B_, P], col, lw)
        # pivot (pleural wing process)
        c.new_path(); c.move_to(sg * hw - 16, py + 16); c.line_to(sg * hw + 16, py + 16); c.line_to(sg * hw, py - 4); c.close_path()
        fill_stroke(c, YEL, INK, 4)
        if hinge > 0:
            for q in (B_, (sg * hw, py + 6)):
                circle(c, q[0], q[1], 22 + 8 * math.sin(hinge * 6)); c.set_source_rgba(*alpha(YEL, 0.9)); c.set_line_width(5); c.stroke()
    # roof plate (notum)
    for col, lw in ((INK, 24), (FUR, 13)):
        line(c, [(-hw + 30, ry), (0, ry - 6 * u), (hw - 30, ry)], col, lw)
    c.restore()


def thorax_front_pts(x, y, s, u, wingL=300):
    hw, py = 170, -128; ry = -130 + 30 * u
    a = math.atan2(py - 6 - ry, 30)
    tip = (hw + math.cos(a) * wingL * 0.6, py - 6 + math.sin(a) * wingL * 0.6)
    return dict(roof=(x, y + s * ry), pivot=(x + s * hw, y + s * py), base=(x + s * (hw - 30), y + s * ry),
                wing=(x + s * tip[0], y + s * tip[1]), wing_l=(x - s * tip[0], y + s * tip[1]))


def bee_xray(c, ph, bk, glow_th=0.0, u_override=None):
    u = math.sin(ph) if u_override is None else u_override
    if glow_th > 0: glow(c, 0, 0, 190, YEL, 0.55 * glow_th)
    bee(c, ph, bk, xr=True)
    thorax_side(c, 0, 4, 0.34, u, interior=0.85)
    fuzzy_circle(c, 0, 0, 85); fill_stroke(c, None, alpha(YEL if glow_th > 0.3 else XRAY, 0.9), 4)
    wings_draw(c, u, bk, 260, far=False, xr=True)


# ---------------------------------------------------------------- scenery (dusk) + icons
def dusk(c, t):
    g = cairo.LinearGradient(0, 850, 0, 1650)
    g.add_color_stop_rgba(0, 0.89, 0.49, 0.34, 0.0); g.add_color_stop_rgba(1, 0.89, 0.49, 0.34, 0.42)
    c.set_source(g); c.rectangle(-400, 0, W + 800, H + 400); c.fill()
    glow(c, 830, 1560, 520, ORANGE, 0.5)
    circle(c, 830, 1575, 95); c.set_source_rgba(0.98, 0.72, 0.42, 0.95); c.fill()
    for col, base, amp, k in ((hx("#2A2238"), 1560, 50, 0.006), (hx("#1C1828"), 1620, 40, 0.009)):
        c.new_path(); c.move_to(-400, H + 400)
        for i in range(0, 1900, 20):
            xx = i - 400; c.line_to(xx, base - amp * math.sin(xx * k + base))
        c.line_to(W + 400, H + 400); c.close_path(); c.set_source_rgba(*col); c.fill()


def flower(c, x, y, t, s=1.0):
    sway = 0.03 * math.sin(t * 1.1)
    c.save(); c.translate(x, y + 470 * s); c.rotate(sway); c.translate(-x, -(y + 470 * s))
    for col, lw in ((INK, 20), (hx("#4E8A4A"), 11)):
        c.new_path(); c.move_to(x - 30 * s, y + 520 * s); c.curve_to(x + 30 * s, y + 330 * s, x - 30 * s, y + 160 * s, x, y)
        c.set_source_rgba(*col); c.set_line_width(lw * s); c.stroke()
    c.new_path(); ellipse(c, x + 60 * s, y + 300 * s, 70 * s, 24 * s, -0.5); fill_stroke(c, hx("#5FA058"), INK, 5)
    c.new_path(); ellipse(c, x - 60 * s, y + 390 * s, 64 * s, 22 * s, 0.6); fill_stroke(c, hx("#5FA058"), INK, 5)
    c.save(); c.translate(x, y); c.rotate(0.15)
    for i in range(9):
        a = i * 2 * math.pi / 9
        c.new_path(); ellipse(c, math.cos(a) * 62 * s, math.sin(a) * 62 * s, 58 * s, 30 * s, a)
        fill_stroke(c, PETAL if i % 2 else mix(PETAL, PETAL2, 0.4), INK, 5)
    circle(c, 0, 0, 42 * s); fill_stroke(c, YEL, INK, 5)
    for i in range(9):
        a = i * 2.4; r = 8 + (i * 7) % 26
        circle(c, math.cos(a) * r * s, math.sin(a) * r * s, 4 * s); c.set_source_rgba(*GOLD); c.fill()
    c.restore(); c.restore()


def ic_direct(c):
    draw_wing(c, -20, -10, -0.55, 100, 34, 1.0, alpha(XRAY, 0.8), INK, False, 4)
    c.new_path(); ellipse(c, -42, 32, 34, 15, 0.9); fill_stroke(c, DVC, INK, 4)
    line(c, [(-28, 8), (-20, -10)], INK, 6)


def ic_think(c):
    for x, y, r in ((-60, 62, 9), (-42, 44, 13)):
        circle(c, x, y, r); fill_stroke(c, WHITE, INK, 4)
    c.new_path()
    for x, y, r in ((-20, -10, 34), (16, -24, 36), (44, 2, 30), (6, 22, 32), (-32, 18, 26)): circle(c, x, y, r)
    fill_stroke(c, WHITE, INK, 4)
    c.new_path()
    for x, y, r in ((-10, -10, 18), (12, -16, 19), (24, 4, 17), (-2, 8, 18)): circle(c, x, y, r)
    fill_stroke(c, hx("#F2A0B0"), INK, 3)


def ic_order(c):
    bolt(c, -42, 0, 0.75, YEL, 4)
    text(c, "=", 0, 14, 44, INK, SLAB, False)
    draw_wing(c, 22, 24, -0.9, 70, 26, 1.0, alpha(XRAY, 0.8), INK, False, 4)
    text(c, "1", 50, -30, 30, RED, SLAB, False)


def ic_brain(c):
    c.new_path()
    for x, y, r in ((-30, -8, 34), (2, -22, 36), (32, -6, 32), (-18, 20, 30), (20, 20, 30)): circle(c, x, y, r)
    fill_stroke(c, hx("#F2A0B0"), INK, 5)
    line(c, [(0, 40), (6, 62)], INK, 10)


def ic_oar(c):
    line(c, [(-62, 62), (40, -40)], INK, 14); line(c, [(-62, 62), (40, -40)], hx("#C98A3A"), 8)
    c.new_path(); ellipse(c, 46, -46, 40, 17, -0.785); fill_stroke(c, hx("#C98A3A"), INK, 5)


def ic_note(c, col=INK):
    c.new_path(); ellipse(c, -18, 40, 26, 18, -0.4); fill_stroke(c, col, None)
    line(c, [(4, 34), (4, -58)], col, 9, cairo.LINE_CAP_BUTT)
    c.new_path(); c.move_to(4, -58); c.curve_to(30, -40, 46, -26, 34, 0); c.curve_to(36, -22, 24, -32, 4, -36); c.close_path()
    c.set_source_rgba(*col); c.fill()


def bzz_text(c, x, y, t, t0, size=74, col=YEL):
    k = eob(ramp(t, t0, t0 + 0.35))
    if k <= 0: return
    c.save(); c.translate(x + 3 * math.sin(t * 40), y + 3 * math.cos(t * 37)); c.rotate(-0.12); c.scale(k, k)
    text(c, "BZZZ", 0, 0, size, col, SLAB, False, outline=INK, olw=10)
    c.restore()


def label_pop(c, s, x, y, t, t0, size=60, col=YEL):
    k = eob(ramp(t, t0, t0 + 0.35))
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(k, k)
    text(c, s, 0, 0, size, col, SLAB, False, outline=INK, olw=10)
    c.restore()


def big_arrow(c, x, y0, y1, col, lw=16, head=46):
    arrow(c, x, y0, x, y1, INK, lw + 10, head + 12)
    arrow(c, x, y0, x, y1, col, lw, head)


# ---------------------------------------------------------------- 1. front: gancho + imposible + freno
def front_view(t):
    up = ease(ramp(t, wt("imposible", "mueve") - 0.2, wt("imposible", "directamente") - 0.2))
    z = ease(ramp(t, wt("freno", "vamos"), T_SLOW + 0.2))
    up *= 1 - z
    push = 1.0 + 0.04 * ease(ramp(t, 0, B("imposible")["start"]))
    px = lerp(BX, ZX, z); py = lerp(BY, ZY, z) - 110 * up
    sc = lerp(BS * push, ZS, z) * (1 - 0.1 * up)
    return px, py, sc, up, z


def bob(t): return 10 * math.sin(t * 2.4)


def scene_front(c, t):
    background(c, t, ORANGE)
    px, py, sc, up, z = front_view(t)
    xr = ease(ramp(t, T_SLOW - 0.5, T_SLOW + 0.3))
    ph = phase(t); bk = blurk(t)
    def scenery():
        c.save(); c.translate(px, py); c.scale(sc / BS, sc / BS); c.translate(-BX, -BY)
        dusk(c, t); flower(c, 235, 1270, t)
        c.restore()
    faded(c, 1 - xr, scenery)
    yb = py + bob(t) * sc / BS
    def real_bee():
        c.save(); c.translate(px, yb); c.scale(sc, sc); c.rotate(0.03 * math.sin(t * 1.7))
        bee(c, ph, bk)
        if bk > 0.05:  # little buzz lines
            for i in range(3):
                a = 0.5 + 0.5 * math.sin(t * 14 + i * 2)
                c.new_path(); c.arc(-10, -70, 290 + 26 * i, -1.25, -0.85)
                c.set_source_rgba(*alpha(CREAM, 0.55 * a * bk)); c.set_line_width(6); c.stroke()
        c.restore()
    faded(c, 1 - xr, real_bee)
    def xray_bee():
        c.save(); c.translate(px, yb); c.scale(sc, sc); c.rotate(0.03 * math.sin(t * 1.7))
        bee_xray(c, ph, bk); c.restore()
    faded(c, xr, xray_bee)
    # gancho: "ese zumbido" -> BZZZ ; "sus putas alas" -> ALAS
    gk = 1 - ramp(t, B("imposible")["start"] - 0.3, B("imposible")["start"] + 0.2)
    if gk > 0:
        faded(c, gk, lambda: bzz_text(c, 830, 830, t, wt("gancho", "zumbido") - 0.1))
        wx, wy = px + sc * 60, yb + sc * -190
        faded(c, gk, lambda: callout(c, "ALAS", wx, wy, 300, 760, t, wt("gancho", "alas", 1) - 0.25, YEL, 40))
    # imposible: three crossed-out badges
    if up > 0.01:
        for key, x, lab, fn in (("directamente", 250, "MÚSCULO EN EL ALA", ic_direct), ("piensa", 540, "PENSARLO", ic_think),
                                ("orden", 830, "UNA ORDEN POR GOLPE", ic_order)):
            t0 = wt("imposible", key) - 0.15
            k = eob(ramp(t, t0, t0 + 0.3)) * up
            if k <= 0: continue
            icon_badge(c, x, 1470, k, "", fn, t, t0 + 0.35, 100)
            if k > 0.3:
                sz = fit_size(c, lab, SANS, 28, 270, True)
                text(c, lab, x, 1470 + 100 + 44, sz, alpha(CREAM, clamp(k)), SANS, True)
    # "no falla ni uno": green ring check around the bee
    k = ramp(t, wt("imposible", "falla") - 0.1, wt("imposible", "falla") + 0.3) * (1 - z)
    if k > 0:
        c.new_path(); c.arc(px + 20 * sc / BS, yb, 330 * sc / BS, -math.pi / 2, -math.pi / 2 + 2 * math.pi * ease(k))
        c.set_source_rgba(*alpha(GREEN, 0.85 * (1 - ramp(t, B("freno")["start"], B("freno")["start"] + 0.4)))); c.set_line_width(8); c.stroke()


# ---------------------------------------------------------------- 2. paso1: tórax = cajita con palancas
def scene_paso1(c, t):
    background(c, t, YEL)
    b = B("paso1")
    tb = wt("paso1", "como")
    kx = ease(ramp(t, tb - 0.45, tb + 0.25))
    ph = phase(t); bk = blurk(t)
    push = 1 + 0.03 * ease(ramp(t, b["start"], tb))
    px, py, sc = ZX, ZY, ZS * push
    yb = py + bob(t) * sc / BS
    t_tor = wt("paso1", "tórax")
    gth = ease(ramp(t, t_tor - 0.2, t_tor + 0.2))
    def xray_view():
        c.save(); c.translate(px, yb); c.scale(sc, sc); c.rotate(0.03 * math.sin(t * 1.7))
        bee_xray(c, ph, bk, glow_th=gth); c.restore()
        callout(c, "TÓRAX", px, yb + 90 * sc, 520, 1640, t, t_tor - 0.1, YEL, 44)
        t_med = wt("paso1", "medio") - 0.3
        callout(c, "CABEZA", px - 118 * sc, yb + 30 * sc, 190, 1500, t, t_med - 0.2, CREAM, 30)
        callout(c, "ABDOMEN", px + 200 * sc, yb + 60 * sc, 860, 1500, t, t_med, CREAM, 30)
    faded(c, 1 - kx, xray_view)
    if kx > 0:
        s = lerp(0.55, 0.85, kx); X0, Y0 = 540, 1130
        tp = wt("paso1", "palancas")
        amp = ease(ramp(t, tp - 0.6, tp + 0.2))
        u = amp * math.sin(phase(t) - phase(tp - 0.6))
        t_eng = wt("paso1", "enganchadas")
        hg = ramp(t, t_eng - 0.1, t_eng + 0.2) * (1 - ramp(t, tp - 0.2, tp + 0.2))
        def box():
            thorax_front(c, X0, Y0, s, u, hinge=hg * (t - t_eng + 0.3))
            text(c, "TÓRAX VISTO DE FRENTE", X0, Y0 + 210, 34, alpha(CREAM, 0.8), SANS, True)
        faded(c, kx, box)
        P = thorax_front_pts(X0, Y0, s, u)
        callout(c, "CAJITA", X0 - 60, Y0 + 60, 260, 1500, t, wt("paso1", "cajita") - 0.1, CREAM, 36)
        callout(c, "BORDE", *P["base"], 830, 1420, t, wt("paso1", "borde") - 0.15, CREAM, 36)
        callout(c, "PALANCAS", *P["wing"], 760, 760, t, tp - 0.1, YEL, 44)
        if amp > 0.3:  # seesaw arrows: roof down -> wing up
            k = clamp((amp - 0.3) / 0.7)
            d = 1 if math.cos(phase(t) - phase(tp - 0.6)) > 0 else -1
            rx, ry = P["roof"]
            big_arrow(c, X0, ry - 110, ry - 110 + 60 * d, alpha(DVC, k) if d > 0 else alpha(DLMC, k), 12, 34)
            wx, wy = P["wing_l"]
            big_arrow(c, wx, wy + 60, wy + 60 - 60 * d, alpha(YEL, k), 12, 34)


# ---------------------------------------------------------------- 3. paso2: two muscle groups take turns
def p2_u(t):
    ta = wt("paso2", "abajo"); ts = wt("paso2", "suben")
    tb = wt("paso2", "delante"); tj = wt("paso2", "bajan")
    if t < tb: return ease(ramp(t, ta - 0.2, ts))
    return 1 - 2 * ease(ramp(t, tb, tj))


def stubs(c, x, y, s):
    """Faint head and abdomen around a thorax_side box (context)."""
    circle(c, x - 265 * s, y + 20 * s, 75 * s); fill_stroke(c, alpha(STEEL, 0.15), alpha(XRAY, 0.5), 4)
    c.new_path(); ellipse(c, x - 258 * s, y + 6 * s, 24 * s, 36 * s, -0.15); fill_stroke(c, None, alpha(XRAY, 0.4), 3)
    c.new_path(); ellipse(c, x + 360 * s, y + 40 * s, 170 * s, 115 * s, 0.25); fill_stroke(c, alpha(STEEL, 0.15), alpha(XRAY, 0.5), 4)


def scene_paso2(c, t):
    background(c, t, YEL)
    b = B("paso2")
    c.save(); cam(c, 1.0 + 0.04 * ease(ramp(t, b["start"], b["end"])), 470, 1180)
    X0, Y0, s = 470, 1190, 1.25
    u = p2_u(t)
    t_dos = wt("paso2", "dos"); t_mus = wt("paso2", "músculos")
    dv = ease(ramp(t, t_dos - 0.2, t_dos + 0.2)); dlm = ease(ramp(t, t_mus - 0.3, t_mus + 0.1))
    t_unos = wt("paso2", "unos"); t_otros = wt("paso2", "otros")
    hl_dv = ramp(t, t_unos - 0.1, t_unos + 0.2) * (1 - ramp(t, t_otros - 0.2, t_otros + 0.1))
    hl_dlm = ramp(t, t_otros - 0.1, t_otros + 0.2)
    pul = pulse_at(t, t_mus - 0.1, 0.7)
    stubs(c, X0, Y0, s)
    thorax_side(c, X0, Y0, s, u, dv, dlm, max(hl_dv, pul), max(hl_dlm, pul), wing_a=wing_ang(u), wingL=300)
    c.restore()
    P = thorax_side_pts(X0, Y0, s, u)
    callout(c, "VERTICALES", *P["dv_l"], 230, 1600, t, t_unos - 0.1, DVC, 38)
    callout(c, "HORIZONTALES", *P["dlm"], 740, 1600, t, t_otros - 0.1, DLMC, 38)
    # contraction arrows
    ta = wt("paso2", "aprietan")
    k = ramp(t, ta - 0.1, ta + 0.2) * (1 - ramp(t, t_otros - 0.3, t_otros))
    if k > 0:
        for xx in (-100, 100):
            ax = X0 + xx * s; ay = P["top"] - 80
            big_arrow(c, ax, ay - 20, ay + 50, alpha(DVC, k), 12, 32)
    ta2 = wt("paso2", "aprietan", 1)
    k = ramp(t, ta2 - 0.1, ta2 + 0.2)
    if k > 0:
        for sg in (-1, 1):
            ax = X0 + sg * (P["hw"] + 110); ay = Y0 + 60
            arrow(c, ax, ay, ax - sg * 70, ay, INK, 22, 44); arrow(c, ax, ay, ax - sg * 70, ay, alpha(DLMC, k), 12, 34)
    ts = wt("paso2", "suben"); tj = wt("paso2", "bajan")
    k1 = 1 - ramp(t, t_otros, t_otros + 0.3)
    if k1 > 0:
        def sub():
            label_pop(c, "SUBEN", 830, 700, t, ts - 0.15, 64, YEL)
            if t >= ts - 0.1: big_arrow(c, 830, 860, 760, YEL, 12, 36)
        faded(c, k1, sub)
    label_pop(c, "BAJAN", 860, 1420, t, tj - 0.15, 64, YEL)
    if t >= tj - 0.1: big_arrow(c, 860, 1250, 1340, YEL, 12, 36)


# ---------------------------------------------------------------- 4. paso3: stretch activation
def p3_u(t):
    t_est = wt("paso3", "estira"); t_con = wt("paso3", "contrae"); t_osc = wt("paso3", "uno", 1)
    if t < t_osc:
        a = ease(ramp(t, B("paso3")["start"] - 0.3, B("paso3")["start"] + 0.3))
        u = lerp(-1, 0, a)
        u = lerp(u, 1, ease(ramp(t, t_est - 0.6, t_est + 0.1)))
        return lerp(u, -1, ease(ramp(t, t_con - 0.05, t_con + 0.3)))
    return math.sin(phase(t) - phase(t_osc) - math.pi / 2)


def scene_paso3(c, t):
    background(c, t, YEL)
    b = B("paso3")
    X0, Y0, s = 430, 1130, 1.0
    u = p3_u(t)
    t_est = wt("paso3", "estira"); t_con = wt("paso3", "contrae"); t_cer = wt("paso3", "cerebro")
    t_osc = wt("paso3", "uno", 1); t_ord = wt("paso3", "orden"); t_una = wt("paso3", "una")
    stretch = ramp(t, t_est - 0.4, t_est) * (1 - ramp(t, t_con, t_con + 0.2))
    snap = pulse_at(t, t_con - 0.05, 0.7)
    hl_dlm = max(stretch * 0.6, snap)
    hl_dv = 0.0
    if t >= t_osc:  # whichever is contracting glows
        hl_dlm = max(0, -u) * 0.8; hl_dv = max(0, u) * 0.8
    c.save(); cam(c, 1.0 + 0.04 * ease(ramp(t, b["start"], b["end"])), X0, Y0)
    stubs(c, X0, Y0, s)
    thorax_side(c, X0, Y0, s, u, 1, 1, hl_dv, hl_dlm, wing_a=wing_ang(u), wingL=290)
    c.restore()
    P = thorax_side_pts(X0, Y0, s, u)
    if stretch > 0:  # pulled from both ends
        for sg in (-1, 1):
            ax = X0 + sg * (P["hw"] + 30); ay = P["dlm"][1]
            arrow(c, ax, ay, ax + sg * 70 * stretch, ay, alpha(WHITE, stretch), 10, 30)
    callout(c, "ESTIRÓN", *P["dlm_l"], 200, 1560, t, t_est - 0.1, DLMC, 40)
    k = 1 - ramp(t, t_osc - 0.3, t_osc)
    if k > 0:
        faded(c, k, lambda: callout(c, "¡SE CONTRAE SOLO!", *P["dlm"], 620, 1440, t, t_con - 0.1, YEL, 38))
    # brain: not needed
    t0 = wt("paso3", "sin") - 0.15
    kb = eob(ramp(t, t0, t0 + 0.3)) * (1 - ramp(t, t_osc + 0.8, t_osc + 1.2))
    if kb > 0:
        icon_badge(c, 820, 760, kb, "CEREBRO", ic_brain, t, t_cer - 0.05, 88)
    # ping-pong: "uno estira al otro, el otro al uno"
    kp = ramp(t, t_osc - 0.2, t_osc + 0.2)
    if kp > 0:
        cx, cy = 820, 760
        def loop():
            circle(c, cx, cy, 92); fill_stroke(c, CREAM, INK, 6)
            rot = (phase(t) - phase(t_osc)) % (2 * math.pi)
            arrowhead_arc(c, cx, cy, 56, rot, rot + 2.4, DVC, 12)
            arrowhead_arc(c, cx, cy, 56, rot + math.pi, rot + math.pi + 2.4, DLMC, 12)
            text(c, "SE TURNAN", cx, cy + 140, 30, CREAM, SANS, True)
        faded(c, kp * (1 - ramp(t, t_una - 0.4, t_una)), loop)
    # one nerve impulse -> many beats
    if t >= t_una - 0.3:
        k = ease(ramp(t, t_una - 0.3, t_una))
        nerve = [(950, 760), (900, 860), (760, 960), (P["dlm_r"][0] + 10, P["dlm_r"][1])]
        def nv():
            line(c, nerve, alpha(YEL, 0.35), 18); line(c, nerve, YEL, 6)
            text(c, "NERVIO", 860, 740, 30, YEL, SANS, True)
        faded(c, k, nv)
        f = ramp(t, t_ord - 0.1, t_ord + 0.45)
        if 0 < f < 1:
            segs = list(zip(nerve[:-1], nerve[1:])); Ls = [math.dist(a, b_) for a, b_ in segs]; d = f * sum(Ls)
            for (a, b_), l in zip(segs, Ls):
                if d <= l:
                    x, y = a[0] + (b_[0] - a[0]) * d / l, a[1] + (b_[1] - a[1]) * d / l
                    glow(c, x, y, 90, YEL, 0.9); bolt(c, x, y, 0.55, YEL, 4); break
                d -= l
        if f >= 1: glow(c, *P["dlm_r"], 140, YEL, 0.5 * (1 - ramp(t, t_ord + 0.45, t_ord + 1.0)))
        # counter panel
        tc = t_ord + 0.45
        kc = eob(ramp(t, t_ord - 0.2, t_ord + 0.15))
        if kc > 0:
            n = 0 if t < tc else 1 + int((phase(t) - phase(tc)) / (2 * math.pi))
            c.save(); c.translate(540, 1500); c.scale(kc, kc)
            shadow(c, lambda: rrect(c, -380, -70, 760, 140, 20), 8, 10, 0.4)
            rrect(c, -380, -70, 760, 140, 20); fill_stroke(c, CREAM, INK, 6)
            bolt(c, -320, 0, 0.75, YEL, 4)
            text(c, "1 ORDEN", -270, 16, 44, INK, SLAB, False, "l")
            arrow(c, -40, 0, 40, 0, RED, 10, 30)
            rrect(c, 70, -48, 120, 96, 12); fill_stroke(c, hx("#1E3A2A"), INK, 4)
            text(c, str(n), 130, 22, 62, hx("#7CFC9A"), MONO, True)
            text(c, "ALETEOS", 210, 16, 40, INK, SLAB, False, "l")
            c.restore()


# ---------------------------------------------------------------- 5. paso4: the wing flips like an oar; leading-edge vortex
CX4, CY4, A4, B4 = 540, 960, 300, 60


def chord_pose(ph):
    """Wing section on a figure-of-eight path (side view, head to the LEFT). Returns x, y, angle of leading edge, s."""
    x = CX4 + A4 * math.cos(ph); y = CY4 + B4 * math.sin(2 * ph)
    sdir = math.tanh(3.0 * -math.sin(ph))  # +1 moving right (back-stroke), -1 moving left (forward stroke)
    ang = -math.pi / 2 + sdir * (math.pi / 2 - 0.62)
    return x, y, ang, sdir


def airfoil(c, x, y, ang, a=1.0, L=150, col=CREAM, lw=5):
    c.save(); c.translate(x, y); c.rotate(ang)
    k = L / 140
    c.new_path(); c.move_to(-70 * k, 0)
    c.curve_to(-20 * k, -13 * k, 40 * k, -16 * k, 60 * k, -7 * k); c.curve_to(72 * k, -2 * k, 72 * k, 5 * k, 60 * k, 7 * k)
    c.curve_to(40 * k, 12 * k, -20 * k, 8 * k, -70 * k, 0); c.close_path()
    fill_stroke(c, alpha(col, a), alpha(INK, a), lw)
    circle(c, 58 * k, 0, 6 * k); c.set_source_rgba(*alpha(RED, a)); c.fill()
    c.restore()


def swirl(c, x, y, r, rot, a, ccw=True, col=XRAY):
    if a <= 0.01: return
    n = 40; d = -1 if ccw else 1
    pts = []
    for i in range(n + 1):
        f = i / n; ang = rot + d * f * 2.6 * math.pi; rr = r * (0.15 + 0.85 * f)
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang) * 0.8))
    line(c, pts[:-2], alpha(col, a), 7)
    arrow(c, *pts[-4], *pts[-1], alpha(col, a), 7, 24)


def scene_paso4(c, t):
    background(c, t, COLD)
    b = B("paso4")
    c.save(); cam(c, 1.0 + 0.04 * ease(ramp(t, b["start"], b["end"])), 540, 1100)
    ph = phase(t)
    # faint bee body under the stroke, body tilted (head up) as in hovering
    def body():
        c.save(); c.translate(560, 1260); c.scale(0.82, 0.82); c.rotate(0.42); bee(c, 0, 0, L=1); c.restore()
    faded(c, 0.5, body)
    # stroke path
    kp = ease(ramp(t, wt("paso4", "no") - 0.3, wt("paso4", "bajan")))
    if kp > 0:
        pts = [(CX4 + A4 * math.cos(2 * math.pi * i / 120), CY4 + B4 * math.sin(4 * math.pi * i / 120)) for i in range(int(120 * kp) + 1)]
        c.set_dash([18, 14]); line(c, pts, alpha(CREAM, 0.5), 5); c.set_dash([])
    # trail of past poses
    for k in range(9, 0, -1):
        x, y, ang, sd = chord_pose(ph - k * 0.32)
        airfoil(c, x, y, ang, 0.08 + 0.05 * (9 - k), 130, LAV, 3)
    x, y, ang, sd = chord_pose(ph)
    # leading-edge vortex above the wing
    t_rem = wt("paso4", "remolino")
    kv = ease(ramp(t, t_rem - 0.3, t_rem + 0.2)) * clamp(abs(sd) * 1.4 - 0.3)
    if kv > 0:
        lx = x + math.cos(ang) * 45; ly = y + math.sin(ang) * 45
        swirl(c, lx - 30 * sd, ly - 50, 50, t * 9 * -sd, kv, ccw=sd > 0)
    airfoil(c, x, y, ang, 1.0, 150, CREAM, 5)
    # downwash
    t_aire = wt("paso4", "aire")
    ka = ramp(t, t_aire - 0.2, t_aire + 0.3)
    if ka > 0:
        for i, xx in enumerate((380, 540, 700)):
            o = ((t * 1.6 + i * 0.33) % 1)
            arrow(c, xx, 1060 + 50 * o, xx, 1120 + 50 * o, alpha(XRAY, ka * (1 - o) * 0.9), 8, 24)
    c.restore()
    # labels
    t_vu = wt("paso4", "vuelta")
    k = eob(ramp(t, t_vu - 0.15, t_vu + 0.2))
    if k > 0:
        for sg in (-1, 1):
            c.save(); c.translate(CX4 + sg * (A4 + 40), CY4); c.scale(k, k)
            arrowhead_arc(c, 0, 0, 52, -math.pi / 2 - sg * 1.2, -math.pi / 2 + sg * 1.4, YEL, 9)
            c.restore()
        if k > 0.5: text(c, "SE DA LA VUELTA", CX4, CY4 - 170, 46, YEL, SLAB, False, outline=INK, olw=9)
    t_re = wt("paso4", "remo") - 0.15
    kr = eob(ramp(t, t_re, t_re + 0.3))
    if kr > 0: icon_badge(c, 190, 1500, kr, "COMO UN REMO", ic_oar, t, None, 88)
    if kv > 0 or t > t_rem:
        lx = x + math.cos(ang) * 45 - 30 * sd; ly = y + math.sin(ang) * 45 - 50
        callout(c, "REMOLINO", lx, ly, 760, 690, t, t_rem - 0.1, XRAY, 40)
    t_so = wt("paso4", "sostiene")
    ks = ramp(t, t_so - 0.3, t_so + 0.1)
    if ks > 0:
        big_arrow(c, 860, 1560, 1560 - 300 * ease(ks), YEL, 18, 50)
        label_pop(c, "LA SOSTIENE", 640, 1660, t, t_so - 0.2, 60, YEL)


# ---------------------------------------------------------------- 6. paso5: pushes of air = sound
def rings(c, cx, cy, ph, bk, a=1.0, spacing=120, n=5, a0=-0.85, a1=0.85, r0=60, col=CREAM):
    cyc = ph / (2 * math.pi)
    if bk < 0.99:
        fr = cyc % 1
        for k in range(n):
            r = r0 + spacing * (fr + k)
            al = a * (1 - bk) * clamp(1 - (r - r0) / (spacing * n)) * min(1, (fr + k) * 2)
            if al <= 0: continue
            c.new_path(); c.arc(cx, cy, r, a0, a1); c.set_source_rgba(*alpha(col, al)); c.set_line_width(14 - 1.6 * k); c.stroke()
    if bk > 0.01:
        for k in range(n * 3):
            r = r0 + spacing / 3 * (k + 0.5)
            al = a * bk * 0.5 * (1 - k / (n * 3))
            c.new_path(); c.arc(cx, cy, r, a0, a1); c.set_source_rgba(*alpha(col, al)); c.set_line_width(5); c.stroke()


def scene_paso5(c, t):
    background(c, t, ORANGE)
    b = B("paso5")
    c.save(); cam(c, 1.0 + 0.04 * ease(ramp(t, b["start"], b["end"])), 540, 1100)
    ph = phase(t); bk = blurk(t)
    bx, by, s = 300, 1080, 0.95
    t_emp = wt("paso5", "empuja")
    kr = ease(ramp(t, t_emp - 0.3, t_emp + 0.2))
    rings(c, bx + 60, by - 120, ph, bk, kr, 125, 5, -0.9, 0.9, 90)
    c.save(); c.translate(bx, by + bob(t) * 0.6); c.scale(s, s); bee(c, ph, bk); c.restore()
    c.restore()
    callout(c, "EMPUJÓN", bx + 60 + 280, by - 120 - 120, 760, 720, t, t_emp + 0.1, CREAM, 38)
    # oscilloscope panel: 230 pushes per second -> a 230 Hz tone
    t_230 = wt("paso5", "doscientos") - 0.2; t_nota = wt("paso5", "nota"); t_zum = wt("paso5", "zumbido")
    kp = eob(ramp(t, t_230, t_230 + 0.35))
    if kp > 0:
        c.save(); c.translate(540, 1480); c.scale(kp, kp)
        rrect(c, -400, -110, 800, 220, 18); fill_stroke(c, CREAM, INK, 6)
        rrect(c, -380, -48, 760, 140, 10); fill_stroke(c, hx("#1E3A2A"), INK, 4)
        text(c, "230 EMPUJONES POR SEGUNDO", 0, -66, 34, INK, SLAB, False)
        c.save(); rrect(c, -380, -48, 760, 140, 10); c.clip()
        km = ease(ramp(t, t_nota - 0.3, t_nota + 0.4))
        pts = []
        for i in range(0, 761, 4):
            xx = -380 + i
            th = i / 760 * 7 * 2 * math.pi - (ph if bk < 0.5 else t * 9)
            spike = math.exp(-((math.cos(th) - 1) ** 2) * 18)  # one push per cycle
            yy = 22 - 50 * lerp(spike, 0.5 + 0.5 * math.cos(th), km) + 25 * km * 0
            pts.append((xx, yy))
        line(c, pts, hx("#7CFC9A"), 6)
        c.restore()
        c.restore()
        if km > 0.5: label_pop(c, "= 230 Hz", 540, 1660, t, t_nota + 0.1, 54, YEL)
    kn = eob(ramp(t, t_nota - 0.15, t_nota + 0.2))
    if kn > 0:
        icon_badge(c, 820, 1040, kn, "NOTA GRAVE", lambda c_: ic_note(c_, INK), t, None, 92)
    bzz_text(c, 330, 800, t, t_zum - 0.1, 80)


# ---------------------------------------------------------------- 7. junto + acelera
JX, JY, JS = 470, 1170, 1.6


def scene_junto(c, t):
    background(c, t, YEL)
    b = B("junto")
    fast = ease(ramp(t, T_REAL + 0.2, B("remate")["start"] - 0.4))
    shake = 7 * fast
    ph = phase(t); bk = blurk(t); u = math.sin(ph)
    c.save(); cam(c, 1.0 + 0.05 * ease(ramp(t, b["start"] - 0.3, B("remate")["start"])), JX, JY)
    c.translate(shake * math.sin(t * 61), shake * math.cos(t * 53))
    yb = JY + bob(t) * 0.8
    t_zum = wt("junto", "zumbido")
    kz = ease(ramp(t, t_zum - 0.3, t_zum + 0.1))
    rings(c, JX + 220, yb - 260, ph, bk, kz * 0.9, 110, 4, -1.2, 0.3, 120)
    t_tor = wt("junto", "tórax")
    c.save(); c.translate(JX, yb); c.scale(JS, JS)
    bee_xray(c, ph, bk, glow_th=pulse_at(t, t_tor - 0.1, 0.8))
    # leading-edge vortex on the forewing
    t_rem = wt("junto", "remolino")
    kv = ease(ramp(t, t_rem - 0.3, t_rem + 0.1))
    if kv > 0:
        a = wing_ang(u); wx, wy = -10 + math.cos(a) * 160, -70 + math.sin(a) * 160
        swirl(c, wx + math.sin(a) * 40, wy - math.cos(a) * 40, 30, t * 8, kv * (1 - bk * 0.5), True, YEL)
    c.restore()
    if fast > 0:  # speed lines
        for i in range(26):
            r0 = 320 + (i * 97 + t * 2600) % 900; a = i * 0.2415
            line(c, [(JX + math.cos(a) * r0, JY + math.sin(a) * r0), (JX + math.cos(a) * (r0 + 130 * fast), JY + math.sin(a) * (r0 + 130 * fast))],
                 alpha(WHITE, 0.35 * fast), 5)
    c.restore()
    lab = 1 - ramp(t, T_REAL - 0.6, T_REAL + 0.4)
    if lab > 0:
        def labels():
            def wp(lx, ly): return (JX + JS * lx, yb + JS * ly)
            a = wing_ang(u)
            callout(c, "TÓRAX", *wp(0, 75), 470, 1640, t, t_tor - 0.1, YEL, 40)
            callout(c, "MÚSCULOS", *wp(-34, 30), 180, 1500, t, wt("junto", "músculos") - 0.1, DVC, 38)
            callout(c, "ESTIRÓN", *wp(30, -10), 790, 1500, t, wt("junto", "estirón") - 0.1, DLMC, 38)
            callout(c, "ALETEO", *wp(-10 + math.cos(a) * 200, -70 + math.sin(a) * 200), 210, 720, t, wt("junto", "aleteo") - 0.1, CREAM, 40)
            vx, vy = -10 + math.cos(a) * 160 + math.sin(a) * 40, -70 + math.sin(a) * 160 - math.cos(a) * 40
            callout(c, "REMOLINO", *wp(vx, vy), 560, 650, t, t_rem - 0.1, YEL, 38)
            callout(c, "ZUMBIDO", JX + 470, yb - 420, 820, 900, t, t_zum - 0.1, CREAM, 38)
        faded(c, lab, labels)
    flash = ramp(t, B("remate")["start"] - 0.45, B("remate")["start"] - 0.3) * (1 - ramp(t, B("remate")["start"] - 0.3, B("remate")["start"] - 0.1))
    if flash > 0: c.set_source_rgba(1, 1, 1, 0.85 * flash); c.paint()


# ---------------------------------------------------------------- 8. remate: the bumblebee "myth" blackboard
def chalk(c, s, x, y, size, t, t0, dur=0.8, col=CHALK, fam=MONO, align="l"):
    k = ramp(t, t0, t0 + dur)
    if k <= 0: return 0
    font(c, fam, size, True); w = c.text_extents(s).x_advance
    x0 = x if align == "l" else x - w / 2
    c.save(); c.rectangle(x0 - 10, y - size * 1.2, (w + 20) * k, size * 1.6); c.clip()
    text(c, s, x0, y, size, alpha(col, 0.92), fam, True, "l")
    c.restore()
    return w


def bumble_pos(t):
    t0 = wt("remate", "abejorros") - 0.35
    s = t - t0
    x = lerp(-160, 700, ease(ramp(s, 0, 2.6)))
    y = 1180 - 80 * math.sin(s * 2.2)
    lp_ = ramp(s, 1.0, 2.2)  # a happy loop-the-loop
    if 0 < lp_ < 1:
        a = lp_ * 2 * math.pi
        x += -90 * math.sin(a) ; y += -90 * (1 - math.cos(a))
    if s > 2.6:
        x = 700 + 60 * math.sin((s - 2.6) * 1.4); y = 1180 - 80 * math.sin(s * 2.2)
    return x, y, s


def scene_remate(c, t):
    background(c, t, ORANGE)
    b = B("remate")
    c.save(); cam(c, 1.0 + 0.05 * ease(ramp(t, b["start"], T_LOOP)), 540, 1050)
    x0, y0, w, h = 95, 640, 890, 760
    shadow(c, lambda: rrect(c, x0, y0, w, h, 22), 14, 20, 0.45)
    rrect(c, x0, y0, w, h, 22); fill_stroke(c, GOLD, INK, 8)
    rrect(c, x0 + 26, y0 + 26, w - 52, h - 52, 10); fill_stroke(c, BOARD, INK, 5)
    c.save(); rrect(c, x0 + 26, y0 + 26, w - 52, h - 52, 10); c.clip()
    for i in range(7):  # old chalk smudges
        ellipse(c, 200 + i * 120, 760 + (i * 137) % 500, 120, 40, 0.3 * i); c.set_source_rgba(1, 1, 1, 0.035); c.fill()
    c.restore()
    rrect(c, x0 + 300, y0 + h - 30, 120, 22, 6); fill_stroke(c, CREAM2, INK, 3)  # chalk stick on the ledge
    chalk(c, "1934", x0 + w - 190, y0 + 100, 40, t, b["start"] + 0.2, 0.4)
    t_fis = wt("remate", "física")
    chalk(c, "LA FÍSICA DICE:", x0 + 70, y0 + 100, 40, t, wt("remate", "según") - 0.1, 0.5, YEL)
    chalk(c, "SUSTENTACIÓN = ½·ρ·v²·S·C", x0 + 70, y0 + 210, 44, t, t_fis - 0.1, 0.9)
    chalk(c, "ALA = 1 cm²  ·  PESO = 0,9 g", x0 + 70, y0 + 300, 38, t, t_fis + 0.5, 0.7)
    t_no = wt("remate", "deberían") - 0.2
    # the crossed-out calculation
    chalk(c, "ALAS DE AVIÓN", x0 + 70, y0 + 450, 54, t, t_no - 0.2, 0.6)
    chalk(c, "= NO VUELA", x0 + 70, y0 + 540, 64, t, t_no + 0.3, 0.6, hx("#FFB3A8"))
    # airfoil sketch
    ka = ramp(t, wt("remate", "tuvieran") - 0.2, wt("remate", "tuvieran") + 0.3)
    if ka > 0:
        c.save(); c.translate(780, y0 + 430); c.scale(1.2, 1.2)
        airfoil(c, 0, 0, -0.12, ka * 0.9, 150, alpha(CHALK, 0.0), 4)
        c.restore()
    t_av = wt("remate", "avión")
    k = ramp(t, wt("remate", "alas", 0) - 0.2, wt("remate", "alas", 0) + 0.3)
    if k > 0:  # yellow chalk ring around the assumption
        c.new_path(); ellipse(c, x0 + 285, y0 + 432, 260, 62, -0.03)
        c.set_source_rgba(*alpha(YEL, 0.9 * k)); c.set_line_width(6); c.stroke()
    t_cal = wt("remate", "cálculo")
    xmark(c, x0 + w / 2, y0 + 420, 230, t, t_cal - 0.05, 22)
    c.restore()
    # the bumblebee flying happily past
    bx, by, s = bumble_pos(t)
    if s > 0:
        for i in range(1, 14):  # dotted trail
            px, py, _ = bumble_pos(t - i * 0.09)
            if _ > 0:
                circle(c, px + 60, py + 10, 6 * (1 - i / 14)); c.set_source_rgba(*alpha(CREAM, 0.6 * (1 - i / 14))); c.fill()
        c.save(); c.translate(bx, by); c.scale(-0.95, 0.95); c.rotate(-0.1 * math.sin(t * 3))
        bee(c, phase(t), blurk(t), chubby=True)
        c.restore()
        t_vol = wt("remate", "volar")
        k = eob(ramp(t, t_vol - 0.1, t_vol + 0.25)) * (1 - ramp(t, t_vol + 1.6, t_vol + 1.9))
        if k > 0:  # "¡pues vuela!"
            c.save(); c.translate(bx + 40, by - 210); c.scale(k, k)
            rrect(c, -150, -46, 300, 92, 46); fill_stroke(c, WHITE, INK, 5)
            c.new_path(); c.move_to(-30, 44); c.line_to(-5, 80); c.line_to(10, 44); c.close_path(); fill_stroke(c, WHITE, None)
            text(c, "¡Y VUELO!", 0, 14, 40, INK, SLAB, False)
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
    ps = [wt("gancho", "zumbido") - 0.1, wt("gancho", "alas", 1) - 0.25]
    ps += [wt("imposible", w) - 0.15 for w in ("directamente", "piensa", "orden")]
    ps += [wt("paso1", "tórax") - 0.1, wt("paso1", "medio") - 0.5, wt("paso1", "cajita") - 0.1, wt("paso1", "borde") - 0.15, wt("paso1", "palancas") - 0.1]
    ps += [wt("paso2", "unos") - 0.1, wt("paso2", "suben") - 0.15, wt("paso2", "otros") - 0.1, wt("paso2", "bajan") - 0.15]
    ps += [wt("paso3", "estira") - 0.1, wt("paso3", "contrae") - 0.1, wt("paso3", "sin") - 0.15, wt("paso3", "orden") - 0.2]
    ps += [wt("paso4", "vuelta") - 0.15, wt("paso4", "remo") - 0.15, wt("paso4", "remolino") - 0.1, wt("paso4", "sostiene") - 0.2]
    ps += [wt("paso5", "empuja") + 0.1, wt("paso5", "doscientos") - 0.2, wt("paso5", "nota") - 0.15, wt("paso5", "zumbido") - 0.1]
    ps += [wt("junto", k) - 0.1 for k in ("tórax", "músculos", "estirón", "aleteo", "remolino", "zumbido")]
    ps += [wt("remate", "volar") - 0.1]
    return ps


def SFX(put, L):
    np = __import__("numpy")
    SR = L["SR"]; N = L["N"]
    tt = np.arange(N) / SR
    ctrl = np.arange(0, N / SR + 0.05, 0.02)
    sl = np.array([slow_log(x) for x in ctrl])
    fv = np.interp(tt, ctrl, F * 10 ** (-sl))                   # flaps per second heard
    ph_am = 2 * np.pi * np.cumsum(fv) / SR
    am = ((1 + np.cos(ph_am)) / 2) ** 4                            # one "push" per visible flap
    cont = np.clip((fv - 15) / 60, 0, 1)
    am = am * (1 - cont) + cont
    f0 = np.interp(tt, ctrl, 230 - 60 * sl / CFG["hud"]["max_log"])  # a little lower while slowed
    ph = 2 * np.pi * np.cumsum(f0) / SR
    buzz = sum(np.sin(k * ph) / k ** 1.2 for k in range(1, 9))     # harmonic-rich (saw-like) buzz
    buzz = L["lp"](buzz, 2500)
    # level: bed while the bee is on screen; quieter under paso4 (no bee), louder in paso5/acelerón
    lc = np.ones_like(ctrl) * 0.6
    lc[(ctrl > B("paso4")["start"] - 0.3) & (ctrl < B("paso5")["start"] - 0.3)] = 0.3
    lc[(ctrl > wt("paso5", "nota") - 0.3) & (ctrl < B("junto")["start"])] = 1.0
    lc[(ctrl > T_REAL) & (ctrl < B("remate")["start"] - 0.3)] = 1.4
    lc[(ctrl > B("remate")["start"] - 0.3) & (ctrl < wt("remate", "abejorros") - 0.3)] = 0.0
    sm = np.copy(lc)
    for i in range(1, len(sm)): sm[i] = sm[i - 1] + (lc[i] - sm[i - 1]) * 0.12
    g = np.interp(tt, ctrl, sm)
    put(buzz * am * g, 0.0, 0.05)
    put(L["zap"](0.5), wt("paso3", "orden") - 0.1, 0.35)
    for w in ("suben", "bajan"):
        put(L["whoosh"](0.35, w == "suben"), wt("paso2", w) - 0.3, 0.3)
    put(L["shimmer"](), wt("paso5", "nota") - 0.1, 0.3)
    put(L["scratch"](), wt("remate", "cálculo") - 0.05, 0.6)
    put(L["ding"](1046), wt("remate", "volar"), 0.25)


# ---------------------------------------------------------------- thumbnails ("ALAS INVISIBLES")
def THUMB_V(c):
    background(c, 3.0, YEL)
    c.save(); c.translate(0, 0); dusk(c, 3.0); c.restore()
    glow(c, 560, 1250, 520, YEL, 0.45)
    c.save(); c.translate(600, 1290); c.scale(2.15, 2.15); c.rotate(-0.06); bee(c, 0.0, 1.0); c.restore()
    for i, ln in enumerate(["ALAS", "INVISIBLES"]):
        sz = fit_size(c, ln, SLAB, 200, 980)
        text(c, ln, 540, 330 + i * 210, sz, YEL if i else WHITE, SLAB, False, outline=INK, olw=22)


def THUMB_H(c):
    g = cairo.LinearGradient(0, 0, 0, 720); g.add_color_stop_rgba(0, *BG_TOP); g.add_color_stop_rgba(1, *BG_BOT); c.set_source(g); c.paint()
    glow(c, 960, 400, 420, YEL, 0.4)
    c.save(); c.translate(980, 470); c.scale(1.15, 1.15); c.rotate(-0.06); bee(c, 0.0, 1.0); c.restore()
    for i, ln in enumerate(["ALAS", "INVISIBLES"]):
        sz = fit_size(c, ln, SLAB, 150, 640)
        text(c, ln, 350, 320 + i * 170, sz, YEL if i else WHITE, SLAB, False, outline=INK, olw=20)
