"""Block scam websites through the Windows hosts file."""
import os
import subprocess
import sys

from .signatures import SCAM_DOMAINS

HOSTS_PATH = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "drivers", "etc", "hosts")
START, END = "# >>> Guardian Shield scam-site block >>>", "# <<< Guardian Shield scam-site block <<<"


def _strip_block(text):
    out, inside = [], False
    for line in text.splitlines():
        if line.strip() == START:
            inside = True
        elif line.strip() == END:
            inside = False
        elif not inside:
            out.append(line)
    return "\n".join(out).rstrip("\n")


def build_block(domains):
    lines = [START]
    for d in sorted(domains):
        lines += [f"0.0.0.0 {d}", f"0.0.0.0 www.{d}"]
    return "\n".join(lines + [END])


def apply_block(path=HOSTS_PATH, domains=SCAM_DOMAINS):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        base = _strip_block(f.read())
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{base}\n\n{build_block(domains)}\n")
    _flush_dns()


def remove_block(path=HOSTS_PATH):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        base = _strip_block(f.read())
    with open(path, "w", encoding="utf-8") as f:
        f.write(base + "\n")
    _flush_dns()


def is_blocked(path=HOSTS_PATH):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return START in f.read()
    except OSError:
        return False


def _flush_dns():
    if sys.platform == "win32":
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, creationflags=0x08000000)


def is_admin():
    if sys.platform != "win32":
        return os.geteuid() == 0
    import ctypes
    return bool(ctypes.windll.shell32.IsUserAnAdmin())


def run_elevated(flag):
    """Relaunch Guardian Shield as administrator just to edit the hosts file."""
    import ctypes
    if getattr(sys, "frozen", False):
        exe, params = sys.executable, flag
    else:
        exe, params = sys.executable, f'-m guardian_shield {flag}'
    rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, os.getcwd(), 0)
    return rc > 32


def set_blocking(enabled):
    """Turn blocking on/off, asking Windows for admin permission when needed. Returns True on success."""
    if is_admin():
        apply_block() if enabled else remove_block()
        return True
    if sys.platform == "win32":
        return run_elevated("--hosts-on" if enabled else "--hosts-off")
    return False
