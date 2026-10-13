"""Settings and activity log, stored only on this PC."""
import json
import os
import threading
from datetime import datetime
from pathlib import Path

DEFAULTS = {
    "remote_block": True,
    "command_warn": True,
    "site_block": False,
    "autostart": True,
    "allowlist": [],
    "first_run_done": False,
}


def data_dir():
    base = os.environ.get("APPDATA") or str(Path.home() / ".config")
    path = Path(os.environ.get("GUARDIAN_SHIELD_HOME") or Path(base) / "GuardianShield")
    path.mkdir(parents=True, exist_ok=True)
    return path


class Store:
    def __init__(self, directory=None):
        self.dir = Path(directory) if directory else data_dir()
        self.settings_file = self.dir / "settings.json"
        self.log_file = self.dir / "activity.json"
        self._lock = threading.Lock()
        self.settings = {**DEFAULTS, **self._read(self.settings_file, {})}
        self.log = self._read(self.log_file, [])

    @staticmethod
    def _read(path, default):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return default

    def save_settings(self):
        with self._lock:
            self.settings_file.write_text(json.dumps(self.settings, indent=2), encoding="utf-8")

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def add_event(self, kind, title, detail=""):
        event = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": kind, "title": title, "detail": detail}
        with self._lock:
            self.log.insert(0, event)
            del self.log[1000:]
            self.log_file.write_text(json.dumps(self.log, indent=2), encoding="utf-8")
        return event

    def clear_log(self):
        with self._lock:
            self.log = []
            self.log_file.write_text("[]", encoding="utf-8")

    def is_trusted(self, tool_id):
        return tool_id in self.settings["allowlist"]
