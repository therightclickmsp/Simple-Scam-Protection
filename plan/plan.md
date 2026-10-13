# Guardian Shield — a Seraph Secure–style anti-scam app for Windows

A free Windows desktop app that runs in the background and stops tech-support scams: it finds and blocks remote-access tools, warns when a scammer uses built-in Windows commands to fake "infections", and checks links for scam patterns.
A small companion web page offers the app download, setup steps, and a live demo of the link checker.

## Who it's for
- Everyday Windows 10/11 users, especially older or less technical people, who are common targets of phone and pop-up scams.
- Family members who install it on a relative's PC and want it to work without accounts or setup.

## Core features and experience
**Windows app (runs in the system tray)**
- **Remote-access tool scan & removal**: on launch and on demand, scans for known remote-control programs often used by scammers (e.g., AnyDesk, TeamViewer, UltraViewer, ScreenConnect, Supremo, LogMeIn, RustDesk, Quick Assist). Shows what was found and offers to close and uninstall/quarantine it.
- **Live remote-access blocking**: watches running programs; if a remote-access tool starts, it is closed immediately and a full-screen warning explains "Someone may be trying to control your computer."
- **Allow-list**: user can mark a tool as trusted (e.g., for work IT support) so it is never blocked. Changing the allow-list requires a short typed confirmation to slow down a scammer coaching the user.
- **Command abuse detection**: detects when tools scammers use to fake problems are opened (Event Viewer, `netstat`, `tree`, `syskey`, `msconfig`, `cmd` "scan" tricks, Task Manager in certain contexts) and shows a clear warning: "If someone on the phone asked you to open this, it's a scam."
- **Link checker (rule-based)**: paste a link or message; the app flags typo-squatting of popular brands (banks, Microsoft, Amazon, PayPal), lookalike characters, suspicious domain endings, raw IP addresses, URL shorteners, and scam keywords. Result: Safe / Suspicious / Dangerous with plain-language reasons.
- **Scam website blocking**: blocks a built-in list of known scam/fake-support domains by updating the Windows hosts file (needs administrator permission once).
- **Activity log**: a simple history of everything blocked or flagged, stored only on the PC.
- **Protection toggle & status**: one big "Protected" status indicator; each protection can be switched on/off.
- Starts automatically with Windows.

**Companion web page (preview link)**
- Landing page explaining what the app does, with a Download button and step-by-step install instructions.
- Live web version of the rule-based link checker so people can try it before installing.

## User flow
1. User opens the web page, reads what it does, tries the link checker, downloads the app.
2. Installs and runs it; a first-run scan lists any remote-access tools found and offers removal.
3. App moves to the system tray showing "Protected".
4. If a remote tool launches or a scam-type command is opened, a large warning appears; the event is logged.
5. User can open the app anytime to check a link, review the log, or manage the allow-list.

## UI/UX feel
- Calm, trustworthy, large and readable — designed for non-technical and older users.
- Few screens: Status, Link Checker, Activity Log, Settings/Allow-list.
- Warnings are bold, full-screen, and plain-spoken; no jargon.

## Implementation phases
**Phase 1 — MVP (built now)**
- Windows app with: remote-access scan/removal, live blocking, allow-list, command abuse warnings, rule-based link checker, hosts-file site blocking, activity log, tray icon, auto-start.
- Companion web page with download, install guide, and web link checker.

**Phase 2**
- Fake virus pop-up detection (browser lock-screen / "call Microsoft" pages).
- Browser extension that blocks scam sites and newly created domains in real time.
- Auto-updating scam domain and remote-tool lists.

**Phase 3**
- Signed installer (no Windows "unknown publisher" warning) and auto-update of the app itself.
- Optional extras: password-protected settings, multi-language interface, macOS version.

## Assumptions
- The Windows app is written in Python with a simple desktop interface and packaged into a single `.exe`. This environment runs on Linux, so the app logic is tested here, but the final `.exe` is built either via a provided one-click build script on a Windows PC or an automated GitHub build; it cannot be test-run on real Windows inside this workspace.
- The `.exe` will be unsigned, so Windows SmartScreen will show a warning on first run.
- No sign-in, no accounts, no guardian alerts, no payments — everything is free and all data stays on the PC.
- Link checking is rule-based only, no AI and no external lookup services.
- Scam-site blocking uses a built-in starter list of domains; it is not a full real-time threat feed.
- Detecting remote-access tools is by known program names/signatures; brand-new or renamed tools may be missed.
- Not an antivirus — meant to run alongside Windows Defender.
- Product name "Guardian Shield" is a placeholder and avoids copying Seraph Secure's branding.
