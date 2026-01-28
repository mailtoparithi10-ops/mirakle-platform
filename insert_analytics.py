import os

# Read the analytics section
with open(r'd:\mirakle_platform-1\analytics_section.html', 'r', encoding='utf-8') as f:
    analytics_content = f.read()

# Read the connector dashboard
with open(r'd:\mirakle_platform-1\templates\connector_dashboard.html', 'r', encoding='utf-8') as f:
    dashboard_content = f.read()

# Find the line after </section> for referrals section (around line 4834)
# We'll insert after the referrals section closes
insert_marker = '            </section>\n\n            <!-- ADD REFERRAL MODAL -->'
replacement = f'            </section>\n\n            {analytics_content}\n\n            <!-- ADD REFERRAL MODAL -->'

# Replace
updated_content = dashboard_content.replace(insert_marker, replacement, 1)

# Write back
with open(r'd:\mirakle_platform-1\templates\connector_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("Analytics section successfully inserted!")
