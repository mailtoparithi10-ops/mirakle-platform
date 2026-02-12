#!/usr/bin/env python3
"""
Merge all database files into one master database
"""

import sqlite3
import os
from datetime import datetime

def merge_databases():
    # List of all database files
    db_files = [
        'instance/mirakle.db',
        'instance/innobridge.db',
        'mirakle.db',
        'innobridge.db',
        'mirakle.db.backup',
        'mirakle_backup_20250922_223712.db',
        'mirakle_backup_20250922_223719.db',
        'mirakle_backup_20250922_223749.db'
    ]
    
    # Filter only existing files
    existing_dbs = [f for f in db_files if os.path.exists(f)]
    
    print("=" * 80)
    print("DATABASE MERGER")
    print("=" * 80)
    print(f"\nFound {len(existing_dbs)} database files:")
    for db in existing_dbs:
        size = os.path.getsize(db) / 1024
        print(f"  - {db} ({size:.2f} KB)")
    
    # Create backup of current instance/mirakle.db
    backup_name = f"instance/mirakle_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    if os.path.exists('instance/mirakle.db'):
        import shutil
        shutil.copy2('instance/mirakle.db', backup_name)
        print(f"\n✓ Created backup: {backup_name}")
    
    # Use instance/mirakle.db as the master
    master_db = 'instance/mirakle.db'
    master_conn = sqlite3.connect(master_db)
    master_cursor = master_conn.cursor()
    
    print(f"\n📊 Master database: {master_db}")
    print("\nMerging data from other databases...")
    
    # Get list of tables in master
    master_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in master_cursor.fetchall()]
    print(f"\nTables in master: {', '.join(tables)}")
    
    total_merged = 0
    
    # Merge each database
    for db_file in existing_dbs:
        if db_file == master_db:
            continue
            
        print(f"\n  Merging: {db_file}")
        
        try:
            # Attach the database
            master_cursor.execute(f"ATTACH DATABASE '{db_file}' AS source")
            
            # Get tables from source
            master_cursor.execute("SELECT name FROM source.sqlite_master WHERE type='table'")
            source_tables = [row[0] for row in master_cursor.fetchall()]
            
            for table in source_tables:
                if table in tables:
                    # Get column names
                    master_cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in master_cursor.fetchall()]
                    
                    # Try to merge data (skip duplicates)
                    try:
                        master_cursor.execute(f"SELECT COUNT(*) FROM source.{table}")
                        source_count = master_cursor.fetchone()[0]
                        
                        if source_count > 0:
                            # Insert data that doesn't exist
                            col_list = ', '.join(columns)
                            master_cursor.execute(f"""
                                INSERT OR IGNORE INTO {table} ({col_list})
                                SELECT {col_list} FROM source.{table}
                            """)
                            merged = master_cursor.rowcount
                            total_merged += merged
                            if merged > 0:
                                print(f"    ✓ {table}: merged {merged} rows")
                    except Exception as e:
                        print(f"    ⚠ {table}: {str(e)}")
            
            # Detach database
            master_cursor.execute("DETACH DATABASE source")
            
        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
    
    master_conn.commit()
    master_conn.close()
    
    print("\n" + "=" * 80)
    print(f"✓ MERGE COMPLETE!")
    print(f"  Total rows merged: {total_merged}")
    print(f"  Master database: {master_db}")
    print(f"  Backup created: {backup_name}")
    print("=" * 80)
    
    # Show final stats
    print("\nFinal database contents:")
    conn = sqlite3.connect(master_db)
    cursor = conn.cursor()
    
    for table in ['users', 'startups', 'opportunities', 'applications', 'referrals']:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} records")
        except:
            pass
    
    conn.close()

if __name__ == "__main__":
    merge_databases()
