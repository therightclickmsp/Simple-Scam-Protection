"""Find and remove remote-access tools."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

from .signatures import REMOTE_TOOLS, match_file, match_remote_tool

UNINSTALL_KEYS = [
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
]


def default_scan_dirs():
    home = Path.home()
    dirs = [home / "Downloads", home / "Desktop", home / "Documents", Path(os.environ.get("TEMP", home / "AppData/Local/Temp"))]
    return [d for d in dirs if d.exists()]


def scan_files(dirs, max_depth=2):
    found = []
    for root in dirs:
        root = Path(root)
        for dirpath, dirnames, filenames in os.walk(root):
            if len(Path(dirpath).relative_to(root).parts) >= max_depth:
                dirnames[:] = []
            for fn in filenames:
                tool = match_file(fn)
                if tool and fn.lower().endswith(".exe"):
                    found.append({"tool_id": tool["id"], "name": tool["name"], "kind": "file",
                                  "path": str(Path(dirpath) / fn)})
    return found


def scan_running():
    import psutil
    found = []
    for p in psutil.process_iter(["pid", "name", "exe"]):
        tool = match_remote_tool(p.info.get("name"))
        if tool:
            found.append({"tool_id": tool["id"], "name": tool["name"], "kind": "running",
                          "pid": p.info["pid"], "path": p.info.get("exe") or ""})
    return found


def scan_installed():
    if sys.platform != "win32":
        return []
    import winreg
    found = []
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for key_path in UNINSTALL_KEYS:
            try:
                key = winreg.OpenKey(hive, key_path)
            except OSError:
                continue
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    sub = winreg.OpenKey(key, winreg.EnumKey(key, i))
                    display = winreg.QueryValueEx(sub, "DisplayName")[0]
                    uninstall = winreg.QueryValueEx(sub, "UninstallString")[0]
                except OSError:
                    continue
                tool = match_installed_name(display)
                if tool:
                    found.append({"tool_id": tool["id"], "name": tool["name"], "kind": "installed",
                                  "path": display, "uninstall": uninstall})
    return found


def match_installed_name(display_name):
    key = (display_name or "").lower().replace(" ", "")
    for tool in REMOTE_TOOLS:
        if tool["id"] in key or tool["name"].split(" ")[0].lower().replace(" ", "") in key:
            return tool
    return None


def full_scan(dirs=None):
    results = scan_running() + scan_installed() + scan_files(dirs if dirs is not None else default_scan_dirs())
    unique, seen = [], set()
    for r in results:
        k = (r["kind"], r.get("pid"), r.get("path"))
        if k not in seen:
            seen.add(k)
            unique.append(r)
    return unique


def kill_tool(tool_id):
    import psutil
    killed = 0
    for p in psutil.process_iter(["name"]):
        tool = match_remote_tool(p.info.get("name"))
        if tool and tool["id"] == tool_id:
            try:
                p.kill()
                killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    return killed


def quarantine(path, quarantine_dir):
    qdir = Path(quarantine_dir)
    qdir.mkdir(parents=True, exist_ok=True)
    target = qdir / (Path(path).name + ".quarantined")
    shutil.move(path, target)
    return str(target)


def remove(finding, quarantine_dir):
    """Close the tool and uninstall or quarantine it. Returns a plain-language result."""
    kill_tool(finding["tool_id"])
    if finding["kind"] == "installed" and finding.get("uninstall"):
        subprocess.Popen(finding["uninstall"], shell=True)
        return f"{finding['name']} was closed and its uninstaller was opened. Follow the steps to remove it."
    if finding["kind"] in ("file", "running") and finding.get("path") and os.path.isfile(finding["path"]):
        try:
            quarantine(finding["path"], quarantine_dir)
            return f"{finding['name']} was closed and moved to quarantine."
        except OSError:
            return f"{finding['name']} was closed, but the file is in use or protected. Restart and scan again."
    return f"{finding['name']} was closed."
