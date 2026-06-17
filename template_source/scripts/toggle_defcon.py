#!/usr/bin/env python3

# Jules Code Team Template
# Copyright (C) 2026  MnemOnicE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import os
import sys

from path_utils import get_agents_dir

_AGENTS_DIR = get_agents_dir()
BOOM_PATH = os.path.join(_AGENTS_DIR, 'config', 'defaults', 'boom.md')
BOOM_DISABLED_PATH = os.path.join(_AGENTS_DIR, 'config', 'defaults', 'boom.disabled')

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
