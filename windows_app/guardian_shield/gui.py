"""Guardian Shield desktop window, warnings and tray icon (tkinter + pystray)."""
import queue
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from . import APP_NAME, __version__, autostart, hosts, scanner
from .linkcheck import check
from .monitor import ProcessMonitor
from .signatures import REMOTE_TOOLS, TOOLS_BY_ID
from .storage import Store

BG, CARD, INK, MUTED = "#F8FAFC", "#FFFFFF", "#0F172A", "#475569"
GREEN, GREEN_L, RED, RED_L, AMBER, AMBER_L, BLUE = ("#059669", "#D1FAE5", "#DC2626", "#FEE2E2",
                                                    "#D97706", "#FEF3C7", "#2563EB")
FONT = "Segoe UI"
TRUST_PHRASE = "I TRUST THIS TOOL"


def font(size=13, weight="normal"):
    return (FONT, size, weight)


class GuardianApp:
    def __init__(self, start_minimized=False):
        self.store = Store()
        self.events = queue.Queue()
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} {__version__}")
        self.root.geometry("980x680")
        self.root.minsize(860, 600)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.hide)
        self._style()
        self.pages = {}
        self._layout()
        self.monitor = ProcessMonitor(self.store, lambda d: self.events.put(("monitor", d)))
        self.monitor.start()
        self.tray = None
        self._start_tray()
        if self.store.settings["autostart"]:
            autostart.set_autostart(True)
        if start_minimized:
            self.root.withdraw()
        if not self.store.settings["first_run_done"]:
            self.root.after(800, self.first_run)
        self.root.after(300, self._poll)

    # ---------- layout ----------
    def _style(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Treeview", font=font(11), rowheight=30)
        s.configure("Treeview.Heading", font=font(11, "bold"))

    def _layout(self):
        side = tk.Frame(self.root, bg=INK, width=230)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Label(side, text="Guardian\nShield", bg=INK, fg="white", font=font(20, "bold"), justify="left").pack(
            anchor="w", padx=24, pady=(28, 30))
        self.body = tk.Frame(self.root, bg=BG)
        self.body.pack(side="left", fill="both", expand=True)
        self.nav = {}
        for key, label, cls in [("status", "Status", StatusPage), ("links", "Check a Link", LinkPage),
                                ("log", "Activity Log", LogPage), ("settings", "Settings & Trusted", SettingsPage)]:
            b = tk.Button(side, text=label, anchor="w", relief="flat", bd=0, padx=24, pady=14, font=font(13, "bold"),
                          bg=INK, fg="#CBD5E1", activebackground="#1E293B", activeforeground="white",
                          cursor="hand2", command=lambda k=key: self.show_page(k))
            b.pack(fill="x")
            self.nav[key] = b
            self.pages[key] = cls(self.body, self)
        tk.Label(side, text="Free • Your data stays\non this PC", bg=INK, fg="#64748B", font=font(10),
                 justify="left").pack(side="bottom", anchor="w", padx=24, pady=20)
        self.show_page("status")

    def show_page(self, key):
        for k, p in self.pages.items():
            p.pack_forget()
            self.nav[k].configure(bg=INK, fg="#CBD5E1")
        self.pages[key].pack(fill="both", expand=True, padx=36, pady=30)
        self.pages[key].refresh()
        self.nav[key].configure(bg="#1E293B", fg="white")

    # ---------- window / tray ----------
    def show(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide(self):
        if self.tray:
            self.root.withdraw()
        else:
            self.quit()

    def quit(self):
        self.monitor.stop()
        if self.tray:
            self.tray.stop()
        self.root.destroy()

    def _start_tray(self):
        try:
            import pystray
            from PIL import Image, ImageDraw
        except ImportError:
            return
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.polygon([(32, 4), (58, 14), (54, 42), (32, 60), (10, 42), (6, 14)], fill=GREEN)
        d.line([(20, 32), (29, 41), (45, 23)], fill="white", width=6)
        menu = pystray.Menu(
            pystray.MenuItem("Open Guardian Shield", lambda: self.events.put(("show", None)), default=True),
            pystray.MenuItem("Scan for remote-access tools", lambda: self.events.put(("scan", None))),
            pystray.MenuItem("Quit", lambda: self.events.put(("quit", None))))
        self.tray = pystray.Icon("GuardianShield", img, f"{APP_NAME} - Protected", menu)
        self.tray.run_detached()

    def notify(self, title, msg):
        if self.tray:
            try:
                self.tray.notify(msg, title)
            except Exception:
                pass

    # ---------- events ----------
    def _poll(self):
        try:
            while True:
                kind, data = self.events.get_nowait()
                if kind == "show":
                    self.show()
                elif kind == "scan":
                    self.show()
                    self.show_page("status")
                    self.pages["status"].scan()
                elif kind == "quit":
                    self.quit()
                    return
                elif kind == "monitor":
                    self.handle_monitor(data)
        except queue.Empty:
            pass
        self.root.after(300, self._poll)

    def handle_monitor(self, d):
        if d["type"] == "remote_block":
            t = d["tool"]
            self.store.add_event("blocked", f"Blocked {t['name']}", "A remote-access tool started and was closed.")
            WarningScreen(self.root, "Someone may be trying to control your computer",
                          f"{t['name']} just tried to start, and Guardian Shield closed it.\n\n"
                          "If a caller, pop-up or message asked you to install or open it, it is a SCAM.\n"
                          "Hang up the phone now. Microsoft, Apple, your bank and the government never call "
                          "you to fix your computer.")
        elif d["type"] == "remote_seen":
            self.store.add_event("flagged", f"{d['tool']['name']} is running", "Remote-access blocking is turned off.")
            self.notify("Remote-access tool running", f"{d['tool']['name']} is running on this PC.")
        elif d["type"] == "remote_trusted":
            self.store.add_event("info", f"{d['tool']['name']} allowed", "This tool is on your trusted list.")
        elif d["type"] == "command":
            c = d["command"]
            self.store.add_event("warned", f"{c['name']} opened", c["message"])
            WarningScreen(self.root, "If someone on the phone asked you to open this, it's a scam",
                          f"{c['name']} was just opened.\n\n{c['message']}\n\n"
                          "Hang up and do not give anyone money, card numbers or access to your computer.",
                          color=AMBER)
        for p in self.pages.values():
            p.refresh()

    def first_run(self):
        self.store.set("first_run_done", True)
        self.show()
        self.show_page("status")
        self.pages["status"].scan()

    def protected(self):
        s = self.store.settings
        return s["remote_block"] and s["command_warn"]

    def run(self):
        self.root.mainloop()


class WarningScreen(tk.Toplevel):
    def __init__(self, master, title, text, color=RED):
        super().__init__(master)
        self.configure(bg=color)
        self.attributes("-topmost", True)
        try:
            self.attributes("-fullscreen", True)
        except tk.TclError:
            self.geometry("1000x700")
        wrap = tk.Frame(self, bg=color)
        wrap.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(wrap, text="⚠  STOP", bg=color, fg="white", font=font(28, "bold")).pack(pady=(0, 10))
        tk.Label(wrap, text=title, bg=color, fg="white", font=font(30, "bold"), wraplength=1000).pack(pady=10)
        tk.Label(wrap, text=text, bg=color, fg="white", font=font(17), wraplength=900, justify="center").pack(pady=20)
        self.btn = tk.Button(wrap, text="Please read the message (3)", font=font(16, "bold"), state="disabled",
                             bg="white", fg=color, relief="flat", padx=30, pady=12, command=self.destroy)
        self.btn.pack(pady=20)
        self._count(3)
        self.bell()

    def _count(self, n):
        if n <= 0:
            self.btn.configure(text="I understand", state="normal", cursor="hand2")
            return
        self.btn.configure(text=f"Please read the message ({n})")
        self.after(1000, self._count, n - 1)


class Page(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=BG)
        self.app = app
        self.build()

    def build(self):
        pass

    def refresh(self):
        pass

    def title(self, text, sub=""):
        tk.Label(self, text=text, bg=BG, fg=INK, font=font(24, "bold")).pack(anchor="w")
        if sub:
            tk.Label(self, text=sub, bg=BG, fg=MUTED, font=font(12), wraplength=680, justify="left").pack(
                anchor="w", pady=(4, 18))

    def card(self, parent=None, **kw):
        f = tk.Frame(parent or self, bg=CARD, highlightbackground="#E2E8F0", highlightthickness=1, **kw)
        return f


def big_button(parent, text, cmd, color=GREEN):
    return tk.Button(parent, text=text, command=cmd, bg=color, fg="white", activebackground=color,
                     activeforeground="white", font=font(13, "bold"), relief="flat", padx=22, pady=10, cursor="hand2")


class StatusPage(Page):
    def build(self):
        self.banner = tk.Frame(self, bg=GREEN_L)
        self.banner.pack(fill="x")
        self.banner_title = tk.Label(self.banner, font=font(26, "bold"), bg=GREEN_L)
        self.banner_title.pack(anchor="w", padx=28, pady=(22, 2))
        self.banner_sub = tk.Label(self.banner, font=font(12), bg=GREEN_L, fg=MUTED)
        self.banner_sub.pack(anchor="w", padx=28, pady=(0, 22))
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", pady=18)
        self.vars = {}
        for key, label in [("remote_block", "Block remote-access tools"),
                           ("command_warn", "Warn about scammer tricks"),
                           ("site_block", "Block scam websites")]:
            c = self.card(row)
            c.pack(side="left", expand=True, fill="both", padx=(0, 12))
            v = tk.BooleanVar(value=self.app.store.settings[key])
            self.vars[key] = v
            tk.Checkbutton(c, text=label, variable=v, font=font(12, "bold"), bg=CARD, fg=INK, activebackground=CARD,
                           command=lambda k=key: self.toggle(k), cursor="hand2").pack(anchor="w", padx=14, pady=16)
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=(6, 8))
        tk.Label(top, text="Remote-access tools on this PC", bg=BG, fg=INK, font=font(16, "bold")).pack(side="left")
        big_button(top, "Scan now", self.scan, BLUE).pack(side="right")
        self.results = self.card()
        self.results.pack(fill="both", expand=True)
        self.findings = []

    def refresh(self):
        ok = self.app.protected()
        bg = GREEN_L if ok else RED_L
        for w in (self.banner, self.banner_title, self.banner_sub):
            w.configure(bg=bg)
        self.banner_title.configure(text="✔  You are Protected" if ok else "✖  Protection is partly OFF",
                                    fg=GREEN if ok else RED)
        self.banner_sub.configure(text="Guardian Shield is watching for remote-access tools and scammer tricks."
                                  if ok else "Turn the protections below back on to stay safe.")
        for k, v in self.vars.items():
            v.set(self.app.store.settings[k])

    def toggle(self, key):
        value = self.vars[key].get()
        if key == "site_block":
            if not hosts.set_blocking(value):
                messagebox.showerror(APP_NAME, "Windows didn't give permission to change website blocking.")
                self.vars[key].set(not value)
                return
        if not value and key != "site_block":
            if not messagebox.askyesno(APP_NAME, "Turning this off makes you easier to scam.\n\n"
                                                 "If someone on the phone told you to do this, hang up.\n\n"
                                                 "Turn it off anyway?"):
                self.vars[key].set(True)
                return
        self.app.store.set(key, value)
        self.app.store.add_event("info", f"{'Turned on' if value else 'Turned off'}: {key.replace('_', ' ')}")
        self.app.tray and setattr(self.app.tray, "title",
                                  f"{APP_NAME} - {'Protected' if self.app.protected() else 'NOT fully protected'}")
        self.refresh()

    def scan(self):
        for w in self.results.winfo_children():
            w.destroy()
        tk.Label(self.results, text="Scanning…", bg=CARD, font=font(13), fg=MUTED).pack(padx=20, pady=20, anchor="w")

        def work():
            found = [f for f in scanner.full_scan() if not self.app.store.is_trusted(f["tool_id"])]
            self.after(0, self.show_results, found)
        threading.Thread(target=work, daemon=True).start()

    def show_results(self, found):
        self.findings = found
        for w in self.results.winfo_children():
            w.destroy()
        self.app.store.add_event("scan", "Scan finished", f"{len(found)} remote-access item(s) found.")
        if not found:
            tk.Label(self.results, text="✔  No remote-access tools found. Nice!", bg=CARD, fg=GREEN,
                     font=font(14, "bold")).pack(padx=20, pady=24, anchor="w")
            return
        tk.Label(self.results, text=f"Found {len(found)} item(s). If you did not install these yourself, remove them.",
                 bg=CARD, fg=RED, font=font(13, "bold")).pack(padx=20, pady=(16, 8), anchor="w")
        for f in found:
            r = tk.Frame(self.results, bg=CARD)
            r.pack(fill="x", padx=20, pady=4)
            tk.Label(r, text=f"{f['name']}  •  {f['kind']}", bg=CARD, fg=INK, font=font(12, "bold")).pack(side="left")
            tk.Label(r, text=f.get("path", "")[:60], bg=CARD, fg=MUTED, font=font(10)).pack(side="left", padx=10)
            big_button(r, "Remove", lambda x=f: self.remove(x), RED).pack(side="right")

    def remove(self, finding):
        msg = scanner.remove(finding, self.app.store.dir / "quarantine")
        self.app.store.add_event("removed", f"Removed {finding['name']}", msg)
        messagebox.showinfo(APP_NAME, msg)
        self.scan()


class LinkPage(Page):
    def build(self):
        self.title("Check a link or message", "Paste a web link, text message or email. Guardian Shield checks it "
                                              "for scam warning signs. Nothing is sent anywhere.")
        c = self.card()
        c.pack(fill="x")
        self.text = tk.Text(c, height=6, font=font(13), relief="flat", wrap="word", bg=CARD, fg=INK)
        self.text.pack(fill="x", padx=14, pady=14)
        btns = tk.Frame(self, bg=BG)
        btns.pack(fill="x", pady=12)
        big_button(btns, "Check it", self.run_check).pack(side="left")
        tk.Button(btns, text="Clear", font=font(12), relief="flat", bg=BG, fg=MUTED, cursor="hand2",
                  command=lambda: (self.text.delete("1.0", "end"), self.show(None))).pack(side="left", padx=10)
        self.result = tk.Frame(self, bg=BG)
        self.result.pack(fill="both", expand=True)

    def run_check(self):
        text = self.text.get("1.0", "end").strip()
        res = check(text)
        if res["verdict"] != "safe":
            self.app.store.add_event("flagged", f"Link check: {res['verdict'].upper()}", text[:120])
        self.show(res)

    def show(self, res):
        for w in self.result.winfo_children():
            w.destroy()
        if not res:
            return
        color, light, label = {"safe": (GREEN, GREEN_L, "✔  Looks Safe"),
                               "suspicious": (AMBER, AMBER_L, "⚠  Suspicious - be careful"),
                               "dangerous": (RED, RED_L, "✖  Dangerous - do NOT click")}[res["verdict"]]
        box = tk.Frame(self.result, bg=light)
        box.pack(fill="both", expand=True)
        tk.Label(box, text=label, bg=light, fg=color, font=font(22, "bold")).pack(anchor="w", padx=22, pady=(18, 8))
        for r in res["reasons"]:
            tk.Label(box, text="•  " + r, bg=light, fg=INK, font=font(12), wraplength=640, justify="left").pack(
                anchor="w", padx=22, pady=3)


class LogPage(Page):
    def build(self):
        self.title("Activity Log", "Everything Guardian Shield blocked, warned about or checked. Stored only on this PC.")
        self.tree = ttk.Treeview(self, columns=("time", "kind", "title", "detail"), show="headings")
        for col, w in [("time", 160), ("kind", 90), ("title", 220), ("detail", 360)]:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True)
        tk.Button(self, text="Clear log", font=font(12), relief="flat", bg=BG, fg=MUTED, cursor="hand2",
                  command=self.clear).pack(anchor="e", pady=10)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for e in self.app.store.log:
            self.tree.insert("", "end", values=(e["time"], e["kind"], e["title"], e["detail"]))

    def clear(self):
        if messagebox.askyesno(APP_NAME, "Clear the whole activity log?"):
            self.app.store.clear_log()
            self.refresh()


class SettingsPage(Page):
    def build(self):
        self.title("Trusted tools & settings",
                   "Only trust a remote-access tool if YOU chose it, e.g. for your work's IT department. "
                   "Never trust a tool because a caller asked you to.")
        self.list = tk.Listbox(self, font=font(13), height=10, activestyle="none", relief="flat",
                               highlightthickness=1, highlightbackground="#E2E8F0", selectbackground=BLUE)
        self.list.pack(fill="both", expand=True)
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", pady=12)
        big_button(row, "Trust selected tool", self.trust, AMBER).pack(side="left")
        big_button(row, "Stop trusting", self.untrust, INK).pack(side="left", padx=10)
        self.auto = tk.BooleanVar(value=self.app.store.settings["autostart"])
        tk.Checkbutton(self, text="Start Guardian Shield when Windows starts", variable=self.auto, bg=BG,
                       font=font(12), command=self.set_auto).pack(anchor="w", pady=(10, 0))

    def refresh(self):
        self.list.delete(0, "end")
        for t in REMOTE_TOOLS:
            mark = "✔ TRUSTED   " if self.app.store.is_trusted(t["id"]) else "                     "
            self.list.insert("end", f"{mark}{t['name']}")

    def _selected(self):
        sel = self.list.curselection()
        return REMOTE_TOOLS[sel[0]] if sel else None

    def trust(self):
        tool = self._selected()
        if not tool:
            return
        if TrustDialog(self, tool["name"]).ok:
            allow = self.app.store.settings["allowlist"] + [tool["id"]]
            self.app.store.set("allowlist", sorted(set(allow)))
            self.app.store.add_event("info", f"Trusted {tool['name']}", "Added to the trusted list.")
            self.refresh()

    def untrust(self):
        tool = self._selected()
        if tool and self.app.store.is_trusted(tool["id"]):
            self.app.store.set("allowlist", [i for i in self.app.store.settings["allowlist"] if i != tool["id"]])
            self.app.store.add_event("info", f"Stopped trusting {TOOLS_BY_ID[tool['id']]['name']}")
            self.refresh()

    def set_auto(self):
        self.app.store.set("autostart", self.auto.get())
        autostart.set_autostart(self.auto.get())


class TrustDialog(tk.Toplevel):
    """Typed confirmation to slow down a scammer coaching the user."""

    def __init__(self, master, tool_name):
        super().__init__(master)
        self.ok = False
        self.title("Are you sure?")
        self.configure(bg=AMBER_L, padx=30, pady=24)
        self.transient(master)
        self.grab_set()
        tk.Label(self, text=f"Trust {tool_name}?", bg=AMBER_L, fg=INK, font=font(18, "bold")).pack(anchor="w")
        tk.Label(self, text="Is someone on the phone telling you to do this? If yes, STOP and hang up.\n\n"
                            f"To continue, type:  {TRUST_PHRASE}", bg=AMBER_L, fg=INK, font=font(12),
                 justify="left").pack(anchor="w", pady=12)
        self.entry = tk.Entry(self, font=font(14), width=28)
        self.entry.pack(anchor="w")
        row = tk.Frame(self, bg=AMBER_L)
        row.pack(fill="x", pady=(16, 0))
        big_button(row, "Confirm", self.confirm, AMBER).pack(side="left")
        tk.Button(row, text="Cancel", font=font(12), relief="flat", bg=AMBER_L, command=self.destroy).pack(
            side="left", padx=10)
        self.wait_window()

    def confirm(self):
        if self.entry.get().strip().upper() == TRUST_PHRASE:
            self.ok = True
            self.destroy()
        else:
            messagebox.showwarning(APP_NAME, f"Please type exactly: {TRUST_PHRASE}", parent=self)


if __name__ == "__main__":
    GuardianApp("--minimized" in sys.argv).run()
