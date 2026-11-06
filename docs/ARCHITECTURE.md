# Architecture — Clean Core, capability-based engines

## Components

```
Yasora Markdown Studio (source repo)
  src/yasora_studio/
    app.py        desktop UI + background worker + progress/cancellation
    paths.py      discovery + output safety, avoids symlinks/loops
    converter.py  single-file conversion, Microsoft MarkItDown convert_local
    updates.py    read-only PyPI/GitHub release checks
  scripts/
    build_desktop.py    PyInstaller frozen runtime and MarkItDown dependencies
    smoke_desktop.py    real conversion in the frozen EXE/app/binary
    check_engine.py     upstream version monitoring
  packaging/
    windows/            Inno Setup; per-user context-menu registration
    macos/              DMG; Apple Silicon and Intel built independently
    linux/              DEB + .desktop integration
  android/
    Android Java UI and separate limited offline converter
  .github/workflows/
    build-release.yml   native build/test/release staging
    engine-watch.yml    opens issue when upstream stable version changes
```

## Engine boundaries

Desktop engine is imported only through `converter.convert_one()`; UI is unaware of MarkItDown internals. We use `convert_local()` rather than a URL-enabled converter API, because this app only accepts filesystem documents. This is intentionally not a fork of Microsoft's repository.

Android has a different converter. Its native dependencies and feature parity must be evaluated separately before claiming equivalence. Future improvements can use on-device parsers or a plugin engine, but never assume native Python + ONNX wheels will run inside Android.

## Update contract

1. On demand, UI reads public PyPI metadata and GitHub Releases metadata (no file content transmitted).
2. If a new MarkItDown stable release exists, the GitHub scheduled workflow opens a review issue.
3. Maintainers update a pinned dependency, run tests on all platforms, check license changes, build signed distribution packages and approve a release.
4. Users install the new complete package. No automatic `pip`, no downloading arbitrary scripts into installed runtime.

## Security and privacy

The engine runs with user permissions. Restrict file selection to trusted content. Keep cloud/OCR options separate and opt-in. Source input is never modified, and default output is under Documents. GUI does not require administrative privileges. Symlink traversal is disabled for folder scans; output folder is excluded from input scanning. Errors remain local.
