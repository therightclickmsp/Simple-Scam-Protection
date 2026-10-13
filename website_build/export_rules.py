"""Export the Windows app's link-checker rules to assets/rules.js so the website uses the exact same rules."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "windows_app"))

from simple_scam_protection import __version__, linkcheck as lc  # noqa: E402
from simple_scam_protection.signatures import REMOTE_TOOLS, SCAM_DOMAINS  # noqa: E402


def table(t):
    return {chr(k): v for k, v in t.items()}


data = {
    "version": __version__,
    "official": lc.OFFICIAL_DOMAINS,
    "brand_labels": lc.BRAND_LABELS,
    "suspicious_tlds": sorted(lc.SUSPICIOUS_TLDS),
    "shorteners": sorted(lc.SHORTENERS),
    "multi_suffix": sorted(lc.MULTI_SUFFIX),
    "bare_tlds": sorted(lc.BARE_TLDS),
    "lookalike": table(lc.LOOKALIKE_DIGITS),
    "confusables": table(lc.CONFUSABLES),
    "sensitive_words": lc.SENSITIVE_WORDS,
    "text_rules": lc.TEXT_RULES,
    "toll_free": lc.TOLL_FREE.pattern,
    "scheme_url": lc.SCHEME_URL.pattern,
    "bare_url": lc.BARE_URL.pattern,
    "ipv4": lc.IPV4.pattern,
    "scam_domains": sorted(SCAM_DOMAINS),
    "remote_tools": [t["name"] for t in REMOTE_TOOLS],
}
out = ROOT / "static_site" / "assets" / "rules.js"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("/* Generated from the Windows app by website_build/export_rules.py - do not edit. */\n"
               f"window.SSP_RULES = {json.dumps(data, ensure_ascii=False)};\n", encoding="utf-8")
print("wrote", out)
