import argparse
import sys


def main():
    parser = argparse.ArgumentParser(prog="GuardianShield")
    parser.add_argument("--minimized", action="store_true", help="start hidden in the system tray")
    parser.add_argument("--hosts-on", action="store_true", help="(admin) add scam-site block to hosts file")
    parser.add_argument("--hosts-off", action="store_true", help="(admin) remove scam-site block")
    parser.add_argument("--check", metavar="TEXT", help="check a link/message and print the result")
    args = parser.parse_args()

    if args.hosts_on or args.hosts_off:
        from . import hosts
        hosts.apply_block() if args.hosts_on else hosts.remove_block()
        return
    if args.check:
        from .linkcheck import check
        result = check(args.check)
        print(result["verdict"].upper(), f"(score {result['score']})")
        for r in result["reasons"]:
            print(" -", r)
        return

    from .gui import GuardianApp
    GuardianApp(start_minimized=args.minimized).run()


if __name__ == "__main__":
    sys.exit(main())
