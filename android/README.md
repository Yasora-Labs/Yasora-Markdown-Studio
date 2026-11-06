# Yasora Markdown Studio — Android companion (alpha)

Android Studio project (Java 17, AGP 8.9.2, Gradle 8.11.1, compileSdk 35). Independent, on-device conversion component; **not** the full Microsoft Python MarkItDown engine.

Capabilities: Android launcher icon; file picker; import text and supported files from Android's Share sheet; preview generated Markdown; save via system `ACTION_CREATE_DOCUMENT` picker; share Markdown text; open GitHub Releases for update checks.

Format support: simple TXT, MD, CSV, JSON, XML, HTML, DOCX paragraph text, PPTX slide text, XLSX data. **No PDF, OCR, image or audio conversion.** Maximum selected file size 20 MB, maximum decompressed OOXML entry 8 MB. Complex table/layout fidelity is not guaranteed. Never sends documents to a server; no INTERNET permission.

Build in Android Studio: open `android/` → Gradle sync → install SDK 35 → Run. GitHub CI also builds `assembleDebug` and runs unit tests. Debug APK is *not* a stable public distribution because debug signing keys can change. To build a stable signed release, configure the four repository signing secrets described in the root README. Never commit the keystore or passwords.

Update button opens official Yasora-Labs GitHub release page in a browser. It does not silently download/install APKs. Future full engine parity needs a separate native or Python-on-Android feasibility/security/license review, and emulator coverage.
