# Simple Scam Protection — PRD

## Original problem
"I want to build a copy of Seraph secure" — approved plan: free Windows anti-tech-support-scam app (tray, remote-access tool blocking, scam-command warnings, rule-based link checker, hosts-file scam-site blocking, activity log, allow-list, autostart) + companion web page (download, install guide, live link checker).

## Architecture
- /app/windows_app: Python package `simple_scam_protection` (tkinter GUI, pystray tray, psutil monitor, winreg autostart/uninstall scan, hosts block, JSON store in %APPDATA%). build_exe.bat (PyInstaller) + GitHub Actions workflow. pytest suite.
- Backend FastAPI: /api/check (reuses linkcheck engine), /api/signatures, /api/stats (Mongo counters), /api/download (zips windows_app).
- Frontend React landing: Hero (app mock), tools marquee, link checker w/ presets, features bento, full-screen warning simulator, install tabs, FAQ.

## Implemented (2026-06)
- All Phase 1 MVP items. Windows app logic unit-tested on Linux; GUI/tray/winreg NOT runnable here (needs real Windows).

## Iteration 2 (2026-06)
- Fake pop-up closer (popup.py): browser window-title scam detection, Ctrl+W tab close, fallback kill browser
- Settings password (auth.py): PBKDF2-SHA256 600k, lockout 5 tries/60s; gates protection-off, trust, clear log, quit, uninstall
- Machine policy %ProgramData%\SimpleScamProtection\policy.json via `--configure` (password hash, allowlist, defaults)
- Inno Setup installer (Python bundled via PyInstaller), silent switches /VERYSILENT /NOAUTOSTART /NOSITEBLOCK /NOPOPUPBLOCK /ALLOW= /PASSWORDHASH=; build_exe.bat auto-downloads private Python + Inno Setup
- Website: new feature cards, pop-up warning simulator, IT/RMM install tab, FAQ

## Iteration 3 (2026-06)
- Renamed product everywhere to "Simple Scam Protection" (package simple_scam_protection, SimpleScamProtection.exe/.msi, data dirs, env vars)
- WiX v5 MSI (installer/SimpleScamProtection.wxs): per-machine x64, MajorUpgrade, properties ALLOW/PASSWORDHASH/NOAUTOSTART/NOSITEBLOCK/NOPOPUPBLOCK, SYSTEM custom actions (--configure --msi, --stop-running, --uninstall-cleanup), interactive uninstall password prompt
- build_exe.bat builds Setup.exe + MSI (private .NET SDK + WiX 5); GitHub workflow builds MSI too
- Website: MSI commands in IT/RMM tab, MSI FAQ, mobile fixes

## Iteration 4 (2026-06)
- Static website in /app/static_site (plain HTML/CSS/JS for www.simplescamprotection.com): client-side link checker (assets/linkcheck.js, rules exported from the app, 30/30 parity), downloads -> GitHub releases (trcmsp/simple-scam-protection), Buy me a coffee nav/mobile/footer links, robots/sitemap/404/.htaccess. Rebuild: website_build/build_site.sh. Preview: /site/index.html
- App v1.3.0: Buy me a coffee button in sidebar; scrollable remote-tools results; Quick Assist trusted by default (+migration); single full-screen warning with 20s dedupe (fixes multi-click "I understand")
- Workflows publish a GitHub Release on tags v*
- Iteration 5: workflows also auto-publish release v<app version> on every push to the default branch (so "Save to GitHub" alone makes downloads live); version read from __init__.py; tests use full os.environ (Windows CI). Buy me a coffee added to React preview site header (desktop + mobile) and footer.

## Backlog
- P1: browser extension; auto-updating lists; code signing
- P2: signed installer + auto-update; password-protected settings; multi-language; macOS
