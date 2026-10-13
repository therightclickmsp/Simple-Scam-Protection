# Guardian Shield — PRD

## Original problem
"I want to build a copy of Seraph secure" — approved plan: free Windows anti-tech-support-scam app (tray, remote-access tool blocking, scam-command warnings, rule-based link checker, hosts-file scam-site blocking, activity log, allow-list, autostart) + companion web page (download, install guide, live link checker).

## Architecture
- /app/windows_app: Python package `guardian_shield` (tkinter GUI, pystray tray, psutil monitor, winreg autostart/uninstall scan, hosts block, JSON store in %APPDATA%). build_exe.bat (PyInstaller) + GitHub Actions workflow. pytest suite.
- Backend FastAPI: /api/check (reuses linkcheck engine), /api/signatures, /api/stats (Mongo counters), /api/download (zips windows_app).
- Frontend React landing: Hero (app mock), tools marquee, link checker w/ presets, features bento, full-screen warning simulator, install tabs, FAQ.

## Implemented (2026-06)
- All Phase 1 MVP items. Windows app logic unit-tested on Linux; GUI/tray/winreg NOT runnable here (needs real Windows).

## Iteration 2 (2026-06)
- Fake pop-up closer (popup.py): browser window-title scam detection, Ctrl+W tab close, fallback kill browser
- Settings password (auth.py): PBKDF2-SHA256 600k, lockout 5 tries/60s; gates protection-off, trust, clear log, quit, uninstall
- Machine policy %ProgramData%\GuardianShield\policy.json via `--configure` (password hash, allowlist, defaults)
- Inno Setup installer (Python bundled via PyInstaller), silent switches /VERYSILENT /NOAUTOSTART /NOSITEBLOCK /NOPOPUPBLOCK /ALLOW= /PASSWORDHASH=; build_exe.bat auto-downloads private Python + Inno Setup
- Website: new feature cards, pop-up warning simulator, IT/RMM install tab, FAQ

## Backlog
- P1: browser extension; auto-updating lists; MSI package
- P2: signed installer + auto-update; password-protected settings; multi-language; macOS
