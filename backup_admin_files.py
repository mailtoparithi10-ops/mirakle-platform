#!/usr/bin/env python3
"""
Backup Script for Admin Dashboard Files
Creates timestamped backups before integration
"""

import os
import shutil
from datetime import datetime

def backup_files():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/admin_dashboard_{timestamp}"
    
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        'templates/admin_dashboard.html',
        'static/css/admin_dashboard.css',
        'static/js/admin_dashboard.js',
        'routes/admin.py'
    ]
    
    for filepath in files_to_backup:
        if os.path.exists(filepath):
            dest = os.path.join(backup_dir, os.path.basename(filepath))
            shutil.copy2(filepath, dest)
            print(f"✓ Backed up: {filepath}")
        else:
            print(f"⚠ Not found: {filepath}")
    
    print(f"\n✓ Backup completed: {backup_dir}")

if __name__ == "__main__":
    backup_files()
