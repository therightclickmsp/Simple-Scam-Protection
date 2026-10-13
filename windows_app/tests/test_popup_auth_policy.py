import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from guardian_shield import auth  # noqa: E402
from guardian_shield.auth import PasswordGuard, make_hash, verify_hash  # noqa: E402
from guardian_shield.popup import clean_title, is_scam_title  # noqa: E402
from guardian_shield.storage import Store, write_policy  # noqa: E402


@pytest.fixture(autouse=True)
def fast_hash(monkeypatch):
    monkeypatch.setattr(auth, "ITERATIONS", 1000)


@pytest.mark.parametrize("title", [
    "Windows Defender Security Alert - Your PC is locked - Google Chrome",
    "VIRUS DETECTED! Call Microsoft Support +1-888-555-0101 - Microsoft\u200b Edge",
    "Microsoft Security Warning: Trojan Spyware Detected — Mozilla Firefox",
    "Your computer has been blocked. Error # 0x80070424. Do not restart - Brave",
    "Call Windows Support 1 (844) 555-0199 and 3 more pages - Google Chrome",
])
def test_scam_popup_titles(title):
    assert is_scam_title(title)


@pytest.mark.parametrize("title", [
    "Inbox (3) - Gmail - Google Chrome",
    "Microsoft Defender Antivirus: how to scan - Microsoft Support - Microsoft Edge",
    "Security alert - Google Account - Google Chrome",
    "Weather - Mozilla Firefox",
    "",
])
def test_normal_titles(title):
    assert not is_scam_title(title)


def test_clean_title():
    assert clean_title("Hello and 2 more pages - Google Chrome") == "Hello"


def test_hash_roundtrip():
    h = make_hash("blue-garden-teapot")
    assert h.startswith("pbkdf2_sha256$") and "blue" not in h
    assert verify_hash(h, "blue-garden-teapot")
    assert not verify_hash(h, "wrong-password-123")
    assert not verify_hash("garbage", "x")
    with pytest.raises(ValueError):
        make_hash("short")


def test_guard_lockout(tmp_path):
    store = Store(tmp_path / "u", policy_file=tmp_path / "none.json")
    guard = PasswordGuard(store)
    assert not guard.is_set()
    guard.set("blue-garden-teapot")
    assert guard.check("blue-garden-teapot", now=100)[0]
    for _ in range(5):
        assert not guard.check("nope", now=100)[0]
    ok, msg = guard.check("blue-garden-teapot", now=101)
    assert not ok and "Wait" in msg
    assert PasswordGuard(Store(tmp_path / "u", policy_file=tmp_path / "none.json")).check("blue-garden-teapot", now=120)[0] is False
    assert guard.check("blue-garden-teapot", now=200)[0]
    guard.clear()
    assert not guard.is_set()


def test_policy_overrides(tmp_path):
    pol = tmp_path / "policy.json"
    write_policy({"password_hash": make_hash("it-admin-secret!"), "allowlist": ["screenconnect"],
                  "defaults": {"site_block": True, "popup_block": False, "password_hash": "x"}}, pol)
    store = Store(tmp_path / "u", policy_file=pol)
    guard = PasswordGuard(store)
    assert guard.managed() and guard.check("it-admin-secret!")[0]
    with pytest.raises(PermissionError):
        guard.set("another-password")
    assert store.is_trusted("screenconnect") and store.policy_trusted("screenconnect")
    assert store.settings["site_block"] is True and store.settings["popup_block"] is False
    assert store.settings["password_hash"] is None


def test_configure_cli(tmp_path):
    env = {"GUARDIAN_SHIELD_POLICY": str(tmp_path / "policy.json"), "GUARDIAN_SHIELD_HOME": str(tmp_path / "u"),
           "PATH": "/usr/bin:/bin"}
    h = make_hash("it-admin-secret!")
    run = lambda *a: subprocess.run([sys.executable, "-m", "guardian_shield", *a], cwd=ROOT, env=env,
                                    capture_output=True, text=True)
    r = run("--configure", "--allow", "ScreenConnect,teamviewer", "--password-hash", h, "--no-popup-block")
    assert r.returncode == 0, r.stderr
    pol = json.loads((tmp_path / "policy.json").read_text())
    assert pol["allowlist"] == ["screenconnect", "teamviewer"] and pol["password_hash"] == h
    assert pol["defaults"]["popup_block"] is False
    assert run("--configure", "--allow", "notatool").returncode == 2
    assert run("--configure", "--password-hash", "plaintext").returncode == 2
