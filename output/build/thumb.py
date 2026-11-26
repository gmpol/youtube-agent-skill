"""Thumbnail: 'NO ES FUEGO' (3 words, linted with yt-package/title.py: 98/100 against the winning title).
Writes ../miniatura.png (1080x1920) and ../miniatura_16x9.png (1280x720)."""
import math, os, cairo
import render as R

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def flame_x(c, x, y, s):
    c.new_path(); c.save(); c.translate(x, y); c.scale(s, s)
    c.arc(0, 0, 105, 0, 2 * math.pi); R.fill_stroke(c, R.CREAM, R.INK, 7)
    c.move_to(0, -70); c.curve_to(55, -10, 55, 55, 0, 62); c.curve_to(-55, 55, -55, -10, 0, -70); R.fill_stroke(c, R.ORANGE, R.INK, 6)
    c.restore()
    R.xmark(c, x, y, 75 * s, 10, 0, 22 * s)

def vertical():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1080, 1920); c = cairo.Context(s)
    R.background(c, 3.0, R.HOT)
    c.save(); c.translate(0, 330); R.cam(c, 1.05, 540, 1080); R.microwave_front(c, 9.0, 1.0, 1.0, 1.0); c.restore()
    R.glow(c, 560, 960, 400, R.HOT, 0.55)
    R.water_molecule(c, 560, 960, -0.5, 3.0, 1.0, labels=True)
    flame_x(c, 880, 700, 1.0)
    for i, ln in enumerate(["NO ES", "FUEGO"]):
        R.text(c, ln, 540, 330 + i * 200, 200, R.YEL if i else R.WHITE, R.SLAB, False, outline=R.INK, olw=22)
    s.write_to_png(os.path.join(OUT, "miniatura.png"))

def horizontal():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1280, 720); c = cairo.Context(s)
    g = cairo.LinearGradient(0, 0, 0, 720); g.add_color_stop_rgba(0, *R.BG_TOP); g.add_color_stop_rgba(1, *R.BG_BOT); c.set_source(g); c.paint()
    R.glow(c, 950, 380, 420, R.HOT, 0.45)
    c.save(); c.translate(700, -310); c.scale(0.62, 0.62); R.microwave_front(c, 9.0, 1.0, 1.0, 1.0); c.restore()
    R.water_molecule(c, 1010, 360, -0.5, 2.2, 1.0, labels=True)
    for i, ln in enumerate(["NO ES", "FUEGO"]):
        R.text(c, ln, 340, 320 + i * 170, 150, R.YEL if i else R.WHITE, R.SLAB, False, outline=R.INK, olw=22)
    flame_x(c, 1180, 620, 0.75)
    s.write_to_png(os.path.join(OUT, "miniatura_16x9.png"))

vertical(); horizontal(); print("ok")
