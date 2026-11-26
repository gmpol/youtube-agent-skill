"""Music + SFX synthesised with numpy (nothing third-party), mixed with the narration.
Guide levels: voice ~17 dB over the music while speaking, music swells where nobody speaks, final -14 LUFS / -1.5 dBTP.
The project's scenes.py may define:  POPS() -> [t, ...]   (pop on each callout/icon)
                                      SFX(put, lib)        (extra events: put(signal, t, gain); lib = dict of generators)
                                      AMBIENT(tt) -> gain array for an ambience bed under the opening + loop (optional)
project.json "music": {"bpm": 118, "roots": [57,53,48,55], "minor": [true,false,false,false]}"""
import json, os, re, subprocess, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
from core import CFG, PROJ, B, wt, T_SLOW, T_REAL, T_LOOP, DUR, CARD_WINS

S = R.S; SR = 44100; N = int(DUR * SR); rng = np.random.default_rng(7)
os.makedirs(os.path.join(PROJ, "stems"), exist_ok=True)

def t_(n): return np.arange(n) / SR
def env(n, a=0.005, d=0.2):
    t = t_(n); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def put(buf, x, at, g=1.0):
    i = int(at * SR)
    if i < 0: x = x[-i:]; i = 0
    if i >= len(buf): return
    x = x[: len(buf) - i]; buf[i:i + len(x)] += g * x
def lp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / np.sqrt(1 + (f / fc) ** 4); return np.fft.irfft(X, len(x))
def hp(x, fc): return x - lp(x, fc)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)

# ------------------------------------------------------------ music
M = CFG.get("music", {}); BPM = M.get("bpm", 118); beat = 60 / BPM; step = beat / 4
roots = M.get("roots", [57, 53, 48, 55]); minor = M.get("minor", [True, False, False, False])
music = np.zeros(N); pat = [0, 1, 2, 1, 0, 2, 1, 2]
def pulse(f, n, duty=0.25): return np.where((f * t_(n)) % 1 < duty, 1.0, -1.0)
for k in range(int(DUR / step) + 1):
    at = k * step; bar = int(at / (beat * 4)) % len(roots); r = roots[bar]; ch = [0, 3, 7] if minor[bar % len(minor)] else [0, 4, 7]
    note = r + 12 + ch[pat[k % 8]] + (12 if (k // 8) % 2 else 0); n = int(step * SR * 0.95)
    put(music, lp(pulse(mtof(note), n), 2600) * env(n, 0.002, 0.09), at, 0.16)
    if k % 4 == 0: nb = int(beat * SR * 0.9); put(music, np.sin(2 * np.pi * mtof(r - 12) * t_(nb)) * env(nb, 0.005, 0.25), at, 0.45)
    if k % 2 == 1: nh = int(0.05 * SR); put(music, hp(rng.standard_normal(nh), 6000) * env(nh, 0.001, 0.015), at, 0.10)
    if k % 16 == 8: ns = int(0.15 * SR); put(music, lp(rng.standard_normal(ns), 3500) * env(ns, 0.001, 0.05), at, 0.22)

# ------------------------------------------------------------ sfx library
def whoosh(d=0.45, up=True):
    n = int(d * SR); x = rng.standard_normal(n) * np.sin(np.pi * t_(n) / d) ** 2
    X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR); X *= np.exp(-((f - (2500 if up else 900)) / 2200) ** 2); return np.fft.irfft(X, n) * 3
def pop(f0=900):
    n = int(0.09 * SR); t = t_(n); return np.sin(2 * np.pi * (f0 + 900 * np.exp(-t * 60)) * t) * env(n, 0.001, 0.03)
def ding(f=1568):
    n = int(1.6 * SR); t = t_(n); return sum(a * np.sin(2 * np.pi * f * m * t) for m, a in [(1, 1), (2, 0.35), (3, 0.12)]) * env(n, 0.002, 0.5)
def scratch(): n = int(0.18 * SR); return lp(rng.standard_normal(n), 4000) * env(n, 0.002, 0.06) * 1.6
def zap(d=0.6):
    n = int(d * SR); t = t_(n); x = np.sign(np.sin(2 * np.pi * 110 * t)) * (0.5 + 0.5 * rng.standard_normal(n)); return lp(x, 3000) * np.sin(np.pi * t / d) * 0.6
def tape_stop(d=1.2):
    n = int(d * SR); t = t_(n); f = 600 * (1 - t / d) ** 2 + 40; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 0.5 * 0.7
def riser(d):
    n = int(d * SR); t = t_(n); f = 200 * 2 ** (4 * t / d)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + lp(rng.standard_normal(n), 5000) * 0.6) * (t / d) ** 2
def boom(): n = int(1.0 * SR); t = t_(n); return np.sin(2 * np.pi * (45 + 80 * np.exp(-t * 12)) * t) * env(n, 0.002, 0.3) * 1.4
def shimmer():
    n = int(1.2 * SR); t = t_(n); return sum(np.sin(2 * np.pi * f * t) * env(n, 0.01, 0.25 + i * 0.1) for i, f in enumerate([2637, 3136, 3951, 4699])) * 0.25
def tone(f, d, a=0.01, dec=None):
    n = int(d * SR); t = t_(n); return np.sin(2 * np.pi * f * t) * (env(n, a, dec) if dec else np.minimum(1, t / a) * np.minimum(1, (d - t) / 0.05))
def noise(d, fc=3000): n = int(d * SR); return lp(rng.standard_normal(n), fc)
def click(): n = int(0.02 * SR); return hp(rng.standard_normal(n), 2000) * env(n, 0.0005, 0.004) * 1.5
LIB = dict(whoosh=whoosh, pop=pop, ding=ding, scratch=scratch, zap=zap, tape_stop=tape_stop, riser=riser, boom=boom,
           shimmer=shimmer, tone=tone, noise=noise, click=click, t_=t_, env=env, lp=lp, hp=hp, SR=SR, N=N)

sfx = np.zeros(N)
for key, t0, t1 in CARD_WINS:
    if t0 > 0.2: put(sfx, whoosh(), t0 - 0.12, 0.55)
for name, a, b, fn in R.TL[1:]: put(sfx, whoosh(0.5, False), a - 0.2, 0.45)
for i, p in enumerate(S.POPS() if hasattr(S, "POPS") else []): put(sfx, pop(700 + 120 * (i % 4)), p, 0.5)
put(sfx, tape_stop(1.3), B("freno")["end"] - 1.0, 0.5)
put(sfx, riser(max(0.5, B("remate")["start"] - T_REAL - 0.3)), T_REAL, 0.5)
put(sfx, boom(), B("remate")["start"] - 0.4, 0.6)
put(sfx, whoosh(0.8, False), T_LOOP + 0.1, 0.35)
if hasattr(S, "SFX"): S.SFX(lambda x, at, g=1.0: put(sfx, x, at, g), LIB)
tt = t_(N)
if hasattr(S, "AMBIENT"): sfx += S.AMBIENT(tt, LIB)

# ------------------------------------------------------------ music automation: swell where nobody speaks
voice_ranges = [(b["start"], b["end"]) for b in R.BEATS.values()]
ctrl = np.arange(0, DUR, 0.05)
target = np.array([0.0 if any(a - 0.15 <= x <= b + 0.15 for a, b in voice_ranges) else 8.0 for x in ctrl])
target[(ctrl > T_REAL + 0.1) & (ctrl < B("remate")["start"] - 0.3)] = 14.0
sm = np.copy(target)
for i in range(1, len(sm)): sm[i] = sm[i - 1] + (target[i] - sm[i - 1]) * (0.35 if target[i] > sm[i - 1] else 0.5)
music_auto = music * 10 ** (np.interp(tt, ctrl, sm) / 20)

# ------------------------------------------------------------ mix
def wav_write(path, x, ch=1):
    with wave.open(path, "wb") as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
def lufs(path):
    o = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1])
with wave.open(os.path.join(PROJ, "narration.wav")) as w:
    voice = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]
stems = {"voice": voice, "music_bed": music, "sfx": sfx}; gain = {}
for k, x in stems.items():
    p = os.path.join(PROJ, "stems", k + ".wav"); g0 = 0.5 / max(1e-9, np.abs(x).max()); wav_write(p, x * g0); gain[k] = (lufs(p), g0)
TGT = {"voice": -16.0, "music_bed": -34.5, "sfx": -24.0}
def scale(k): L, g0 = gain[k]; return g0 * 10 ** ((TGT[k] - L) / 20)
mix = voice * scale("voice") + music_auto * scale("music_bed") + sfx * scale("sfx")
st = np.stack([mix, mix], 1); w_ = music_auto * scale("music_bed") * 0.15; st[:, 0] += w_; st[:, 1] -= w_
raw = os.path.join(PROJ, "mix_raw.wav"); wav_write(raw, st.reshape(-1) * 0.9, 2)
o = subprocess.run(["ffmpeg", "-nostats", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
m = json.loads(o[o.rfind("{"): o.rfind("}") + 1])
flt = (f"loudnorm=I=-14:TP=-1.5:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
       f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", flt + ",aresample=44100", os.path.join(PROJ, "mix.wav")], check=True)
os.remove(raw)
wav_write(os.path.join(PROJ, "stems", "music_final.wav"), music_auto * scale("music_bed"))
wav_write(os.path.join(PROJ, "stems", "voice_final.wav"), voice * scale("voice"))
print("mix LUFS", lufs(os.path.join(PROJ, "mix.wav")))
