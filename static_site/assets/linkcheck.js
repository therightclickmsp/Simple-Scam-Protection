/* Simple Scam Protection link checker - runs fully in the browser (same rules as the Windows app). */
(function (root) {
  "use strict";
  const R = root.SSP_RULES;
  const ALL_OFFICIAL = {};
  Object.entries(R.official).forEach(([brand, domains]) => domains.forEach((d) => { ALL_OFFICIAL[d] = brand; }));
  const SUSPICIOUS = new Set(R.suspicious_tlds);
  const SHORTENERS = new Set(R.shorteners);
  const MULTI = new Set(R.multi_suffix);
  const BARE_TLDS = new Set(R.bare_tlds);
  const SCAM = new Set(R.scam_domains);
  const TEXT_RULES = R.text_rules.map(([p, reason, pts]) => [new RegExp(p), reason, pts]);
  const TOLL_FREE = new RegExp(R.toll_free);
  const IPV4 = new RegExp(R.ipv4);
  const TRAIL = /[.,;:!?)\]}]+$/;

  const translate = (s, map) => Array.from(s).map((c) => (c in map ? map[c] : c)).join("");
  const count = (s, ch) => s.split(ch).length - 1;
  const brandName = (b) => R.brand_labels[b] || b.charAt(0).toUpperCase() + b.slice(1).toLowerCase();
  const split = (s) => s.split(/[.-]/).filter(Boolean);

  function levenshtein(a, b) {
    a = Array.from(a); b = Array.from(b);
    let prev = Array.from({ length: b.length + 1 }, (_, i) => i);
    a.forEach((ca, i) => {
      const cur = [i + 1];
      b.forEach((cb, j) => cur.push(Math.min(prev[j + 1] + 1, cur[j] + 1, prev[j] + (ca !== cb ? 1 : 0))));
      prev = cur;
    });
    return prev[prev.length - 1];
  }

  function registrable(host) {
    const labels = host.replace(/^\.+|\.+$/g, "").split(".");
    if (labels.length >= 3 && MULTI.has(labels.slice(-2).join("."))) return labels.slice(-3).join(".");
    return labels.slice(-2).join(".");
  }

  function extractUrls(text) {
    const urls = [];
    for (const m of text.matchAll(new RegExp(R.scheme_url, "gi"))) urls.push(m[0].replace(TRAIL, ""));
    const rest = text.replace(new RegExp(R.scheme_url, "gi"), " ");
    for (const m of rest.matchAll(new RegExp(R.bare_url, "gi"))) {
      if (BARE_TLDS.has(m[1].toLowerCase())) urls.push(m[0].replace(TRAIL, ""));
    }
    const seen = new Set();
    return urls.filter((u) => !seen.has(u.toLowerCase()) && seen.add(u.toLowerCase()));
  }

  function parse(url) {
    const m = url.match(/^([^:/?#]+):\/\/([^/?#]*)/);
    if (!m) return { scheme: "", netloc: "", host: "" };
    const netloc = m[2];
    let host = netloc.slice(netloc.lastIndexOf("@") + 1);
    host = host.startsWith("[") ? host.slice(1, host.indexOf("]") + 1 || undefined).replace("]", "") : host.split(":")[0];
    return { scheme: m[1].toLowerCase(), netloc, host: host.toLowerCase() };
  }

  function impersonated(host, reg) {
    if (reg in ALL_OFFICIAL) return null;
    const tokens = split(host);
    const first = reg.split(".")[0];
    for (const brand of Object.keys(R.official)) {
      if (tokens.includes(brand) || (brand.length >= 5 && host.includes(brand))) {
        return `Uses the name '${brandName(brand)}' but is NOT an official ${brandName(brand)} website (real one: ${R.official[brand][0]}).`;
      }
    }
    for (const tok of [...split(first), first.replaceAll("-", "")]) {
      const norm = translate(tok, R.lookalike).replaceAll("rn", "m").replaceAll("vv", "w");
      for (const brand of Object.keys(R.official)) {
        if (brand.length < 5) continue;
        if (norm === brand && tok !== brand) {
          return `Swaps letters for look-alike characters to imitate ${brandName(brand)} ('${tok}' looks like '${brand}').`;
        }
        const limit = brand.length >= 7 ? 2 : 1;
        const d = levenshtein(tok, brand);
        if (d > 0 && d <= limit && Math.abs(Array.from(tok).length - brand.length) <= limit) {
          return `Misspells '${brandName(brand)}' ('${tok}') - a trick called typo-squatting.`;
        }
      }
    }
    return null;
  }

  function analyzeUrl(raw) {
    const reasons = [];
    let score = 0;
    let url = /^[a-z]+:\/\//i.test(raw) ? raw : "http://" + raw;
    url = url.replace(/^hxxp/i, "http");
    const p = parse(url);
    const host = p.host;
    if (!host) return { url: raw, host: "", score: 0, reasons: [], official: null };
    const reg = registrable(host);
    const add = (pts, reason) => { score += pts; reasons.push(reason); };
    const isIp = IPV4.test(host);

    if (SCAM.has(host) || SCAM.has(reg)) add(100, "This website is on Simple Scam Protection's list of known scam / fake-support sites.");
    if (p.netloc.includes("@")) add(35, "Contains an '@' symbol that hides the real website address.");
    if (isIp) add(45, "Uses a raw number address (IP) instead of a normal website name - legitimate companies don't.");
    if (host.includes("xn--")) add(40, "Uses a disguised international address (punycode) that can imitate real websites.");
    if (Array.from(host).some((c) => c.codePointAt(0) > 127)) {
      add(40, "Contains special look-alike letters from other alphabets.");
      const ascii = registrable(translate(host, R.confusables));
      if (ascii in ALL_OFFICIAL) add(30, `It is disguised to look exactly like ${ascii}.`);
    }
    const official = ALL_OFFICIAL[reg] || null;
    const imp = isIp ? null : impersonated(translate(host, R.confusables), reg);
    if (imp) add(50, imp);
    const tld = host.slice(host.lastIndexOf(".") + 1);
    if (SUSPICIOUS.has(tld) && !official) add(20, `Ends in '.${tld}', a domain ending frequently used by scam sites.`);
    if (SHORTENERS.has(host) || SHORTENERS.has(reg)) add(20, "Is a shortened link that hides where it really goes.");
    if (count(host, ".") >= 3 && !official) add(10, "Has an unusually long chain of sub-addresses.");
    if (count(host, "-") >= 2 && !official) add(10, "Has many hyphens - common in fake 'support' and 'alert' sites.");
    if (!official) {
      const hit = R.sensitive_words.find((w) => url.toLowerCase().includes(w));
      if (hit) add(10, `Contains words like '${hit}' that scam sites use to look official.`);
    }
    if (p.scheme === "http" && raw.toLowerCase().startsWith("http://") && !official) add(5, "Is not secure (no https).");
    return { url: raw, host, score, reasons, official: official && !reasons.length ? brandName(official) : null };
  }

  function check(input) {
    const text = (input || "").trim();
    if (!text) return { verdict: "safe", score: 0, reasons: ["Nothing to check - paste a link or message."], urls: [] };
    const urls = extractUrls(text).map(analyzeUrl);
    const reasons = [];
    let score = 0;
    urls.forEach((u) => {
      score = Math.max(score, u.score);
      u.reasons.forEach((r) => reasons.push(`${u.host}: ${r}`));
    });
    let textScore = 0;
    const low = text.toLowerCase();
    const hits = new Set();
    TEXT_RULES.forEach(([re, reason, pts], i) => {
      if (re.test(low)) { hits.add(i); textScore += pts; reasons.push(reason); }
    });
    if (TOLL_FREE.test(text)) {
      hits.add("phone"); textScore += 15;
      reasons.push("Contains a toll-free phone number. Real virus warnings never show a number to call.");
    }
    if (hits.has(0) && (hits.has(2) || hits.has("phone"))) {
      textScore += 20;
      reasons.push("This is the classic fake virus warning used by tech-support scammers.");
    }
    score += Math.min(textScore, 60);
    const verdict = score >= 60 ? "dangerous" : score >= 25 ? "suspicious" : "safe";
    if (!reasons.length) {
      const off = urls.find((u) => u.official);
      if (off) reasons.push(`This is an official ${off.official} website.`);
      reasons.push("No warning signs found. Still - if in doubt, don't click, and never call numbers from pop-ups.");
    }
    return { verdict, score: Math.min(score, 100), reasons,
      urls: urls.map((u) => ({ url: u.url, host: u.host, score: Math.min(u.score, 100) })) };
  }

  root.SSPLinkCheck = { check, extractUrls, analyzeUrl };
})(typeof window !== "undefined" ? window : globalThis);
