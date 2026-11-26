#!/usr/bin/env bash
# Full pipeline for one project folder:  engine/make.sh <project_dir> [steps...]
# steps: voice align subs sheet video audio mux thumb review   (default: all except sheet)
set -euo pipefail
E="$(cd "$(dirname "$0")" && pwd)"; export PROJ="$(cd "$1" && pwd)"; shift
export HF_HUB_DISABLE_XET=1
STEPS="${*:-voice align subs video audio mux thumb review}"
for s in $STEPS; do
  echo "== $s"
  case $s in
    voice)  python3 "$E/narration.py" ;;
    align)  python3 "$E/align.py" | sed -n 1p ;;
    subs)   python3 "$E/subs.py" | sed -n 1p ;;
    video)  python3 "$E/render.py" --video "$PROJ/video_mudo.mp4" --jobs "${JOBS:-2}" ;;
    audio)  python3 "$E/audio.py" ;;
    mux)    ffmpeg -v error -y -i "$PROJ/video_mudo.mp4" -i "$PROJ/mix.wav" \
              -filter_complex "[0:v]ass=$PROJ/subs.ass:fontsdir=$HOME/.local/share/fonts[v]" -map "[v]" -map 1:a \
              -c:v libx264 -preset slow -crf 18 -profile:v high -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 44100 \
              -shortest -movflags +faststart "$PROJ/video_final.mp4" && echo "mux ok" ;;
    thumb)  python3 "$E/thumb.py" ;;
    review) python3 "$E/review.py" 2>&1 | grep -v -i warning ;;
  esac
done
