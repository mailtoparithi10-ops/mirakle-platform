#!/usr/bin/env python3
"""
Script to add floating elements CSS and JS to all non-dashboard template pages
"""
import os
import re

# Pages to update (excluding dashboards and meeting pages)
pages_to_update = [
    'about.html',
    'blog.html',
    'contact.html',
    'connector.html',
    'corporate.html',
    'investor.html',
    'login.html',
    'opportunities.html',
    'products.html',
    'request_demo.html',
    'signup.html',
    'startup_portal.html',
    'thank_you.html',
    'admin_login.html'
]

templates_dir = 'templates'

def add_floating_elements_to_page(filepath):
    """Add floating elements CSS and JS to a template page"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modified = False
        
        # Add CSS if not already present
        if 'floating-elements.css' not in content:
            # Find the last <link> tag in <head>
            css_pattern = r'(<link[^>]*rel=["\']stylesheet["\'][^>]*>)'
            matches = list(re.finditer(css_pattern, content))
            if matches:
                last_link = matches[-1]
                insert_pos = last_link.end()
                content = (content[:insert_pos] + 
                          '\n    <link rel="stylesheet" href="/static/css/floating-elements.css">' +
                          content[insert_pos:])
                modified = True
                print(f"  ✅ Added CSS to {os.path.basename(filepath)}")
        
        # Add JS if not already present
        if 'floating-elements.js' not in content:
            # Find </body> tag
            body_end = content.rfind('</body>')
            if body_end != -1:
                # Check if Font Awesome is already included
                if 'font-awesome' not in content.lower() or 'fa-' not in content:
                    fa_script = '\n    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/js/all.min.js"></script>'
                else:
                    fa_script = ''
                
                insert_text = f'{fa_script}\n    <script src="/static/js/floating-elements.js"></script>\n'
                content = content[:body_end] + insert_text + content[body_end:]
                modified = True
                print(f"  ✅ Added JS to {os.path.basename(filepath)}")
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        else:
            print(f"  ⏭️  {os.path.basename(filepath)} already has floating elements")
            return False
            
    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")
        return False

def main():
    print("🎨 Adding Floating Elements to Frontend Pages")
    print("=" * 60)
    
    updated_count = 0
    skipped_count = 0
    
    for page in pages_to_update:
        filepath = os.path.join(templates_dir, page)
        if os.path.exists(filepath):
            print(f"\n📄 Processing: {page}")
            if add_floating_elements_to_page(filepath):
                updated_count += 1
            else:
                skipped_count += 1
        else:
            print(f"\n⚠️  File not found: {page}")
    
    print("\n" + "=" * 60)
    print(f"✨ Complete!")
    print(f"   Updated: {updated_count} pages")
    print(f"   Skipped: {skipped_count} pages")
    print(f"\n🎯 Floating elements will now animate on all frontend pages!")

if __name__ == "__main__":
    main()
