"""Background watcher for remote-access tools and scam-abused commands."""
import threading
import time

from .signatures import match_remote_tool, match_scam_command

REMOTE_CONTEXT_SECONDS = 15 * 60


class Classifier:
    """Decides what to do with a newly started process (pure logic, easy to test)."""

    def __init__(self, store):
        self.store = store
        self.last_remote = 0.0

    def classify(self, name, cmdline="", now=None):
        now = now or time.time()
        tool = match_remote_tool(name)
        if tool:
            self.last_remote = now
            if self.store.is_trusted(tool["id"]):
                return {"type": "remote_trusted", "tool": tool}
            if self.store.settings["remote_block"]:
                return {"type": "remote_block", "tool": tool}
            return {"type": "remote_seen", "tool": tool}
        if self.store.settings["command_warn"]:
            recent = now - self.last_remote < REMOTE_CONTEXT_SECONDS
            cmd = match_scam_command(name, cmdline, recent_remote=recent)
            if cmd:
                return {"type": "command", "command": cmd}
        return None


class ProcessMonitor(threading.Thread):
    def __init__(self, store, on_event, interval=1.5):
        super().__init__(daemon=True)
        self.classifier = Classifier(store)
        self.on_event = on_event
        self.interval = interval
        self.seen = set()
        self._halt = threading.Event()

    def stop(self):
        self._halt.set()

    def run(self):
        import psutil
        first = True
        while not self._halt.is_set():
            current = set()
            for p in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
                key = (p.info["pid"], p.info.get("create_time"))
                current.add(key)
                if key in self.seen:
                    continue
                name = p.info.get("name") or ""
                cmdline = " ".join(p.info.get("cmdline") or [])
                decision = self.classifier.classify(name, cmdline)
                if not decision or (first and decision["type"] == "command"):
                    continue
                if decision["type"] == "remote_block":
                    try:
                        for child in p.children(recursive=True):
                            child.kill()
                        p.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                self.on_event(decision)
            self.seen = current
            first = False
            self._halt.wait(self.interval)
