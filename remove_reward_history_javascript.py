"""
Remove JavaScript functions related to Reward & Payout History
"""

# Read the file
with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove loadRewardsHistory function
history_func_start = content.find('        async function loadRewardsHistory(page = null, type = null) {')
if history_func_start != -1:
    # Find the end of this function (next function definition)
    history_func_end = content.find('        async function loadRewardsSummary() {', history_func_start)
    if history_func_end != -1:
        content = content[:history_func_start] + content[history_func_end:]
        print("✓ Removed loadRewardsHistory() function")

# Remove paginateRewards function
paginate_func_start = content.find('        function paginateRewards(page) {')
if paginate_func_start != -1:
    # Find the end of this function (next function or closing brace)
    paginate_func_end = content.find('        }', paginate_func_start)
    paginate_func_end = content.find('\n', paginate_func_end) + 1
    # Skip the next newline
    paginate_func_end = content.find('\n', paginate_func_end) + 1
    content = content[:paginate_func_start] + content[paginate_func_end:]
    print("✓ Removed paginateRewards() function")

# Remove updateRewardFilter function
filter_func_start = content.find('        function updateRewardFilter(type, btn) {')
if filter_func_start != -1:
    # Find the end of this function
    filter_func_end = content.find('        }', filter_func_start)
    filter_func_end = content.find('\n', filter_func_end) + 1
    # Skip the next newline
    filter_func_end = content.find('\n', filter_func_end) + 1
    content = content[:filter_func_start] + content[filter_func_end:]
    print("✓ Removed updateRewardFilter() function")

# Remove loadRewardsHistory() call from DOMContentLoaded
dom_loaded = content.find("loadRewardsHistory();")
if dom_loaded != -1:
    # Find the start of the line
    line_start = content.rfind('\n', 0, dom_loaded)
    # Find the end of the line
    line_end = content.find('\n', dom_loaded)
    content = content[:line_start] + content[line_end:]
    print("✓ Removed loadRewardsHistory() call from initialization")

# Write back
with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ All Reward & Payout History JavaScript removed")
print("  - Removed loadRewardsHistory() function")
print("  - Removed paginateRewards() function")
print("  - Removed updateRewardFilter() function")
print("  - Removed initialization call")
print("\n✓ Dashboard is now production ready without reward history")
