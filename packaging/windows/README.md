Windows packaging notes — Talki App

Quick reference for building a Windows executable for `talki_app`.

Options
- Local (from Linux): use the included scripts (`build_windows.sh`, `build_windows_onefile.sh`, `build_windows_onedir.sh`). These use PyInstaller + MinGW where applicable.
- CI (recommended for reproducible artifacts): GitHub Actions workflow `Build Windows executable (PyInstaller)` — run manually from the Actions tab or push to `main`/`master`.

Local (Linux) — quick steps
1. Ensure MinGW is installed and `pyinstaller` is available:
   sudo apt-get install -y mingw-w64
   pip install pyinstaller
2. Run the helper script (one-file):
   ./build_windows_onefile.sh
3. Transfer `dist/talki-app.exe` to a Windows machine and run it.

CI (GitHub Actions)
- Trigger `workflow_dispatch` or push to `main/master`.
- The artifact `talki-windows-exe` will contain the `.exe` in the workflow artifacts.

Notes & troubleshooting
- The app imports large ML libraries (torch/transformers/whisper). CI or local builds may take a long time to install those wheels.
- If PyInstaller misses Qt plugins or DLLs, edit `packaging/windows/talki_app.spec` to add `datas`/`binaries` or run PyInstaller with extra `--add-data` flags.
- For production installers consider packaging the generated `.exe` into an installer (NSIS, Inno) on Windows.
