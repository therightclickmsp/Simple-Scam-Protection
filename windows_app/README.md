# Guardian Shield (Windows)

Free tool that stops tech-support scams. Runs in the system tray.

- Finds and removes remote-access tools (AnyDesk, TeamViewer, UltraViewer, ScreenConnect, RustDesk, Quick Assist, ...)
- Instantly closes remote-access tools when they start, with a full-screen warning
- Allow-list for tools you trust (needs a typed confirmation)
- Warns when Event Viewer, netstat, tree, syskey, msconfig are opened (scammer tricks)
- Rule-based link & message checker
- Blocks known scam sites via the hosts file (asks for admin once)
- Local activity log, auto-start with Windows

## Build the .exe (one click)
1. Install Python 3.10+ from python.org (tick "Add Python to PATH").
2. Double-click `build_exe.bat`.
3. Your app appears in `dist\GuardianShield.exe`. Double-click to run.

Windows SmartScreen may say "Windows protected your PC" because the app is not signed:
click **More info** then **Run anyway**.

## Or build on GitHub
Push this folder to a GitHub repo - `.github/workflows/build-windows.yml` builds the exe; download it from the
Actions tab ("Artifacts").

## Run from source
```
py -m pip install -r requirements.txt
py -m guardian_shield
py -m guardian_shield --check "http://paypa1-login.xyz"
```

Data (settings + activity log) is stored only in `%APPDATA%\GuardianShield`. Not an antivirus - keep Windows Defender on.
