"""Settings password: PBKDF2-SHA256 hash, constant-time verify, persisted lockout after failed attempts."""
import base64
import hashlib
import hmac
import json
import os
import secrets
import tempfile
import time
from pathlib import Path

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 600_000
SALT_BYTES = 16
KEY_BYTES = 32
MIN_LENGTH = 12
MAX_FAILURES = 5
LOCK_SECONDS = 60


def _derive(password, salt, iterations):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, KEY_BYTES)


def make_hash(password):
    if len(password) < MIN_LENGTH:
        raise ValueError(f"Use at least {MIN_LENGTH} characters (tip: three words, like 'blue-garden-teapot').")
    salt = secrets.token_bytes(SALT_BYTES)
    digest = _derive(password, salt, ITERATIONS)
    return f"{ALGORITHM}${ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_hash(stored, password):
    try:
        algo, iters, salt_b64, hash_b64 = stored.split("$")
        salt = base64.b64decode(salt_b64, validate=True)
        expected = base64.b64decode(hash_b64, validate=True)
        if algo != ALGORITHM or len(salt) < 16 or len(expected) != KEY_BYTES:
            return False
        return hmac.compare_digest(_derive(password, salt, int(iters)), expected)
    except (ValueError, AttributeError, TypeError):
        return False


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.stem + "-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class PasswordGuard:
    def __init__(self, store):
        self.store = store
        self.lock_file = store.dir / "lockout.json"

    def managed(self):
        return bool(self.store.policy.get("password_hash"))

    def current(self):
        return self.store.policy.get("password_hash") or self.store.settings.get("password_hash")

    def is_set(self):
        return bool(self.current())

    def _state(self):
        try:
            return json.loads(self.lock_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {"failures": 0, "locked_until": 0.0}

    def check(self, password, now=None):
        """Returns (ok, message)."""
        now = now or time.time()
        state = self._state()
        if now < state.get("locked_until", 0):
            return False, f"Too many wrong tries. Wait {int(state['locked_until'] - now) + 1} seconds."
        if verify_hash(self.current(), password):
            atomic_write(self.lock_file, json.dumps({"failures": 0, "locked_until": 0.0}))
            return True, ""
        failures = state.get("failures", 0) + 1
        state = {"failures": failures, "locked_until": 0.0}
        if failures >= MAX_FAILURES:
            state = {"failures": 0, "locked_until": now + LOCK_SECONDS}
        atomic_write(self.lock_file, json.dumps(state))
        return False, "That password is not correct."

    def set(self, password):
        if self.managed():
            raise PermissionError("The password is managed by your IT administrator.")
        self.store.set("password_hash", make_hash(password))

    def clear(self):
        if self.managed():
            raise PermissionError("The password is managed by your IT administrator.")
        self.store.set("password_hash", None)
