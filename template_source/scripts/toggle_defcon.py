#!/usr/bin/env python3
import argparse
import os
import sys

BOOM_PATH = "template_source/.agents/config/defaults/boom.md"
BOOM_DISABLED_PATH = "template_source/.agents/config/defaults/boom.disabled"

def main():
    parser = argparse.ArgumentParser(description="Defcon 1 Kill Switch for Boom Persona")
    parser.add_argument("--status", choices=["normal", "emergency"], required=True, help="Set the operational status")
    args = parser.parse_args()

    if args.status == "emergency":
        if os.path.exists(BOOM_PATH):
            os.rename(BOOM_PATH, BOOM_DISABLED_PATH)
            print("🚨 DEFCON 1 ACTIVATED: Boom persona has been disabled (renamed to boom.disabled).")
        elif os.path.exists(BOOM_DISABLED_PATH):
            print("ℹ️  System is already in EMERGENCY mode (Boom is disabled).")
        else:
            print("⚠️  Error: boom.md not found in defaults. Cannot disable.")
            sys.exit(1)

    elif args.status == "normal":
        if os.path.exists(BOOM_DISABLED_PATH):
            os.rename(BOOM_DISABLED_PATH, BOOM_PATH)
            print("✅ DEFCON 1 DEACTIVATED: Boom persona restored.")
        elif os.path.exists(BOOM_PATH):
            print("ℹ️  System is already in NORMAL mode (Boom is active).")
        else:
            print("⚠️  Error: boom.disabled not found. Cannot restore.")
            sys.exit(1)

if __name__ == "__main__":
    main()
