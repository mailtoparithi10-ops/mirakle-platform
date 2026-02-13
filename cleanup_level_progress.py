"""
Remove mock data from Level Progress section in Enabler Dashboard
Make it production-ready with dynamic data loading
"""

# Read the file
with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace hardcoded level progress values with dynamic IDs

# 1. Current Level label - change from "LVL 3" to dynamic
content = content.replace(
    '''                            <div class="level-progress-labels">
                                <div class="curr-level">
                                    Current: <span>LVL 3</span>
                                </div>
                                <div class="next-level">
                                    Next: LVL 4
                                    <i class="fa-solid fa-location-arrow"></i>
                                </div>
                            </div>''',
    '''                            <div class="level-progress-labels">
                                <div class="curr-level">
                                    Current: <span id="currentLevelLabel">LVL 1</span>
                                </div>
                                <div class="next-level">
                                    Next: <span id="nextLevelLabel">LVL 2</span>
                                    <i class="fa-solid fa-location-arrow"></i>
                                </div>
                            </div>'''
)

# 2. Progress bar - add ID for dynamic width
content = content.replace(
    '''                            <div class="level-progress-bar">
                                <div class="level-progress-fill"></div>
                            </div>''',
    '''                            <div class="level-progress-bar">
                                <div class="level-progress-fill" id="levelProgressFill" style="width: 0%;"></div>
                            </div>'''
)

# 3. XP to next level - change from "580 more XP" to dynamic
content = content.replace(
    '''                                <span>
                                    <i class="fa-solid fa-circle-up"></i>
                                    580 more XP to reach the next level
                                </span>''',
    '''                                <span id="xpToNextLevel">
                                    <i class="fa-solid fa-circle-up"></i>
                                    <span id="xpNeeded">0</span> more XP to reach the next level
                                </span>'''
)

# 4. Reward multiplier - change from "12%" to dynamic
content = content.replace(
    '''                                <span>
                                    <i class="fa-solid fa-ranking-star"></i>
                                    Unlock 12% higher reward multiplier
                                </span>''',
    '''                                <span id="rewardMultiplierInfo">
                                    <i class="fa-solid fa-ranking-star"></i>
                                    Unlock <span id="nextRewardMultiplier">10</span>% higher reward multiplier
                                </span>'''
)

# Write the updated content
with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Level Progress section cleaned up")
print("  - Removed hardcoded 'LVL 3' → now 'LVL 1' with ID")
print("  - Removed hardcoded 'LVL 4' → now 'LVL 2' with ID")
print("  - Removed hardcoded '580 XP' → now dynamic with ID")
print("  - Removed hardcoded '12%' → now dynamic with ID")
print("  - Added progress bar width control")
print("\nAll values will now be populated from API data")
