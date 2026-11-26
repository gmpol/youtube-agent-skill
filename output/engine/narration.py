"""Build the narration track: one edge-tts clip per beat, joined with the pauses from beats.json.
Writes build/narration.wav (44.1 kHz mono) and build/beats_timed.json (start/end of each beat)."""
import json, os, subprocess, sys, wave
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PROJ = os.path.abspath(os.environ.get("PROJ", "."))
import json as _j
CFG = _j.load(open(os.path.join(PROJ, "project.json")))
import numpy as np

HERE = PROJ
VOICE = CFG.get("voice", "es-ES-AlvaroNeural")
RATE = CFG.get("rate", "+15%")
SR = 44100
LEAD = 0.25  # silence before the first word

beats = json.load(open(os.path.join(HERE, "beats.json")))
clips = os.path.join(HERE, "clips"); os.makedirs(clips, exist_ok=True)


def tts(text, out_mp3):
    cmd = ["edge-tts", "--voice", VOICE, f"--rate={RATE}", "--text", text, "--write-media", out_mp3]
    if os.environ.get("HTTPS_PROXY"):
        cmd[1:1] = ["--proxy", os.environ["HTTPS_PROXY"]]
    subprocess.run(cmd, check=True, capture_output=True)


def load(mp3):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp3, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    # trim TTS leading/trailing silence so the pauses are the ones we choose
    nz = np.where(np.abs(x) > 0.01)[0]
    return x[max(nz[0] - 600, 0): nz[-1] + 1200] if len(nz) else x


out = [np.zeros(int(LEAD * SR), np.float32)]
t = LEAD
timed = []
for b in beats:
    mp3 = os.path.join(clips, b["id"] + ".mp3")
    if not os.path.exists(mp3) or os.environ.get("FORCE"):
        tts(b["text"], mp3)
    x = load(mp3)
    dur = len(x) / SR
    timed.append({**b, "start": round(t, 3), "end": round(t + dur, 3)})
    out += [x, np.zeros(int(b["pause"] * SR), np.float32)]
    t += dur + b["pause"]
out.append(np.zeros(int(0.15 * SR), np.float32))
y = np.concatenate(out)
with wave.open(os.path.join(HERE, "narration.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
json.dump(timed, open(os.path.join(HERE, "beats_timed.json"), "w"), ensure_ascii=False, indent=1)
for b in timed:
    print(f'{b["id"]:10s} {b["start"]:6.2f} -> {b["end"]:6.2f}  ({b["end"]-b["start"]:.1f}s)')
print("total", round(len(y) / SR, 2), "s")
