"""Paso 5: check the final file against the style guide. Prints a report; writes review_frames.png."""
import json, os, re, subprocess, unicodedata, wave
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
import numpy as np

HERE = os.path.abspath(os.environ.get("PROJ", ".")); VID = os.path.join(HERE, "video_final.mp4")
CFG = json.load(open(os.path.join(HERE, "project.json")))
def run(*a): return subprocess.run(a, capture_output=True, text=True)

# 1. container
p = json.loads(run("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", VID).stdout)
v = next(s for s in p["streams"] if s["codec_type"] == "video"); a = [s for s in p["streams"] if s["codec_type"] == "audio"]
print(f"[1] {float(p['format']['duration']):.2f} s · {v['width']}x{v['height']} · {v['r_frame_rate']} fps · {v['codec_name']} {v.get('profile')} · "
      f"audio: {len(a)} pista(s) {a[0]['codec_name'] if a else '-'} {a[0].get('channels') if a else ''}ch · {int(p['format']['size'])/1e6:.1f} MB")

# 2. loudness of the delivered file
o = run("ffmpeg", "-nostats", "-i", VID, "-af", "ebur128=peak=true", "-f", "null", "-").stderr
I = re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1]; LRA = re.findall(r"LRA:\s+(-?[\d.]+) LU", o)[-1]; TP = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", o)[-1]
print(f"[2] integrado {I} LUFS (guía −14) · LRA {LRA} LU (guía 2–4) · pico verdadero {TP} dBTP (guía < −1)")

# 3. end of the audio: is the last word cut?
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", VID, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
words = json.load(open(os.path.join(HERE, "words.json")))
last_end = words[-1]["end"]; dur = len(x) / 16000
tail = x[int((dur - 0.15) * 16000):]
print(f"[3] última palabra termina en {last_end:.2f} s; el audio dura {dur:.2f} s → margen {dur-last_end:.2f} s; "
      f"nivel últimos 150 ms {20*np.log10(np.sqrt((tail**2).mean())+1e-9):.1f} dBFS")

# 4. voice vs music under the voice (stems as mixed, before the final linear gain)
def rd(n):
    with wave.open(os.path.join(HERE, "stems", n)) as w: return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
vo, mu = rd("voice_final.wav"), rd("music_final.wav"); n = min(len(vo), len(mu)); vo, mu = vo[:n], mu[:n]
mask = np.zeros(n, bool)
for w_ in words: mask[int(w_["start"] * 44100): int(w_["end"] * 44100)] = True
rms = lambda s: 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-9)
print(f"[4] con voz: voz {rms(vo[mask]):.1f} dB · música {rms(mu[mask]):.1f} dB → la voz va {rms(vo[mask]) - rms(mu[mask]):.1f} dB por encima "
      f"(guía ≈ 16–18) · sin voz la música sube a {rms(mu[~mask]):.1f} dB")

# 5. subtitles vs what is actually heard in the FINAL file
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(VID, language="es", word_timestamps=True, initial_prompt=CFG.get("whisper_prompt", ""))
heard = [w for s in segs for w in s.words]
def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))
def ass_t(s): h, m_, s_ = s.split(":"); return int(h) * 3600 + int(m_) * 60 + float(s_)
subs = []
for ln in open(os.path.join(HERE, "subs.ass")):
    if ln.startswith("Dialogue:"):
        f = ln.split(",", 9); txt = re.sub(r"\{[^}]*\}", "", f[9]).strip()
        subs.append((ass_t(f[1]), ass_t(f[2]), txt))
ok = 0; bad = []
for t0, t1, txt in subs:
    said = " ".join(w.word for w in heard if w.start < t1 and w.end > t0)
    want = [norm(w) for w in txt.split() if norm(w) and not norm(w).isdigit()]
    got = norm(said)
    hit = sum(1 for w in want if w in got) / max(1, len(want))
    (ok := ok + 1) if hit >= 0.6 else bad.append((round(t0, 2), txt, said.strip()))
print(f"[5] subtítulos que coinciden con lo que se oye en ese momento: {ok}/{len(subs)}")
for b in bad[:8]: print("     ✗", b)

# 6. five frames
D = float(p["format"]["duration"]); ts = [round(D * k, 1) for k in (0.02, 0.25, 0.5, 0.75, 0.95)]
sel = "+".join(f"eq(n\\,{int(t*30)})" for t in ts)
run("ffmpeg", "-v", "error", "-y", "-i", VID, "-vf", f"select='{sel}',scale=360:-1,tile=5x1", "-frames:v", "1", os.path.join(HERE, "review_frames.png"))
for t in ts:
    said = " ".join(w.word.strip() for w in heard if w.start <= t + 0.6 and w.end >= t - 0.6)
    sub = next((s[2] for s in subs if s[0] <= t < s[1]), "—")
    print(f"     frame {t:5.1f}s · subtítulo en pantalla: «{sub}» · se oye: «{said}»")
