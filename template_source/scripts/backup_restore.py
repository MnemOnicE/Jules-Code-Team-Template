#!/usr/bin/env python3

# Jules Code Team Template - Backup/Restore Utility
# Copyright (C) 2026  MnemOnicE

import os
import sys
import json
import shutil
import argparse
import tarfile
import tempfile
from pathlib import Path
from datetime import datetime

def create_backup(output_path=None):
    """Create a backup of the current agent state"""
    if not Path('.agents').exists():
        print("❌ No .agents directory found. Nothing to backup.")
        return False

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"agents_backup_{timestamp}.tar.gz"

    print(f"📦 Creating backup: {output_path}")

    try:
        with tarfile.open(output_path, "w:gz") as tar:
            # Backup agent configurations and memory
            backup_items = [
                '.agents/config',
                '.agents/memory',
                '.agents/rules',
                'session.json',
                'AI_MEMORY.md'
            ]

            for item in backup_items:
                if Path(item).exists():
                    print(f"   Adding {item}")
                    tar.add(item)
                else:
                    print(f"   Skipping {item} (not found)")

        print("✅ Backup created successfully"        return True

    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def restore_backup(backup_path, force=False):
    """Restore agent state from backup"""
    if not Path(backup_path).exists():
        print(f"❌ Backup file not found: {backup_path}")
        return False

    if Path('.agents').exists() and not force:
        print("⚠️  .agents directory already exists. Use --force to overwrite.")
        return False

    print(f"📦 Restoring from backup: {backup_path}")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract backup
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(temp_dir)

            # Restore files
            temp_path = Path(temp_dir)
            restore_items = ['.agents', 'session.json', 'AI_MEMORY.md']

            for item in restore_items:
                src = temp_path / item
                if src.exists():
                    print(f"   Restoring {item}")
                    if src.is_file():
                        shutil.copy2(src, item)
                    else:
                        if Path(item).exists():
                            shutil.rmtree(item)
                        shutil.copytree(src, item)

        print("✅ Restore completed successfully"        return True

    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False

def list_backups():
    """List available backup files"""
    backups = list(Path('.').glob('agents_backup_*.tar.gz'))
    if not backups:
        print("No backup files found.")
        return

    print("Available backups:")
    for backup in sorted(backups, reverse=True):
        size = backup.stat().st_size / 1024 / 1024  # MB
        print(".1f")

def main():
    parser = argparse.ArgumentParser(
        description="Backup and restore agent configurations and memory"
    )
    parser.add_argument(
        'action',
        choices=['backup', 'restore', 'list'],
        help='Action to perform'
    )
    parser.add_argument(
        '--file', '-f',
        help='Backup file path (for restore)'
    )
    parser.add_argument(
        '--force', '-y',
        action='store_true',
        help='Force overwrite during restore'
    )

    args = parser.parse_args()

    if args.action == 'backup':
        success = create_backup()
    elif args.action == 'restore':
        if not args.file:
            print("❌ --file required for restore action")
            return 1
        success = restore_backup(args.file, args.force)
    elif args.action == 'list':
        list_backups()
        return 0

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())