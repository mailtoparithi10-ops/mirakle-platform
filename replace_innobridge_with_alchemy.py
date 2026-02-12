#!/usr/bin/env python3
"""
Script to replace all InnoBridge references with Alchemy
"""
import os
import re

def replace_in_file(filepath, case_sensitive=False):
    """Replace InnoBridge with Alchemy in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace all variations
        if case_sensitive:
            content = content.replace('InnoBridge', 'Alchemy')
            content = content.replace('INNOBRIDGE', 'ALCHEMY')
            content = content.replace('innobridge', 'alchemy')
        else:
            # Case-insensitive replacement preserving case
            content = re.sub(r'InnoBridge', 'Alchemy', content)
            content = re.sub(r'INNOBRIDGE', 'ALCHEMY', content)
            content = re.sub(r'innobridge', 'alchemy', content, flags=re.IGNORECASE)
        
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
    files_to_process = [
        # Templates
        'templates/index.html',
        'templates/corporate.html',
        'templates/startup_portal.html',
        'templates/enabler.html',
        'templates/account_success.html',
        'templates/admin_dashboard.html',
        'templates/admin_login.html',
        'templates/login.html',
        'templates/signup.html',
        'templates/thank_you.html',
        'templates/startup_dashboard.html',
        'templates/corporate_dashboard.html',
        'templates/enabler_dashboard.html',
        
        # JavaScript
        'static/js/index.js',
        'static/js/corporate.js',
        'static/js/startup_dashboard.js',
        'static/js/innobridge.js',
        'static/js/investor.js',
        'static/js/main.js',
        'static/js/floating-elements.js',
        
        # CSS
        'static/css/floating-elements.css',
    ]
    
    print("=" * 60)
    print("REPLACING INNOBRIDGE WITH ALCHEMY")
    print("=" * 60)
    
    updated_count = 0
    for filepath in files_to_process:
        if os.path.exists(filepath):
            if replace_in_file(filepath):
                print(f"✓ Updated: {filepath}")
                updated_count += 1
            else:
                print(f"  Skipped: {filepath} (no changes needed)")
        else:
            print(f"✗ Not found: {filepath}")
    
    print("=" * 60)
    print(f"Total files updated: {updated_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()
