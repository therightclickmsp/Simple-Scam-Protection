"""Checks the website's JavaScript link checker gives exactly the same answers as the Windows app (needs node)."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "windows_app"))
from simple_scam_protection.linkcheck import check  # noqa: E402

CASES = [
    "", "   ", "see you at dinner", "https://www.amazon.com/your-orders", "http://paypa1.com",
    "https://paypa1-secure-login.xyz/verify-account", "http://192.168.1.5/login",
    "VIRUS DETECTED call Microsoft Support 1-888-555-0199",
    "WARNING! Your computer is infected with a Trojan virus. Do not shut down your PC. Call Microsoft Support "
    "immediately at 1-844-555-0199 or visit support-microsoft-alert-fix.cc",
    "Your Norton subscription was renewed for $399.99. To get a refund call us today and install AnyDesk.",
    "https://micros0ft.com/account", "https://www.microsoft.com/en-us/windows", "http://аpple.com/id",
    "https://xn--pple-43d.com", "bit.ly/3abcde", "http://user@evil.example.com/paypal", "rnicrosoft.com",
    "amazon-refund-dept.com", "Your package could not be delivered. Pay the customs fee at usps-redelivery-fee.com",
    "Buy gift cards and send the codes. Urgent! hxxp://wellsfargo-secure-login.com", "https://www.bbc.co.uk/news",
    "Check www.google.com, and bit.ly/x).", "https://a.b.c.d.example.top/path", "http://my-bank-secure-help.online",
    "Your account has been suspended, verify your identity at https://chase.com.verify-me.ru",
    "The IRS has issued a warrant for your arrest", "Contact apple support", "file.txt and notes.doc", "faceb00k.com",
    "http://[::1]:8080/x",
]

node = r"""
const fs = require("fs"); globalThis.window = globalThis;
eval(fs.readFileSync(process.argv[1], "utf8")); eval(fs.readFileSync(process.argv[2], "utf8"));
const cases = JSON.parse(fs.readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(cases.map((c) => SSPLinkCheck.check(c))));
"""
assets = ROOT / "static_site" / "assets"
out = subprocess.run(["node", "-e", node, str(assets / "rules.js"), str(assets / "linkcheck.js")],
                     input=json.dumps(CASES), capture_output=True, text=True, check=True)
js = json.loads(out.stdout)
bad = 0
for case, got in zip(CASES, js):
    want = check(case)
    if got != want:
        bad += 1
        print("MISMATCH:", repr(case), "\n  py:", want, "\n  js:", got)
print(f"{len(CASES) - bad}/{len(CASES)} cases identical")
sys.exit(1 if bad else 0)
