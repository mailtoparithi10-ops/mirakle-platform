#!/usr/bin/env python3
"""
Remove payout form section from enabler profile, keep only points and notifications
"""

# Read the file
with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start of the payout section (info-banner about payouts)
payout_start = content.find('<div class="info-banner">\n                            <i class="fa-solid fa-circle-info"></i>\n                            <span>\n                                To receive payouts')

# Find the end of the payout section (before the hidden form)
payout_end = content.find('<!-- Hidden Form for Photo Removal -->')

if payout_start > 0 and payout_end > 0:
    # Extract the part before payout section
    before_payout = content[:payout_start]
    
    # Extract the part after payout section
    after_payout = content[payout_end:]
    
    # Create new simplified section with just points info and notifications
    new_section = '''<div class="info-banner" style="background: #fef3c7; border-color: #fbbf24;">
                            <i class="fa-solid fa-coins" style="color: #f59e0b;"></i>
                            <span style="color: #92400e;">
                                <strong>Points System Active:</strong> Earn points for successful referrals and program connections. Payout features will be available in future updates.
                            </span>
                        </div>

                        <div class="settings-list">
                            <div class="settings-row">
                                <div class="settings-label">
                                    <div class="settings-title">Email notifications</div>
                                    <div class="settings-desc">Program updates, new opportunities, and reward
                                        confirmations.</div>
                                </div>
                                <div class="toggle-switch active"
                                    onclick="this.classList.toggle('active'); showToast('Setting updated', 'success')">
                                    <div class="toggle-thumb"></div>
                                </div>
                            </div>
                            <div class="settings-row">
                                <div class="settings-label">
                                    <div class="settings-title">Digest summary</div>
                                    <div class="settings-desc">Weekly summary of referrals and ecosystem signals.</div>
                                </div>
                                <div class="toggle-switch active"
                                    onclick="this.classList.toggle('active'); showToast('Setting updated', 'success')">
                                    <div class="toggle-thumb"></div>
                                </div>
                            </div>
                            <div class="settings-row">
                                <div class="settings-label">
                                    <div class="settings-title">Product announcements</div>
                                    <div class="settings-desc">New features for connectors and ecosystem tools.</div>
                                </div>
                                <div class="toggle-switch"
                                    onclick="this.classList.toggle('active'); showToast('Setting updated', 'success')">
                                    <div class="toggle-thumb"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                '''
    
    # Combine everything
    content = before_payout + new_section + after_payout
    
    # Write back
    with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Removed payout form section")
    print("✅ Added points system info banner")
    print("✅ Kept notification settings")
    print("✅ Profile section now shows only points and notifications")
    print("\n🔄 Please restart the server")
else:
    print("❌ Could not find payout section to remove")
