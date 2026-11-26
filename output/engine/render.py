"""Render a project's frames.  PROJ=<dir> python3 render.py --sheet out.png t1 t2 ... | --still t out.png | --video out.mp4"""
import argparse, math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import *  # noqa
sys.path.insert(0, PROJ)
import scenes as S  # the project's illustrations

XF_DEFAULT = 0.35

def timeline():
    """scenes.SCENES: [(name, t_start, t_end, fn)]. The loop tail (frame 0 again) is appended here."""
    sc = list(S.SCENES) + [("loop", T_LOOP + 0.15, DUR + 1, lambda c, t: S.LOOP_FN(c, 0.0))]
    return sc
TL = timeline()
XF = {"loop": 0.6, **getattr(S, "XF", {})}

def draw_scene(c, fn, t):
    c.save(); fn(c, t); c.restore(); c.new_path()

def frame(t):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_antialias(cairo.ANTIALIAS_GOOD)
    idx = [i for i, sc in enumerate(TL) if sc[1] <= t < sc[2]] or [len(TL) - 1]
    i = idx[0]; name, a, b, fn = TL[i]
    draw_scene(c, fn, t)
    xf = XF.get(name, XF_DEFAULT)
    if i > 0 and t < a + xf:
        c.push_group(); draw_scene(c, TL[i - 1][3], t); c.pop_group_to_source()
        c.paint_with_alpha(1 - ease((t - a) / xf))
    if name == "loop": hud(c, 0.0); cards(c, 0.0)
    else: hud(c, t); cards(c, t)
    return s

def render_range(f0, f1, out):
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        s = frame(f / FPS); s.flush(); enc.stdin.write(bytes(s.get_data()))
    enc.stdin.close(); enc.wait()

def sheet(out, ts):
    cols = min(len(ts), 6); rows = math.ceil(len(ts) / cols); sw, sh = W // 3, H // 3
    Sf = cairo.ImageSurface(cairo.FORMAT_ARGB32, sw * cols, sh * rows); c = cairo.Context(Sf)
    for k, t in enumerate(ts):
        c.save(); c.translate((k % cols) * sw, (k // cols) * sh); c.scale(1 / 3, 1 / 3)
        c.set_source_surface(frame(t), 0, 0); c.paint(); c.restore()
        text(c, f"{t:.1f}s", (k % cols) * sw + 8, (k // cols) * sh + 30, 26, YEL, SANS, True, "l")
    Sf.write_to_png(out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", nargs=2); ap.add_argument("--sheet", nargs="+"); ap.add_argument("--video")
    ap.add_argument("--jobs", type=int, default=os.cpu_count())
    a = ap.parse_args()
    if a.still: frame(float(a.still[0])).write_to_png(a.still[1])
    elif a.sheet: sheet(a.sheet[0], [float(x) for x in a.sheet[1:]])
    elif a.video:
        from multiprocessing import Pool
        n = int(DUR * FPS); J = a.jobs; step = math.ceil(n / J)
        parts = [(i * step, min(n, (i + 1) * step), os.path.join(PROJ, f"part{i}.mp4")) for i in range(J)]
        with Pool(J) as p: p.starmap(render_range, parts)
        lst = os.path.join(PROJ, "parts.txt"); open(lst, "w").write("".join(f"file '{x[2]}'\n" for x in parts))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", a.video], check=True)
        for x in parts: os.remove(x[2])
        os.remove(lst)
        print("video", a.video, n, "frames", DUR, "s")
