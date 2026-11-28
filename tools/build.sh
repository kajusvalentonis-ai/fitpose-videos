#!/usr/bin/env bash
# Build one finished video: render frames, make soundtrack from the video's sfx list, mux.
# Usage: tools/build.sh <name> <NN>   e.g. tools/build.sh knees 06  -> videos/06_knees.mp4
set -euo pipefail
NAME=$1; NUM=$2
HERE=$(cd "$(dirname "$0")" && pwd)
export WORK=${WORK:-$HERE/work}
mkdir -p "$WORK/out"
python3 "$HERE/render.py" video "$NAME"
python3 - "$NAME" "$HERE" <<'EOF'
import re, json, subprocess, sys, os
name, here = sys.argv[1], sys.argv[2]
src = open(os.path.join(here, 'ads.html')).read()
m = re.search(r"V\." + name + r"=\{D:([\d.]+),beats:\[[^\]]*\],sfx:(\[.*?\]\]),", src)
js = re.sub(r"(?<![\d])\.(\d)", r"0.\1", m.group(2).replace("'", '"'))
json.loads(js)
subprocess.run(['python3', os.path.join(here, 'audio.py'), name, m.group(1), js], check=True)
EOF
ffmpeg -v error -y -i "$WORK/out/${NAME}_v.mp4" -i "$WORK/out/$NAME.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$WORK/out/final.tmp.mp4"
mv "$WORK/out/final.tmp.mp4" "$HERE/../videos/${NUM}_${NAME}.mp4"
echo "built videos/${NUM}_${NAME}.mp4"
