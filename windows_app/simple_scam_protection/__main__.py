import argparse
import sys


def apply_msi_properties(args):
    """MSI passes every property as KEY=VALUE (empty when not set on the msiexec command line)."""
    props = dict(item.split("=", 1) for item in args.msi if "=" in item)
    if props.get("ALLOW"):
        args.allow = props["ALLOW"]
    if props.get("PASSWORDHASH"):
        args.password_hash = props["PASSWORDHASH"]
    args.site_block = not props.get("NOSITEBLOCK")
    args.no_popup_block = bool(props.get("NOPOPUPBLOCK"))


def stop_running():
    """Close other running copies (the one-file .exe runs as a parent + child process)."""
    import os
    import psutil
    mine = {os.getpid(), os.getppid()}
    for proc in psutil.process_iter(["pid", "name"]):
        if (proc.info["name"] or "").lower() == "simplescamprotection.exe" and proc.info["pid"] not in mine:
            try:
                proc.kill()
            except psutil.Error:
                pass
    return 0


def uninstall_cleanup():
    """(admin) Used by both uninstallers: remove the hosts-file block and the machine policy."""
    import shutil
    from . import hosts
    from .storage import policy_path
    stop_running()
    try:
        hosts.remove_block()
    except OSError:
        pass
    shutil.rmtree(policy_path().parent, ignore_errors=True)
    return 0


def configure(args):
    """Machine-wide setup used by the installer and RMM tools (run as administrator / SYSTEM)."""
    from . import hosts
    if args.msi is not None:
        apply_msi_properties(args)
    from .signatures import TOOLS_BY_ID
    from .storage import write_policy
    updates, defaults = {}, {}
    if args.password_hash:
        if not args.password_hash.startswith("pbkdf2_sha256$") or args.password_hash.count("$") != 3:
            print("Invalid --password-hash. Create one with: SimpleScamProtection.exe --hash-password", file=sys.stderr)
            return 2
        updates["password_hash"] = args.password_hash
    if args.allow is not None:
        ids = [i.strip().lower() for i in args.allow.split(",") if i.strip()]
        unknown = [i for i in ids if i not in TOOLS_BY_ID]
        if unknown:
            print(f"Unknown tool id(s): {', '.join(unknown)}. Valid: {', '.join(TOOLS_BY_ID)}", file=sys.stderr)
            return 2
        updates["allowlist"] = ids
    if args.site_block is not None:
        defaults["site_block"] = args.site_block
        try:
            hosts.apply_block() if args.site_block else hosts.remove_block()
        except OSError as e:
            print(f"Could not update the hosts file (antivirus may protect it): {e}", file=sys.stderr)
    if args.no_popup_block:
        defaults["popup_block"] = False
    if defaults:
        updates["defaults"] = defaults
    write_policy(updates)
    print("Simple Scam Protection policy updated.")
    return 0


def hash_password():
    """Opens a small window (the .exe has no console) and copies the hash to the clipboard."""
    import tkinter as tk
    from .auth import make_hash
    from .gui import SetPasswordDialog, font

    class Collector:
        value = None

        def set(self, pw):
            self.value = make_hash(pw)

    root = tk.Tk()
    root.title("Simple Scam Protection - password hash for IT deployment")
    collector = Collector()
    root.withdraw()
    if not SetPasswordDialog(root, collector).ok:
        root.destroy()
        return 1
    root.deiconify()
    root.clipboard_clear()
    root.clipboard_append(collector.value)
    tk.Label(root, text="Copied to clipboard. Use it as /PASSWORDHASH=... or --password-hash",
             font=font(12, "bold")).pack(padx=20, pady=(20, 8), anchor="w")
    e = tk.Entry(root, font=("Consolas", 10), width=110)
    e.insert(0, collector.value)
    e.configure(state="readonly")
    e.pack(padx=20, pady=(0, 20))
    print(collector.value)
    root.mainloop()
    return 0


def confirm_uninstall():
    """Shown by the interactive uninstaller. Exit code 0 = allow, 1 = cancel."""
    import tkinter as tk
    from tkinter import messagebox
    from .storage import Store
    from .auth import PasswordGuard
    root = tk.Tk()
    root.withdraw()
    guard = PasswordGuard(Store())
    if guard.is_set():
        from .gui import PasswordDialog
        ok = PasswordDialog(root, guard, "Enter the Simple Scam Protection password to uninstall it.").ok
    else:
        ok = messagebox.askyesno("Simple Scam Protection", "Is someone on the phone asking you to remove Simple Scam Protection?\n\n"
                                 "If YES - click 'No', hang up, it's a scam.\n\nRemove Simple Scam Protection?",
                                 icon="warning")
    root.destroy()
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(prog="SimpleScamProtection")
    p.add_argument("--minimized", action="store_true", help="start hidden in the system tray")
    p.add_argument("--hosts-on", action="store_true", help="(admin) add scam-site block to hosts file")
    p.add_argument("--hosts-off", action="store_true", help="(admin) remove scam-site block")
    p.add_argument("--check", metavar="TEXT", help="check a link/message and print the result")
    p.add_argument("--configure", action="store_true", help="(admin) write machine-wide policy")
    p.add_argument("--password-hash", help="with --configure: settings password hash from --hash-password")
    p.add_argument("--allow", help="with --configure: comma-separated trusted tool ids, e.g. screenconnect")
    p.add_argument("--site-block", dest="site_block", action="store_true", default=None)
    p.add_argument("--no-site-block", dest="site_block", action="store_false")
    p.add_argument("--no-popup-block", action="store_true")
    p.add_argument("--hash-password", action="store_true", help="create a password hash for RMM deployment")
    p.add_argument("--msi", nargs="*", help=argparse.SUPPRESS)
    p.add_argument("--confirm-uninstall", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--stop-running", action="store_true", help="close any running copy")
    p.add_argument("--uninstall-cleanup", action="store_true", help=argparse.SUPPRESS)
    args = p.parse_args()

    if args.configure:
        return configure(args)
    if args.hash_password:
        return hash_password()
    if args.confirm_uninstall:
        return confirm_uninstall()
    if args.stop_running:
        return stop_running()
    if args.uninstall_cleanup:
        return uninstall_cleanup()
    if args.hosts_on or args.hosts_off:
        from . import hosts
        hosts.apply_block() if args.hosts_on else hosts.remove_block()
        return 0
    if args.check:
        from .linkcheck import check
        result = check(args.check)
        print(result["verdict"].upper(), f"(score {result['score']})")
        for r in result["reasons"]:
            print(" -", r)
        return 0

    from .gui import ScamProtectionApp
    ScamProtectionApp(start_minimized=args.minimized).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
