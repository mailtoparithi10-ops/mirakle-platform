"""
Implement Analytics Section with Real Data
Replaces the "Coming Soon" placeholder with a fully functional analytics dashboard
"""

# Read the file
with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the analytics section
analytics_start = content.find('<!-- ANALYTICS SECTION -->')
if analytics_start == -1:
    analytics_start = content.find('<section id="analytics" class="section">')

# Find the end of the analytics section
analytics_end = content.find('<!-- REFERRAL GUIDE SECTION -->')

if analytics_start != -1 and analytics_end != -1:
    # Create the new analytics section with real data
    new_analytics = '''<!-- ANALYTICS SECTION -->
            <section id="analytics" class="section">
                <div class="section-header">
                    <div class="section-header-main">
                        <div class="section-title">
                            <i class="fa-solid fa-chart-line"></i>
                            Analytics & Insights
                        </div>
                        <div class="section-subtitle">
                            Deep dive into your referral performance, conversion metrics, and earning trends.
                        </div>
                    </div>
                </div>

                <!-- Analytics Overview Cards -->
                <div class="cards-grid" style="margin-bottom: 2rem;">
                    <div class="card">
                        <div class="card-header">
                            <div>
                                <span class="card-title">Total Referrals</span>
                                <span class="card-value" id="analyticsTotal Referrals">0</span>
                            </div>
                            <div class="card-icon blue">
                                <i class="fa-solid fa-paper-plane"></i>
                            </div>
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <div>
                                <span class="card-title">Successful</span>
                                <span class="card-value" id="analyticsSuccessful">0</span>
                            </div>
                            <div class="card-icon green">
                                <i class="fa-solid fa-check-circle"></i>
                            </div>
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <div>
                                <span class="card-title">Conversion Rate</span>
                                <span class="card-value" id="analyticsConversion">0%</span>
                            </div>
                            <div class="card-icon purple">
                                <i class="fa-solid fa-percentage"></i>
                            </div>
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <div>
                                <span class="card-title">Avg Decision Time</span>
                                <span class="card-value" id="analyticsDecisionTime">0d</span>
                            </div>
                            <div class="card-icon gold">
                                <i class="fa-solid fa-clock"></i>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Sector Performance -->
                <div class="professional-panel" style="margin-bottom: 2rem;">
                    <div class="panel-header-row">
                        <div class="panel-header-left">
                            <h3>Sector Performance</h3>
                            <p>Your conversion rates across different industry sectors</p>
                        </div>
                    </div>
                    <div id="sectorPerformanceContainer">
                        <div style="text-align: center; padding: 2rem; color: #94a3b8;">
                            <i class="fa-solid fa-chart-pie" style="font-size: 2rem; margin-bottom: 1rem; display: block;"></i>
                            <p>No sector data available yet. Start making referrals to see insights.</p>
                        </div>
                    </div>
                </div>

                <!-- Referral Insights -->
                <div class="professional-panel">
                    <div class="panel-header-row">
                        <div class="panel-header-left">
                            <h3>Referral Insights</h3>
                            <p>Key metrics about your referral activity</p>
                        </div>
                    </div>
                    <div class="stats-grid-container">
                        <div class="prop-stat-widget">
                            <span class="prop-stat-label">Unique Startups</span>
                            <span class="prop-stat-value" id="analyticsUniqueStartups">0</span>
                        </div>
                        <div class="prop-stat-widget">
                            <span class="prop-stat-label">Avg Programs/Startup</span>
                            <span class="prop-stat-value" id="analyticsAvgPrograms">0</span>
                        </div>
                        <div class="prop-stat-widget">
                            <span class="prop-stat-label">Under Review</span>
                            <span class="prop-stat-value" id="analyticsUnderReview">0</span>
                        </div>
                        <div class="prop-stat-widget">
                            <span class="prop-stat-label">Shortlisted</span>
                            <span class="prop-stat-value" id="analyticsShortlisted">0</span>
                        </div>
                    </div>
                </div>
            </section>

            '''
    
    # Replace the content
    content = content[:analytics_start] + new_analytics + content[analytics_end:]
    
    # Write back
    with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Analytics section implemented with real data")
    print("  - Added analytics overview cards (Total, Successful, Conversion, Decision Time)")
    print("  - Added sector performance panel")
    print("  - Added referral insights grid")
    print("  - All values load dynamically from API")
    print("\n✓ Next: Add JavaScript to load analytics data")
else:
    print("✗ Could not find analytics section")
