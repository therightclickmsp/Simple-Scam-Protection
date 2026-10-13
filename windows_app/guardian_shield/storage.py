"""Settings and activity log, stored only on this PC, plus an optional machine-wide IT policy."""
import json
import os
import threading
from datetime import datetime
from pathlib import Path

DEFAULTS = {
    "remote_block": True,
    "command_warn": True,
    "popup_block": True,
    "site_block": False,
    "autostart": True,
    "allowlist": [],
    "first_run_done": False,
    "password_hash": None,
}
POLICY_DEFAULT_KEYS = {"remote_block", "command_warn", "popup_block", "site_block"}


def data_dir():
    base = os.environ.get("APPDATA") or str(Path.home() / ".config")
    path = Path(os.environ.get("GUARDIAN_SHIELD_HOME") or Path(base) / "GuardianShield")
    path.mkdir(parents=True, exist_ok=True)
    return path


def policy_path():
    """Machine-wide policy written by the installer / RMM (admin-only writable in ProgramData)."""
    base = os.environ.get("ProgramData") or str(Path.home() / ".config")
    return Path(os.environ.get("GUARDIAN_SHIELD_POLICY") or Path(base) / "GuardianShield" / "policy.json")


def read_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_policy(updates, path=None):
    from .auth import atomic_write
    path = Path(path or policy_path())
    policy = {**read_json(path, {}), **updates}
    atomic_write(path, json.dumps(policy, indent=2))
    return policy


class Store:
    def __init__(self, directory=None, policy_file=None):
        from .auth import atomic_write
        self._write = atomic_write
        self.dir = Path(directory) if directory else data_dir()
        self.dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.dir / "settings.json"
        self.log_file = self.dir / "activity.json"
        self._lock = threading.Lock()
        self.policy = read_json(policy_file or policy_path(), {})
        defaults = {k: v for k, v in self.policy.get("defaults", {}).items() if k in POLICY_DEFAULT_KEYS}
        self.settings = {**DEFAULTS, **defaults, **read_json(self.settings_file, {})}
        self.log = read_json(self.log_file, [])

    def save_settings(self):
        with self._lock:
            self._write(self.settings_file, json.dumps(self.settings, indent=2))

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def add_event(self, kind, title, detail=""):
        event = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": kind, "title": title, "detail": detail}
        with self._lock:
            self.log.insert(0, event)
            del self.log[1000:]
            self._write(self.log_file, json.dumps(self.log, indent=2))
        return event

    def clear_log(self):
        with self._lock:
            self.log = []
            self._write(self.log_file, "[]")

    def is_trusted(self, tool_id):
        return tool_id in self.settings["allowlist"] or tool_id in self.policy.get("allowlist", [])

    def policy_trusted(self, tool_id):
        return tool_id in self.policy.get("allowlist", [])
