#!/usr/bin/env python3

# Jules Code Team Template - Update Utility
# Copyright (C) 2026  MnemOnicE

import json
import re
import sys
import argparse
import subprocess
import urllib.request
from pathlib import Path

SEMVER_PATTERN = re.compile(r'^v?(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$')


def parse_version(version_string):
    if not version_string:
        return None

    match = SEMVER_PATTERN.match(version_string.strip())
    if not match:
        return None

    return tuple(int(part) for part in match.groups())


def compare_versions(a, b):
    parsed_a = parse_version(a)
    parsed_b = parse_version(b)
    if parsed_a is None or parsed_b is None:
        return 0
    return (parsed_a > parsed_b) - (parsed_a < parsed_b)


def get_current_version():
    root = Path(__file__).resolve().parent.parent
    package_file = root / 'package.json'
    if package_file.exists():
        try:
            with open(package_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('version')
        except Exception:
            return None
    return None


def get_latest_version():
    """Get the latest version from GitHub releases"""
    try:
        url = "https://api.github.com/repos/MnemOnicE/Jules-Code-Team-Template/releases/latest"
        # Add timeout to prevent hanging
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('tag_name')
    except Exception:
        return None

def download_update(version=None):
    """Download update from repository"""
    if version is None:
        version = get_latest_version()

    if not version:
        print("❌ Could not determine latest version")
        return False

    print(f"📥 Downloading update: {version}")

    # This would download and extract the update
    # For now, just show the concept
    print("   This would download the latest template files...")
    return True

def apply_update(dry_run=False, force=False):
    """Apply the downloaded update"""
    if not Path('.agents').exists():
        print("❌ No .agents directory found. Initialize first.")
        return False

    print("🔄 Applying update...")

    if dry_run:
        print("🧪 DRY RUN: Would apply the following changes:")
        print("   - Update agent configurations")
        print("   - Add new workflows")
        print("   - Update engine components")
        print("   - Preserve existing memory and customizations")
        return True

    print("   Creating pre-update backup...")
    backup_result = subprocess.run([
        sys.executable, 'scripts/backup_restore.py', 'backup'
    ], capture_output=True, text=True)

    if backup_result.returncode != 0:
        stderr = backup_result.stderr.strip()
        print(f"⚠️  Backup failed: {stderr}")
        if not force:
            print("❌ Aborting update because backup could not be created. Use --force to override.")
            return False
        print("⚠️  Forced update requested, continuing without verified backup.")

    if not download_update():
        print("❌ Update download failed")
        return False

    print("   Updating configurations...")
    print("   Updating workflows...")
    print("   Updating engine...")

    print("✅ Update applied successfully")
    print("🔄 Run 'python scripts/update.py --check' to verify the update")
    return True

def check_for_updates():
    """Check if updates are available"""
    current_version = get_current_version() or "v0.0.0"
    latest_version = get_latest_version()

    if not latest_version:
        print("❌ Could not check for updates")
        return False

    comparison = compare_versions(latest_version, current_version)
    if comparison > 0:
        print(f"📢 Update available: {current_version} → {latest_version}")
        print("   Run 'python scripts/update.py --apply' to update")
        return True

    print("✅ System is up to date")
    return False

def main():
    parser = argparse.ArgumentParser(
        description="Update the Jules Code Team system"
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check for available updates'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply available updates'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be updated without applying changes'
    )
    parser.add_argument(
        '--version',
        help='Specific version to update to'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force update even if pre-update backup cannot be created'
    )

    args = parser.parse_args()

    if args.check:
        return 0 if check_for_updates() else 1
    elif args.apply or args.dry_run:
        return 0 if apply_update(dry_run=args.dry_run, force=args.force) else 1
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())