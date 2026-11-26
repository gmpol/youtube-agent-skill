# Writing `scenes.py` for a project

A project folder (`output/videos/<slug>/`) already has `project.json`, `beats.json`, `beats_timed.json`,
`words.json` (whisper word timings of the real narration) and `subs.ass`. You write `scenes.py`: the
illustrations. Everything is drawn with pycairo, no images or footage from anywhere.

Reference for look and quality: `output/build/render.py` (the finished microwave video, same style).
Style rules: `output/guia_de_estilo.md` (read §1, §2, §5).

## Contract

```python
from core import *          # primitives, palette, timing helpers, W=1080, H=1920

def scene_xxx(c, t): ...    # draw the WHOLE frame for global time t (background included)

SCENES = [                  # contiguous, covering 0 .. T_LOOP+0.15; crossfades happen at each boundary
    ("front", 0.0, T_SLOW + 0.5, scene_front),
    ("paso1", ..., ..., scene_paso1),
    ...
    ("remate", B("remate")["start"] - 0.1, T_LOOP + 0.15, scene_remate),
]
LOOP_FN = scene_front       # called as LOOP_FN(c, 0.0): must draw EXACTLY frame 0 (the video loops into it)
XF = {"remate": 0.08}       # optional per-scene crossfade length (default 0.35 s)
def POPS(): return [...]    # times of callouts/icons appearing (a pop SFX is put on each)
def SFX(put, L): ...        # optional extra sounds: put(L["ding"](), t, 0.4) ; L has whoosh pop ding scratch zap
                            # tape_stop riser boom shimmer tone(f, d, a, dec) noise(d, fc) click t_ env lp hp SR N
def THUMB_V(c): ...         # 1080x1920 thumbnail
def THUMB_H(c): ...         # 1280x720 thumbnail
```

The HUD (speed label + gauge + counter, y 90–200) and the numbered step cards (y 222–~460) are drawn by
the engine on top of your scene. Captions are burned at y≈500–580. **Keep your illustration between
y≈600 and y≈1700**, nothing important in the bottom 220 px or the right 140 px (platform UI).

## Timing helpers (all in seconds of the final video)
- `B("paso2")["start"]`, `["end"]`, `["pause"]` – beat boundaries. Beat ids: gancho, imposible, freno, paso1..paso5, junto, acelera, remate.
- `wt("paso2", "imán")` – when that word starts (`end=True` for its end; `nth=1` for the 2nd match). Accent/case-insensitive substring match. Make every callout, icon and change land on the word that says it.
- `T_SLOW` (slow motion reached), `T_REAL` ("a velocidad real" said; then 4 s with no voice = the acelerón), `T_LOOP` (loop dissolve), `DUR`.
- `slow_log(t)`, `speed_fraction(t)` (1 = real speed), `anim_time(t)`: physical time — for something that really oscillates at f Hz use `phase = 2*pi*f*anim_time(t)` so it is visible in slow motion and becomes a blur in the acelerón.
- `ramp(t, t0, t1)`, `ease`, `eob` (pop), `lerp`, `mix`, `alpha`, `pulse_at`.

## Primitives
`rrect, circle, fill_stroke(c, fill, stroke=INK, lw)` (thick dark outlines = the style), `shadow(c, path_fn)`,
`text(c, s, x, y, size, color, fam=SANS|SLAB|MONO, bold, align, outline=INK, olw)`, `fit_size`, `line`, `arrow`,
`glow`, `wave(c, x0, x1, y, amp, wavelength, phase, color, lw)`, `callout(c, label, ax, ay, lx, ly, t, t0, color)`,
`xmark`, `icon_badge(c, x, y, k, label, draw_fn, t, crossed_at)`, `cam(c, scale, cx, cy)`, `background(c, t, tint)`.
Palette: INK CREAM CREAM2 RED GOLD ORANGE ORANGE2 RUST YEL STEEL LAV WHITE COLD HOT XRAY GREEN METAL DARK NIGHT.
Gotcha: cairo keeps the current point; `text`/`line`/`circle` already reset it, but if you call `c.arc` yourself
after drawing text, call `c.new_path()` first or you get a stray line.

## Shape of every video (same as the microwave)
1. `front` (gancho + imposible + freno): the object, big, centred, warm colours on the dark background, gentle
   push-in. In `imposible`, 3 crossed-out icon badges appear on their words (like the microwave's llama/resistencia/brasas).
   During `freno` zoom in and fade to the see-through / cut-away version.
2. One scene per paso (1–5), each a different view; something new every 2–3 s, synced to words; callouts with leader lines.
3. `junto`: the full cut-away, labels lighting up in order on each word of the junto line.
4. `acelera` (+ the 4 s silent gap): same view, everything speeds up to a blur, speed lines, slight shake, white flash at the end.
5. `remate`: the final twist, then the dissolve back to frame 0 (LOOP_FN).

## Commands (from repo root)
```bash
E=output/engine; P=output/videos/<slug>
PROJ=$P python3 $E/render.py --sheet $P/sheet.png 0 3 8 ...     # contact sheet; LOOK at it with the Read tool
PROJ=$P python3 $E/render.py --still 12.3 $P/still.png
JOBS=2 $E/make.sh $P video audio mux thumb review                 # full render (2–4 min) + checks
```
`review` must print: −14 LUFS, voice 16–18 dB over music, subtitles N/N, frames listed.
