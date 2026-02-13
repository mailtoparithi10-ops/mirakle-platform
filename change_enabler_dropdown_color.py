#!/usr/bin/env python3
"""
Change the color of text in enabler dropdown buttons to yellow/gold for better visibility
"""

# Read the file
with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the profile-name color to make it yellow/gold
old_profile_name_style = '''.profile-name {
            color: white;
            font-size: 0.85rem;
            font-weight: 700;
        }'''

new_profile_name_style = '''.profile-name {
            color: #ffdf00;
            font-size: 0.85rem;
            font-weight: 700;
        }'''

content = content.replace(old_profile_name_style, new_profile_name_style)

# Also make dropdown button text more visible by default (yellow instead of white)
# This will make all dropdown button text yellow
old_dropdown_toggle = '''        .dropdown-toggle {
            background: rgba(255, 255, 255, 0.05);
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.3);'''

new_dropdown_toggle = '''        .dropdown-toggle {
            background: rgba(255, 255, 255, 0.05);
            color: #ffdf00 !important;
            border: 1px solid rgba(255, 255, 255, 0.3);'''

# Replace both occurrences
content = content.replace(old_dropdown_toggle, new_dropdown_toggle)

# Write back
with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Changed dropdown button text color to yellow (#ffdf00)")
print("✅ Changed profile name color to yellow (#ffdf00)")
print("✅ All dropdown buttons now have yellow text for better visibility")
print("\n🔄 Please restart the server and do a HARD REFRESH (Ctrl+Shift+R)")
