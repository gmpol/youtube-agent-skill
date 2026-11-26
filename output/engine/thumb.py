"""Thumbnails from scenes.THUMB_V(c) (1080x1920) and scenes.THUMB_H(c) (1280x720) -> miniatura.png / miniatura_16x9.png"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
from core import cairo, PROJ
for fn, (w, h), name in [("THUMB_V", (1080, 1920), "miniatura.png"), ("THUMB_H", (1280, 720), "miniatura_16x9.png")]:
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s); getattr(R.S, fn)(c); s.write_to_png(os.path.join(PROJ, name))
print("thumbs ok")
