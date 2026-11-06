#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../.."
arch="$(uname -m)"
[ "$arch" = "arm64" ] || [ "$arch" = "x86_64" ] || { echo "Unsupported CPU arch: $arch"; exit 1; }
app="dist/YasoraMarkdownStudio.app"
[ -d "$app" ] || { echo "Missing frozen app"; exit 1; }
mkdir -p dist/release build/dmg
cp -R "$app" build/dmg/
ln -s /Applications build/dmg/Applications
hdiutil create -volname "Yasora Markdown Studio" -srcfolder build/dmg -ov -format UDZO "dist/release/Yasora-Studio-macOS-${arch}.dmg"
