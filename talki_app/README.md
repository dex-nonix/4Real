talki_app — UI-first package (bundles STT engine internally).

Install (editable, local):
```bash
pip install -e /home/dex/Desktop/shadewalk/4Real/talki_app
```

Quick test (import):
```bash
python -c "import talki_app; print('OK')"
```

Run UI (requires UI extras):
```bash
python -m talki_app.aio_talki_async
```

Windows packaging (how to build .exe)

- Local (Linux) quick build (PyInstaller + MinGW where applicable):

```bash
# one-file build (cross-friendly helper)
./build_windows_onefile.sh

# one-dir build
./build_windows_onedir.sh
```

- CI (reproducible): use the GitHub Actions workflow `Build Windows executable (PyInstaller)` (Actions tab). The workflow uploads the built `.exe` as an artifact named `talki-windows-exe`.

Notes
- The package declares heavy ML deps (torch, transformers, faster-whisper). Installing those on CI or locally will take time and may increase artifact size.
- If PyInstaller misses Qt plugins or native DLLs, update `packaging/windows/talki_app.spec` or run PyInstaller with additional `--add-data` / `--hidden-import` flags.
- For a Windows installer wrap the produced `.exe` with NSIS/Inno or a native installer builder on the Windows machine.


Originals in `utils/` remain unchanged. This package is a self-contained copy.
