# Mandatory release QA gate

- [ ] GitHub public repository exists under Yasora-Labs and upstream attribution is preserved.
- [ ] Tests pass for desktop paths/conversion and Android fixtures.
- [ ] Each frozen desktop binary successfully converts HTML and PDF, DOCX, XLSX, PPTX samples on a clean OS runner.
- [ ] Windows Inno Setup creates Start Menu shortcut; optional desktop failure does not abort; file/folder right-click inputs work, with spaces and Unicode.
- [ ] Windows uninstall removes only owned app entries; does not touch Documents or original files.
- [ ] macOS DMG contains .app, launches on both Intel and Apple Silicon machines; Developer ID signing and Apple notarization verified.
- [ ] Linux DEB installs on clean Ubuntu/Debian machine, launches without system Python, unregisters cleanly.
- [ ] Android APK launches on emulator and physical device; supports correct SAF share, open, save and no internet permission. PDF lack clearly disclosed.
- [ ] Stable Android signing key is retained securely (never commit keystore).
- [ ] Update checks correctly show installed, latest and offline/unavailable states; nothing executes from a remote URL.
- [ ] Test failed conversion, cancellation, existing files, reparse/symlinks, empty directory, filesystem permissions, 1 GB source, path traversal, `.md` output loop.
- [ ] Review actual third-party licenses of **all** bundled transitive dependencies, not just Microsoft MarkItDown MIT.
- [ ] Review macOS Gatekeeper/Windows SmartScreen messages before public release.
- [ ] Compute SHA256 of all artifacts and verify GitHub draft files match.
- [ ] QA reviewer gives GO; only then publish the draft release.
