#!/usr/bin/env python3
"""
Safely archive old database files
"""

import os
import shutil
from datetime import datetime

def archive_old_databases():
    # Create archive directory
    archive_dir = 'database_archives'
    os.makedirs(archive_dir, exist_ok=True)
    
    # List of old database files to archive (NOT the active one)
    old_db_files = [
        'mirakle.db',  # Root directory copy
        'innobridge.db',  # Root directory copy
        'mirakle.db.backup',
        'mirakle_backup_20250922_223712.db',
        'mirakle_backup_20250922_223719.db',
        'mirakle_backup_20250922_223749.db',
        'instance/innobridge.db'  # Old innobridge in instance
    ]
    
    # DO NOT archive the active database
    active_db = 'instance/mirakle.db'
    
    print("=" * 80)
    print("ARCHIVING OLD DATABASE FILES")
    print("=" * 80)
    print(f"\nActive database (KEEPING): {active_db}")
    print(f"Archive directory: {archive_dir}/")
    print("\nArchiving old files:")
    
    archived_count = 0
    total_size = 0
    
    for db_file in old_db_files:
        if os.path.exists(db_file):
            size = os.path.getsize(db_file) / 1024
            total_size += size
            
            # Create archive filename with timestamp
            filename = os.path.basename(db_file)
            archive_path = os.path.join(archive_dir, filename)
            
            # If file already exists in archive, add timestamp
            if os.path.exists(archive_path):
                name, ext = os.path.splitext(filename)
                archive_path = os.path.join(archive_dir, f"{name}_archived{ext}")
            
            # Move file to archive
            shutil.move(db_file, archive_path)
            print(f"  ✓ Archived: {db_file} ({size:.2f} KB)")
            archived_count += 1
        else:
            print(f"  ⊘ Not found: {db_file}")
    
    print("\n" + "=" * 80)
    print(f"✓ ARCHIVING COMPLETE!")
    print(f"  Files archived: {archived_count}")
    print(f"  Total size: {total_size:.2f} KB")
    print(f"  Location: {archive_dir}/")
    print("\n  Active database: {active_db}")
    print("=" * 80)
    
    # List what's in the archive
    print("\nArchived files:")
    for f in os.listdir(archive_dir):
        if f.endswith('.db'):
            path = os.path.join(archive_dir, f)
            size = os.path.getsize(path) / 1024
            print(f"  - {f} ({size:.2f} KB)")
    
    print("\n💡 Note: Files are archived, not deleted. You can restore them if needed.")

if __name__ == "__main__":
    archive_old_databases()
