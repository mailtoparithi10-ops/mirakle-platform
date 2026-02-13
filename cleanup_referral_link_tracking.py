"""
Clean up Referral Link Tracking section - Remove mock data and add proper empty state
This ensures new users see a clean, empty section that loads real data from API
"""

import re

# Read the file
with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace hardcoded card values with dynamic IDs and 0 values
content = re.sub(
    r'<div class="card-value" id="totalLinksCount">8</div>',
    '<div class="card-value" id="totalLinksCount">0</div>',
    content
)

content = re.sub(
    r'<div class="card-value" id="totalClicksCount">247</div>',
    '<div class="card-value" id="totalClicksCount">0</div>',
    content
)

content = re.sub(
    r'<div class="card-value" id="conversionsCount">23</div>',
    '<div class="card-value" id="conversionsCount">0</div>',
    content
)

content = re.sub(
    r'<div class="card-value" id="linkEarnings">₹11,500</div>',
    '<div class="card-value" id="linkEarnings">₹0</div>',
    content
)

# 2. Remove hardcoded trend indicators and replace with neutral state
content = re.sub(
    r'<div class="trend-indicator trend-up">\s*<i class="fa-solid fa-arrow-up"></i>\s*\+2 this month\s*</div>',
    '<div class="trend-indicator trend-neutral"><i class="fa-solid fa-minus"></i> No links yet</div>',
    content,
    count=1
)

content = re.sub(
    r'<div class="trend-indicator trend-up">\s*<i class="fa-solid fa-arrow-up"></i>\s*\+18% vs last month\s*</div>',
    '<div class="trend-indicator trend-neutral"><i class="fa-solid fa-minus"></i> No clicks yet</div>',
    content,
    count=1
)

content = re.sub(
    r'<div class="trend-indicator trend-up">\s*<i class="fa-solid fa-arrow-up"></i>\s*9\.3% conversion rate\s*</div>',
    '<div class="trend-indicator trend-neutral"><i class="fa-solid fa-minus"></i> No conversions yet</div>',
    content,
    count=1
)

content = re.sub(
    r'<div class="trend-indicator trend-up">\s*<i class="fa-solid fa-arrow-up"></i>\s*\+₹2,300 this month\s*</div>',
    '<div class="trend-indicator trend-neutral"><i class="fa-solid fa-minus"></i> No earnings yet</div>',
    content,
    count=1
)

# 3. Remove hardcoded filter counts
content = re.sub(
    r'Active \(6\)',
    'Active (<span id="activeLinksCount">0</span>)',
    content
)

content = re.sub(
    r'High Performing \(3\)',
    'High Performing (<span id="highPerformingLinksCount">0</span>)',
    content
)

# 4. Replace all mock referral link rows with empty state
mock_links_pattern = r'(<tbody id="referralLinksTableBody">)(.*?)(</tbody>)'

empty_state_html = r'''\1
                            <tr id="referralLinksEmptyState">
                                <td colspan="8" style="text-align: center; padding: 3rem; color: #64748b;">
                                    <i class="fa-solid fa-link-slash" style="font-size: 3rem; color: #e2e8f0; margin-bottom: 1rem;"></i>
                                    <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">No referral links yet</div>
                                    <div style="font-size: 0.9rem; margin-bottom: 1.5rem;">Generate your first referral link to start tracking performance</div>
                                    <button class="btn btn-primary" onclick="generateNewReferralLink()">
                                        <i class="fa-solid fa-plus"></i> Generate First Link
                                    </button>
                                </td>
                            </tr>
                        \3'''

content = re.sub(mock_links_pattern, empty_state_html, content, flags=re.DOTALL)

# 5. Update table footer
content = re.sub(
    r'<span>Showing 5 of 8 referral links</span>',
    '<span id="referralLinksCount">No referral links yet</span>',
    content
)

# 6. Replace the refreshReferralTracking function with real API call
old_refresh_function = r'''function refreshReferralTracking\(\) \{
            console\.log\("🔄 Refreshing referral link tracking data\.\.\."\);
            // Add loading state
            const refreshBtn = event\.target;
            const originalText = refreshBtn\.innerHTML;
            refreshBtn\.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Refreshing\.\.\.';
            refreshBtn\.disabled = true;

            // Simulate API call
            setTimeout\(\(\) => \{
                refreshBtn\.innerHTML = originalText;
                refreshBtn\.disabled = false;
                showToast\('Referral tracking data refreshed successfully!', 'success'\);
            \}, 1500\);
        \}'''

new_refresh_function = '''async function refreshReferralTracking() {
            console.log("🔄 Refreshing referral link tracking data...");
            const refreshBtn = event.target;
            const originalText = refreshBtn.innerHTML;
            refreshBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Refreshing...';
            refreshBtn.disabled = true;

            try {
                await loadReferralLinkTracking();
                showToast('Referral tracking data refreshed successfully!', 'success');
            } catch (err) {
                console.error('Error refreshing referral tracking:', err);
                showToast('Failed to refresh data', 'error');
            } finally {
                refreshBtn.innerHTML = originalText;
                refreshBtn.disabled = false;
            }
        }'''

content = re.sub(old_refresh_function, new_refresh_function, content, flags=re.DOTALL)

# 7. Add new loadReferralLinkTracking function before refreshReferralTracking
load_function = '''
        // Load referral link tracking data from API
        async function loadReferralLinkTracking() {
            try {
                const res = await fetch('/api/referrals/link-tracking');
                const json = await res.json();

                if (json.success && json.data) {
                    const data = json.data;
                    const summary = data.summary || {};
                    const links = data.links || [];

                    // Update summary cards
                    document.getElementById('totalLinksCount').textContent = summary.total_links || 0;
                    document.getElementById('totalClicksCount').textContent = summary.total_clicks || 0;
                    document.getElementById('conversionsCount').textContent = summary.total_conversions || 0;
                    document.getElementById('linkEarnings').textContent = `₹${summary.total_earnings || 0}`;

                    // Update filter counts
                    const activeCount = links.filter(l => l.clicks > 0).length;
                    const highPerformingCount = links.filter(l => l.conversion_rate > 8).length;
                    
                    const activeCountEl = document.getElementById('activeLinksCount');
                    const highPerformingCountEl = document.getElementById('highPerformingLinksCount');
                    
                    if (activeCountEl) activeCountEl.textContent = activeCount;
                    if (highPerformingCountEl) highPerformingCountEl.textContent = highPerformingCount;

                    // Update table
                    const tbody = document.getElementById('referralLinksTableBody');
                    const countLabel = document.getElementById('referralLinksCount');
                    
                    if (countLabel) {
                        countLabel.textContent = links.length === 0 
                            ? 'No referral links yet' 
                            : `Showing ${links.length} referral link${links.length !== 1 ? 's' : ''}`;
                    }

                    if (links.length === 0) {
                        tbody.innerHTML = `
                            <tr id="referralLinksEmptyState">
                                <td colspan="8" style="text-align: center; padding: 3rem; color: #64748b;">
                                    <i class="fa-solid fa-link-slash" style="font-size: 3rem; color: #e2e8f0; margin-bottom: 1rem;"></i>
                                    <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">No referral links yet</div>
                                    <div style="font-size: 0.9rem; margin-bottom: 1.5rem;">Generate your first referral link to start tracking performance</div>
                                    <button class="btn btn-primary" onclick="generateNewReferralLink()">
                                        <i class="fa-solid fa-plus"></i> Generate First Link
                                    </button>
                                </td>
                            </tr>
                        `;
                    } else {
                        tbody.innerHTML = links.map(link => {
                            const conversionRateColor = link.conversion_rate > 8 ? '#22c55e' : link.conversion_rate > 5 ? '#f59e0b' : '#6b7280';
                            const earningsColor = link.earnings > 2000 ? '#22c55e' : link.earnings > 1000 ? '#f59e0b' : '#6b7280';
                            
                            return `
                                <tr>
                                    <td style="font-weight: 600;">${link.program_name}</td>
                                    <td>
                                        <code style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem;">${link.token}</code>
                                    </td>
                                    <td><strong>${link.clicks}</strong></td>
                                    <td><strong style="color: ${conversionRateColor};">${link.conversions}</strong></td>
                                    <td><span style="color: ${conversionRateColor}; font-weight: 600;">${link.conversion_rate.toFixed(1)}%</span></td>
                                    <td><strong style="color: ${earningsColor};">₹${link.earnings.toFixed(0)}</strong></td>
                                    <td>${new Date(link.created_at).toLocaleDateString()}</td>
                                    <td>
                                        <button class="btn-icon" onclick="copyReferralLink('${link.token}')" title="Copy Link">
                                            <i class="fa-solid fa-copy"></i>
                                        </button>
                                        <button class="btn-icon" onclick="viewLinkAnalytics('${link.token}')" title="View Analytics">
                                            <i class="fa-solid fa-chart-line"></i>
                                        </button>
                                    </td>
                                </tr>
                            `;
                        }).join('');
                    }
                }
            } catch (err) {
                console.error('Error loading referral link tracking:', err);
            }
        }

        '''

# Insert the new function before refreshReferralTracking
content = content.replace(
    '        // --- Referral Link Tracking Functions ---',
    load_function + '        // --- Referral Link Tracking Functions ---'
)

# Write the updated content
with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Removed mock data from Referral Link Tracking section")
print("✓ Added proper empty state for new users")
print("✓ Made all counts dynamic (0 for new users)")
print("✓ Added loadReferralLinkTracking() function")
print("✓ Updated refreshReferralTracking() to call API")
print("\nNew users will now see:")
print("  - All counts showing 0")
print("  - Empty table with 'No referral links yet' message")
print("  - Button to generate first link")
print("\nThe section will populate automatically when:")
print("  - User generates their first referral link")
print("  - API returns real link tracking data from /api/referrals/link-tracking")
