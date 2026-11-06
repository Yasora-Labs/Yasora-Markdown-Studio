# Known limitations and release risks

- **Platform builds not executed here.** Mac DMG, Windows Setup.exe, Linux DEB and Android APK are deliverables of the included GitHub workflow, not files prebuilt in this source ZIP. Treat all native artifacts as unverified until their jobs and smoke tests pass.
- **Code signing is pending.** Windows needs Authenticode, macOS needs Developer ID + notarization. Android needs a persistent signing key (GitHub Secrets). Without signing, the debug APK is suitable only for technical evaluation.
- **Android ≠ desktop engine.** Android has an independent limited Java parser; PDF/OCR/audio/complex content are not supported there yet.
- **Linux target:** DEB targets Ubuntu/Debian x64, not every Linux distribution. Host glibc/desktop libraries still required. Generic AppImage/Flatpak may be added later.
- **Cloud extras:** `markitdown[all]` includes optional dependencies for cloud service integrations, but doesn't supply remote API credentials or make all conversion modes function offline.
- **Image text and scanned PDFs:** OCR is not guaranteed by MarkItDown itself. The app does not invent OCR results.
- **Unsupported formats and layout:** Conversion can lose visual formatting; always keep originals.
- **GUI and launch UX:** Tkinter is bundled but appearance follows the OS/Tk theme rather than matching a bespoke native UI toolkit. Drag-and-drop is not yet included; choose files/folders through file pickers.
- **Installer context menus:** Windows 11 may show actions under 'Show more options'; macOS/Linux use standard Open With/File association, not a custom Finder/Nautilus context extension.
- **Updater:** Only update *checks* are implemented. Security-conscious installation of new full releases is manual, not a background silent updater.
- **No auto publication:** GitHub draft release requires review and explicit maintainer publishing.
