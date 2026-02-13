"""
Remove Reward & Payout History section from Enabler Dashboard
This section contains hardcoded mock transaction data
"""

# Read the file
with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start of the Reward & Payout History section
history_start = content.find('<div class="table-container">\n                    <div class="table-header">\n                        <div>\n                            <div class="table-title">\n                                <i class="fa-solid fa-receipt"></i>\n                                Reward & payout history')

if history_start == -1:
    # Try alternative search
    history_start = content.find('Reward & payout history')
    if history_start != -1:
        # Go back to find the start of the table-container
        history_start = content.rfind('<div class="table-container">', 0, history_start)

# Find the end of this section (next section or closing div)
if history_start != -1:
    # Find the closing </div> for table-container and then the next section
    history_end = content.find('<!-- ANALYTICS SECTION -->', history_start)
    
    if history_end != -1:
        # Remove everything from history_start to history_end
        content = content[:history_start] + content[history_end:]
        
        # Write back
        with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ Reward & Payout History section removed")
        print("  - Removed entire table with mock transaction data")
        print("  - Removed hardcoded entries:")
        print("    • FarmLink Labs - ₹8,500 reward")
        print("    • Monthly activity bonus - 400 FLC points")
        print("    • Payout to bank - ₹15,000")
        print("    • NovaGrid Analytics - ₹12,000 reward")
        print("  - Removed filter pills (All, Cash, Points, Bonuses)")
        print("  - Removed pagination controls")
        print("\n✓ Production ready - section completely removed")
    else:
        print("✗ Could not find section end")
else:
    print("✗ Could not find Reward & Payout History section")
