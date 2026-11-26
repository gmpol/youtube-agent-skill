"""One-off: apply align.py's clamp (no word before its beat) to an existing words.json."""
import json, os, sys
P = os.path.abspath(os.environ.get("PROJ", ".")); W = os.path.join(P, "words.json")
beats = {b["id"]: b for b in json.load(open(os.path.join(P, "beats_timed.json")))}
words = json.load(open(W)); n = 0
for w in words:
    b0 = beats[w["beat"]]["start"]
    if w["start"] < b0: w["start"] = round(b0, 3); w["end"] = round(max(w["end"], b0 + 0.08), 3); n += 1
json.dump(words, open(W, "w"), ensure_ascii=False, indent=0); print(os.path.basename(P), "clamped", n, "words")
