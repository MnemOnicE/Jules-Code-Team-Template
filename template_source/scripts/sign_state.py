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

import hashlib
import json
import os
import sys

from path_utils import get_agents_dir


def sign_state():
    """
    Calculates a SHA-256 hash of the session.json file.
    This creates a cryptographic anchor for the current state, preventing
    drift between the machine state and the human narrative.
    """
    try:
        target_file = os.path.join(get_agents_dir(), 'memory', 'session.json')
    except FileNotFoundError:
        print("ERROR: session.json not found. State cannot be signed.")
        sys.exit(1)

    if not target_file:
        print("ERROR: session.json not found. State cannot be signed.")
        sys.exit(1)

    try:
        with open(target_file, 'rb') as f:
            file_content = f.read()

        # Calculate SHA-256 hash
        sha256_hash = hashlib.sha256(file_content).hexdigest()

        # Return the first 8 characters (Short Hash) for readability/logs
        # This is sufficient to detect if the file has changed between writes
        short_hash = sha256_hash[:8]
        print(f"{short_hash}")

    except Exception as e:
        print(f"ERROR: Could not sign state. {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    sign_state()
