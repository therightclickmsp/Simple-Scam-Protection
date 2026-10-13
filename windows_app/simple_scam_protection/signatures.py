"""Known remote-access tools, scam-abused Windows commands and scam domains."""
import fnmatch

REMOTE_TOOLS = [
    {"id": "anydesk", "name": "AnyDesk", "processes": ["anydesk.exe"], "files": ["anydesk*.exe"]},
    {"id": "teamviewer", "name": "TeamViewer",
     "processes": ["teamviewer.exe", "teamviewer_service.exe", "tv_w32.exe", "tv_x64.exe", "teamviewerqs*.exe"],
     "files": ["teamviewer*.exe"]},
    {"id": "ultraviewer", "name": "UltraViewer",
     "processes": ["ultraviewer_desktop.exe", "ultraviewer_service.exe", "uvupdater.exe"], "files": ["ultraviewer*.exe"]},
    {"id": "screenconnect", "name": "ScreenConnect / ConnectWise Control",
     "processes": ["screenconnect.clientservice.exe", "screenconnect.windowsclient.exe", "connectwisecontrol*.exe"],
     "files": ["screenconnect*.exe", "connectwisecontrol*.exe"]},
    {"id": "supremo", "name": "Supremo", "processes": ["supremo.exe", "supremoservice.exe", "supremohelper.exe"],
     "files": ["supremo*.exe"]},
    {"id": "logmein", "name": "LogMeIn / GoTo Resolve",
     "processes": ["logmein.exe", "lmiguardiansvc.exe", "logmeinrescue*.exe", "lmi_rescue*.exe", "gotoassist*.exe"],
     "files": ["logmein*.exe", "gotoassist*.exe"]},
    {"id": "rustdesk", "name": "RustDesk", "processes": ["rustdesk.exe"], "files": ["rustdesk*.exe"]},
    {"id": "quickassist", "name": "Microsoft Quick Assist", "processes": ["quickassist.exe"], "files": []},
    {"id": "ammyy", "name": "Ammyy Admin", "processes": ["aa_v3.exe", "ammyy_admin.exe"], "files": ["aa_v3*.exe", "ammyy*.exe"]},
    {"id": "splashtop", "name": "Splashtop", "processes": ["srserver.exe", "strwinclt.exe", "sragent.exe"],
     "files": ["splashtop*.exe"]},
    {"id": "zohoassist", "name": "Zoho Assist", "processes": ["zaservice.exe", "zohoassist*.exe", "zohours.exe"],
     "files": ["zohoassist*.exe", "zasetup*.exe"]},
    {"id": "aeroadmin", "name": "AeroAdmin", "processes": ["aeroadmin.exe"], "files": ["aeroadmin*.exe"]},
    {"id": "hoptodesk", "name": "HopToDesk", "processes": ["hoptodesk.exe"], "files": ["hoptodesk*.exe"]},
    {"id": "remoteutilities", "name": "Remote Utilities", "processes": ["rutserv.exe", "rfusclient.exe"], "files": []},
    {"id": "getscreen", "name": "Getscreen.me", "processes": ["getscreen.exe"], "files": ["getscreen*.exe"]},
    {"id": "dwservice", "name": "DWService", "processes": ["dwagent.exe", "dwagsvc.exe"], "files": ["dwagent*.exe"]},
    {"id": "vnc", "name": "VNC (UltraVNC / TightVNC)", "processes": ["winvnc.exe", "tvnserver.exe", "winvnc4.exe"],
     "files": []},
    {"id": "radmin", "name": "Radmin", "processes": ["rserver3.exe", "radmin.exe"], "files": []},
    {"id": "iperius", "name": "Iperius Remote", "processes": ["iperiusremote.exe"], "files": ["iperiusremote*.exe"]},
]
TOOLS_BY_ID = {t["id"]: t for t in REMOTE_TOOLS}

SCAM_COMMANDS = [
    {"id": "eventvwr", "name": "Event Viewer", "processes": ["eventvwr.exe"], "cmdline": ["eventvwr.msc"],
     "message": "Event Viewer is full of normal warnings that every computer has. Scammers show it to make you "
                "think your PC is broken or hacked. It is not."},
    {"id": "netstat", "name": "netstat (network list)", "processes": ["netstat.exe"], "cmdline": [],
     "message": "This list of normal internet connections is used by scammers to claim 'hackers are connected'. "
                "It is not proof of anything."},
    {"id": "tree", "name": "tree (folder list)", "processes": ["tree.com"], "cmdline": [],
     "message": "Scammers run 'tree' to make text scroll by and pretend it is a virus scan. It isn't."},
    {"id": "syskey", "name": "syskey", "processes": ["syskey.exe"], "cmdline": [],
     "message": "Scammers use syskey to lock you out of your own computer and demand money."},
    {"id": "msconfig", "name": "System Configuration (msconfig)", "processes": ["msconfig.exe"], "cmdline": [],
     "message": "Scammers open this to point at normal settings and say your warranty or licence has 'expired'."},
    {"id": "taskmgr", "name": "Task Manager", "processes": ["taskmgr.exe"], "cmdline": [], "needs_remote": True,
     "message": "Task Manager was opened shortly after a remote-access tool. Scammers use it to point at normal "
                "programs and call them 'viruses'."},
]

SCAM_DOMAINS = {
    "microsoft-support-alert.com", "windows-defender-alert.net", "microsoft-security-warning.com",
    "pc-security-warning.com", "call-tech-support-now.com", "windows-error-help.com", "virus-alert-microsoft.com",
    "apple-support-alert.com", "icloud-locked-support.com", "your-pc-is-infected.com", "pc-cleaner-alert.net",
    "norton-renewal-billing.com", "mcafee-renewal-center.com", "geeksquad-renewal.com", "paypal-refund-center.com",
    "amazon-refund-dept.com", "techsupport-helpline-24x7.com", "windows-firewall-warning.com",
    "system-error-0x80070424.com", "anydesk-support-help.com", "remote-tech-assist.com", "refund-department.net",
    "secure-banking-verify.com", "microsoft-account-unlock.com", "defender-firewall-alert.xyz",
    "usps-redelivery-fee.com", "irs-tax-refund-claim.com", "wellsfargo-secure-login.com", "chase-verify-account.com",
}


def _match(name, patterns):
    return any(fnmatch.fnmatch(name, p) for p in patterns)


def match_remote_tool(process_name):
    name = (process_name or "").lower()
    for tool in REMOTE_TOOLS:
        if _match(name, tool["processes"]):
            return tool
    return None


def match_scam_command(process_name, cmdline="", recent_remote=False):
    name = (process_name or "").lower()
    cmd = (cmdline or "").lower()
    for c in SCAM_COMMANDS:
        if _match(name, c["processes"]) or any(p in cmd for p in c["cmdline"]):
            if c.get("needs_remote") and not recent_remote:
                return None
            return c
    return None


def match_file(filename):
    name = filename.lower()
    for tool in REMOTE_TOOLS:
        if _match(name, tool["files"]) or _match(name, tool["processes"]):
            return tool
    return None
