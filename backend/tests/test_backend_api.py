"""Backend API tests for Simple Scam Protection."""
import io
import os
import zipfile

import pytest
import requests
from dotenv import load_dotenv

load_dotenv("/app/frontend/.env")
BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# --- /api/ root ---
def test_root(session):
    r = session.get(f"{API}/")
    assert r.status_code == 200
    j = r.json()
    assert "version" in j and "Simple Scam Protection" in j["message"]


# --- /api/check verdicts ---
@pytest.mark.parametrize("text,expected_verdict", [
    ("https://www.amazon.com", "safe"),
    ("http://paypa1.com", {"suspicious", "dangerous"}),  # typo-squat should at least be suspicious
    ("http://192.168.1.5/login", "dangerous"),
    ("VIRUS DETECTED call Microsoft Support 1-888-555-0199", "dangerous"),
    ("see you at dinner", "safe"),
    ("", "safe"),
])
def test_check_verdicts(session, text, expected_verdict):
    r = session.post(f"{API}/check", json={"text": text})
    assert r.status_code == 200, r.text
    data = r.json()
    assert set(data.keys()) >= {"verdict", "score", "reasons", "urls"}
    assert isinstance(data["reasons"], list) and len(data["reasons"]) >= 1
    assert isinstance(data["score"], int)
    if isinstance(expected_verdict, set):
        assert data["verdict"] in expected_verdict, f"Got {data['verdict']} for {text!r}"
    else:
        assert data["verdict"] == expected_verdict, f"Got {data['verdict']} for {text!r}"


def test_check_paypa1_is_not_safe(session):
    """paypa1.com (digit 1 for letter l) must NOT be classified safe."""
    r = session.post(f"{API}/check", json={"text": "http://paypa1.com"})
    assert r.status_code == 200
    assert r.json()["verdict"] != "safe"


def test_check_amazon_url_present(session):
    r = session.post(f"{API}/check", json={"text": "https://www.amazon.com"})
    data = r.json()
    assert len(data["urls"]) == 1
    assert data["urls"][0]["host"] == "www.amazon.com"


# --- /api/signatures ---
def test_signatures(session):
    r = session.get(f"{API}/signatures")
    assert r.status_code == 200
    data = r.json()
    assert "remote_tools" in data and isinstance(data["remote_tools"], list)
    assert "AnyDesk" in data["remote_tools"]
    assert "TeamViewer" in data["remote_tools"]
    assert data["scam_domain_count"] > 0
    assert isinstance(data["commands"], list) and len(data["commands"]) > 0


# --- /api/stats increments ---
def test_stats_increment_on_check(session):
    before = session.get(f"{API}/stats").json()
    session.post(f"{API}/check", json={"text": "hello"})
    after = session.get(f"{API}/stats").json()
    assert after["checks"] >= before["checks"] + 1


def test_stats_increment_on_download(session):
    before = session.get(f"{API}/stats").json()
    r = session.get(f"{API}/download", stream=True)
    assert r.status_code == 200
    r.content  # consume
    after = session.get(f"{API}/stats").json()
    assert after["downloads"] >= before["downloads"] + 1


# --- /api/download zip contents ---
def test_download_zip_contents(session):
    r = session.get(f"{API}/download")
    assert r.status_code == 200
    assert r.headers.get("content-type") == "application/zip"
    assert "attachment" in r.headers.get("content-disposition", "")
    z = zipfile.ZipFile(io.BytesIO(r.content))
    names = z.namelist()
    assert any(n.startswith("SimpleScamProtection/") for n in names)
    assert any("simple_scam_protection" in n for n in names)
    assert any(n.endswith("linkcheck.py") for n in names)
    # No pycache
    assert not any("__pycache__" in n for n in names)
