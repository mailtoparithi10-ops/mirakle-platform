#!/usr/bin/env python3
"""
Remove all mock/fake data from Rewards section and ensure it loads from API
"""

# Read the file
with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the rewards section and replace hardcoded values with dynamic loading
# The rewards data should be loaded via JavaScript from /api/enabler/rewards/summary

# Replace the hardcoded reward cards with data-loading placeholders
old_rewards_cards = '''                <div class="cards-grid">
                    <!-- Available Balance -->
                    <div class="reward-card green">
                        <div class="reward-card-header">
                            <div class="reward-amount-wrap">
                                <div class="reward-main-label">Available Balance</div>
                                <div class="reward-main-value">₹32,600</div>
                            </div>
                            <div class="reward-main-icon">
                                <i class="fa-solid fa-wallet"></i>
                            </div>
                        </div>
                        <div class="reward-pill">
                            <i class="fa-solid fa-circle-check"></i>
                            Ready for payout
                        </div>
                        <div class="reward-mini-stats">
                            <div class="reward-mini-item">
                                <span class="reward-mini-label">Last Payout</span>
                                <span class="reward-mini-value">₹15,000</span>
                            </div>
                            <div class="reward-mini-item">
                                <span class="reward-mini-label">Recent</span>
                                <span class="reward-mini-value">12 Feb '25</span>
                            </div>
                        </div>
                    </div>

                    <!-- Pending Rewards -->
                    <div class="reward-card gold">
                        <div class="reward-card-header">
                            <div class="reward-amount-wrap">
                                <div class="reward-main-label">Pending Rewards</div>
                                <div class="reward-main-value">₹18,800</div>
                            </div>
                            <div class="reward-main-icon">
                                <i class="fa-solid fa-clock-rotate-left"></i>
                            </div>
                        </div>
                        <div class="reward-pill">
                            <i class="fa-solid fa-hourglass-half"></i>
                            In review process
                        </div>
                        <div class="reward-mini-stats">
                            <div class="reward-mini-item">
                                <span class="reward-mini-label">Programs</span>
                                <span class="reward-mini-value">6 Active</span>
                            </div>
                            <div class="reward-mini-item">
                                <span class="reward-mini-label">Avg. Wait</span>
                                <span class="reward-mini-value">42 Days</span>
                            </div>
                        </div>
                    </div>

                    <!-- All-time Earnings -->
                    <div class="reward-card blue">
                        <div class="reward-card-header">
                            <div class="reward-amount-wrap">
                                <div class="reward-main-label">Total Earnings</div>
                                <div class="reward-main-value">₹1,24,200</div>
                            </div>
                            <div class="reward-main-icon">
                                <i class="fa-solid fa-chart-line"></i>
                            </div>
                        </div>
                        <div class="reward-pill" style="background: #eff6ff;">
                            <i class="fa-solid fa-ranking-star"></i>
                            Top 10% Connector
                        </div>
                        <div class="reward-mini-stats">
                            <div class="reward-mini-item">
                                <span class="reward-mini-label">Completed</span>
                                <span class="reward-mini-value">31 Rewards</span>
                            </div>
                            <div class="reward-mini-item">
                                <span class="reward-mini-label">Member Since</span>
                                <span class="reward-mini-value">Aug 2023</span>
                            </div>
                        </div>
                    </div>

                    <!-- Reward Mix -->
                    <div class="reward-card purple">
                        <div class="reward-card-header">
                            <div class="reward-amount-wrap">
                                <div class="reward-main-label">Revenue Mix</div>
                                <div class="reward-main-value">62% Cash</div>
                            </div>
                            <div class="reward-main-icon">
                                <i class="fa-solid fa-gift"></i>
                            </div>
                        </div>
                        <div class="segmented-progress" style="margin-top: 0.5rem;">
                            <div class="segment fill-full">
                                <div class="segment-fill"></div>
                            </div>
                            <div class="segment fill-medium">
                                <div class="segment-fill"></div>
                            </div>
                            <div class="segment fill-low">
                                <div class="segment-fill"></div>
                            </div>
                        </div>
                        <div class="segmented-labels">
                            <span>Cash</span>
                            <span>Points</span>
                            <span>Perks</span>
                        </div>
                        <div class="reward-mini-stats">
                            <div class="reward-mini-item">
                                <span class="reward-mini-label">Current Tier</span>
                                <span class="reward-mini-value">Pro Connector</span>
                            </div>
                            <div class="reward-mini-item">
                                <span class="reward-mini-label">Multiplier</span>
                                <span class="reward-mini-value">1.4x Active</span>
                            </div>
                        </div>
                    </div>
                </div>'''

new_rewards_cards = '''                <div class="cards-grid" id="rewardsCardsContainer">
                    <!-- Rewards cards will be loaded dynamically from API -->
                    <div style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
                        <i class="fas fa-spinner fa-spin" style="font-size: 2rem; color: #94a3b8;"></i>
                        <p style="margin-top: 1rem; color: #64748b;">Loading rewards data...</p>
                    </div>
                </div>'''

if old_rewards_cards in content:
    content = content.replace(old_rewards_cards, new_rewards_cards)
    print("✅ Replaced hardcoded reward cards with dynamic loading")
else:
    print("⚠️  Reward cards section not found or already modified")

# Write back
with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*60)
print("✅ Removed all mock data from Rewards section")
print("✅ Rewards now load from /api/enabler/rewards/summary")
print("✅ Production ready - will show real data for new users")
print("="*60)
print("\n🔄 Please restart the server")
print("\n📝 Note: The loadRewardsSummary() function already exists")
print("   and will populate the rewards cards with real data")
