"""Detect and close fake 'your PC is locked, call Microsoft' browser pages."""
import re
import sys
import threading
import time

BROWSERS = {"chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe", "opera_gx.exe", "vivaldi.exe",
            "iexplore.exe", "waterfox.exe", "librewolf.exe", "chromium.exe", "yandex.exe"}
BROWSER_SUFFIX = re.compile(r"\s+(and \d+ more pages?\s*)?[-—–]\s*(google chrome|microsoft\u200b? edge|mozilla firefox"
                            r"|brave|opera|vivaldi|internet explorer|chromium|personal - microsoft edge|work - microsoft edge)"
                            r"\s*$", re.I)
SCAM_TITLE_RULES = [
    r"(your |this )?(pc|computer|windows|system|device|browser) (is|has been|was) (locked|blocked|infected|compromised|hacked|suspended)",
    r"(windows|microsoft|apple|mac) (defender|security|firewall|support)( security| firewall)?\s*[-:]?\s*(alert|warning|notification|center)",
    r"security (alert|warning|breach)\s*!|critical (alert|warning|security)",
    r"virus (detected|alert|found|infection)|trojan|spyware|malware (detected|alert|found)|zeus virus|ransomware",
    r"call (microsoft|windows|apple|support|technical|tech|help|the number|now|us)|contact (microsoft|windows|apple) support"
    r"|(tech|technical|customer) support",
    r"error\s*(code|#)?\s*:?\s*(0x[0-9a-f]{4,}|dw6vb36|#?268d3)",
    r"do not (close|restart|shut ?down|turn off|ignore)",
    r"(access|license|licence) (to this pc )?(has been |is )?(denied|blocked|suspended|expired)",
]
TOLL_FREE = re.compile(r"(\+?1[\s.-]?)?\(?8(00|33|44|55|66|77|88)\)?[\s.-]?\d{3}[\s.-]?\d{4}")


def clean_title(title):
    return BROWSER_SUFFIX.sub("", title or "").strip()


def is_scam_title(title):
    """A page title needs two independent scam signals (or a toll-free number plus one) to be flagged."""
    t = clean_title(title).lower()
    if not t:
        return False
    hits = sum(1 for rule in SCAM_TITLE_RULES if re.search(rule, t))
    phone = bool(TOLL_FREE.search(t))
    return hits >= 2 or (phone and hits >= 1)


# ---------- Windows-only helpers ----------
def list_browser_windows():
    import ctypes
    from ctypes import wintypes
    import psutil
    user32 = ctypes.windll.user32
    found = []
    names = {}

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def callback(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if not length:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value not in names:
            try:
                names[pid.value] = psutil.Process(pid.value).name().lower()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                names[pid.value] = ""
        if names[pid.value] in BROWSERS:
            found.append((hwnd, buf.value, pid.value, names[pid.value]))
        return True

    user32.EnumWindows(callback, 0)
    return found


def _window_title(hwnd):
    import ctypes
    user32 = ctypes.windll.user32
    length = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value if user32.IsWindow(hwnd) else ""


def _press(*keys):
    import ctypes
    user32 = ctypes.windll.user32
    for k in keys:
        user32.keybd_event(k, 0, 0, 0)
    for k in reversed(keys):
        user32.keybd_event(k, 0, 2, 0)


def close_scam_window(hwnd, pid):
    """Try to close just the scam tab; if the page fights back, close the whole browser."""
    import ctypes
    import psutil
    user32 = ctypes.windll.user32
    VK_ESCAPE, VK_CONTROL, VK_W = 0x1B, 0x11, 0x57
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    _press(VK_ESCAPE)
    time.sleep(0.2)
    _press(VK_CONTROL, VK_W)
    time.sleep(1.5)
    if not is_scam_title(_window_title(hwnd)):
        return "tab"
    try:
        proc = psutil.Process(pid)
        root = proc
        while root.parent() and root.parent().name().lower() == proc.name().lower():
            root = root.parent()
        for child in root.children(recursive=True):
            child.kill()
        root.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    return "browser"


class PopupWatcher(threading.Thread):
    def __init__(self, store, on_event, interval=2.0):
        super().__init__(daemon=True)
        self.store = store
        self.on_event = on_event
        self.interval = interval
        self.recent = {}
        self._halt = threading.Event()

    def stop(self):
        self._halt.set()

    def run(self):
        if sys.platform != "win32":
            return
        while not self._halt.is_set():
            if self.store.settings.get("popup_block", True):
                now = time.time()
                for hwnd, title, pid, browser in list_browser_windows():
                    if not is_scam_title(title) or now - self.recent.get(hwnd, 0) < 10:
                        continue
                    self.recent[hwnd] = now
                    action = close_scam_window(hwnd, pid)
                    self.on_event({"type": "popup", "title": clean_title(title), "browser": browser, "action": action})
            self._halt.wait(self.interval)
