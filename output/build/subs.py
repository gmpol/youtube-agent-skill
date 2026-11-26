"""words.json -> subs.ass in the guide's caption style (top, white Inter ExtraBold, keyword in #F2C94C)."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
words = json.load(open(os.path.join(HERE, "words.json")))

# spoken numbers shown as digits, like the reference ("cada 24 horas")
MERGE = [(["dos", "mil", "cuatrocientos", "cincuenta"], "2.450"), (["seis"], "6"), (["doce"], "12")]
KEY = {"microondas", "agua", "2.450", "millones", "llama", "resistencia", "rojo", "sopa", "hierve", "lento", "magnetrón",
       "voltios", "wifi", "fuertes", "metal", "rebotan", "imán", "positivo", "negativo", "girar", "gira", "calor",
       "queman", "frías", "6", "plato", "calientes", "12", "rejilla", "luz", "enchufe", "roce", "real",
       "centímetros", "contagio", "lasaña", "helada", "realidad…", "cocina", "diminuto", "sentido", "vecinas…", "molécula"}

def bare(w): return re.sub(r"[^\wáéíóúñü.]", "", w.lower()).strip(".") or w.lower()

toks = []
i = 0
while i < len(words):
    for seq, show in MERGE:
        n = len(seq)
        if [bare(w["word"]) for w in words[i:i + n]] == seq:
            toks.append({"word": show + re.sub(r"^.*?([.,:…?]*)$", r"\1", words[i + n - 1]["word"]),
                         "start": words[i]["start"], "end": words[i + n - 1]["end"], "beat": words[i]["beat"]}); i += n
            break
    else:
        toks.append(dict(words[i])); i += 1

# chunk: up to 3 words (4 if all short), break on punctuation, long gaps and beat changes
chunks, cur = [], []
for k, t in enumerate(toks):
    cur.append(t)
    nxt = toks[k + 1] if k + 1 < len(toks) else None
    punct = re.search(r"[.,:?…!]$", t["word"])
    limit = 4 if sum(len(x["word"]) for x in cur) < 14 else 3
    if (not nxt or punct or len(cur) >= limit or nxt["beat"] != t["beat"] or nxt["start"] - t["end"] > 0.3):
        chunks.append(cur); cur = []

def ts(t):
    t = max(t, 0); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

YEL = r"{\c&H4CC9F2&}"; WHT = r"{\c&HFFFFFF&}"
lines = []
for n, c in enumerate(chunks):
    start = c[0]["start"] - 0.05
    end = chunks[n + 1][0]["start"] - 0.05 if n + 1 < len(chunks) else c[-1]["end"] + 0.4
    end = min(end, c[-1]["end"] + 0.6)
    keys = [w for w in c if bare(w["word"]).rstrip(".…") in {k.rstrip(".…") for k in KEY}]
    digits = [w for w in c if re.match(r"\d", w["word"])]
    hi = digits[0] if digits else keys[-1] if keys else max(c, key=lambda w: len(w["word"])) if any(len(w["word"]) >= 7 for w in c) else None
    txt = " ".join((YEL + w["word"] + WHT) if w is hi else w["word"] for w in c)
    pop = r"{\fscx92\fscy92\t(0,90,\fscx100\fscy100)}"
    lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},Cap,,0,0,0,,{pop}{txt}")

head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter ExtraBold,70,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,0,4,8,120,160,500,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open(os.path.join(HERE, "subs.ass"), "w").write(head + "\n".join(lines) + "\n")
print(len(chunks), "caption chunks; avg %.2f s" % (sum(c[-1]["end"] - c[0]["start"] for c in chunks) / len(chunks)))
for c in chunks[:8]: print("  ", round(c[0]["start"], 2), " ".join(w["word"] for w in c))
