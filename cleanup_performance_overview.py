#!/usr/bin/env python3
"""
Clean up Performance Overview section in Enabler Dashboard
Remove all mock/fake data and make it load dynamically from API
"""

# Read the template file
with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace hardcoded card values with IDs for dynamic loading
# Total Referrals card
content = content.replace(
    '<div class="card-value" id="totalReferralsValue">28</div>',
    '<div class="card-value" id="totalReferralsValue">0</div>'
)
content = content.replace(
    '''<div class="trend-indicator trend-up">
                            <i class="fa-solid fa-arrow-up-right"></i>
                            <span>+18% vs last month</span>
                        </div>
                        <div class="chip-row">
                            <span class="chip">
                                <i class="fa-solid fa-users"></i>
                                16 unique startups referred
                            </span>
                        </div>''',
    '''<div class="trend-indicator trend-neutral" id="totalReferralsTrend">
                            <i class="fa-solid fa-minus"></i>
                            <span>No change</span>
                        </div>
                        <div class="chip-row">
                            <span class="chip" id="uniqueStartupsChip">
                                <i class="fa-solid fa-users"></i>
                                <span id="uniqueStartupsCount">0</span> unique startups referred
                            </span>
                        </div>'''
)

# Confirmed Earnings card
content = content.replace(
    '<div class="card-value" id="confirmedEarningsValue">₹85,400</div>',
    '<div class="card-value" id="confirmedEarningsValue">₹0</div>'
)
content = content.replace(
    '''<div class="trend-indicator trend-up">
                            <i class="fa-solid fa-arrow-up-right"></i>
                            <span>+₹12,800 this month</span>
                        </div>
                        <div class="chip-row">
                            <span class="chip">
                                <i class="fa-solid fa-circle-check"></i>
                                9 completed program rewards
                            </span>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <div>
                                <div class="card-title">FLC Points</div>
                                <div class="card-value" id="flcPointsValue">3,420</div>''',
    '''<div class="trend-indicator trend-neutral" id="earningsTrend">
                            <i class="fa-solid fa-minus"></i>
                            <span>No earnings yet</span>
                        </div>
                        <div class="chip-row">
                            <span class="chip" id="completedRewardsChip">
                                <i class="fa-solid fa-circle-check"></i>
                                <span id="completedRewardsCount">0</span> completed program rewards
                            </span>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <div>
                                <div class="card-title">FLC Points</div>
                                <div class="card-value" id="flcPointsValue">0</div>'''
)

# FLC Points card
content = content.replace(
    '''<div class="trend-indicator trend-neutral">
                            <i class="fa-solid fa-gauge-simple"></i>
                            <span>Level 3 • Connector</span>
                        </div>
                        <div class="chip-row">
                            <span class="chip">
                                <i class="fa-solid fa-arrow-up"></i>
                                580 points to next level
                            </span>
                        </div>''',
    '''<div class="trend-indicator trend-neutral" id="levelTrend">
                            <i class="fa-solid fa-gauge-simple"></i>
                            <span id="levelStatus">Level 1 • New Enabler</span>
                        </div>
                        <div class="chip-row">
                            <span class="chip" id="pointsToNextChip">
                                <i class="fa-solid fa-arrow-up"></i>
                                <span id="pointsToNext">500</span> points to next level
                            </span>
                        </div>'''
)

# Conversion Rate card
content = content.replace(
    '<div class="card-value" id="conversionRateValue">32%</div>',
    '<div class="card-value" id="conversionRateValue">0%</div>'
)
content = content.replace(
    '''<div class="trend-indicator trend-up">
                            <i class="fa-solid fa-arrow-up-right"></i>
                            <span>+6% vs previous period</span>
                        </div>
                        <div class="chip-row">
                            <span class="chip">
                                <i class="fa-solid fa-circle-dot"></i>
                                9 / 28 referrals converted
                            </span>
                        </div>''',
    '''<div class="trend-indicator trend-neutral" id="conversionTrend">
                            <i class="fa-solid fa-minus"></i>
                            <span>No data yet</span>
                        </div>
                        <div class="chip-row">
                            <span class="chip" id="conversionChip">
                                <i class="fa-solid fa-circle-dot"></i>
                                <span id="conversionStats">0 / 0</span> referrals converted
                            </span>
                        </div>'''
)

# 2. Replace Impact Insights with dynamic loading
content = content.replace(
    '''<div class="insights-list"
                        style="grid-template-columns: repeat(3, 1fr); display: grid; gap: 1.5rem;">
                        <div class="insight-item">
                            <div class="insight-bullet">
                                <i class="fa-solid fa-arrow-trend-up"></i>
                            </div>
                            <div class="insight-text">
                                <span class="insight-highlight">Fintech & healthtech programs</span> have the
                                highest conversion from your network in the past 90 days.
                            </div>
                        </div>
                        <div class="insight-item">
                            <div class="insight-bullet">
                                <i class="fa-solid fa-clock-rotate-left"></i>
                            </div>
                            <div class="insight-text">
                                Startups you refer within <span class="insight-highlight">72 hours of program
                                    launch</span> are 2.3x more likely to be shortlisted.
                            </div>
                        </div>
                        <div class="insight-item">
                            <div class="insight-bullet">
                                <i class="fa-solid fa-bullseye"></i>
                            </div>
                            <div class="insight-text">
                                Focusing on <span class="insight-highlight">3–5 highly relevant startups per
                                    program</span> yields better results than broad sharing.
                            </div>
                        </div>
                    </div>''',
    '''<div class="insights-list" id="impactInsightsList" style="grid-template-columns: repeat(3, 1fr); display: grid; gap: 1.5rem;">
                        <div class="insight-item">
                            <div class="insight-bullet">
                                <i class="fa-solid fa-info-circle"></i>
                            </div>
                            <div class="insight-text">
                                Start making referrals to see personalized insights about your network's performance.
                            </div>
                        </div>
                    </div>'''
)

# 3. Replace Recent Referral Activity table with dynamic loading
content = content.replace(
    '''<tbody id="recentReferralsBody">
                                <tr>
                                    <td>
                                        <div>NovaGrid Analytics</div>
                                        <div class="label-muted">AI for energy optimization</div>
                                    </td>
                                    <td>
                                        <span class="pill">
                                            <span class="pill-dot blue"></span>
                                            Smart City Innovation Cohort
                                        </span>
                                    </td>
                                    <td>
                                        <span class="status-pill in-progress">In review</span>
                                    </td>
                                    <td>₹12,000</td>
                                    <td>2 days ago</td>
                                </tr>
                                <tr>
                                    <td>
                                        <div>FarmLink Labs</div>
                                        <div class="label-muted">Agri supply-chain SaaS</div>
                                    </td>
                                    <td>
                                        <span class="pill">
                                            <span class="pill-dot green"></span>
                                            Retail Innovation Sprint
                                        </span>
                                    </td>
                                    <td>
                                        <span class="status-pill completed">Completed</span>
                                    </td>
                                    <td>₹8,500</td>
                                    <td>5 days ago</td>
                                </tr>
                                <tr>
                                    <td>
                                        <div>MedSync Health</div>
                                        <div class="label-muted">Remote patient monitoring</div>
                                    </td>
                                    <td>
                                        <span class="pill">
                                            <span class="pill-dot amber"></span>
                                            Healthcare Pilot Program
                                        </span>
                                    </td>
                                    <td>
                                        <span class="status-pill pending">Shortlisted</span>
                                    </td>
                                    <td>₹15,000</td>
                                    <td>1 week ago</td>
                                </tr>
                                <tr>
                                    <td>
                                        <div>RouteX Logistics</div>
                                        <div class="label-muted">Urban last-mile optimization</div>
                                    </td>
                                    <td>
                                        <span class="pill">
                                            <span class="pill-dot slate"></span>
                                            Mobility & Logistics Challenge
                                        </span>
                                    </td>
                                    <td>
                                        <span class="status-pill in-progress">Pitch scheduled</span>
                                    </td>
                                    <td>₹10,000</td>
                                    <td>1 week ago</td>
                                </tr>
                            </tbody>''',
    '''<tbody id="recentReferralsBody">
                                <tr>
                                    <td colspan="5" style="text-align: center; padding: 2rem; color: #94a3b8;">
                                        <i class="fas fa-spinner fa-spin" style="font-size: 1.5rem; margin-bottom: 0.5rem;"></i>
                                        <p>Loading referrals...</p>
                                    </td>
                                </tr>
                            </tbody>'''
)

# 4. Update table footer to show dynamic counts
content = content.replace(
    '''<div class="table-footer">
                            <div>
                                Showing <strong>4</strong> of <strong>12</strong> active referrals
                            </div>''',
    '''<div class="table-footer">
                            <div id="referralsTableFooter">
                                Showing <strong id="referralsShowing">0</strong> of <strong id="referralsTotal">0</strong> referrals
                            </div>'''
)

# 5. Update Level Progress card with dynamic values
content = content.replace(
    '''<div class="level-main-title">
                                    Level Progress
                                    <span class="level-number-badge">
                                        <span>LVL 3</span>
                                        <i class="fa-solid fa-bolt"></i>
                                    </span>
                                </div>
                                <div class="level-rating">
                                    <i class="fa-solid fa-star"></i>
                                    Trusted Connector • Top 18%
                                </div>
                                <div class="level-meta">
                                    <span><i class="fa-solid fa-arrow-trend-up"></i> Growth streak: 5
                                        weeks</span>
                                    <span><i class="fa-regular fa-clock"></i> Joined 7 months ago</span>
                                </div>
                            </div>
                            <div class="xp-badge">
                                XP
                                <span id="xpValue">3,420</span>''',
    '''<div class="level-main-title">
                                    Level Progress
                                    <span class="level-number-badge" id="levelBadge">
                                        <span id="levelNumber">LVL 1</span>
                                        <i class="fa-solid fa-bolt"></i>
                                    </span>
                                </div>
                                <div class="level-rating" id="levelRating">
                                    <i class="fa-solid fa-star"></i>
                                    <span id="levelTier">New Enabler</span>
                                </div>
                                <div class="level-meta">
                                    <span id="growthStreak"><i class="fa-solid fa-arrow-trend-up"></i> Just started</span>
                                    <span id="joinedDate"><i class="fa-regular fa-clock"></i> Recently joined</span>
                                </div>
                            </div>
                            <div class="xp-badge">
                                XP
                                <span id="xpValue">0</span>'''
)

# 6. Update milestone values
content = content.replace(
    '''<div class="milestone-value">
                                    <span>9</span>
                                    <span>completed programs</span>
                                </div>
                                <div class="milestone-tag">
                                    <i class="fa-solid fa-circle-check"></i>
                                    1 more to reach LVL 4
                                </div>''',
    '''<div class="milestone-value">
                                    <span id="completedProgramsCount">0</span>
                                    <span>completed programs</span>
                                </div>
                                <div class="milestone-tag" id="programsMilestoneTag">
                                    <i class="fa-solid fa-circle-check"></i>
                                    <span id="programsToNextLevel">10</span> more to reach next level
                                </div>'''
)

content = content.replace(
    '''<div class="milestone-value">
                                    <span>16</span>
                                    active startups
                                </div>''',
    '''<div class="milestone-value">
                                    <span id="activeStartupsCount">0</span>
                                    active startups
                                </div>'''
)

# Write the updated content
with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*60)
print("✅ Removed all mock data from Performance Overview section")
print("✅ Added IDs for dynamic data loading")
print("✅ Set default values to 0 for new users")
print("✅ Ready for API integration")
print("="*60)
print("\nNext: Update JavaScript to load data from /api/enabler/dashboard/overview")
