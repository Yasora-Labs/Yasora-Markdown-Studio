#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../.."
[ -x dist/YasoraMarkdownStudio/YasoraMarkdownStudio ] || { echo "Missing PyInstaller Linux binary"; exit 1; }
package=build/deb/yasora-markdown-studio
mkdir -p "$package/DEBIAN" "$package/opt/yasora-markdown-studio" "$package/usr/share/applications" "$package/usr/share/icons/hicolor/256x256/apps" dist/release
cp -a dist/YasoraMarkdownStudio/. "$package/opt/yasora-markdown-studio/"
cat > "$package/DEBIAN/control" <<'CONTROL'
Package: yasora-markdown-studio
Version: 0.4.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Yasora-Labs <opensource@users.noreply.github.com>
Depends: libc6, libx11-6
Description: Local graphical Markdown document conversion powered by MarkItDown
 Includes an app-private Python runtime and dependencies.
CONTROL
cat > "$package/usr/share/applications/yasora-markdown-studio.desktop" <<'DESKTOP'
[Desktop Entry]
Type=Application
Name=Yasora Markdown Studio
Comment=Convert documents to Markdown locally
Exec=/opt/yasora-markdown-studio/YasoraMarkdownStudio %f
TryExec=/opt/yasora-markdown-studio/YasoraMarkdownStudio
Icon=yasora-markdown-studio
Categories=Office;Utility;
Terminal=false
MimeType=text/plain;text/html;application/pdf;
DESKTOP
cp src/yasora_studio/assets/studio.png "$package/usr/share/icons/hicolor/256x256/apps/yasora-markdown-studio.png"
dpkg-deb --root-owner-group --build "$package" "dist/release/Yasora-Studio-Linux-amd64.deb"
