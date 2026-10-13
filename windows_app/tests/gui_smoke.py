"""Smoke test the tkinter GUI under a virtual display (run with xvfb-run)."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
tmp = tempfile.mkdtemp()
os.environ["GUARDIAN_SHIELD_HOME"] = tmp
os.environ["GUARDIAN_SHIELD_POLICY"] = os.path.join(tmp, "policy.json")

from guardian_shield import auth, gui  # noqa: E402
from guardian_shield.signatures import TOOLS_BY_ID, SCAM_COMMANDS  # noqa: E402

auth.ITERATIONS = 1000
gui.WarningScreen._count = lambda self, n: self.btn.configure(state="normal")
app = gui.GuardianApp(start_minimized=False)
app.store.set("first_run_done", True)
steps = []


def run():
    for page in ["status", "links", "log", "settings", "status"]:
        app.show_page(page)
        app.root.update()
    lp = app.pages["links"]
    lp.text.insert("1.0", "Your PC is infected! call 1-888-555-0101")
    lp.run_check()
    app.handle_monitor({"type": "remote_block", "tool": TOOLS_BY_ID["anydesk"]})
    app.handle_monitor({"type": "command", "command": SCAM_COMMANDS[0]})
    app.handle_monitor({"type": "popup", "title": "Your PC is locked", "browser": "chrome.exe", "action": "tab"})
    app.root.update()
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
