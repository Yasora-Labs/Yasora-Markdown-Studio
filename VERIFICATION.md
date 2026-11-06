# Verification record — 2026-11-06

## Passed in this container (Debian Linux, no native GUI/Android SDK)

- `python -m unittest discover -s tests -v`: 4/4 tests passed (recursive paths, output loops, filename collisions, atomic write/skip/overwrite, invalid source).
- `javac DocumentConverter.java StandaloneSmoke.java` and `java org.yasoralabs.markitdown.StandaloneSmoke`: 6/6 Java converter smoke checks passed.
- `python -m compileall -q src scripts run_studio.py`: passed.
- `bash -n packaging/macos/*.sh packaging/linux/*.sh`: passed.
- YAML workflow basic parse and source manifest checks: passed.

## NOT passed / NOT attempted

- PyInstaller build on Windows/macOS/Linux: not executed (target-native environments and downloaded MarkItDown engine unavailable here).
- Frozen executables converting real HTML/PDF/DOCX/PPTX/XLSX: **not executed**, required by GitHub workflow.
- Inno Setup Windows Setup.exe compilation, install, Start Menu, Windows 11 right-click and uninstall: **not executed**.
- macOS DMG app launch, signing, notarization and both architectures: **not executed**.
- Linux .deb installation on clean target host: **not executed**.
- Gradle/Android APK build, emulator test, signing: **not executed**.
- GitHub repository creation or publish: **not executed**. Repository has not been created.

## Safety gate

Do not present the source archive as Windows/macOS/Linux/Android installable packages. They must be produced by native runners, smoke-tested and signed as appropriate. The GitHub pipeline stages a **draft** prerelease for human approval; it does not automatically publish the artifacts to the public.
