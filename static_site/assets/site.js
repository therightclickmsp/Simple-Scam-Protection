/* Simple Scam Protection website - interactions (no frameworks, no tracking). */
(function () {
  "use strict";
  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => Array.from(el.querySelectorAll(sel));

  function h(tag, attrs = {}, children = []) {
    const el = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => (k === "text" ? (el.textContent = v) : el.setAttribute(k, v)));
    [].concat(children).forEach((c) => el.append(c));
    return el;
  }

  function icon(name, cls) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", "ico " + cls);
    const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
    use.setAttribute("href", "#i-" + name);
    svg.append(use);
    return svg;
  }

  let toastTimer;
  function toast(msg) {
    const t = $("#toast");
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove("show"), 2200);
  }

  function copy(text, msg) {
    const done = () => toast(msg);
    if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, done);
    else done();
  }

  // Version + year
  $$("[data-version]").forEach((el) => (el.textContent = window.SSP_RULES.version.split(".").slice(0, 2).join(".")));
  $("#year").textContent = new Date().getFullYear();

  // Mobile menu
  const menuBtn = $("#menu-btn");
  const menu = $("#mobile-menu");
  menuBtn.addEventListener("click", () => {
    const open = menu.classList.toggle("hidden") === false;
    menuBtn.setAttribute("aria-expanded", String(open));
  });
  $$("a", menu).forEach((a) => a.addEventListener("click", () => menu.classList.add("hidden")));

  // Tools marquee
  const tools = window.SSP_RULES.remote_tools;
  $("#tools-marquee").append(...tools.concat(tools).map((t) => h("span", { class: "font-mono-gs whitespace-nowrap text-sm text-slate-300", text: t })));

  // Link checker
  const STYLES = {
    safe: { icon: "shield-check", label: "Looks safe", box: "border-emerald-300 bg-emerald-50", ink: "text-emerald-700", dot: "bg-emerald-700" },
    suspicious: { icon: "shield-alert", label: "Suspicious - be careful", box: "border-amber-300 bg-amber-50", ink: "text-amber-700", dot: "bg-amber-700" },
    dangerous: { icon: "shield-x", label: "Dangerous - do not click", box: "border-red-300 bg-red-50", ink: "text-red-700", dot: "bg-red-700" },
  };
  const input = $("#checker-input");

  function showResult(result) {
    const s = STYLES[result.verdict];
    const copyBtn = h("button", { type: "button", "data-testid": "link-checker-copy-button", class: "inline-flex items-center gap-1.5 rounded-full bg-white px-3 py-1 text-sm font-semibold text-slate-700 hover:bg-slate-100" }, [icon("copy", "h-4 w-4"), " Copy"]);
    copyBtn.addEventListener("click", () => copy(`Simple Scam Protection says: ${s.label.toUpperCase()}\n- ${result.reasons.join("\n- ")}`, "Result copied - share it with family"));
    const card = h("div", { "data-testid": "link-checker-verdict-card", class: `rise rounded-2xl border-2 p-6 md:p-8 ${s.box}` }, [
      h("div", { class: "flex flex-wrap items-center justify-between gap-4" }, [
        h("div", { class: `flex items-center gap-3 ${s.ink}` }, [
          icon(s.icon, "h-10 w-10"),
          h("p", { "data-testid": "link-checker-verdict", class: "font-display text-2xl font-extrabold sm:text-3xl", text: s.label }),
        ]),
        h("div", { class: "flex items-center gap-3" }, [
          h("span", { "data-testid": "link-checker-score", class: "font-mono-gs rounded-full bg-white px-3 py-1 text-sm font-semibold text-slate-700", text: `risk ${result.score}/100` }),
          copyBtn,
        ]),
      ]),
      h("ul", { class: "mt-5 space-y-2.5", "data-testid": "link-checker-reasons" }, result.reasons.map((r) =>
        h("li", { class: "flex gap-3 text-base leading-relaxed text-slate-800 md:text-lg" }, [
          h("span", { class: `mt-2.5 h-2 w-2 shrink-0 rounded-full ${s.dot}` }),
          h("span", { class: "min-w-0 [overflow-wrap:anywhere]", text: r }),
        ]))),
    ]);
    $("#verdict").replaceChildren(card);
  }

  function run(text) {
    if (!text.trim()) return toast("Paste a link or message first");
    showResult(window.SSPLinkCheck.check(text));
  }

  $("#checker-form").addEventListener("submit", (e) => { e.preventDefault(); run(input.value); });
  input.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) run(input.value); });
  $$(".preset").forEach((b) => b.addEventListener("click", () => { input.value = b.dataset.text; run(b.dataset.text); }));

  // Full-screen warning preview
  const SCENARIOS = {
    remote: { bg: "bg-red-600", title: "Someone may be trying to control your computer", text: "AnyDesk just tried to start, and Simple Scam Protection closed it. If a caller, pop-up or message asked you to install or open it, it is a SCAM. Hang up the phone now. Microsoft, Apple, your bank and the government never call you to fix your computer." },
    popup: { bg: "bg-red-600", title: "That was a FAKE virus warning", text: "A web page pretending to be a Microsoft security alert appeared, and Simple Scam Protection closed it. Your computer is NOT locked or infected. Do NOT call the number it showed. When you reopen your browser, don't click 'Restore pages'." },
    command: { bg: "bg-amber-600", title: "If someone on the phone asked you to open this, it's a scam", text: "Event Viewer was just opened. It is full of normal warnings that every computer has. Scammers show it to make you think your PC is broken or hacked. It is not. Hang up and don't give anyone money or access." },
  };
  let overlay = null;

  function showWarning(kind) {
    if (overlay) overlay.remove();
    const s = SCENARIOS[kind];
    let n = 3;
    const btn = h("button", { type: "button", "data-testid": "warning-overlay-close-button", disabled: "", class: "mt-10 rounded-2xl bg-white px-8 py-4 text-lg font-bold text-slate-900 transition-opacity disabled:opacity-60", text: `Please read the message (${n})` });
    overlay = h("div", { "data-testid": "warning-overlay", role: "alertdialog", "aria-modal": "true", class: `fixed inset-0 z-[100] grid place-items-center overflow-y-auto p-6 text-center text-white ${s.bg}` }, [
      h("div", { class: "rise max-w-3xl" }, [
        h("p", { class: "flex items-center justify-center gap-3 text-2xl font-extrabold tracking-widest" }, [icon("alert", "h-8 w-8"), " STOP"]),
        h("h3", { class: "font-display mt-5 text-3xl font-extrabold sm:text-5xl", text: s.title }),
        h("p", { class: "mt-6 text-lg leading-relaxed text-white/95 sm:text-xl", text: s.text }),
        btn,
        h("p", { class: "mt-6 text-sm text-white/70", text: "This is a preview of the Windows app's full-screen warning." }),
      ]),
    ]);
    const timer = setInterval(() => {
      n -= 1;
      if (n > 0) { btn.textContent = `Please read the message (${n})`; return; }
      clearInterval(timer);
      btn.disabled = false;
      btn.textContent = "I understand";
      btn.focus();
    }, 1000);
    btn.addEventListener("click", () => { overlay.remove(); overlay = null; document.body.style.overflow = ""; });
    document.body.style.overflow = "hidden";
    document.body.append(overlay);
  }
  $$("[data-warning]").forEach((b) => b.addEventListener("click", () => showWarning(b.dataset.warning)));

  // Install tabs
  $$(".tab").forEach((tab) => tab.addEventListener("click", () => {
    $$(".tab").forEach((t) => { t.classList.toggle("is-active", t === tab); t.setAttribute("aria-selected", String(t === tab)); });
    $$(".tab-panel").forEach((p) => p.classList.toggle("hidden", p.dataset.panel !== tab.dataset.tab));
  }));

  // Copy buttons for commands
  $$(".copy-btn").forEach((b) => b.addEventListener("click", () => copy($("code", b.parentElement).textContent, "Command copied")));
})();
