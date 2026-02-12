#!/usr/bin/env python3
"""
Comprehensive script to replace ALL InnoBridge references with Alchemy
"""
import os
import glob

def replace_in_file(filepath):
    """Replace InnoBridge with Alchemy in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace all variations
        content = content.replace('InnoBridge', 'Alchemy')
        content = content.replace('INNOBRIDGE', 'ALCHEMY')
        content = content.replace('innobridge', 'alchemy')
        content = content.replace('InnoBridge', 'Alchemy')  # Redundant but safe
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("COMPREHENSIVE INNOBRIDGE → ALCHEMY REPLACEMENT")
    print("=" * 60)
    
    # Get all HTML, JS, and CSS files
    patterns = [
        'templates/**/*.html',
        'static/js/**/*.js',
        'static/css/**/*.css',
    ]
    
    all_files = []
    for pattern in patterns:
        all_files.extend(glob.glob(pattern, recursive=True))
    
    updated_count = 0
    skipped_count = 0
    
    for filepath in sorted(all_files):
        if replace_in_file(filepath):
            print(f"✓ Updated: {filepath}")
            updated_count += 1
        else:
            skipped_count += 1
    
    print("=" * 60)
    print(f"✓ Files updated: {updated_count}")
    print(f"  Files skipped: {skipped_count} (no changes needed)")
    print(f"  Total processed: {len(all_files)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
