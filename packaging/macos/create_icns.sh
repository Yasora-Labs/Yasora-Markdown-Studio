#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../.."
src="src/yasora_studio/assets/studio.png"
iconset="build/YasoraStudio.iconset"
mkdir -p "$iconset"
for sz in 16 32 128 256 512; do
  sips -s format png -z "$sz" "$sz" "$src" --out "$iconset/icon_${sz}x${sz}.png" >/dev/null
  twice=$((sz*2))
  sips -s format png -z "$twice" "$twice" "$src" --out "$iconset/icon_${sz}x${sz}@2x.png" >/dev/null
done
iconutil -c icns "$iconset" -o "src/yasora_studio/assets/studio.icns"
