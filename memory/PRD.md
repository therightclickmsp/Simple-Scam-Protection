# Guardian Shield — PRD

## Original problem
"I want to build a copy of Seraph secure" — approved plan: free Windows anti-tech-support-scam app (tray, remote-access tool blocking, scam-command warnings, rule-based link checker, hosts-file scam-site blocking, activity log, allow-list, autostart) + companion web page (download, install guide, live link checker).

## Architecture
- /app/windows_app: Python package `guardian_shield` (tkinter GUI, pystray tray, psutil monitor, winreg autostart/uninstall scan, hosts block, JSON store in %APPDATA%). build_exe.bat (PyInstaller) + GitHub Actions workflow. pytest suite.
- Backend FastAPI: /api/check (reuses linkcheck engine), /api/signatures, /api/stats (Mongo counters), /api/download (zips windows_app).
- Frontend React landing: Hero (app mock), tools marquee, link checker w/ presets, features bento, full-screen warning simulator, install tabs, FAQ.

## Implemented (2026-06)
- All Phase 1 MVP items. Windows app logic unit-tested on Linux; GUI/tray/winreg NOT runnable here (needs real Windows).

## Backlog
- P1: fake virus pop-up/browser lock detection; browser extension; auto-updating lists
- P2: signed installer + auto-update; password-protected settings; multi-language; macOS
