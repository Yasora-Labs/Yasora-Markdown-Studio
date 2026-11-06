# Yasora Markdown Studio

**Open-source, cross-platform graphical document conversion — powered by Microsoft's [MarkItDown](https://github.com/microsoft/markitdown) on Windows, macOS and Linux.**

**Product:** Yasora-Labs · **App version:** 0.4.0-alpha · **Bundled desktop engine target:** MarkItDown 0.1.9 · **License:** MIT (application code). Independent project; not affiliated with or endorsed by Microsoft.

> **Release status (6 Nov 2026):** Source release candidate. The GitHub Actions build pipeline is included, but actual Windows/macOS/Linux native build, installation, signing, notarization and Android device tests have not yet run in this conversation. No release installer is asserted to exist until the workflow succeeds. Do not publish a public stable release before the checklist passes.

## What users get after a verified GitHub build

| Target | Artifact | End-user requirements |
| --- | --- | --- |
| Windows 10/11 x64 | `Yasora-Studio-Windows-x64-Setup.exe` | Double-click install; no Python or uv. Start Menu. Optional Explorer right-click actions. |
| macOS Apple Silicon | `Yasora-Studio-macOS-arm64.dmg` | Drag `.app` into Applications; no separate Python. Unsigned until signing configured. |
| macOS Intel | `Yasora-Studio-macOS-x86_64.dmg` | Drag `.app` into Applications; no separate Python. Unsigned until signing configured. |
| Ubuntu/Debian x64 | `Yasora-Studio-Linux-amd64.deb` | Install DEB; bundled Python. Host GUI/OS libraries still apply. |
| Android 7.0+ | `Yasora-Studio-Android-signed.apk` when signing is configured, otherwise `Yasora-Studio-Android-DEBUG.apk` | Android app with **limited, separate offline converter**, not Microsoft MarkItDown. |

### Desktop features

- Native-looking GUI: choose files or folders, convert folders recursively, view progress and errors, choose output destination, cancel after the current file, optionally overwrite converted files.
- First-run default output: `~/Documents/Yasora Markdown Studio` (Windows: `%USERPROFILE%\Documents\Yasora Markdown Studio`; path can be changed).
- Fully local conversions by default. The bundled MarkItDown library performs the conversion; the app does not upload user documents. Cloud-supported MarkItDown extras may require explicitly configured third-party cloud services.
- Retains original extensions in generated names (`report.pdf.md`, `report.docx.md`) to avoid output collisions. Input documents are never modified.
- **Check Updates** button checks stable MarkItDown on PyPI and the Yasora GitHub Releases API. It does not silently download or execute code. Upgrade by installing a newly built, tested release containing the newer engine.
- Windows installer registers Start Menu launcher and optional per-user Explorer file/folder context actions. The Desktop shortcut is opt-in to avoid problems with redirected/protected Desktop folders.

### Android feature distinction

The Android source, under `android/`, uses an independent Java document parser and Android's document picker. It currently handles TXT, MD, HTML, CSV, JSON, XML, DOCX, PPTX and XLSX. **No PDF, OCR or Microsoft's full Python engine on Android.** The APK can be built without your own server or cloud credentials. Large or complex files may lose fidelity. The Android update button opens the GitHub releases page; it does not silently update the APK.

## Getting the actual installers

1. Create an empty **public** repository named `Yasora-Markdown-Studio` under the `Yasora-Labs` organization, or run the included guarded PowerShell publisher from your Windows machine after a source review.
2. Push all source files including `.github/workflows/build-release.yml`.
3. In **Actions**, run `Build all platform installers (draft release only)` using `workflow_dispatch`. This compiles on **each target operating system** (required by PyInstaller), runs tests and uploads artifacts to that workflow run.
4. After debugging any failing platform job, create/push a `v0.4.0-alpha.1` tag. The workflow will rebuild everything and create a **DRAFT** GitHub pre-release with the artifacts and `SHA256SUMS.txt`. Publishing is deliberately a manual maintainer decision.
5. Validate the installers on clean Windows/macOS/Linux virtual machines and an Android device. Configure code-signing, macOS notarization and a persistent Android keystore before final public release.

**Caution:** GitHub Actions workflows are build recipes, not evidence that working installers already exist. The action may fail until platform-specific dependencies and native testing are completed.

## Developer quick start

```bash
python -m venv .venv
# activate it according to your platform
python -m pip install -r requirements-desktop.txt
python -m unittest discover -s tests -v
python run_studio.py
python scripts/build_desktop.py
python scripts/smoke_desktop.py
```

For Android, use Android Studio or the Gradle/GitHub workflow from `android/`. The Android source requires Android SDK 35, Gradle 8.11.1 and JDK 17.

## Installation and update safety

- Windows installer uses **Inno Setup** with per-user, lowest privilege installation. Registry keys it owns are removed during uninstall; no Defender or PowerShell execution-policy changes.
- Do not install into `D:\Software` or bypass Controlled Folder Access in order to build or run this product. Installation is under the current user's app directory.
- Desktop frozen binaries must **not** `pip install --upgrade` into PyInstaller's runtime. The `Check Updates` button is informational; rebuilding each OS release is the safe supported engine-update path.
- Output can contain private text from source documents; review before uploading to chatbots or GitHub. User documents are not committed to this project.
- macOS and Windows unsigned releases can trigger OS security warnings. Do not bypass those warnings for third-party distribution; publish properly signed packages.

See [Architecture](docs/ARCHITECTURE.md), [release checklist](docs/RELEASE_CHECKLIST.md), [known limitations](docs/KNOWN_LIMITATIONS.md), and [Claude review handoff](handoff.md).
