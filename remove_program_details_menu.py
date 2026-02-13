"""
Remove non-functional "Program Details" menu item from Enabler Dashboard
This menu item references a section that doesn't exist
"""

# Read the file
with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the Program Details dropdown item
program_details_line = '                    <button class="dropdown-item" onclick="showSection(\'program-details\')"><i class="fas fa-info-circle"></i> Program Details</button>'

if program_details_line in content:
    # Find and remove the line
    content = content.replace(program_details_line + '\n', '')
    print("✓ Removed 'Program Details' dropdown menu item")
else:
    # Try alternative format
    alt_line = '<button class="dropdown-item" onclick="showSection(\'program-details\')"><i class="fas fa-info-circle"></i> Program Details</button>'
    if alt_line in content:
        content = content.replace(alt_line + '\n', '')
        print("✓ Removed 'Program Details' dropdown menu item (alternative format)")

# Remove the program-details handling in showSection function
# Find and remove the condition
old_condition = '''            } else if (sectionId === 'program-details') {
                sectionTitle.textContent = 'Program Specifics';
                sectionSubtitle.textContent = 'Review detailed information before referring a startup.';
'''

if old_condition in content:
    content = content.replace(old_condition, '')
    print("✓ Removed 'program-details' condition from showSection function")

# Remove the tab mapping
old_mapping = "            if (sectionId === 'program-details') tabId = 'tab-programs';\n"
if old_mapping in content:
    content = content.replace(old_mapping, '')
    print("✓ Removed 'program-details' tab mapping")

# Write back
with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ Non-functional 'Program Details' menu removed")
print("  - Removed dropdown menu item")
print("  - Removed JavaScript handling code")
print("  - Removed tab mapping")
print("\n✓ Users will no longer see a broken menu option")
