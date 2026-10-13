# Simple Scam Protection (Windows)

Free tool that stops tech-support scams. Runs in the system tray.

- Finds and removes remote-access tools (AnyDesk, TeamViewer, UltraViewer, ScreenConnect, RustDesk, Quick Assist, ...)
- Instantly closes remote-access tools when they start, with a full-screen warning
- **Closes fake virus pop-ups** ("Your PC is locked - call Microsoft") in Chrome, Edge, Firefox, Brave, Opera
- Warns when Event Viewer, netstat, tree, syskey, msconfig are opened (scammer tricks)
- **Settings password**: needed to turn protection off, trust a tool, clear the log, quit or uninstall
- Trusted list (needs a typed confirmation), rule-based link checker, scam-site blocking, local activity log

## Build (one click - no Python install needed)
Double-click `build_exe.bat`. It downloads private copies of Python, Inno Setup, the .NET SDK and WiX Toolset 5 into `.build\` and produces:

- `dist\SimpleScamProtectionSetup.exe` - the installer (Python is bundled inside; end users need nothing else)
- `dist\SimpleScamProtection.msi` - MSI package for Intune, Group Policy, SCCM/MECM and RMM tools
- `dist\SimpleScamProtection.exe` - portable single-file version

Or push this folder to GitHub: `.github/workflows/build-windows.yml` builds all three; download from Actions > Artifacts.

Windows SmartScreen may say "Windows protected your PC" because the app is not signed: click **More info** > **Run anyway**.

## Silent install (RMM / Intune / GPO / PDQ)
Runs fine as SYSTEM. Installs per-machine to `C:\Program Files\Simple Scam Protection`, auto-starts for every user at logon.

```
SimpleScamProtectionSetup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /LOG="C:\Windows\Temp\SimpleScamProtection.log"
```

| Option | Effect |
|---|---|
| `/NOAUTOSTART` | Don't start for all users at logon |
| `/NOSITEBLOCK` | Don't add the scam-site block to the hosts file |
| `/NOPOPUPBLOCK` | Don't close fake virus pop-ups by default |
| `/ALLOW=screenconnect,teamviewer` | Pre-trust your own remote tools (so your RMM/remote agent isn't blocked) |
| `/PASSWORDHASH=pbkdf2_sha256$...` | Lock settings with a password (see below) |
| `/DIR="D:\Apps\Simple Scam Protection"` | Custom install folder |

Tool ids: anydesk, teamviewer, ultraviewer, screenconnect, supremo, logmein, rustdesk, quickassist, ammyy, splashtop,
zohoassist, aeroadmin, hoptodesk, remoteutilities, getscreen, dwservice, vnc, radmin, iperius.

**Password hash** - create it once on any PC so the plain password never appears in RMM scripts or logs:
```
SimpleScamProtection.exe --hash-password
```
Exit codes: `0` success; Inno Setup standard codes otherwise (see `/LOG`).

**Silent uninstall** (skips the password prompt, admin only):
```
"C:\Program Files\Simple Scam Protection\unins000.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
```

**Change policy later without reinstalling** (as admin/SYSTEM):
```
"C:\Program Files\Simple Scam Protection\SimpleScamProtection.exe" --configure --allow screenconnect --password-hash "pbkdf2_sha256$..."
```
Policy lives in `C:\ProgramData\SimpleScamProtection\policy.json` (only admins can change it). User settings and the activity
log stay in `%APPDATA%\SimpleScamProtection`.

## MSI (Intune / Group Policy / SCCM)
```
msiexec /i SimpleScamProtection.msi /qn /norestart ALLOW=screenconnect PASSWORDHASH="pbkdf2_sha256$..." /l*v C:\Windows\Temp\ssp-msi.log
msiexec /x SimpleScamProtection.msi /qn /norestart
```
| Property | Effect |
|---|---|
| `ALLOW=screenconnect,teamviewer` | Pre-trust your own remote tools |
| `PASSWORDHASH=pbkdf2_sha256$...` | Lock settings & uninstall with a password |
| `NOAUTOSTART=1` | Don't start for all users at logon |
| `NOSITEBLOCK=1` | Don't add the scam-site block to the hosts file |
| `NOPOPUPBLOCK=1` | Don't close fake virus pop-ups by default |

- Per-machine, 64-bit, installs to `C:\Program Files\Simple Scam Protection`. Upgrades in place (same UpgradeCode); downgrades are blocked.
- **Intune** (Line-of-business app): upload the .msi, put properties in "Command-line arguments". Detection uses the MSI product code automatically.
- **Group Policy**: Computer Configuration > Software Installation > New Package > Assigned. Use a transform (.mst) or `--configure` afterwards for properties.
- Interactive uninstall asks for the settings password; `/qn` uninstall skips it. Uninstall removes the hosts block and machine policy.
- Use either the MSI or the Setup.exe on a PC - not both.

## Run from source
```
py -m pip install -r requirements.txt
py -m simple_scam_protection
py -m simple_scam_protection --check "http://paypa1-login.xyz"
```
Not an antivirus - keep Windows Defender on.
