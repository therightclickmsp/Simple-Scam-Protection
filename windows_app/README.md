# Guardian Shield (Windows)

Free tool that stops tech-support scams. Runs in the system tray.

- Finds and removes remote-access tools (AnyDesk, TeamViewer, UltraViewer, ScreenConnect, RustDesk, Quick Assist, ...)
- Instantly closes remote-access tools when they start, with a full-screen warning
- **Closes fake virus pop-ups** ("Your PC is locked - call Microsoft") in Chrome, Edge, Firefox, Brave, Opera
- Warns when Event Viewer, netstat, tree, syskey, msconfig are opened (scammer tricks)
- **Settings password**: needed to turn protection off, trust a tool, clear the log, quit or uninstall
- Trusted list (needs a typed confirmation), rule-based link checker, scam-site blocking, local activity log

## Build (one click - no Python install needed)
Double-click `build_exe.bat`. It downloads a private copy of Python and Inno Setup into `.build\` and produces:

- `dist\GuardianShieldSetup.exe` - the installer (Python is bundled inside; end users need nothing else)
- `dist\GuardianShield.exe` - portable single-file version

Or push this folder to GitHub: `.github/workflows/build-windows.yml` builds both; download from Actions > Artifacts.

Windows SmartScreen may say "Windows protected your PC" because the app is not signed: click **More info** > **Run anyway**.

## Silent install (RMM / Intune / GPO / PDQ)
Runs fine as SYSTEM. Installs per-machine to `C:\Program Files\Guardian Shield`, auto-starts for every user at logon.

```
GuardianShieldSetup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /LOG="C:\Windows\Temp\GuardianShield.log"
```

| Option | Effect |
|---|---|
| `/NOAUTOSTART` | Don't start for all users at logon |
| `/NOSITEBLOCK` | Don't add the scam-site block to the hosts file |
| `/NOPOPUPBLOCK` | Don't close fake virus pop-ups by default |
| `/ALLOW=screenconnect,teamviewer` | Pre-trust your own remote tools (so your RMM/remote agent isn't blocked) |
| `/PASSWORDHASH=pbkdf2_sha256$...` | Lock settings with a password (see below) |
| `/DIR="D:\Apps\Guardian Shield"` | Custom install folder |

Tool ids: anydesk, teamviewer, ultraviewer, screenconnect, supremo, logmein, rustdesk, quickassist, ammyy, splashtop,
zohoassist, aeroadmin, hoptodesk, remoteutilities, getscreen, dwservice, vnc, radmin, iperius.

**Password hash** - create it once on any PC so the plain password never appears in RMM scripts or logs:
```
GuardianShield.exe --hash-password
```
Exit codes: `0` success; Inno Setup standard codes otherwise (see `/LOG`).

**Silent uninstall** (skips the password prompt, admin only):
```
"C:\Program Files\Guardian Shield\unins000.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
```

**Change policy later without reinstalling** (as admin/SYSTEM):
```
"C:\Program Files\Guardian Shield\GuardianShield.exe" --configure --allow screenconnect --password-hash "pbkdf2_sha256$..."
```
Policy lives in `C:\ProgramData\GuardianShield\policy.json` (only admins can change it). User settings and the activity
log stay in `%APPDATA%\GuardianShield`.

## Run from source
```
py -m pip install -r requirements.txt
py -m guardian_shield
py -m guardian_shield --check "http://paypa1-login.xyz"
```
Not an antivirus - keep Windows Defender on.
