"""Smoke test the tkinter GUI under a virtual display (run with xvfb-run)."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
tmp = tempfile.mkdtemp()
os.environ["SIMPLE_SCAM_PROTECTION_HOME"] = tmp
os.environ["SIMPLE_SCAM_PROTECTION_POLICY"] = os.path.join(tmp, "policy.json")

from simple_scam_protection import auth, gui  # noqa: E402
from simple_scam_protection.signatures import TOOLS_BY_ID, SCAM_COMMANDS  # noqa: E402

auth.ITERATIONS = 1000
gui.WarningScreen._count = lambda self, n: (setattr(self, "ready", True), self.btn.configure(state="normal"))
app = gui.ScamProtectionApp(start_minimized=False)
app.store.set("first_run_done", True)
steps = []


def run():
    for page in ["status", "links", "log", "settings", "status"]:
        app.show_page(page)
        app.root.update()
    lp = app.pages["links"]
    lp.text.insert("1.0", "Your PC is infected! call 1-888-555-0101")
    lp.run_check()
    for _ in range(6):  # AnyDesk starting several processes at once
        app.handle_monitor({"type": "remote_block", "tool": TOOLS_BY_ID["anydesk"]})
    app.handle_monitor({"type": "command", "command": SCAM_COMMANDS[0]})
    app.handle_monitor({"type": "popup", "title": "Your PC is locked", "browser": "chrome.exe", "action": "tab"})
    app.root.update()
    warnings = [w for w in app.root.winfo_children() if isinstance(w, gui.WarningScreen)]
    assert len(warnings) == 1, f"expected 1 warning window, got {len(warnings)}"
    assert "FAKE" in warnings[0].title_lbl.cget("text")
    assert sum(1 for e in app.store.log if e["title"] == "Blocked AnyDesk") == 1
    warnings[0].btn.invoke()
    app.root.update()
    assert not [w for w in app.root.winfo_children() if isinstance(w, gui.WarningScreen)], "one click should close"
    assert app.store.is_trusted("quickassist")
    sp = app.pages["status"]
    sp.show_results([{"tool_id": "anydesk", "name": f"AnyDesk {i}", "kind": "file", "path": "C:/x.exe"} for i in range(30)])
    app.root.update()
    assert sp.results.canvas.bbox("all")[3] > sp.results.canvas.winfo_height(), "results should be scrollable"
    sp.results.canvas.yview_moveto(1.0)
    app.root.update()
    assert sp.results.canvas.yview()[0] > 0, "scrolling should move the list"
    assert any("coffee" in str(w.cget("text")).lower() for w in app.root.winfo_children()[0].winfo_children()
               if isinstance(w, gui.tk.Button))
    app.guard.set("blue-garden-teapot")
    app.pages["settings"].refresh()
    app.root.update()
    assert len(app.store.log) >= 4, app.store.log
    assert app.guard.is_set()
    steps.append("ok")
    app.monitor.stop()
    app.popups.stop()
    app.root.destroy()


app.root.after(500, run)
app.root.mainloop()
print("GUI SMOKE", "PASS" if steps else "FAIL")
sys.exit(0 if steps else 1)
