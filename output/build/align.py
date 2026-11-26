"""Whisper the generated narration, then align whisper's word timings onto the script's own words
(so the subtitles keep the script's spelling: "magnetrón", "wifi", "lasaña").
Writes build/words.json: [{word, start, end, beat}]."""
import difflib, json, os, re, unicodedata
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
from faster_whisper import WhisperModel

HERE = os.path.dirname(os.path.abspath(__file__))
beats = json.load(open(os.path.join(HERE, "beats_timed.json")))
model = WhisperModel(os.environ.get("WMODEL", "small"), device="cpu", compute_type="int8")
segs, _ = model.transcribe(os.path.join(HERE, "narration.wav"), language="es", word_timestamps=True, beam_size=5,
                           initial_prompt="microondas, magnetrón, wifi, lasaña, rejilla, molécula")
heard = [w for s in segs for w in s.words]


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


script = []
for b in beats:
    for w in b["text"].split():
        script.append({"word": w, "beat": b["id"], "bstart": b["start"], "bend": b["end"]})

a = [norm(x["word"]) for x in script]
h = [norm(w.word) for w in heard]
sm = difflib.SequenceMatcher(a=a, b=h, autojunk=False)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
        for k in range(i2 - i1):
            script[i1 + k]["start"], script[i1 + k]["end"] = heard[j1 + k].start, heard[j1 + k].end
    elif tag == "replace" and j2 > j1:  # spread the heard span over the script words
        t0, t1 = heard[j1].start, heard[j2 - 1].end
        n = i2 - i1
        for k in range(n):
            script[i1 + k]["start"] = t0 + (t1 - t0) * k / n
            script[i1 + k]["end"] = t0 + (t1 - t0) * (k + 1) / n

# words whisper missed: interpolate between neighbours
for i, w in enumerate(script):
    if "start" not in w:
        prev = next((script[j]["end"] for j in range(i - 1, -1, -1) if "end" in script[j]), w["bstart"])
        nxt = next((script[j]["start"] for j in range(i + 1, len(script)) if "start" in script[j]), w["bend"])
        w["start"], w["end"] = prev, max(prev + 0.05, min(nxt, prev + 0.35))
        w["guessed"] = True

matched = sum(1 for w in script if not w.get("guessed"))
ratio = sm.ratio()
out = [{"word": w["word"], "start": round(w["start"], 3), "end": round(w["end"], 3), "beat": w["beat"],
        **({"guessed": True} if w.get("guessed") else {})} for w in script]
json.dump(out, open(os.path.join(HERE, "words.json"), "w"), ensure_ascii=False, indent=0)
print(f"script words {len(script)}, whisper words {len(heard)}, match ratio {ratio:.3f}, timed {matched}, guessed {len(script)-matched}")
print("whisper heard:", " ".join(w.word.strip() for w in heard)[:600])
