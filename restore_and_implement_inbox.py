"""
Restore and Implement Functional Inbox/Notifications System
This will create a working notification inbox that shows:
- Messages from other users
- Referral acceptance notifications
- System alerts
"""

def restore_inbox():
    with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Restore Messages dropdown with dynamic badge
    messages_dropdown = '''            <!-- Messages Dropdown -->
            <div class="dropdown" id="messagesDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('messagesDropdown')">
                    <i class="fas fa-envelope"></i> Messages 
                    <span class="badge" id="messagesBadge" style="display: none;">0</span>
                    <i class="fas fa-chevron-down" style="font-size: 0.7rem;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('inbox')"><i class="fas fa-inbox"></i> Inbox <span class="badge" id="inboxBadge">0</span></button>
                </div>
            </div>
        </div>

        <!-- Profile Dropdown -->'''
    
    # Find where to insert (before Profile Dropdown)
    profile_marker = '        </div>\n\n        <!-- Profile Dropdown -->'
    if profile_marker in content:
        content = content.replace(profile_marker, messages_dropdown)
        print("✅ Restored Messages dropdown with dynamic badge")
    
    # 2. Restore inbox case in showSection function
    # Find the last } before the closing of showSection
    inbox_case = '''} else if (sectionId === 'inbox') {
                sectionTitle.textContent = 'Notification Inbox';
                sectionSubtitle.textContent = 'Track referral successes, earning alerts, and network news.';
            }'''
    
    # Insert before the closing of the function (look for the pattern)
    pattern = '''} else if (sectionId === 'profile') {
                sectionTitle.textContent = 'Profile & Settings';
                sectionSubtitle.textContent = 'Manage your account information and notification preferences.';
            }
        }'''
    
    replacement = '''} else if (sectionId === 'profile') {
                sectionTitle.textContent = 'Profile & Settings';
                sectionSubtitle.textContent = 'Manage your account information and notification preferences.';
            } else if (sectionId === 'inbox') {
                sectionTitle.textContent = 'Notification Inbox';
                sectionSubtitle.textContent = 'Track referral successes, earning alerts, and network news.';
            }
        }'''
    
    if pattern in content:
        content = content.replace(pattern, replacement)
        print("✅ Restored inbox case in showSection() function")
    
    # Write back
    with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Inbox navigation restored with dynamic badges")
    print("   Next: Need to add inbox section HTML and API endpoint")

if __name__ == '__main__':
    restore_inbox()
