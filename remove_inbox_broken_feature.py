"""
Remove Broken Inbox Feature from Enabler Dashboard
The inbox button exists in navigation but the actual inbox section HTML doesn't exist.
This causes a broken experience where clicking inbox hides all content.
"""

def remove_inbox_feature():
    with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the inbox button from Messages dropdown
    # The button has a hardcoded badge "4" which is mock data
    inbox_button = '''                    <button class="dropdown-item" onclick="showSection('inbox')"><i class="fas fa-inbox"></i> Inbox <span class="badge">4</span></button>'''
    
    if inbox_button in content:
        content = content.replace(inbox_button, '')
        print("✅ Removed inbox button from Messages dropdown")
    else:
        print("⚠️  Inbox button not found (might have different formatting)")
    
    # Remove the inbox case from showSection function
    inbox_case = """} else if (sectionId === 'inbox') {
                sectionTitle.textContent = 'Notification Inbox';
                sectionSubtitle.textContent = 'Track referral successes, earning alerts, and network news.';
            }"""
    
    if inbox_case in content:
        content = content.replace(inbox_case, '}')
        print("✅ Removed inbox case from showSection() function")
    else:
        print("⚠️  Inbox case not found in showSection()")
    
    # Write back
    with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n📋 Summary:")
    print("   - Removed inbox navigation button (showed fake badge '4')")
    print("   - Removed inbox case from showSection() function")
    print("   - No actual inbox section HTML existed (broken feature)")
    print("\n⚠️  Note: The inbox feature was non-functional:")
    print("   • Navigation button existed but section HTML didn't")
    print("   • Clicking inbox would hide all content and show nothing")
    print("   • Badge showed hardcoded '4' notifications (mock data)")

if __name__ == '__main__':
    remove_inbox_feature()
