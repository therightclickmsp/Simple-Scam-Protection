"""Rule-based scam link and message checker (no network, no AI)."""
import re
from urllib.parse import urlparse

from .signatures import SCAM_DOMAINS

OFFICIAL_DOMAINS = {
    "microsoft": ["microsoft.com", "live.com", "outlook.com", "office.com", "windows.com", "xbox.com",
                  "bing.com", "microsoftonline.com", "msn.com", "office365.com"],
    "apple": ["apple.com", "icloud.com"],
    "amazon": ["amazon.com", "amazon.co.uk", "amazon.ca", "amazon.de", "amazon.in", "amazon.com.au", "amazonaws.com"],
    "paypal": ["paypal.com", "paypal.me"],
    "google": ["google.com", "gmail.com", "youtube.com", "google.co.uk"],
    "netflix": ["netflix.com"],
    "chase": ["chase.com"],
    "wellsfargo": ["wellsfargo.com"],
    "bankofamerica": ["bankofamerica.com", "bofa.com"],
    "citibank": ["citi.com", "citibank.com"],
    "facebook": ["facebook.com", "fb.com", "meta.com"],
    "instagram": ["instagram.com"],
    "ebay": ["ebay.com", "ebay.co.uk"],
    "walmart": ["walmart.com"],
    "usps": ["usps.com"],
    "fedex": ["fedex.com"],
    "dhl": ["dhl.com"],
    "irs": ["irs.gov"],
    "norton": ["norton.com"],
    "mcafee": ["mcafee.com"],
    "geeksquad": ["geeksquad.com", "bestbuy.com"],
    "coinbase": ["coinbase.com"],
    "hsbc": ["hsbc.com", "hsbc.co.uk"],
    "barclays": ["barclays.co.uk", "barclays.com"],
}
BRAND_LABELS = {"bankofamerica": "Bank of America", "wellsfargo": "Wells Fargo", "geeksquad": "Geek Squad",
                "usps": "USPS", "irs": "IRS", "dhl": "DHL", "hsbc": "HSBC", "paypal": "PayPal", "ebay": "eBay",
                "fedex": "FedEx", "mcafee": "McAfee"}
ALL_OFFICIAL = {d: b for b, ds in OFFICIAL_DOMAINS.items() for d in ds}

SUSPICIOUS_TLDS = {"xyz", "top", "tk", "ml", "ga", "cf", "gq", "click", "loan", "work", "zip", "mov", "cc",
                   "buzz", "rest", "cam", "icu", "online", "site", "support", "help", "tech", "su", "pw", "monster",
                   "cyou", "sbs", "cfd", "quest", "live", "shop"}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly", "ow.ly", "rb.gy", "tiny.cc",
              "shorturl.at", "buff.ly", "rebrand.ly", "t.ly", "s.id", "v.gd"}
MULTI_SUFFIX = {"co.uk", "org.uk", "gov.uk", "ac.uk", "com.au", "co.in", "co.nz", "com.br", "co.jp", "co.za"}
BARE_TLDS = {"com", "net", "org", "info", "biz", "io", "co", "us", "uk", "ca", "de", "au", "in", "gov", "edu",
             "me", "app", "ru", "cn", "ly", "gd", "at", "gl"} | SUSPICIOUS_TLDS
LOOKALIKE_DIGITS = str.maketrans({"0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t", "8": "b", "@": "a"})
CONFUSABLES = str.maketrans({"а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x", "і": "i", "ј": "j",
                             "ԁ": "d", "ѕ": "s", "ɡ": "g", "ⅼ": "l", "ο": "o", "α": "a", "ν": "v", "ı": "i"})
SENSITIVE_WORDS = ["login", "signin", "verify", "secure", "account", "update", "support", "helpdesk",
                   "refund", "billing", "unlock", "wallet", "recover"]

TEXT_RULES = [
    (r"virus|infected|malware|trojan|spyware|hacked|your (pc|computer) (is|has been) (locked|blocked)",
     "Says your computer is infected or locked. Real security warnings never ask you to call or pay.", 15),
    (r"do not (shut down|turn off|restart|close)",
     "Tells you not to turn off your computer - a classic pressure tactic.", 15),
    (r"(call|contact) (microsoft|apple|windows|amazon|support|tech)|microsoft support|windows support|apple support"
     r"|tech(nical)? support|help ?desk|customer support",
     "Pushes you to call 'support'. Microsoft, Apple and banks never ask you to call from a pop-up or text.", 15),
    (r"gift ?card|google play card|itunes card|steam card|bitcoin|crypto|wire transfer|western union|zelle|moneygram",
     "Asks for gift cards, crypto or wire transfers - payments scammers prefer because they can't be undone.", 25),
    (r"refund|overcharged|overpaid|subscription (renewal|renewed)|auto[- ]?renew",
     "Talks about a refund or renewal you didn't expect - the 'refund scam' trick.", 15),
    (r"anydesk|teamviewer|ultraviewer|remote access|screenconnect|quick assist|rustdesk|supremo|logmein",
     "Mentions remote-access software. Never let a stranger connect to your computer.", 25),
    (r"account (has been |is |was )?(suspended|locked|compromised|disabled|on hold)|unusual (sign[- ]?in|activity)"
     r"|verify your (account|identity|information)|confirm your (details|identity)",
     "Claims there is a problem with your account and asks you to verify it.", 15),
    (r"urgent|immediately|within 24 hours|final (notice|warning)|act now|right away|expires? today",
     "Uses urgency to rush you. Scammers don't want you to stop and think.", 10),
    (r"\birs\b|social security|warrant|arrest|police|legal action|lawsuit",
     "Threatens legal trouble or uses a government agency's name to scare you.", 15),
    (r"(package|parcel|shipment).{0,30}(not be delivered|was not delivered|on hold|undeliverable)"
     r"|delivery (failed|attempt)|redelivery|customs fee",
     "Fake delivery problem - a very common text-message scam.", 15),
]
TOLL_FREE = re.compile(r"(\+?1[\s.-]?)?\(?8(00|33|44|55|66|77|88)\)?[\s.-]?\d{3}[\s.-]?\d{4}")
SCHEME_URL = re.compile(r"(?:(?:https?|hxxps?)://|www\.)[^\s<>\"']+", re.I)
BARE_URL = re.compile(r"\b(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+([a-z]{2,24})\b(?:/[^\s<>\"']*)?", re.I)
IPV4 = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def levenshtein(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def registrable_domain(host):
    labels = host.strip(".").split(".")
    if len(labels) >= 3 and ".".join(labels[-2:]) in MULTI_SUFFIX:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def brand_name(brand):
    return BRAND_LABELS.get(brand, brand.capitalize())


def extract_urls(text):
    urls = [m.group(0).rstrip(".,;:!?)]}") for m in SCHEME_URL.finditer(text)]
    rest = SCHEME_URL.sub(" ", text)
    for m in BARE_URL.finditer(rest):
        if m.group(1).lower() in BARE_TLDS:
            urls.append(m.group(0).rstrip(".,;:!?)]}"))
    seen, out = set(), []
    for u in urls:
        if u.lower() not in seen:
            seen.add(u.lower())
            out.append(u)
    return out


def _impersonated_brand(host, reg):
    """Return (brand, reason) if the host imitates a brand it doesn't belong to."""
    if reg in ALL_OFFICIAL:
        return None
    tokens = [t for t in re.split(r"[.-]", host) if t]
    name_tokens = [t for t in re.split(r"[.-]", reg.split(".")[0]) if t]
    for brand in OFFICIAL_DOMAINS:
        if any(t == brand for t in tokens) or (len(brand) >= 5 and brand in host):
            return brand, (f"Uses the name '{brand_name(brand)}' but is NOT an official {brand_name(brand)} "
                           f"website (real one: {OFFICIAL_DOMAINS[brand][0]}).")
    for tok in name_tokens + [reg.split(".")[0].replace("-", "")]:
        norm = tok.translate(LOOKALIKE_DIGITS).replace("rn", "m").replace("vv", "w")
        for brand in OFFICIAL_DOMAINS:
            if len(brand) < 5:
                continue
            if norm == brand and tok != brand:
                return brand, (f"Swaps letters for look-alike characters to imitate {brand_name(brand)} "
                               f"('{tok}' looks like '{brand}').")
            limit = 2 if len(brand) >= 7 else 1
            if 0 < levenshtein(tok, brand) <= limit and abs(len(tok) - len(brand)) <= limit:
                return brand, (f"Misspells '{brand_name(brand)}' ('{tok}') - a trick called typo-squatting.")
    return None


def analyze_url(raw):
    reasons, score = [], 0
    url = raw if re.match(r"^[a-z]+://", raw, re.I) else "http://" + raw
    url = re.sub(r"^hxxp", "http", url, flags=re.I)
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if not host:
        return {"url": raw, "host": "", "score": 0, "reasons": [], "official": None}
    reg = registrable_domain(host)

    def add(points, reason):
        nonlocal score
        score += points
        reasons.append(reason)

    if host in SCAM_DOMAINS or reg in SCAM_DOMAINS:
        add(100, "This website is on Guardian Shield's list of known scam / fake-support sites.")
    if "@" in parsed.netloc:
        add(35, "Contains an '@' symbol that hides the real website address.")
    if IPV4.match(host):
        add(45, "Uses a raw number address (IP) instead of a normal website name - legitimate companies don't.")
    if "xn--" in host:
        add(40, "Uses a disguised international address (punycode) that can imitate real websites.")
    if any(ord(c) > 127 for c in host):
        add(40, "Contains special look-alike letters from other alphabets.")
        host_ascii = host.translate(CONFUSABLES)
        if registrable_domain(host_ascii) in ALL_OFFICIAL:
            add(30, f"It is disguised to look exactly like {registrable_domain(host_ascii)}.")
    official = ALL_OFFICIAL.get(reg)
    imp = None if IPV4.match(host) else _impersonated_brand(host.translate(CONFUSABLES), reg)
    if imp:
        add(50, imp[1])
    tld = host.rsplit(".", 1)[-1]
    if tld in SUSPICIOUS_TLDS and not official:
        add(20, f"Ends in '.{tld}', a domain ending frequently used by scam sites.")
    if host in SHORTENERS or reg in SHORTENERS:
        add(20, "Is a shortened link that hides where it really goes.")
    if host.count(".") >= 3 and not official:
        add(10, "Has an unusually long chain of sub-addresses.")
    if host.count("-") >= 2 and not official:
        add(10, "Has many hyphens - common in fake 'support' and 'alert' sites.")
    if not official:
        hits = [w for w in SENSITIVE_WORDS if w in url.lower()]
        if hits:
            add(10, f"Contains words like '{hits[0]}' that scam sites use to look official.")
    if parsed.scheme == "http" and raw.lower().startswith("http://") and not official:
        add(5, "Is not secure (no https).")
    return {"url": raw, "host": host, "score": score, "reasons": reasons,
            "official": brand_name(official) if official and not reasons else None}


def check(text):
    text = (text or "").strip()
    if not text:
        return {"verdict": "safe", "score": 0, "reasons": ["Nothing to check - paste a link or message."], "urls": []}
    urls = [analyze_url(u) for u in extract_urls(text)]
    reasons, score = [], 0
    for u in urls:
        score = max(score, u["score"])
        reasons += [f"{u['host']}: {r}" for r in u["reasons"]]
    text_score, low = 0, text.lower()
    for pattern, reason, pts in TEXT_RULES:
        if re.search(pattern, low):
            text_score += pts
            reasons.append(reason)
    if TOLL_FREE.search(text):
        text_score += 15
        reasons.append("Contains a toll-free phone number. Real virus warnings never show a number to call.")
    score += min(text_score, 60)
    verdict = "dangerous" if score >= 60 else "suspicious" if score >= 25 else "safe"
    if not reasons:
        officials = [u["official"] for u in urls if u["official"]]
        if officials:
            reasons.append(f"This is an official {officials[0]} website.")
        reasons.append("No warning signs found. Still - if in doubt, don't click, and never call numbers from pop-ups.")
    return {"verdict": verdict, "score": min(score, 100), "reasons": reasons,
            "urls": [{"url": u["url"], "host": u["host"], "score": min(u["score"], 100)} for u in urls]}
