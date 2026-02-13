"""
Clean up Analytics section - Replace with "Coming Soon" placeholder
This removes all mock data and shows a professional placeholder for production
"""

# Read the file
with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the analytics section start and end
analytics_start = content.find('<!-- ANALYTICS SECTION -->\n            <section id="analytics" class="section">')
if analytics_start == -1:
    analytics_start = content.find('<section id="analytics" class="section">')

# Find the end of the analytics section (next section tag)
analytics_end = content.find('</section>', analytics_start)
analytics_end = content.find('</section>', analytics_end + 1)  # Get the closing tag

if analytics_start != -1 and analytics_end != -1:
    # Replace the entire analytics section with a coming soon placeholder
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

                <!-- Coming Soon Placeholder -->
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 400px; text-align: center; padding: 3rem;">
                    <div style="width: 120px; height: 120px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 2rem; box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);">
                        <i class="fa-solid fa-chart-line" style="font-size: 3rem; color: white;"></i>
                    </div>
                    <h2 style="font-size: 2rem; font-weight: 800; color: #1e293b; margin-bottom: 1rem;">
                        Advanced Analytics Coming Soon
                    </h2>
                    <p style="font-size: 1.1rem; color: #64748b; max-width: 600px; margin-bottom: 2rem; line-height: 1.6;">
                        We're building powerful analytics tools to help you track your referral performance, conversion rates, and earnings trends. Stay tuned for detailed insights and actionable data.
                    </p>
                    <div style="display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center;">
                        <div style="padding: 1rem 1.5rem; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0;">
                            <i class="fa-solid fa-chart-pie" style="color: #3b82f6; margin-right: 0.5rem;"></i>
                            <span style="color: #475569; font-weight: 600;">Performance Metrics</span>
                        </div>
                        <div style="padding: 1rem 1.5rem; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0;">
                            <i class="fa-solid fa-chart-bar" style="color: #10b981; margin-right: 0.5rem;"></i>
                            <span style="color: #475569; font-weight: 600;">Conversion Tracking</span>
                        </div>
                        <div style="padding: 1rem 1.5rem; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0;">
                            <i class="fa-solid fa-chart-area" style="color: #f59e0b; margin-right: 0.5rem;"></i>
                            <span style="color: #475569; font-weight: 600;">Earnings Trends</span>
                        </div>
                    </div>
                    <div style="margin-top: 2rem; padding: 1rem 2rem; background: rgba(102, 126, 234, 0.1); border-radius: 12px; border: 1px solid rgba(102, 126, 234, 0.2);">
                        <p style="color: #667eea; font-weight: 600; margin: 0;">
                            <i class="fa-solid fa-bell" style="margin-right: 0.5rem;"></i>
                            You'll be notified when analytics features go live
                        </p>
                    </div>
                </div>
            </section>'''
    
    # Replace the content
    content = content[:analytics_start] + new_analytics + content[analytics_end + 10:]
    
    # Write back
    with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Analytics section cleaned up")
    print("  - Removed all mock data (28 referrals, ₹85,400 earnings, etc.)")
    print("  - Removed hardcoded sectors (HealthTech 48%, FinTech 36%, etc.)")
    print("  - Removed fake status breakdown (14 under review, 9 completed, 5 rejected)")
    print("  - Removed fake earnings (₹85,400 total, ₹12,500 pending)")
    print("  - Removed fake response times (2.4 days avg, 6 hours fastest)")
    print("  - Added professional 'Coming Soon' placeholder")
    print("\n✓ Production ready - new users will see a clean placeholder")
else:
    print("✗ Could not find analytics section")
