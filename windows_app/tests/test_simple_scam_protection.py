import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simple_scam_protection import hosts, scanner  # noqa: E402
from simple_scam_protection.linkcheck import check, extract_urls  # noqa: E402
from simple_scam_protection.monitor import Classifier  # noqa: E402
from simple_scam_protection.signatures import match_remote_tool, match_scam_command  # noqa: E402
from simple_scam_protection.storage import Store  # noqa: E402


def test_official_sites_safe():
    for url in ["https://www.paypal.com/signin", "https://login.microsoftonline.com", "amazon.co.uk", "chase.com"]:
        assert check(url)["verdict"] == "safe", url


def test_typosquat_and_lookalike():
    for url in ["http://paypa1.com", "https://rnicrosoft.com", "amaz0n-support.com", "https://micorsoft.com/login"]:
        assert check(url)["verdict"] != "safe", url


def test_dangerous_cases():
    assert check("http://192.168.4.20/paypal/login")["verdict"] == "dangerous"
    assert check("https://paypal.com.secure-login.xyz/verify")["verdict"] == "dangerous"
    assert check("microsoft-support-alert.com")["verdict"] == "dangerous"
    assert check("https://xn--pypal-4ve.com")["verdict"] != "safe"
    msg = "VIRUS DETECTED! Do not shut down your PC. Call Microsoft Support at 1-888-555-0199 now."
    assert check(msg)["verdict"] == "dangerous"


def test_shortener_and_text():
    assert check("bit.ly/3xYz")["verdict"] != "dangerous"
    assert check("Pay the refund fee with Google Play gift cards and install AnyDesk")["verdict"] == "dangerous"
    assert check("Hi grandma, see you at dinner tonight!")["verdict"] == "safe"


def test_extract_urls():
    urls = extract_urls("go to www.example.com or paypa1.xyz, not file.txt")
    assert "www.example.com" in urls and "paypa1.xyz" in urls and len(urls) == 2


def test_signature_matching():
    assert match_remote_tool("AnyDesk.exe")["id"] == "anydesk"
    assert match_remote_tool("TeamViewer_Service.exe")["id"] == "teamviewer"
    assert match_remote_tool("notepad.exe") is None
    assert match_scam_command("eventvwr.exe")["id"] == "eventvwr"
    assert match_scam_command("mmc.exe", "mmc.exe C:\\Windows\\system32\\eventvwr.msc")["id"] == "eventvwr"
    assert match_scam_command("taskmgr.exe") is None
    assert match_scam_command("taskmgr.exe", recent_remote=True)["id"] == "taskmgr"


def test_classifier_allowlist(tmp_path):
    store = Store(tmp_path)
    c = Classifier(store)
    assert c.classify("anydesk.exe", now=1000)["type"] == "remote_block"
    assert c.classify("taskmgr.exe", now=1100)["type"] == "command"
    assert c.classify("taskmgr.exe", now=1000 + 3600) is None
    store.set("allowlist", ["anydesk"])
    assert c.classify("anydesk.exe")["type"] == "remote_trusted"
    store.set("command_warn", False)
    assert c.classify("netstat.exe") is None


def test_hosts_block_roundtrip(tmp_path):
    f = tmp_path / "hosts"
    f.write_text("127.0.0.1 localhost\n")
    hosts.apply_block(str(f), {"bad.com"})
    hosts.apply_block(str(f), {"bad.com"})
    text = f.read_text()
    assert text.count(hosts.START) == 1 and "0.0.0.0 www.bad.com" in text
    assert hosts.is_blocked(str(f))
    hosts.remove_block(str(f))
    assert f.read_text().strip() == "127.0.0.1 localhost"


def test_file_scan_and_quarantine(tmp_path):
    dl = tmp_path / "Downloads"
    dl.mkdir()
    (dl / "AnyDesk (1).exe").write_bytes(b"x")
    (dl / "report.pdf").write_bytes(b"x")
    found = scanner.scan_files([dl])
    assert [f["tool_id"] for f in found] == ["anydesk"]
    target = scanner.quarantine(found[0]["path"], tmp_path / "q")
    assert Path(target).exists() and not (dl / "AnyDesk (1).exe").exists()


def test_store_log(tmp_path):
    s = Store(tmp_path)
    s.add_event("blocked", "Blocked AnyDesk")
    assert Store(tmp_path).log[0]["title"] == "Blocked AnyDesk"


def test_quickassist_trusted_by_default_and_for_existing_users(tmp_path):
    assert Store(tmp_path / "new").is_trusted("quickassist")
    old = tmp_path / "old"
    old.mkdir()
    (old / "settings.json").write_text('{"allowlist": ["anydesk"]}')
    s = Store(old)
    assert s.is_trusted("quickassist") and s.is_trusted("anydesk")
    s.set("allowlist", ["anydesk"])  # user later un-trusts it: must stay un-trusted
    assert not Store(old).is_trusted("quickassist")
