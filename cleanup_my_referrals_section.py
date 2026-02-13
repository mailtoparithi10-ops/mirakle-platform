"""
Clean up My Referrals section - Remove mock data and add proper empty state
This ensures new users see a clean, empty table that loads real data from API
"""

import re

# Read the file
with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove hardcoded badge count from dropdown menu
content = re.sub(
    r'(<button class="dropdown-item" onclick="showSection\(\'referrals\'\)"><i class="fas fa-users"></i> My Referrals) <span class="badge">12</span>',
    r'\1',
    content
)

# 2. Remove hardcoded filter counts - make them dynamic
content = re.sub(
    r'Active \(14\)',
    'Active (<span id="activeReferralsCount">0</span>)',
    content
)

content = re.sub(
    r'Completed \(9\)',
    'Completed (<span id="completedReferralsCount">0</span>)',
    content
)

# 3. Replace all mock referral rows with a single empty state row
# Find the tbody section and replace its content
mock_data_pattern = r'(<tbody id="referralsTableBody">)(.*?)(</tbody>)'

empty_state_html = r'''\1
                            <tr id="referralsEmptyState">
                                <td colspan="6" style="text-align: center; padding: 3rem; color: #64748b;">
                                    <i class="fa-solid fa-inbox" style="font-size: 3rem; color: #e2e8f0; margin-bottom: 1rem;"></i>
                                    <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">No referrals yet</div>
                                    <div style="font-size: 0.9rem;">Start referring startups to programs and track them here</div>
                                </td>
                            </tr>
                        \3'''

content = re.sub(mock_data_pattern, empty_state_html, content, flags=re.DOTALL)

# 4. Update the table footer count to be dynamic
content = re.sub(
    r'<span id="referralsTableCount">Showing 3 of 12 referrals</span>',
    '<span id="referralsTableCount">Showing 0 referrals</span>',
    content
)

# 5. Update the loadMyReferrals function to handle empty state and update counts
# Find the loadMyReferrals function and enhance it
old_load_function = r'(async function loadMyReferrals\(\) \{[\s\S]*?)(if \(json\.success\) \{)'

new_load_function = r'''\1if (json.success) {
                    const referrals = json.referrals || [];
                    
                    // Update filter counts
                    const activeCount = referrals.filter(r => r.status === 'pending' || r.status === 'pending_link').length;
                    const completedCount = referrals.filter(r => r.status === 'accepted').length;
                    
                    const activeCountEl = document.getElementById('activeReferralsCount');
                    const completedCountEl = document.getElementById('completedReferralsCount');
                    
                    if (activeCountEl) activeCountEl.textContent = activeCount;
                    if (completedCountEl) completedCountEl.textContent = completedCount;
                    
                    // Update table count
                    const countLabel = document.getElementById('referralsTableCount');
                    if (countLabel) {
                        countLabel.textContent = referrals.length === 0 
                            ? 'No referrals yet' 
                            : `Showing ${referrals.length} referral${referrals.length !== 1 ? 's' : ''}`;
                    }
                    
                    // Show empty state or populate table
                    if (referrals.length === 0) {
                        tbody.innerHTML = `
                            <tr id="referralsEmptyState">
                                <td colspan="6" style="text-align: center; padding: 3rem; color: #64748b;">
                                    <i class="fa-solid fa-inbox" style="font-size: 3rem; color: #e2e8f0; margin-bottom: 1rem;"></i>
                                    <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">No referrals yet</div>
                                    <div style="font-size: 0.9rem;">Start referring startups to programs and track them here</div>
                                </td>
                            </tr>
                        `;
                    } else {'''

content = re.sub(old_load_function, new_load_function, content, flags=re.DOTALL)

# Write the updated content
with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Removed mock referral data from My Referrals section")
print("✓ Added proper empty state for new users")
print("✓ Made filter counts dynamic")
print("✓ Updated table footer to show dynamic count")
print("\nNew users will now see:")
print("  - Empty table with 'No referrals yet' message")
print("  - Filter counts showing 0")
print("  - Clean, professional empty state")
print("\nThe table will populate automatically when:")
print("  - User creates their first referral")
print("  - API returns real referral data")
