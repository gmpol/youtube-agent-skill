"""Synthesise music + SFX (numpy only, nothing third-party), then mix with the narration.
Levels from guia_de_estilo.md §5: voice on top, music ~16-18 dB under the voice, swells only where there is no voice,
final -14 LUFS integrated, true peak <= -1.5 dBTP.  Writes build/mix.wav and build/stems/*.wav."""
import json, os, re, subprocess, wave
import numpy as np
import render as R

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
DUR = R.DUR
N = int(DUR * SR)
rng = np.random.default_rng(7)
os.makedirs(os.path.join(HERE, "stems"), exist_ok=True)

def t_(n): return np.arange(n) / SR
def env(n, a=0.005, d=0.2):
    t = t_(n); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def put(buf, x, at, g=1.0):
    i = int(at * SR)
    if i >= len(buf): return
    x = x[: len(buf) - i]; buf[i:i + len(x)] += g * x
def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
    return y
def onepole_lp_fast(x, fc):  # vectorised-ish via FFT brickwall-ish for long signals
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / np.sqrt(1 + (f / fc) ** 4); return np.fft.irfft(X, len(x))

# ------------------------------------------------------------ music: soft chiptune, 118 BPM, Am-F-C-G
BPM = 118; beat = 60 / BPM; step = beat / 4
music = np.zeros(N)
roots = [57, 53, 48, 55]  # A3 F3 C3 G3 (midi)
chords = [[0, 3, 7], [0, 4, 7], [0, 4, 7], [0, 4, 7]]
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def pulse(f, n, duty=0.25):
    ph = (f * t_(n)) % 1; return np.where(ph < duty, 1.0, -1.0)
pat = [0, 1, 2, 1, 0, 2, 1, 2]  # arpeggio order
nsteps = int(DUR / step) + 1
for k in range(nsteps):
    at = k * step; bar = int(at / (beat * 4)) % 4
    r = roots[bar]; ch = chords[bar]
    note = r + 12 + ch[pat[k % 8]] + (12 if (k // 8) % 2 else 0)
    n = int(step * SR * 0.95)
    put(music, onepole_lp_fast(pulse(mtof(note), n), 2600) * env(n, 0.002, 0.09), at, 0.16)
    if k % 4 == 0:  # bass on the beat
        nb = int(beat * SR * 0.9); put(music, np.sin(2 * np.pi * mtof(r - 12) * t_(nb)) * env(nb, 0.005, 0.25), at, 0.45)
    if k % 2 == 1:  # soft hat
        nh = int(0.05 * SR); h = rng.standard_normal(nh); h = h - lowpass(h, 6000); put(music, h * env(nh, 0.001, 0.015), at, 0.10)
    if k % 16 == 8:  # soft snare/clap on 3
        ns = int(0.15 * SR); s = onepole_lp_fast(rng.standard_normal(ns), 3500); put(music, s * env(ns, 0.001, 0.05), at, 0.22)

# ------------------------------------------------------------ sfx
sfx = np.zeros(N)
def whoosh(d=0.45, up=True):
    n = int(d * SR); x = rng.standard_normal(n); t = t_(n)
    e = np.sin(np.pi * t / d) ** 2
    X = np.fft.rfft(x * e); f = np.fft.rfftfreq(n, 1 / SR); X *= np.exp(-((f - (2500 if up else 900)) / 2200) ** 2); return np.fft.irfft(X, n) * 3
def pop(f0=900):
    n = int(0.09 * SR); t = t_(n); return np.sin(2 * np.pi * (f0 + 900 * np.exp(-t * 60)) * t) * env(n, 0.001, 0.03)
def ding():
    n = int(1.6 * SR); t = t_(n)
    return sum(a * np.sin(2 * np.pi * f * t) for f, a in [(1568, 1), (3136, 0.35), (4704, 0.12)]) * env(n, 0.002, 0.5)
def scratch():
    n = int(0.18 * SR); return onepole_lp_fast(rng.standard_normal(n), 4000) * env(n, 0.002, 0.06) * 1.6
def zap(d=0.6):
    n = int(d * SR); t = t_(n); x = np.sign(np.sin(2 * np.pi * 110 * t)) * (0.5 + 0.5 * rng.standard_normal(n))
    return onepole_lp_fast(x, 3000) * np.sin(np.pi * t / d) * 0.6
def tape_stop(d=1.2):
    n = int(d * SR); t = t_(n); f = 600 * (1 - t / d) ** 2 + 40
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 0.5 * 0.7
def riser(d):
    n = int(d * SR); t = t_(n); f = 200 * 2 ** (4 * t / d)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + onepole_lp_fast(rng.standard_normal(n), 5000) * 0.6
    return s * (t / d) ** 2
def boom():
    n = int(1.0 * SR); t = t_(n); return np.sin(2 * np.pi * (45 + 80 * np.exp(-t * 12)) * t) * env(n, 0.002, 0.3) * 1.4
def shimmer():
    n = int(1.2 * SR); t = t_(n)
    return sum(np.sin(2 * np.pi * f * t) * env(n, 0.01, 0.25 + i * 0.1) for i, f in enumerate([2637, 3136, 3951, 4699])) * 0.25

for key, t0, t1 in R.CARD_WINS:  # whoosh as each card arrives
    if t0 > 0.2: put(sfx, whoosh(), t0 - 0.12, 0.55)
for name, a, b in R.SCENES[1:]:  # and on every scene change
    put(sfx, whoosh(0.5, False), a - 0.2, 0.45)
wt = R.wt
pops = [wt("imposible", w) - 0.15 for w in ("llama", "resistencia", "rojo")] + \
       [wt("paso1", "magnetrón"), wt("paso1", "voltios") - 0.2, wt("paso1", "escupe") + 0.2, wt("paso1", "wifi") - 0.2,
        wt("paso2", "metal") - 0.2, wt("paso2", "rebotan"), wt("paso3", "positivo"), wt("paso3", "negativo"),
        wt("paso4", "queman"), wt("paso4", "frías"), wt("paso4", "seis"), wt("paso5", "doce") - 0.3, wt("paso5", "agujeros") - 0.2] + \
       [wt("junto", w) for w in ("enchufe", "magnetrón", "ondas", "agua", "calor")]
for i, p in enumerate(pops): put(sfx, pop(700 + 120 * (i % 4)), p, 0.5)
for w in ("llama", "resistencia", "rojo"): put(sfx, scratch(), wt("imposible", w) + 0.2, 0.5)
put(sfx, ding(), wt("imposible", "hierve", end=True) + 0.05, 0.45)
put(sfx, tape_stop(1.3), wt("freno", "veces"), 0.5)
put(sfx, zap(0.8), wt("paso1", "voltios") - 0.6, 0.35)
put(sfx, zap(0.5), wt("junto", "enchufe"), 0.25)
put(sfx, riser(R.B("remate")["start"] - R.T_REAL - 0.3), R.T_REAL, 0.5)
put(sfx, boom(), R.B("remate")["start"] - 0.4, 0.6)
put(sfx, shimmer(), wt("remate", "helada") - 0.2, 0.5)
put(sfx, whoosh(0.8, False), R.T_LOOP + 0.1, 0.35)

# microwave hum: under the opening and back again on the loop, so the seam is inaudible
hum = (np.sin(2 * np.pi * 100 * t_(N)) * 0.5 + np.sin(2 * np.pi * 200 * t_(N)) * 0.2 + onepole_lp_fast(rng.standard_normal(N), 900) * 0.6)
tt = t_(N); humg = np.where(tt < R.T_LENTO, 1.0, 0) * np.clip((R.T_LENTO + 0.3 - tt) / 0.6, 0, 1) + np.clip((tt - R.T_LOOP) / 0.8, 0, 1)
sfx += hum * np.clip(humg, 0, 1) * 0.10

# ------------------------------------------------------------ music level automation (no voice -> swell)
voice_ranges = [(b["start"], b["end"]) for b in R.BEATS.values()]
def speaking(x): return any(a - 0.15 <= x <= b + 0.15 for a, b in voice_ranges)
g_db = np.full(N, 0.0)
ctrl = np.arange(0, DUR, 0.05)
target = np.array([0.0 if speaking(x) else 8.0 for x in ctrl])
target[(ctrl > R.T_REAL + 0.1) & (ctrl < R.B("remate")["start"] - 0.3)] = 14.0  # the acelerón: music takes over
sm = np.copy(target)
for i in range(1, len(sm)): sm[i] = sm[i - 1] + (target[i] - sm[i - 1]) * (0.35 if target[i] > sm[i - 1] else 0.5)
g_db = np.interp(tt, ctrl, sm)
music_auto = music * 10 ** (g_db / 20)

# ------------------------------------------------------------ stems -> loudness -> mix
def wav_write(path, x, ch=1):
    with wave.open(path, "wb") as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
def lufs(path):
    o = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1])

with wave.open(os.path.join(HERE, "narration.wav")) as w:
    voice = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]

stems = {"voice": voice, "music_bed": music, "sfx": sfx}
gain = {}
for k, x in stems.items():
    p = os.path.join(HERE, "stems", k + ".wav"); wav_write(p, x / max(1e-9, np.abs(x).max()) * 0.5); gain[k] = (lufs(p), 0.5 / max(1e-9, np.abs(x).max()))
TGT = {"voice": -16.0, "music_bed": -33.0, "sfx": -24.0}
def scale(k): L, g0 = gain[k]; return g0 * 10 ** ((TGT[k] - L) / 20)
mix = voice * scale("voice") + music_auto * scale("music_bed") + sfx * scale("sfx")
st = np.stack([mix, mix], 1)
st[:, 0] += music_auto * scale("music_bed") * 0.15; st[:, 1] -= music_auto * scale("music_bed") * 0.15  # a little width
raw = os.path.join(HERE, "mix_raw.wav"); wav_write(raw, st.reshape(-1) * 0.9, 2)
print("stem LUFS (raw):", {k: v[0] for k, v in gain.items()})

# two-pass loudnorm to -14 LUFS / -1.5 dBTP
o = subprocess.run(["ffmpeg", "-nostats", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
m = json.loads(o[o.rfind("{"): o.rfind("}") + 1])
flt = (f"loudnorm=I=-14:TP=-1.5:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
       f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", flt + ",aresample=44100", os.path.join(HERE, "mix.wav")], check=True)
# documentation: music level under the voice vs the voice itself
wav_write(os.path.join(HERE, "stems", "music_final.wav"), music_auto * scale("music_bed"))
wav_write(os.path.join(HERE, "stems", "voice_final.wav"), voice * scale("voice"))
print("mix LUFS", lufs(os.path.join(HERE, "mix.wav")))
