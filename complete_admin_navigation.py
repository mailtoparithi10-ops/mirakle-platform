#!/usr/bin/env python3
"""
Complete Admin Dashboard Navigation Transformation
Add top navigation structure to replace sidebar
"""

print("🎨 Completing Admin Dashboard Navigation")
print("=" * 70)

# Read the file
with open("templates/admin_dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

print(f"✅ Read file ({len(content)} characters)")

# Top navigation HTML to add after <body>
top_nav_html = """
    <!-- Top Navigation -->
    <nav class="top-nav">
        <div class="nav-brand">
            <i class="fas fa-shield-alt"></i>
            ADMIN
        </div>
        
        <div class="nav-dropdowns">
            <!-- Dashboard Dropdown -->
            <div class="dropdown" id="dashboardDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('dashboardDropdown')">
                    <i class="fas fa-chart-line"></i>
                    Dashboard
                    <i class="fas fa-chevron-down" style="font-size: 0.7rem; margin-left: 4px;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('dashboard')">
                        <i class="fas fa-home"></i>
                        Overview
                    </button>
                    <button class="dropdown-item" onclick="showSection('analytics')">
                        <i class="fas fa-chart-bar"></i>
                        Analytics
                    </button>
                </div>
            </div>

            <!-- Users Dropdown -->
            <div class="dropdown" id="usersDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('usersDropdown')">
                    <i class="fas fa-users"></i>
                    Users
                    <i class="fas fa-chevron-down" style="font-size: 0.7rem; margin-left: 4px;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('users')">
                        <i class="fas fa-users"></i>
                        All Users
                    </button>
                    <button class="dropdown-item" onclick="showSection('startups')">
                        <i class="fas fa-rocket"></i>
                        Startups
                    </button>
                    <button class="dropdown-item" onclick="showSection('corporate')">
                        <i class="fas fa-building"></i>
                        Corporate
                    </button>
                    <button class="dropdown-item" onclick="showSection('connectors')">
                        <i class="fas fa-handshake"></i>
                        Connectors
                    </button>
                </div>
            </div>

            <!-- Programs Dropdown -->
            <div class="dropdown" id="programsDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('programsDropdown')">
                    <i class="fas fa-trophy"></i>
                    Programs
                    <i class="fas fa-chevron-down" style="font-size: 0.7rem; margin-left: 4px;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('programs')">
                        <i class="fas fa-trophy"></i>
                        All Programs
                    </button>
                    <button class="dropdown-item" onclick="showSection('referrals')">
                        <i class="fas fa-exchange-alt"></i>
                        Referrals
                    </button>
                </div>
            </div>

            <!-- Activity Dropdown -->
            <div class="dropdown" id="activityDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('activityDropdown')">
                    <i class="fas fa-bolt"></i>
                    Activity
                    <i class="fas fa-chevron-down" style="font-size: 0.7rem; margin-left: 4px;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('meetings')">
                        <i class="fas fa-video"></i>
                        Meetings
                    </button>
                    <button class="dropdown-item" onclick="showSection('leads')">
                        <i class="fas fa-hand-holding-heart"></i>
                        Leads
                    </button>
                    <button class="dropdown-item" onclick="showSection('inbox')">
                        <i class="fas fa-envelope"></i>
                        Inbox
                    </button>
                </div>
            </div>

            <!-- Tools Dropdown -->
            <div class="dropdown" id="toolsDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('toolsDropdown')">
                    <i class="fas fa-tools"></i>
                    Tools
                    <i class="fas fa-chevron-down" style="font-size: 0.7rem; margin-left: 4px;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="seedMockData()">
                        <i class="fas fa-database"></i>
                        Seed Mock Data
                    </button>
                    <button class="dropdown-item" onclick="document.getElementById('globalSearchInput').focus()">
                        <i class="fas fa-search"></i>
                        Global Search
                    </button>
                </div>
            </div>

            <!-- Profile Dropdown -->
            <div class="dropdown profile-dropdown" id="profileDropdown">
                <button class="profile-toggle" onclick="toggleDropdown('profileDropdown')">
                    <div class="avatar">A</div>
                    <span class="profile-name">Admin</span>
                    <i class="fas fa-chevron-down" style="font-size: 0.7rem; color: #94a3b8;"></i>
                </button>
                <div class="dropdown-menu" style="right: 0; left: auto;">
                    <button class="dropdown-item" onclick="goToPlatform()">
                        <i class="fas fa-arrow-left"></i>
                        Back to Platform
                    </button>
                    <button class="dropdown-item" onclick="window.location.href='/logout'">
                        <i class="fas fa-sign-out-alt"></i>
                        Logout
                    </button>
                </div>
            </div>
        </div>
    </nav>

"""

# Find <body> tag and insert navigation after it
if "<body>" in content:
    content = content.replace("<body>", "<body>" + top_nav_html)
    print("✅ Added top navigation structure")
else:
    print("❌ Could not find <body> tag")
    exit(1)

# Update the main content wrapper to use new class
content = content.replace('<main class="admin-content">', '<main class="main-content">')
print("✅ Updated main content class")

# Save the file
with open("templates/admin_dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Saved updated file")
print(f"📊 Final size: {len(content)} characters")
print("\n🎉 Admin Dashboard Navigation Complete!")
print("\n✨ Added Features:")
print("   • Modern top navigation bar")
print("   • Dashboard dropdown (Overview, Analytics)")
print("   • Users dropdown (All Users, Startups, Corporate, Connectors)")
print("   • Programs dropdown (All Programs, Referrals)")
print("   • Activity dropdown (Meetings, Leads, Inbox)")
print("   • Tools dropdown (Seed Data, Global Search)")
print("   • Profile dropdown (Back to Platform, Logout)")
print("\n🚀 Next: Run test_admin_dashboard_redesign.py to verify")
