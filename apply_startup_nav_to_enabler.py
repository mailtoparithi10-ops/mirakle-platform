#!/usr/bin/env python3
"""
Phase 2: Replace sidebar navigation with top navigation
Preserves all sections and functionality
"""

import re

print("🎨 Phase 2: Updating Navigation Structure")
print("=" * 70)

# Read the current file
with open("templates/enabler_dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

print(f"✅ Read file ({len(content)} characters)")

# Find the body tag and sidebar section
# We need to replace the sidebar with top navigation

# Create the new top navigation HTML
top_nav_html = """<body>
    <!-- Top Nav -->
    <nav class="top-nav">
        <a href="/" class="nav-brand" style="text-decoration: none;">
            <i class="fas fa-hexagon-nodes"></i>
            ALCHEMY
        </a>

        <div class="nav-dropdowns">
            <!-- Dashboard Dropdown -->
            <div class="dropdown" id="dashboardDropdown">
                <button class="dropdown-toggle active" onclick="toggleDropdown('dashboardDropdown')">
                    <i class="fas fa-grid-2"></i> Dashboard <i class="fas fa-chevron-down" style="font-size: 0.7rem;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('overview')"><i class="fas fa-home"></i> Overview</button>
                    <button class="dropdown-item" onclick="showSection('analytics')"><i class="fas fa-chart-line"></i> Analytics</button>
                    <button class="dropdown-item" onclick="showSection('rewards')"><i class="fas fa-coins"></i> Rewards</button>
                </div>
            </div>

            <!-- Programs Dropdown -->
            <div class="dropdown" id="programsDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('programsDropdown')">
                    <i class="fas fa-rocket"></i> Programs <i class="fas fa-chevron-down" style="font-size: 0.7rem;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('programs')"><i class="fas fa-list"></i> My Programs</button>
                    <button class="dropdown-item" onclick="showSection('program-details')"><i class="fas fa-info-circle"></i> Program Details</button>
                </div>
            </div>

            <!-- Referrals Dropdown -->
            <div class="dropdown" id="referralsDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('referralsDropdown')">
                    <i class="fas fa-handshake"></i> Referrals <i class="fas fa-chevron-down" style="font-size: 0.7rem;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('referrals')"><i class="fas fa-users"></i> My Referrals</button>
                    <button class="dropdown-item" onclick="showSection('referral-tracking')"><i class="fas fa-chart-bar"></i> Tracking</button>
                    <button class="dropdown-item" onclick="showSection('guide')"><i class="fas fa-book"></i> Guide</button>
                </div>
            </div>

            <!-- Messages Dropdown -->
            <div class="dropdown" id="messagesDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('messagesDropdown')">
                    <i class="fas fa-envelope"></i> Messages <i class="fas fa-chevron-down" style="font-size: 0.7rem;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('inbox')"><i class="fas fa-inbox"></i> Inbox</button>
                </div>
            </div>
        </div>

        <!-- Profile Dropdown -->
        <div class="dropdown profile-dropdown" id="profileDropdown">
            <div class="profile-toggle dropdown-toggle" onclick="toggleDropdown('profileDropdown')">
                <div class="avatar">
                    {% if current_user.profile_pic %}
                    <img src="{{ current_user.profile_pic }}" alt="Avatar" style="width: 100%; height: 100%; object-fit: cover;">
                    {% else %}
                    {{ current_user.name[0] if current_user.name else 'E' }}
                    {% endif %}
                </div>
                <span class="profile-name">{{ current_user.name }}</span>
                <i class="fas fa-chevron-down" style="color: rgba(255,255,255,0.4); font-size: 0.7rem; margin-left: 5px;"></i>
            </div>
            <div class="dropdown-menu" style="left: auto; right: 0; min-width: 200px;">
                <button class="dropdown-item" onclick="showSection('profile')"><i class="fas fa-user"></i> Profile</button>
                <a href="/" class="dropdown-item" style="text-decoration: none;"><i class="fas fa-house"></i> Back to Home</a>
                <div style="border-top: 1px solid #f1f5f9; margin: 0.5rem 0;"></div>
                <a href="/logout" class="dropdown-item" style="color: #ef4444; text-decoration: none;"><i class="fas fa-right-from-bracket"></i> Sign Out</a>
            </div>
        </div>
    </nav>

"""

# Find and replace the body tag and sidebar
# Pattern to match from <body> to the end of sidebar
pattern = r'<body>.*?</div>\s*<!-- Sidebar End -->'

# If that pattern doesn't exist, try a simpler one
if not re.search(pattern, content, re.DOTALL):
    # Try to find just the sidebar div
    pattern = r'<body>.*?<div class="sidebar">.*?</div>\s*</div>'
    
if not re.search(pattern, content, re.DOTALL):
    # Even simpler - just find body and sidebar
    pattern = r'<body>.*?(?=<div class="main-content">)'

# Replace with new navigation
content = re.sub(pattern, top_nav_html, content, flags=re.DOTALL)

print("✅ Replaced sidebar with top navigation")

# Update the dashboard-content class to remove the height constraint
content = content.replace(
    "height: calc(100vh - 88px);",
    "min-height: calc(100vh - 150px);"
)
print("✅ Updated dashboard-content height")

# Save the file
with open("templates/enabler_dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Saved updated file")
print(f"📊 Final size: {len(content)} characters")
print("\n🎉 Phase 2 Complete: Navigation Structure Updated!")
print("\nNext steps:")
print("1. Test the dashboard in browser")
print("2. Verify all sections are accessible")
print("3. Check dropdown functionality")
print("4. Ensure all data displays correctly")
